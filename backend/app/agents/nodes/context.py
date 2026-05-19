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

Example response:
{{
  "technical_stack": ["Python", "React"],
  "normalized_technologies": ["Python", "React"],
  "project_domains": ["fintech"],
  "role_requirements": ["REST APIs", "database design"],
  "jd_summary": "Looking for...",
  "resume_summary": "Experienced...",
  "experience_level": "Mid"
}}

Rules:
- Merge JD requirements with resume evidence
- Be specific and accurate based on inputs
- If data is missing, use appropriate defaults
- Max 15 items per list

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
