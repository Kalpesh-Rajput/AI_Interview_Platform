from app.agents.state import InterviewState
from app.core.config import get_settings
from app.schemas.interview import QuestionItem
from app.services.openrouter import OpenRouterClient, parse_json_response

EXPLANATION_PROMPT = """You are an interview explanation agent helping recruiters understand what each question evaluates.

For each question, write a SHORT explanation (2-4 sentences max) that:
- Explains what the question is testing
- Explains why it matters for this role/candidate
- Provides quick technical context
- Is technically accurate — do NOT hallucinate or invent incorrect details
- Does NOT include expected answers or long rubrics

Return ONLY valid JSON with this structure:
{{
  "explanations": [
    {{"index": 0, "explanation": "explanation text"}},
    {{"index": 1, "explanation": "explanation text"}},
    ...
  ]
}}

Questions:
{questions}

Role context:
{context}
"""


async def explanation_agent(state: InterviewState) -> dict:
    settings = get_settings()
    client = OpenRouterClient()

    questions_payload = [
        {
            "index": i,
            "question": q.question,
            "difficulty": q.difficulty,
            "related_technology": q.related_technology,
            "category": q.category,
        }
        for i, q in enumerate(state["questions"])
    ]

    messages = [
        {
            "role": "user",
            "content": EXPLANATION_PROMPT.format(
                questions=questions_payload,
                context=state["context"].model_dump_json(),
            ),
        }
    ]
    response = await client.chat_completion(
        settings.model_explanation, messages, temperature=0.3, max_tokens=4000, json_mode=True, operation="explanation"
    )
    data = parse_json_response(response)

    updated: list[QuestionItem] = []
    explanation_map = {}
    
    # Handle both direct and alternative field names
    explanations = data.get("explanations", data.get("answers", []))
    for item in explanations:
        idx = item.get("index", item.get("idx", 0))
        explanation = item.get("explanation", item.get("text", "Evaluates relevant technical understanding for this role."))
        explanation_map[int(idx)] = str(explanation)[:500]

    for i, q in enumerate(state["questions"]):
        explanation = explanation_map.get(i, "Evaluates relevant technical understanding for this role.")
        updated.append(q.model_copy(update={"explanation": explanation}))

    return {"questions": updated}
