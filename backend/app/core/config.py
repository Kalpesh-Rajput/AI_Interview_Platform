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
    return Settings()
