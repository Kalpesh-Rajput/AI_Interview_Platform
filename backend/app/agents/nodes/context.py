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
- jd_explanation_for_hr: (string) A comprehensive, clear, and detailed explanation of the role expectations mentioned in the Job Description. It must be written in a highly professional and easy-to-understand way (5-8 sentences), specifically outlining what the candidate will be doing, the core expectations of the role, the business or technical impact of their work, and why this position is crucial for the team's success. Make sure to capture the expectations and requirements of the role in depth.
- extracted_skills_with_levels: (list of objects) Every technical skill, language, database, tool, or concept found ONLY in the Job Description. Do NOT include skills that are present only in the resume but not in the JD. Each object MUST have "skill" and "level" keys. Do NOT omit any skill mentioned in the JD.
- self_rating_questions: (list of strings) Exactly 5 concise, punchy, and conversational single-liner screening questions based on the core skills or tools in the Job Description. Each question must have a natural human touch (easy and friendly for a recruiter to ask) and ask the candidate about their years of experience, self-rated level (e.g., out of 10 or Beginner/Intermediate/Expert), or confidence/understanding level for that specific skill or tool.

Example response:
{{
  "technical_stack": ["Python", "React"],
  "normalized_technologies": ["Python", "React"],
  "project_domains": ["fintech"],
  "role_requirements": ["REST APIs", "database design"],
  "jd_summary": "Looking for...",
  "resume_summary": "Experienced...",
  "experience_level": "Mid",
  "jd_explanation_for_hr": "This role is for a Senior Software Engineer who will spearhead the design and development of our next-generation web platforms. The candidate is expected to architect robust, scalable backend APIs using Python (FastAPI/Django) and construct highly responsive, fluid user interfaces with React and Tailwind CSS. They will collaborate closely with product managers and UX designers to translate business requirements into efficient technical solutions. Beyond writing high-quality code, the engineer will champion engineering best practices, mentor junior team members, and drive containerization and CI/CD automation efforts. Ultimately, their contributions will directly enhance platform reliability, optimize database performance, and deliver a frictionless user experience for millions of global customers.",
  "extracted_skills_with_levels": [
    {{"skill": "Python", "level": "Mid"}},
    {{"skill": "React", "level": "Intermediate"}},
    {{"skill": "REST APIs", "level": "Advanced"}}
  ],
  "self_rating_questions": [
    "How many years have you worked with Python, and how would you rate yourself out of 10?",
    "How would you rate your experience with React (Beginner, Mid, or Expert), and what is your rating out of 10?",
    "What is your self-rating out of 10 for building REST APIs, and what is your total years of experience?",
    "How confident are you with database indexing and query optimization on a scale of 1 to 10?",
    "Have you set up production CI/CD pipelines before, and how would you rate your expertise?"
  ]
}}

Rules:
- Merge JD requirements with resume evidence for fields other than extracted_skills_with_levels and self_rating_questions
- The extracted_skills_with_levels and self_rating_questions MUST be extracted/derived ONLY from the Job Description (JD), NOT from the resume.
- All self_rating_questions MUST be short, punchy, conversational single-liners (with a friendly human touch) testing years of experience or self-ratings for core JD skills. They must be direct and easy to ask.
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
            normalized["jd_explanation_for_hr"] = str(data[key])[:3000]
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
