import json
import logging
from typing import Any, AsyncIterator

import httpx

from app.core.config import get_settings

try:
    from langsmith.client import Client as LangSmithClient
    from langsmith.schemas import RunTypeEnum
except ImportError:  # pragma: no cover
    LangSmithClient = None  # type: ignore[assignment]
    RunTypeEnum = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class LangSmithLogger:
    def __init__(self, settings):
        self.enabled = False
        self.client = None
        self.project_name = settings.langsmith_project
        if not settings.langsmith_enabled or LangSmithClient is None:
            return
        try:
            self.client = LangSmithClient(
                api_key=settings.langsmith_api_key,
                api_url=settings.langsmith_api_url or None,
            )
            self.enabled = True
        except Exception as exc:
            logger.warning("LangSmith initialization failed: %s", exc)

    def create_run(self, name: str, inputs: dict[str, Any], run_type: str = "llm") -> None:
        if not self.enabled or self.client is None:
            return
        try:
            self.client.create_run(
                name=name,
                inputs=inputs,
                run_type=RunTypeEnum.llm if RunTypeEnum is not None else run_type,
                project_name=self.project_name,
            )
        except Exception as exc:
            logger.warning("LangSmith run logging failed: %s", exc)


class OpenRouterError(Exception):
    pass


class OpenRouterClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.langsmith = LangSmithLogger(self.settings)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://interview-intelligence.app",
            "X-Title": "Interview Intelligence Platform",
        }

    def _models_to_try(self, primary: str) -> list[str]:
        seen: set[str] = set()
        models: list[str] = []
        for m in [primary, *self.settings.fallback_model_list]:
            if m and m not in seen:
                seen.add(m)
                models.append(m)
        return models

    def _log_langsmith_run(
        self,
        operation: str | None,
        model: str,
        messages: list[dict[str, str]],
        content: str,
    ) -> None:
        if not self.langsmith.enabled:
            return
        run_name = f"Interview Intelligence: {operation or 'chat_completion'}"
        inputs = {
            "model": model,
            "messages": messages,
            "response": content,
        }
        self.langsmith.create_run(run_name, inputs, run_type="llm")

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.4,
        max_tokens: int = 4096,
        json_mode: bool = False,
        operation: str | None = None,
    ) -> str:
        if not self.settings.openrouter_api_key:
            raise OpenRouterError("OPENROUTER_API_KEY is not configured.")

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None

        for attempt_model in self._models_to_try(model):
            for retry in range(3):
                try:
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        response = await client.post(
                            f"{self.settings.openrouter_base_url}/chat/completions",
                            headers=self._headers(),
                            json={**payload, "model": attempt_model},
                        )
                    if response.status_code == 429:
                        last_error = OpenRouterError("Rate limited by OpenRouter.")
                        continue
                    if response.status_code >= 500:
                        last_error = OpenRouterError(
                            f"OpenRouter server error ({response.status_code})."
                        )
                        continue
                    if response.status_code >= 400:
                        detail = response.text[:500]
                        raise OpenRouterError(
                            f"OpenRouter request failed ({response.status_code}): {detail}"
                        )

                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    self._log_langsmith_run(operation, attempt_model, messages, content)
                    return content.strip()

                except httpx.RequestError as exc:
                    last_error = exc
                    logger.warning(
                        "OpenRouter request failed model=%s retry=%s: %s",
                        attempt_model,
                        retry,
                        exc,
                    )

        raise OpenRouterError(
            f"All model attempts failed. Last error: {last_error}"
        )

    async def stream_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        if not self.settings.openrouter_api_key:
            raise OpenRouterError("OPENROUTER_API_KEY is not configured.")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.settings.openrouter_base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise OpenRouterError(
                        f"Stream failed ({response.status_code}): {body.decode()[:300]}"
                    )
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        parsed = json.loads(chunk)
                        delta = parsed["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


def parse_json_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        ).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise OpenRouterError(f"Failed to parse JSON from model response: {exc}") from exc
