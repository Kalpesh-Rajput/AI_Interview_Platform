import json
import logging
from typing import Any, AsyncIterator

import httpx

from app.core.config import get_settings

try:
    from langsmith import traceable
except ImportError:
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    pass


class OpenRouterClient:
    def __init__(self) -> None:
        self.settings = get_settings()

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



    @traceable(name="OpenRouter Chat Completion", run_type="llm")
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

                    usage = data.get("usage", {})
                    input_tokens = usage.get("prompt_tokens")
                    output_tokens = usage.get("completion_tokens")

                    try:
                        from langsmith import get_current_run_tree
                        run_tree = get_current_run_tree()
                        if run_tree:
                            if run_tree.metadata is None:
                                run_tree.metadata = {}
                            run_tree.metadata.update({
                                "ls_provider": "openrouter",
                                "ls_model_name": attempt_model,
                            })
                            if input_tokens is not None or output_tokens is not None:
                                from app.core.config import estimate_cost
                                cost_dict = estimate_cost(attempt_model, input_tokens or 0, output_tokens or 0)
                                
                                usage_block = {
                                    "input_tokens": input_tokens or 0,
                                    "output_tokens": output_tokens or 0,
                                    "total_tokens": (input_tokens or 0) + (output_tokens or 0),
                                    "prompt_tokens": input_tokens or 0,
                                    "completion_tokens": output_tokens or 0,
                                    "input_cost": cost_dict["input_cost"],
                                    "output_cost": cost_dict["output_cost"],
                                    "total_cost": cost_dict["total_cost"]
                                }
                                
                                try:
                                    if run_tree.outputs is None:
                                        run_tree.outputs = {}
                                    run_tree.outputs["usage_metadata"] = usage_block
                                    run_tree.outputs["response_metadata"] = {
                                        "token_usage": {
                                            "prompt_tokens": input_tokens or 0,
                                            "completion_tokens": output_tokens or 0,
                                            "total_tokens": (input_tokens or 0) + (output_tokens or 0)
                                        }
                                    }
                                except Exception as set_exc:
                                    logger.warning("Failed to set usage_metadata in outputs: %s", set_exc)

                                try:
                                    if run_tree.extra is None:
                                        run_tree.extra = {}
                                    run_tree.extra["token_usage"] = {
                                        "prompt_tokens": input_tokens or 0,
                                        "completion_tokens": output_tokens or 0,
                                        "total_tokens": (input_tokens or 0) + (output_tokens or 0)
                                    }
                                    run_tree.extra["usage_metadata"] = usage_block
                                    
                                    # update metadata (which is stored in extra['metadata'])
                                    if run_tree.metadata is not None:
                                        run_tree.metadata["usage_metadata"] = usage_block
                                        run_tree.metadata["token_usage"] = {
                                            "prompt_tokens": input_tokens or 0,
                                            "completion_tokens": output_tokens or 0,
                                            "total_tokens": (input_tokens or 0) + (output_tokens or 0)
                                        }
                                except Exception as set_exc:
                                    logger.warning("Failed to set extra/metadata token usage: %s", set_exc)
                                try:
                                    from app.core.config import token_tracker
                                    tracker = token_tracker.get()
                                    if tracker is not None:
                                        tracker["prompt_tokens"] += input_tokens or 0
                                        tracker["completion_tokens"] += output_tokens or 0
                                        tracker["input_cost"] = tracker.get("input_cost", 0.0) + cost_dict["input_cost"]
                                        tracker["output_cost"] = tracker.get("output_cost", 0.0) + cost_dict["output_cost"]
                                        tracker["total_cost"] = tracker.get("total_cost", 0.0) + cost_dict["total_cost"]
                                except Exception as tracker_exc:
                                    logger.warning("Failed to update token tracker: %s", tracker_exc)
                    except Exception as exc:
                        logger.warning("Failed to log usage to LangSmith: %s", exc)

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

    @traceable(name="OpenRouter Stream Completion", run_type="llm")
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
