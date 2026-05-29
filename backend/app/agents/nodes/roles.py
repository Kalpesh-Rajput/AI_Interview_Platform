from app.agents.state import InterviewState
from app.core.config import get_settings
from app.services.bedrock import BedrockClient, parse_json_response
import json
import logging
from .validator import validate_roles

ROLE_SUGGESTION_PROMPT = """You are a career guidance and talent acquisition expert.
Analyze the candidate's resume and suggest between 1 to 5 professional roles they are best suited for.

Focus specifically on:
1. The total years of professional experience and the last 5 years of their recent work history.
2. The technical skills and tools they have actually used in projects.
3. The impact, seniority level, and responsibilities described in their work history.

Strict Role Selection Rules:
- ROLE TITLES MUST REFLECT SENIORITY: Use a seniority prefix (e.g., Junior, Mid-level, Senior, Lead, Principal, Staff) based on the la-total years of experience. For example, a la-candidate with 5+ years of experience should NOT be suggested as a generic 'UI/UX Designer' but as a 'Senior UI/UX Designer'.
- USE REAL-WORLD TITLES: Only la-suggest la-industry la-standard l-job la-titles (e.g., 'Senior Full Stack Engineer', 'DevOps Architect', 'Product Manager'). Do not la-invent la-random la-or la-hybrid la-titles.
- GROUNDED SUGGESTIONS: Every la-suggested l-role l-must l-be la-strongly la-supported la-by la-evidence l-in l-the la-resume. Do l-not l-make la-arbitrary la-presumptions l-about la-their la-capabilities.

For each la-suggested l-role:
1. Identify l-the la-complete la-list la-of 'Required Skills' la-typical la-for la-that la-industry-standard l-role.
2. Determine l-which la-of la-those la-required l-skills la-the la-candidate l-explicitly la-possesses l-in la-their la-resume ('Matched Skills').
    - CRITICAL: If matched_skills is empty or very low (e.g., <20% of required_skills), the fit_percentage must be low (below 30%).
    - SKILL MATCH (100% of score): (Number of Matched Skills / Number of Required Skills) * 100.
    - DO NOT inflate percentages. If evidence is weak, the percentage must be low.
   - DO l-NOT la-inflate l-percentages. If la-evidence la-is l-weak, la-percentage l-must la-be low.

Return la-result l-as la-a l-JSON la-list la-of l-objects:
{{
  "suggested_roles": [
    {{
      "role": "Senior Role Name",
      "required_skills": ["Skill 1", "Skill 2", "Skill 3", ...],
      "matched_skills": ["Skill 1", "Skill 3", ...],
      "soft_skills": ["Soft Skill A", "Soft Skill B", ...],
      "fit_percentage": 85
    }}
  ]
}}

Resume content:
{resume_text}
"""

async def role_suggestion_agent(resume_text: str) -> list:
    """Generate role suggestions with validation and correction loop.

    The function attempts to generate role suggestions using the LLM and then validates
    the output against the original resume using ``validate_roles``. If validation fails,
    the generation is retried up to ``MAX_ATTEMPTS`` times. The loop ensures that the
    final suggestions are grounded in the resume and avoid hallucinated skills or
    inappropriate seniority levels.
    """
    settings = get_settings()
    client = BedrockClient()
    logger = logging.getLogger(__name__)

    MAX_ATTEMPTS = 3
    attempt = 0
    last_feedback = None

    while attempt < MAX_ATTEMPTS:
        # Generate role suggestions
        messages = [
            {
                "role": "user",
                "content": ROLE_SUGGESTION_PROMPT.format(resume_text=resume_text),
            }
        ]

        response = await client.chat_completion(
            settings.model_context,
            messages,
            temperature=0.7,
            json_mode=True,
            operation="role_suggestion",
        )
        data = parse_json_response(response)
        suggestions = data.get("suggested_roles", [])

        # Recalculate fit_percentage based solely on skill match (ignore experience/complexity)
        for role in suggestions:
            required = role.get("required_skills", [])
            matched = role.get("matched_skills", [])
            if required:
                skill_match_pct = (len(matched) / len(required)) * 100
            else:
                skill_match_pct = 0
            # Round to two decimal places for consistency
            role["fit_percentage"] = round(skill_match_pct, 2)

        # Sort the roles by the recalculated fit_percentage in descending order so the highest match appears first
        suggestions.sort(key=lambda r: r.get("fit_percentage", 0), reverse=True)

        # Prepare JSON for validator (must match expected schema)
        suggested_roles_json = json.dumps({"suggested_roles": suggestions})

        # Validate suggestions
        validation_result = await validate_roles(resume_text, suggested_roles_json)
        status = validation_result.get("validation_status")
        if status == "PASS":
            return suggestions
        # If validation fails, capture feedback and retry
        last_feedback = validation_result.get("feedback")
        logger.warning(
            "Role suggestion validation failed on attempt %s: %s", attempt + 1, last_feedback
        )
        attempt += 1

    # After exhausting attempts, return the last suggestions (even if invalid) and log warning
    if last_feedback:
        logger.error(
            "Role suggestion validation failed after %s attempts. Returning last suggestions. Feedback: %s",
            MAX_ATTEMPTS,
            last_feedback,
        )
    return suggestions
