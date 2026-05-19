from app.agents.state import InterviewState
from app.schemas.interview import ParsedDocument
from app.services.openrouter import OpenRouterClient, parse_json_response
from app.core.config import get_settings

PARSING_PROMPT = """You are a document parsing agent for interview preparation.

Extract structured information from the document. Return ONLY a JSON object with EXACTLY these fields:
- raw_text: (string, max 1000 chars) Summary of the document's key content
- technologies: (list of strings) Technology names found
- projects: (list of strings) Project descriptions or names
- experience: (list of strings) Experience/role highlights
- frameworks_tools: (list of strings) Frameworks, libraries, or tools mentioned

You MUST return valid JSON with ALL these exact field names.

Example response structure:
{{
  "raw_text": "Summary here",
  "technologies": ["tech1", "tech2"],
  "projects": ["project1"],
  "experience": ["exp1"],
  "frameworks_tools": ["framework1"]
}}

Rules:
- Only extract facts stated or clearly implied
- Do not invent technologies, projects, or experience
- Keep each list to max 15 items
- Normalize tech names (React.js -> React)
- If a field has no content, use empty array [] or empty string ""

Document type: {doc_type}
---
{content}
"""


def _normalize_parsed_data(data: dict) -> dict:
    """Normalize LLM response to match ParsedDocument schema."""
    normalized = {
        "raw_text": "",
        "technologies": [],
        "projects": [],
        "experience": [],
        "frameworks_tools": [],
    }
    
    if not data:
        return normalized
    
    # Map common alternative field names to our schema
    field_mappings = {
        "raw_text": ["raw_text", "summary", "overview", "description"],
        "technologies": ["technologies", "tech", "skills", "technologies_found", "required_skills"],
        "projects": ["projects", "project_descriptions", "portfolio", "work_samples"],
        "experience": ["experience", "work_experience", "professional_experience", "employment", "responsibilities"],
        "frameworks_tools": ["frameworks_tools", "tools", "libraries", "frameworks", "technical_tools"],
    }
    
    for target_field, alternatives in field_mappings.items():
        for alt_field in alternatives:
            if alt_field in data:
                value = data[alt_field]
                if value:
                    if isinstance(value, str):
                        normalized[target_field] = value if target_field == "raw_text" else [value]
                    elif isinstance(value, list):
                        normalized[target_field] = value
                break
    
    # Ensure all fields are the correct type
    normalized["raw_text"] = str(normalized.get("raw_text", ""))[:1000]
    normalized["technologies"] = [str(t)[:100] for t in normalized.get("technologies", []) if t][:15]
    normalized["projects"] = [str(p)[:200] for p in normalized.get("projects", []) if p][:15]
    normalized["experience"] = [str(e)[:200] for e in normalized.get("experience", []) if e][:15]
    normalized["frameworks_tools"] = [str(f)[:100] for f in normalized.get("frameworks_tools", []) if f][:15]
    
    return normalized


async def parsing_agent(state: InterviewState) -> dict:
    settings = get_settings()
    client = OpenRouterClient()

    jd_parsed = await _parse_document(client, settings.model_parsing, state["jd_text"], "Job Description")
    resume_parsed = await _parse_document(
        client, settings.model_parsing, state["resume_text"], "Resume"
    )

    return {"jd_parsed": jd_parsed, "resume_parsed": resume_parsed}


async def _parse_document(
    client: OpenRouterClient, model: str, content: str, doc_type: str
) -> ParsedDocument:
    truncated = content[:12000]
    if not truncated.strip():
        # Return empty document if content is empty
        return ParsedDocument(raw_text=f"Empty {doc_type}")
    
    messages = [
        {
            "role": "user",
            "content": PARSING_PROMPT.format(doc_type=doc_type, content=truncated),
        }
    ]
    response = await client.chat_completion(model, messages, temperature=0.2, json_mode=True, operation="parsing")
    data = parse_json_response(response)
    
    # Normalize the data before creating ParsedDocument
    normalized_data = _normalize_parsed_data(data)
    return ParsedDocument(**normalized_data)
