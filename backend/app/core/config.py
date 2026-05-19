from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    langsmith_api_key: str = ""
    langsmith_api_url: str = ""
    langsmith_project: str = "Interview Intelligence"

    model_parsing: str = "google/gemini-2.0-flash-001"
    model_context: str = "google/gemini-2.0-flash-001"
    model_questions: str = "anthropic/claude-3.5-sonnet"
    model_explanation: str = "anthropic/claude-3.5-sonnet"
    model_supervisor: str = "openai/gpt-4.1"

    fallback_models: str = "deepseek/deepseek-chat,openai/gpt-4o-mini"

    max_supervisor_retries: int = 3
    quality_threshold: float = 0.75

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

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
