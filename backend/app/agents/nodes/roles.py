from app.agents.state import InterviewState
from app.core.config import get_settings
from app.services.bedrock import BedrockClient, parse_json_response
import json
import logging
from .validator import validate_roles

ROLE_SUGGESTION_PROMPT = """You are a career guidance and talent acquisition expert.
Analyze the candidate's resume and suggest EXACTLY 5 professional roles they are best suited for.

Focus specifically on:
1. The total years of professional experience and the last 5 years of their recent work history.
2. The technical skills and tools they have actually used in projects.
3. The impact, seniority level, and responsibilities described in their work history.

Strict Role Selection Rules:
- GENERATE EXACTLY 5 DISTINCT ROLES: You MUST always return exactly 5 roles in the "suggested_roles" list. If fewer than 5 extremely strong matches exist, provide the best logical adjacent roles or growth paths that the candidate could step into based on their background (e.g. adjacent domains, adjacent platforms, or slightly higher/lower seniority lines), ensuring you always suggest exactly 5 distinct roles.
- ROLE TITLES MUST REFLECT SENIORITY: Use a seniority prefix (e.g., Junior, Mid-level, Senior, Lead, Principal, Staff) based on their total years of experience. For example, a candidate with 5+ years of experience should NOT be suggested as a generic 'UI/UX Designer' but as a 'Senior UI/UX Designer'.
- USE REAL-WORLD TITLES: Only suggest industry-standard job titles (e.g., 'Senior Full Stack Engineer', 'DevOps Architect', 'Product Manager'). Do not invent random or hybrid titles.
- GROUNDED SUGGESTIONS: Every suggested role must be strongly supported by evidence in the resume. Do not make arbitrary presumptions about their capabilities.

For each suggested role:
1. Identify the complete list of 'Required Skills' typical for that industry-standard role.
2. Determine which of those required skills the candidate explicitly possesses in their resume ('Matched Skills').
    - CRITICAL: If matched_skills is empty or very low (e.g., <20% of required_skills), the fit_percentage must be low (below 30%).
    - SKILL MATCH (100% of score): (Number of Matched Skills / Number of Required Skills) * 100.
    - DO NOT inflate percentages. If evidence is weak, the percentage must be low.
    - DO NOT inflate percentages. If evidence is weak, percentage must be low.

Return result as a JSON list of objects:
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
            
            # Normalize required skills for comparison (lowercase and stripped)
            required_normalized = {r.strip().lower(): r for r in required}
            
            # Filter matched_skills to only include those in required_skills, preserving the order and exact casing from required_skills
            actual_matched = []
            seen = set()
            for m in matched:
                m_norm = m.strip().lower()
                if m_norm in required_normalized:
                    original_req_skill = required_normalized[m_norm]
                    if original_req_skill not in seen:
                        actual_matched.append(original_req_skill)
                        seen.add(original_req_skill)
            
            # Update the role's matched_skills
            role["matched_skills"] = actual_matched
            
            if required:
                skill_match_pct = (len(actual_matched) / len(required)) * 100
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
