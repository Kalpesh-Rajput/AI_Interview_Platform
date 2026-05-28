import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agents.graph import run_interview_pipeline
from app.agents.nodes.context import context_extraction_agent
from app.agents.nodes.parsing import parsing_agent
from app.agents.nodes.roles import role_suggestion_agent
from app.agents.nodes.jd_only_questions import jd_only_question_agent
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


@router.post("/generate-jd-only", response_model=GenerateResponse)
async def generate_jd_only(payload: dict):
    jd_text = payload.get("jd_text", "").strip()
    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description text is required.")

    try:
        # Simulate InterviewState for parsing and context extraction
        state = {
            "jd_text": jd_text,
            "resume_text": "No resume provided",
            "retry_count": 0,
            "supervisor_feedback": "",
        }

        # Run parsing
        parsing_result = await parsing_agent(state)
        state.update(parsing_result)

        # Run context extraction
        context_result = await context_extraction_agent(state)
        state.update(context_result)

        # Generate 5 technical questions based on context
        questions = await jd_only_question_agent(state["context"].model_dump_json())

        return GenerateResponse(
            questions=questions,
            context=state["context"],
            retries=0,
            quality_score=1.0,
        )
    except Exception as exc:
        logger.exception("JD-only generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")


@router.post("/suggest-roles")
async def suggest_roles(payload: dict):
    resume_text = payload.get("resume_text", "").strip()
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required.")

    try:
        roles = await role_suggestion_agent(resume_text)
        return {"suggested_roles": roles}
    except Exception as exc:
        logger.exception("Role suggestion failed")
        raise HTTPException(status_code=500, detail=f"Role suggestion failed: {exc}")
