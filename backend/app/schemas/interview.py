from typing import Literal

from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    question: str
    difficulty: Literal["Medium", "Hard"]
    related_technology: str
    explanation: str
    answer: str = ""
    category: Literal["technical", "scenario"] = "technical"


class ParsedDocument(BaseModel):
    raw_text: str
    technologies: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    frameworks_tools: list[str] = Field(default_factory=list)


class SkillWithLevel(BaseModel):
    skill: str
    level: str


class StructuredContext(BaseModel):
    technical_stack: list[str] = Field(default_factory=list)
    normalized_technologies: list[str] = Field(default_factory=list)
    project_domains: list[str] = Field(default_factory=list)
    role_requirements: list[str] = Field(default_factory=list)
    jd_summary: str = ""
    resume_summary: str = ""
    experience_level: str = ""
    jd_explanation_for_hr: str = ""
    extracted_skills_with_levels: list[SkillWithLevel] = Field(default_factory=list)
    self_rating_questions: list[str] = Field(default_factory=list)


class SupervisorResult(BaseModel):
    approved: bool
    quality_score: float = Field(ge=0, le=1)
    feedback: str = ""
    issues: list[str] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    questions: list[QuestionItem]
    context: StructuredContext | None = None
    retries: int = 0
    quality_score: float = 0.0


class GenerateRequest(BaseModel):
    jd_text: str
    resume_text: str
