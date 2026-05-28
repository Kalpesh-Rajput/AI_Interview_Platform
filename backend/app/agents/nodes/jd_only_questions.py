import json
from app.agents.state import InterviewState
from app.core.config import get_settings
from app.schemas.interview import QuestionItem
from app.services.bedrock import BedrockClient, parse_json_response

JD_ONLY_QUESTIONS_PROMPT = """You are an expert technical interviewer.
Generate EXACTLY 5 technical interview questions based ONLY on the provided job description context.

Requirements:
- Questions must be based solely on the required technologies, skills, and responsibilities in the JD.
- They should test fundamental and advanced knowledge of the role's requirements.
- Avoid generic questions; make them specific to the JD's context.
- Difficulty must be one of: Medium, Hard.
- Each question must include a detailed answer (6-8 sentences).

Return ONLY valid JSON with this structure:
{{
    "questions": [
        {{
            "question": "question text",
            "difficulty": "Medium",
            "related_technology": "Tech Name",
            "category": "technical",
            "answer": "Detailed answer text"
        }}
    ]
}}

Context:
{context}
"""

async def jd_only_question_agent(context_json: str) -> list[QuestionItem]:
    settings = get_settings()
    client = BedrockClient()

    messages = [
        {
            "role": "user",
            "content": JD_ONLY_QUESTIONS_PROMPT.format(context=context_json),
        }
    ]
    response = await client.chat_completion(
        settings.model_questions, messages, temperature=0.5, max_tokens=4000, json_mode=True, operation="jd_only_generation"
    )
    data = parse_json_response(response)

    raw_questions = data.get("questions", [])
    questions = []
    for q in raw_questions:
        try:
            questions.append(QuestionItem(
                question=q.get("question", ""),
                difficulty=q.get("difficulty", "Medium") if q.get("difficulty") in ["Medium", "Hard"] else "Medium",
                related_technology=q.get("related_technology", "General"),
                category="technical",
                answer=q.get("answer", ""),
                explanation=""
            ))
        except Exception:
            continue

    return questions[:5]
