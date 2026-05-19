from typing import TypedDict

from app.schemas.interview import (
    ParsedDocument,
    QuestionItem,
    StructuredContext,
    SupervisorResult,
)


class InterviewState(TypedDict, total=False):
    jd_text: str
    resume_text: str
    jd_parsed: ParsedDocument
    resume_parsed: ParsedDocument
    context: StructuredContext
    questions: list[QuestionItem]
    supervisor_result: SupervisorResult
    retry_count: int
    supervisor_feedback: str
