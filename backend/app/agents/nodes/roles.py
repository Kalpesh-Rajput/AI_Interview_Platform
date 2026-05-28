from app.agents.state import InterviewState
from app.core.config import get_settings
from app.services.bedrock import BedrockClient, parse_json_response

ROLE_SUGGESTION_PROMPT = """You are a career guidance and talent acquisition expert.
Analyze the candidate's resume and suggest between 1 to 5 professional roles they are best suited for.

Focus specifically on:
1. The last 5 years of their professional experience.
2. The technical skills and tools they have actually used in projects.
3. The impact and responsibilities described in their work history.

For each suggested role, provide the information in the following format:
Role: [Role Name]
Technical Skills: [List of relevant technical skills from the resume that make them a fit for this role]
Soft Skills: [List of relevant soft skills or behavioral traits from the resume that match this role]

Return the result as a JSON list of objects:
{{
  "suggested_roles": [
    {{
      "role": "Role Name",
      "technical_skills": "Skill 1, Skill 2, ...",
      "soft_skills": "Skill A, Skill B, ..."
    }}
  ]
}}

Resume content:
{resume_text}
"""

async def role_suggestion_agent(resume_text: str) -> list:
    settings = get_settings()
    client = BedrockClient()

    messages = [
        {
            "role": "user",
            "content": ROLE_SUGGESTION_PROMPT.format(resume_text=resume_text),
        }
    ]

    response = await client.chat_completion(
        settings.model_context, messages, temperature=0.7, json_mode=True, operation="role_suggestion"
    )
    data = parse_json_response(response)
    return data.get("suggested_roles", [])
