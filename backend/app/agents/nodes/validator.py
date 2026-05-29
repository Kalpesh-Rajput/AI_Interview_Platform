"""Local validator for role suggestion output.

The original implementation called the LLM again to validate the generated
roles. For reliability and speed we now perform the validation locally. The
validator checks two things:

1. **Hallucinated matched skills** – every skill listed in ``matched_skills``
   must appear verbatim (case‑insensitive) in the original ``resume_text``.
2. **Fit percentage consistency** – the ``fit_percentage`` reported by the
   generator must reflect the proportion of matched skills to required skills.
   The project specification now states that the threshold is based *only* on
   skill match, so we compute ``skill_match_pct = (len(matched) / len(required)) *
   100`` and compare it to the supplied ``fit_percentage`` (allowing a small
   tolerance of ±5%).

If all roles pass these checks the function returns ``{"validation_status":
"PASS"}``. Otherwise it returns ``{"validation_status": "FAIL", "feedback":
<details>}`` where ``feedback`` contains a human‑readable description of the
issues.
"""

from __future__ import annotations

import json
import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


def _skill_in_resume(skill: str, resume_text: str) -> bool:
    """Return ``True`` if *skill* appears in *resume_text* (case‑insensitive).

    The check uses a word‑boundary regex to avoid partial matches (e.g., ``"SQL"``
    should not match ``"NoSQL"``). Non‑alphanumeric characters in the skill are
    escaped.
    """
    pattern = r"\b" + re.escape(skill) + r"\b"
    return re.search(pattern, resume_text, flags=re.IGNORECASE) is not None


def _validate_role(role: Dict, resume_text: str) -> List[str]:
    """Validate a single role dictionary.

    Returns a list of feedback strings for any problems found.
    """
    feedback: List[str] = []
    role_name = role.get("role", "<unknown>")
    required: List[str] = role.get("required_skills", [])
    matched: List[str] = role.get("matched_skills", [])
    fit = role.get("fit_percentage")

    # 1. Hallucinated matched skills
    for skill in matched:
        if not _skill_in_resume(skill, resume_text):
            feedback.append(
                f"Role '{role_name}': matched skill '{skill}' not found in resume."
            )

    # 2. Fit percentage consistency (skill‑match only)
    if required:
        skill_match_pct = (len(matched) / len(required)) * 100
        if isinstance(fit, (int, float)):
            if abs(fit - skill_match_pct) > 5:
                feedback.append(
                    f"Role '{role_name}': fit_percentage {fit} does not match skill match percentage {skill_match_pct:.1f}."
                )
        else:
            feedback.append(
                f"Role '{role_name}': fit_percentage is missing or not a number."
            )
    else:
        feedback.append(
            f"Role '{role_name}': required_skills list is empty, cannot validate fit_percentage."
        )

    return feedback


async def validate_roles(resume_text: str, suggested_roles_json: str) -> dict:
    """Validate the JSON output from ``role_suggestion_agent``.

    The function parses ``suggested_roles_json`` (a JSON string containing a
    ``suggested_roles`` list) and runs the local checks described above. It
    returns a dictionary compatible with the original contract:

    ``{"validation_status": "PASS"}`` or ``{"validation_status": "FAIL",
    "feedback": "..."}``.
    """
    try:
        data = json.loads(suggested_roles_json)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse suggested_roles_json: %s", exc)
        return {"validation_status": "FAIL", "feedback": "Invalid JSON in suggested_roles_json."}

    roles = data.get("suggested_roles", [])
    all_feedback: List[str] = []
    for role in roles:
        all_feedback.extend(_validate_role(role, resume_text))

    if not all_feedback:
        return {"validation_status": "PASS"}
    return {"validation_status": "FAIL", "feedback": " ".join(all_feedback)}
