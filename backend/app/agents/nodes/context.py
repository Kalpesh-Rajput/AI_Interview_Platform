from app.agents.state import InterviewState
from app.core.config import get_settings
from app.schemas.interview import StructuredContext
from app.services.bedrock import BedrockClient, parse_json_response

CONTEXT_PROMPT = """You are a context extraction agent for technical interviews.

Analyze the parsed job description and resume data. Return ONLY valid JSON with EXACTLY these fields:
- technical_stack: (list of strings) Combined technologies from both documents
- normalized_technologies: (list of strings) Deduplicated normalized tech names
- project_domains: (list of strings) Application domains (fintech, e-commerce, etc)
- role_requirements: (list of strings) Key responsibilities and required skills from JD
- jd_summary: (string) 2-3 sentence summary of job description
- resume_summary: (string) 2-3 sentence summary of candidate
- experience_level: (string) One of: Junior, Mid, Senior, or Lead
- jd_explanation_for_hr: (string) A brief, non-technical explanation (3-4 sentences) of the Job Description, written specifically for HR/recruiters who do not have a technical background, explaining what the role does and why it is important.
- extracted_skills_with_levels: (list of objects) Every technical skill, language, database, tool, or concept found in the Job Description, along with its required/preferred level of experience or proficiency (e.g. Mid, Senior, Lead, Intermediate, Advanced, etc.). Each object MUST have "skill" and "level" keys. Do NOT omit any skill mentioned.
- self_rating_questions: (list of strings) Exactly 5 basic questions asking the candidate how they would rate themselves for these extracted skills and to explain their experience (e.g., "On a scale of 1 to 10, how would you rate your proficiency in Python, and what real-world projects support this rating?").

Example response:
{{
  "technical_stack": ["Python", "React"],
  "normalized_technologies": ["Python", "React"],
  "project_domains": ["fintech"],
  "role_requirements": ["REST APIs", "database design"],
  "jd_summary": "Looking for...",
  "resume_summary": "Experienced...",
  "experience_level": "Mid",
  "jd_explanation_for_hr": "This role is for a software engineer who will build web applications. They will use Python for backend logic and React for the user interface. Their work will help our customers have a faster and smoother checkout experience.",
  "extracted_skills_with_levels": [
    {{"skill": "Python", "level": "Mid"}},
    {{"skill": "React", "level": "Intermediate"}},
    {{"skill": "REST APIs", "level": "Advanced"}}
  ],
  "self_rating_questions": [
    "On a scale of 1-10, how would you rate your experience and proficiency with Python?",
    "How would you rate your skills in React and building responsive frontends?",
    "How would you rate your experience in designing and developing REST APIs?",
    "On a scale of 1-10, how comfortable are you with SQL databases and query optimization?",
    "How would you rate your experience in team collaboration and agile workflows?"
  ]
}}

Rules:
- Merge JD requirements with resume evidence
- Be specific and accurate based on inputs
- If data is missing, use appropriate defaults
- Max 15 items per list (except extracted_skills_with_levels which should capture all skills in JD)

Job Description parsed:
{jd_parsed}

Resume parsed:
{resume_parsed}
"""


def _normalize_context_data(data: dict) -> dict:
    """Normalize LLM response to match StructuredContext schema."""
    normalized = {
        "technical_stack": [],
        "normalized_technologies": [],
        "project_domains": [],
        "role_requirements": [],
        "jd_summary": "",
        "resume_summary": "",
        "experience_level": "Mid",
        "jd_explanation_for_hr": "",
        "extracted_skills_with_levels": [],
        "self_rating_questions": [],
    }
    
    if not data:
        return normalized
    
    # Map alternative field names
    field_mappings = {
        "technical_stack": ["technical_stack", "tech_stack", "technologies"],
        "normalized_technologies": ["normalized_technologies", "technologies", "tech"],
        "project_domains": ["project_domains", "domains", "industry"],
        "role_requirements": ["role_requirements", "requirements", "skills"],
        "jd_summary": ["jd_summary", "job_summary", "position_overview"],
        "resume_summary": ["resume_summary", "candidate_summary", "profile_summary"],
        "experience_level": ["experience_level", "level", "seniority"],
    }
    
    for target_field, alternatives in field_mappings.items():
        for alt_field in alternatives:
            if alt_field in data:
                value = data[alt_field]
                if value:
                    if target_field in ["jd_summary", "resume_summary", "experience_level"]:
                        normalized[target_field] = str(value)[:500]
                    else:
                        if isinstance(value, str):
                            normalized[target_field] = [value]
                        elif isinstance(value, list):
                            normalized[target_field] = value
                break

    # Map the new fields
    jd_explanation_keys = ["jd_explanation_for_hr", "jd_explanation", "explanation_for_hr", "hr_explanation", "hr_jd_summary", "jd_hr_explanation"]
    for key in jd_explanation_keys:
        if key in data:
            normalized["jd_explanation_for_hr"] = str(data[key])[:800]
            break

    skills_keys = ["extracted_skills_with_levels", "skills_with_levels", "skills_levels"]
    raw_skills = []
    for key in skills_keys:
        if key in data and isinstance(data[key], list):
            raw_skills = data[key]
            break
            
    # Process raw_skills list
    for item in raw_skills:
        if isinstance(item, dict):
            skill_name = str(item.get("skill", item.get("name", ""))).strip()
            level_name = str(item.get("level", item.get("experience", "Mid"))).strip()
            if skill_name:
                normalized["extracted_skills_with_levels"].append({
                    "skill": skill_name[:100],
                    "level": level_name[:50]
                })
        elif isinstance(item, str):
            # If skill is just a string, e.g. "Python: Mid"
            if ":" in item:
                parts = item.split(":", 1)
                skill_name = parts[0].strip()
                level_name = parts[1].strip()
            else:
                skill_name = item.strip()
                level_name = "Mid"
            if skill_name:
                normalized["extracted_skills_with_levels"].append({
                    "skill": skill_name[:100],
                    "level": level_name[:50]
                })

    questions_keys = ["self_rating_questions", "rating_questions", "basic_questions"]
    for key in questions_keys:
        if key in data and isinstance(data[key], list):
            normalized["self_rating_questions"] = [str(q)[:300] for q in data[key] if q][:5]
            break
    
    # Ensure proper types and limits
    normalized["technical_stack"] = [str(t)[:100] for t in normalized.get("technical_stack", []) if t][:15]
    normalized["normalized_technologies"] = [str(t)[:100] for t in normalized.get("normalized_technologies", []) if t][:15]
    normalized["project_domains"] = [str(d)[:100] for d in normalized.get("project_domains", []) if d][:15]
    normalized["role_requirements"] = [str(r)[:150] for r in normalized.get("role_requirements", []) if r][:15]
    
    # Validate experience level
    valid_levels = ["Junior", "Mid", "Senior", "Lead"]
    if normalized["experience_level"] not in valid_levels:
        normalized["experience_level"] = "Mid"
    
    return normalized


async def context_extraction_agent(state: InterviewState) -> dict:
    settings = get_settings()
    client = BedrockClient()

    messages = [
        {
            "role": "user",
            "content": CONTEXT_PROMPT.format(
                jd_parsed=state["jd_parsed"].model_dump_json(),
                resume_parsed=state["resume_parsed"].model_dump_json(),
            ),
        }
    ]
    response = await client.chat_completion(
        settings.model_context, messages, temperature=0.2, json_mode=True, operation="context_extraction"
    )
    data = parse_json_response(response)
    
    # Normalize the data before creating StructuredContext
    normalized_data = _normalize_context_data(data)
    context = StructuredContext(**normalized_data)
    return {"context": context}
