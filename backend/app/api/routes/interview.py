import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agents.graph import run_interview_pipeline
from app.schemas.interview import (
    GenerateRequest,
    GenerateResponse,
    QuestionItem,
    StructuredContext,
)
from app.services.file_parser import extract_text_from_bytes

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/upload/jd")
async def upload_jd(file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = extract_text_from_bytes(content, file.filename or "jd.txt")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"filename": file.filename, "text": text, "preview": text[:500]}


@router.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = extract_text_from_bytes(content, file.filename or "resume.txt")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"filename": file.filename, "text": text, "preview": text[:500]}


@router.post("/generate", response_model=GenerateResponse)
async def generate_questions(payload: GenerateRequest):
    if not payload.jd_text.strip() or not payload.resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Both job description and resume text are required.",
        )

    try:
        result = await run_interview_pipeline(
            payload.jd_text.strip(),
            payload.resume_text.strip(),
        )
    except Exception as exc:
        logger.exception("Interview generation failed")
        raise HTTPException(
            status_code=500,
            detail=f"Question generation failed: {exc}",
        ) from exc

    raw_questions = result.get("questions", [])
    questions: list[QuestionItem] = []
    for q in raw_questions:
        if isinstance(q, QuestionItem):
            questions.append(q)
        elif isinstance(q, dict):
            questions.append(QuestionItem(**q))
        else:
            questions.append(QuestionItem(**q.model_dump()))

    context = result.get("context")
    if context and not isinstance(context, StructuredContext):
        context = StructuredContext(**context.model_dump() if hasattr(context, "model_dump") else context)

    return GenerateResponse(
        questions=questions,
        context=context,
        retries=result.get("retries", 0),
        quality_score=result.get("quality_score", 0.0),
    )
