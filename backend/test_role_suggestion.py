"""
Test script for the role suggestion validation‑correction loop.

This script does not require real AWS Bedrock credentials. It monkey‑patches
``app.agents.nodes.roles.BedrockClient`` to return a deterministic mock response
that includes a hallucinated skill. The ``role_suggestion_agent`` will then invoke
the validation loop, detect the failure, retry up to the maximum attempts, and
finally return the (still invalid) suggestions while logging the validation
feedback.
"""

import asyncio
import json
import sys
import importlib
import os
from pathlib import Path

# Ensure the project root is on the import path
sys.path.append(str(Path(__file__).parent.parent))

# Import the target function and the module containing the Bedrock client
# Import the role suggestion agent from the correct package path.
from backend.app.agents.nodes.roles import role_suggestion_agent
import backend.app.agents.nodes.roles as roles_module


class MockBedrockClient:
    """Mock Bedrock client that returns a fixed response containing a hallucinated skill.

    The response mimics the structure expected by ``parse_json_response``.
    """

    async def chat_completion(self, *args, **kwargs):
        """Return a deterministic JSON string based on the requested operation.

        The real ``BedrockClient.chat_completion`` returns a plain string containing the
        model's response (already stripped). Our mock mirrors that behavior by returning a
        JSON string that ``parse_json_response`` can consume.
        """
        operation = kwargs.get("operation")
        # Role suggestion operation returns a JSON with a hallucinated matched skill.
        if operation == "role_suggestion":
            return json.dumps(
                {
                    "suggested_roles": [
                        {
                            "role": "Senior UI/UX Designer",
                            "required_skills": ["Design", "Prototyping", "User Research"],
                            "matched_skills": ["Design", "Data Analysis"],
                            "soft_skills": ["Communication"],
                            "fit_percentage": 85,
                        }
                    ]
                }
            )
        # Validation operation returns a FAIL status with feedback about the hallucination.
        if operation == "role_validation":
            return json.dumps(
                {
                    "validation_status": "FAIL",
                    "feedback": "Matched skill 'Data Analysis' not found in resume.",
                }
            )
        # Default fallback – return an empty JSON object.
        return json.dumps({})


async def main():
    # Ensure required environment variables for Settings are present.
    # ``cors_origins`` is required in Settings; an empty string is acceptable for tests.
    os.environ.setdefault("CORS_ORIGINS", "")

    # Sample resume text that does NOT contain "Data Analysis"
    resume_text = (
        "John Doe\n"
        "Software Engineer with 5 years experience in Python, FastAPI, SQL, and AWS.\n"
    )

    # Monkey‑patch the BedrockClient used inside ``role_suggestion_agent`` and the validator.
    # The validator imports BedrockClient from ``app.services.bedrock`` directly, so we need to
    # patch that reference as well.
    import backend.app.services.bedrock as bedrock_module

    # Patch the roles module (generator) and the Bedrock service module to use the mock client.
    original_roles_client = roles_module.BedrockClient
    original_bedrock_client = bedrock_module.BedrockClient

    roles_module.BedrockClient = MockBedrockClient
    bedrock_module.BedrockClient = MockBedrockClient
    try:
        suggestions = await role_suggestion_agent(resume_text)
        print("Final suggestions returned by role_suggestion_agent:")
        print(json.dumps(suggestions, indent=2))
    finally:
        # Restore original client classes to avoid side effects for other tests or runtime.
        roles_module.BedrockClient = original_roles_client
        bedrock_module.BedrockClient = original_bedrock_client


if __name__ == "__main__":
    asyncio.run(main())
