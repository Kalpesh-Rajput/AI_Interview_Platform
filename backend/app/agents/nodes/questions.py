import json
from app.agents.state import InterviewState
from app.core.config import get_settings
from app.schemas.interview import QuestionItem
from app.services.bedrock import BedrockClient, parse_json_response

QUESTION_PROMPT = """You are an expert technical interviewer helping recruiters prepare contextual questions.

Generate EXACTLY 10 interview questions based on the structured context below.

Distribution (strict):
- 7 knowledge-checking questions (category: "technical") - based SOLELY on job description skills and requirements
- 3 scenario-based deep evaluation questions (category: "scenario") - based EXCLUSIVELY on candidate's actual resume experience

Requirements:
- Technical questions (first 7) must be based ONLY on the job description technologies and role requirements.
- CRITICAL: If the job description explicitly mentions 'client requirements', prioritize these heavily; the majority of the technical questions must be derived directly from those specific requirements.
- Avoid generic textbook questions (e.g. "What is OOP?", "Explain REST").
- Technical questions should test: conceptual understanding, implementation knowledge, architectural awareness, debugging approach, and real-world reasoning related to the job requirements.
- Scenario questions (last 3) must simulate real production situations: outages, scaling, API failures, performance, deployment, DB optimization, etc.
- Scenario questions should feel like senior engineer interview discussions.
- Scenario questions must be based EXCLUSIVELY on the candidate's actual resume experience items and projects. Do NOT invent, assume, or extrapolate any experience not explicitly stated in the resume.
- Do NOT invent new candidate experiences, companies, or accomplishments that are not present in the resume for scenario questions.
- Ensure each question is unique and not repeated or lightly paraphrased.
- Difficulty must be one of: Medium, Hard
- Do NOT include explanations yet (only question, difficulty, related_technology, category, answer).

Distribution specifics:
 - Exactly 10 questions total.
 - Exactly 3 questions must be category `scenario`.
 - The remaining 7 must be category `technical` and among these exactly 4 must be `Medium` and 3 must be `Hard`.
 - question difficulty must be `Medium` or `Hard`.

{feedback_block}

Return ONLY valid JSON with EXACTLY this structure; include an `answer` field with a detailed response of 6-8 sentences explaining the correct approach, reasoning, and practical implications, including concrete examples, comparisons, and tradeoffs:
{{
    "questions": [
        {{
            "question": "question text",
            "difficulty": "Medium",
            "related_technology": "Tech Name",
            "category": "technical",
            "answer": "Detailed answer text with reasoning and examples"
        }}
    ]
}}

Job description context (for technical questions):
{context}

Candidate resume experience (for scenario questions ONLY):
{resume_experience}
"""


async def question_generation_agent(state: InterviewState) -> dict:
    settings = get_settings()
    client = BedrockClient()

    feedback_block = ""
    if state.get("supervisor_feedback"):
        feedback_block = (
            f"Previous attempt was rejected. Improve based on this feedback:\n"
            f"{state['supervisor_feedback']}\n"
        )

    resume_experience = state["resume_parsed"].experience if state.get("resume_parsed") else []
    messages = [
        {
            "role": "user",
            "content": QUESTION_PROMPT.format(
                context=state["context"].model_dump_json(),
                resume_experience=json.dumps(resume_experience, ensure_ascii=False, indent=2),
                feedback_block=feedback_block,
            ),
        }
    ]
    response = await client.chat_completion(
        settings.model_questions, messages, temperature=0.5, max_tokens=6000, json_mode=True, operation="question_generation"
    )
    data = parse_json_response(response)
    
    # Handle both 'questions' and alternative field names
    raw_questions = data.get("questions", data.get("interview_questions", []))
    questions: list[QuestionItem] = []
    
    for q in raw_questions:
        try:
            # Normalize field names and include answer
            q_data = {
                "question": q.get("question", q.get("text", "")),
                "difficulty": q.get("difficulty", q.get("level", "Medium")),
                "related_technology": q.get("related_technology", q.get("technology", "General")),
                "category": q.get("category", "technical"),
                "explanation": "",
                "answer": q.get("answer", q.get("solution", "")),
            }

            # Normalize difficulty to allowed values
            if q_data["difficulty"] not in ["Medium", "Hard"]:
                alt = str(q_data["difficulty"]).capitalize()
                q_data["difficulty"] = "Hard" if alt == "Hard" else "Medium"

            # Validate category
            if q_data["category"] not in ["technical", "scenario"]:
                q_data["category"] = "technical"

            questions.append(QuestionItem(**q_data))
        except Exception:
            # Skip malformed questions
            continue

    technical = [q for q in questions if q.category == "technical"]
    scenario = [q for q in questions if q.category == "scenario"]

    if len(questions) != 10 or len(technical) != 7 or len(scenario) != 3:
        questions = _rebalance_questions(questions)

    # Ensure difficulty distribution among the 7 technical questions: exactly 4 Medium and 3 Hard
    tech_indices = [i for i, q in enumerate(questions) if q.category == "technical"][:7]

    # Ensure no 'Easy' exists and normalize types
    for i in tech_indices:
        if questions[i].difficulty not in ["Medium", "Hard"]:
            questions[i] = questions[i].model_copy(update={"difficulty": "Medium"})

    # Count current
    medium_idxs = [i for i in tech_indices if questions[i].difficulty == "Medium"]
    hard_idxs = [i for i in tech_indices if questions[i].difficulty == "Hard"]

    # Convert extras to satisfy counts
    while len(medium_idxs) > 4:
        idx = medium_idxs.pop()
        questions[idx] = questions[idx].model_copy(update={"difficulty": "Hard"})
        hard_idxs.append(idx)

    while len(medium_idxs) < 4 and hard_idxs:
        idx = hard_idxs.pop()
        questions[idx] = questions[idx].model_copy(update={"difficulty": "Medium"})
        medium_idxs.append(idx)

    # Ensure scenario questions are not Easy
    for i, q in enumerate(questions):
        if q.category == "scenario" and q.difficulty not in ["Medium", "Hard"]:
            questions[i] = q.model_copy(update={"difficulty": "Medium"})

    return {"questions": questions[:10]}


def _rebalance_questions(questions: list[QuestionItem]) -> list[QuestionItem]:
    """Ensure 7 technical + 3 scenario questions."""
    for i, q in enumerate(questions):
        if i < 7 and q.category != "technical":
            questions[i] = q.model_copy(update={"category": "technical"})
        elif i >= 7 and q.category != "scenario":
            questions[i] = q.model_copy(update={"category": "scenario"})
    
    while len(questions) < 10:
        idx = len(questions)
        cat = "technical" if idx < 7 else "scenario"
        questions.append(
            QuestionItem(
                question="Placeholder — regeneration required.",
                difficulty="Medium",
                related_technology="General",
                explanation="",
                category=cat,
            )
        )
    return questions[:10]
