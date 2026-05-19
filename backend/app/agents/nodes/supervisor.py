from app.agents.state import InterviewState
from app.core.config import get_settings
from app.schemas.interview import SupervisorResult
from app.services.openrouter import OpenRouterClient, parse_json_response

SUPERVISOR_PROMPT = """You are a supervisor agent validating interview question quality for recruiters.

Evaluate the 10 questions and their explanations against these criteria:
1. Technical correctness (no hallucinated concepts)
2. Contextual relevance to JD and resume
3. Non-generic, practical questions
4. Exactly 7 technical + 3 realistic scenario questions
5. Explanation accuracy and conciseness (not too long, no expected answers)
6. Recruiter usefulness

Return ONLY valid JSON with this structure:
{{
  "approved": true/false,
  "quality_score": 0.75,
  "feedback": "actionable feedback if rejected",
  "issues": ["issue1", "issue2"]
}}

Approve only if quality_score >= {threshold} AND all critical checks pass.

Structured context:
{context}

Questions with explanations:
{questions}
"""


async def supervisor_agent(state: InterviewState) -> dict:
    settings = get_settings()
    client = OpenRouterClient()

    questions_payload = [q.model_dump() for q in state["questions"]]

    messages = [
        {
            "role": "user",
            "content": SUPERVISOR_PROMPT.format(
                threshold=settings.quality_threshold,
                context=state["context"].model_dump_json(),
                questions=questions_payload,
            ),
        }
    ]
    response = await client.chat_completion(
        settings.model_supervisor, messages, temperature=0.2, max_tokens=2000, json_mode=True, operation="supervisor"
    )
    data = parse_json_response(response)
    
    # Normalize field names and provide defaults
    normalized_data = {
        "approved": data.get("approved", False),
        "quality_score": float(data.get("quality_score", data.get("score", 0.0))),
        "feedback": str(data.get("feedback", data.get("comments", ""))),
        "issues": data.get("issues", data.get("problems", [])),
    }
    
    # Ensure quality_score is in valid range
    normalized_data["quality_score"] = max(0.0, min(1.0, normalized_data["quality_score"]))
    
    # Ensure issues is a list
    if not isinstance(normalized_data["issues"], list):
        normalized_data["issues"] = []
    
    result = SupervisorResult(**normalized_data)

    retry_count = state.get("retry_count", 0)
    if not result.approved:
        retry_count += 1

    return {
        "supervisor_result": result,
        "supervisor_feedback": result.feedback,
        "retry_count": retry_count,
    }


def should_regenerate(state: InterviewState) -> str:
    """Determine if questions should be regenerated or returned."""
    settings = get_settings()
    result = state.get("supervisor_result")
    retries = state.get("retry_count", 0)

    if result and result.approved and result.quality_score >= settings.quality_threshold:
        return "end"

    if retries >= settings.max_supervisor_retries:
        return "end"

    return "regenerate"
