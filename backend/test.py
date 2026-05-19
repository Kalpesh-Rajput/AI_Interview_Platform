import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

try:
    region = os.getenv("AWS_REGION", "ap-south-1")
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

    print("Bearer Token Loaded ✅")
    print(repr(bearer_token[:15] + "..."))

    # Create Bedrock OpenAI-compatible client
    client = OpenAI(
        api_key=bearer_token,
        base_url=f"https://bedrock-runtime.{region}.amazonaws.com/openai/v1"
    )

    # Test Gemma model
    response = client.chat.completions.create(
        model="google.gemma-3-27b-it",
        messages=[
            {
                "role": "user",
                "content": "Generate one technical interview question for a Python backend developer."
            }
        ],
        max_tokens=100,
        temperature=0.4
    )

    print("\nBedrock Working ✅")
    print(response.choices[0].message.content)

except Exception as e:
    print("\nBedrock Error ❌")
    print(e)