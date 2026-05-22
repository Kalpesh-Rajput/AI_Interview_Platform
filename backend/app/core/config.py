from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AWS Bedrock Configuration
    aws_bearer_token_bedrock: str = ""
    aws_region: str = "ap-south-1"

    # OpenRouter Configuration (Legacy - kept for backwards compatibility)
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    langsmith_api_key: str = ""
    langsmith_api_url: str = ""
    langsmith_project: str = "Interview Intelligence"

    model_parsing: str = "google.gemma-3-27b-it"
    model_context: str = "google.gemma-3-27b-it"
    model_questions: str = "google.gemma-3-27b-it"
    model_explanation: str = "google.gemma-3-27b-it"
    model_supervisor: str = "google.gemma-3-27b-it"

    fallback_models: str = ""

    max_supervisor_retries: int = 3
    quality_threshold: float = 0.75

    cors_origins: str

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def fallback_model_list(self) -> list[str]:
        return [m.strip() for m in self.fallback_models.split(",") if m.strip()]

    @property
    def langsmith_enabled(self) -> bool:
        return bool(self.langsmith_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.langsmith_enabled:
        import os
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        if settings.langsmith_project:
            os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        if settings.langsmith_api_url:
            os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_api_url
    return settings


import contextvars
from typing import Any
# ContextVar to track accumulated token usage and cost within a request
token_tracker: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar("token_tracker", default=None)


def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> dict[str, float]:
    """Estimate model cost in USD based on input/output tokens."""
    input_rate = 0.00000015
    output_rate = 0.00000060
    
    name_lower = model_name.lower()
    if "gemma-3-27b" in name_lower:
        input_rate = 0.00000027
        output_rate = 0.00000027
    elif "gemma" in name_lower:
        input_rate = 0.00000010
        output_rate = 0.00000010
    elif "llama-3-8b" in name_lower or "llama3-8b" in name_lower or "llama-3.1-8b" in name_lower:
        input_rate = 0.00000005
        output_rate = 0.00000008
    elif "llama-3-70b" in name_lower or "llama3-70b" in name_lower or "llama-3.1-70b" in name_lower:
        input_rate = 0.00000035
        output_rate = 0.00000040
    elif "claude-3-5-sonnet" in name_lower:
        input_rate = 0.00000300
        output_rate = 0.00001500
    elif "claude-3-haiku" in name_lower:
        input_rate = 0.00000025
        output_rate = 0.00000125
        
    input_cost = (input_tokens or 0) * input_rate
    output_cost = (output_tokens or 0) * output_rate
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost
    }

