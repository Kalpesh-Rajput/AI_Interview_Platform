import json
import logging
import asyncio
import os
from typing import Any, AsyncIterator
from concurrent.futures import ThreadPoolExecutor

import botocore.exceptions

from app.core.config import get_settings

try:
    import boto3
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    import botocore.parsers
except ImportError:
    raise ImportError("boto3 is required for Bedrock integration. Install it with: pip install boto3")

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


class BedrockError(Exception):
    pass


class BedrockClient:
    """AWS Bedrock client for LLM interactions using bearer token authentication."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.langsmith = LangSmithLogger(self.settings)
        self._executor = ThreadPoolExecutor(max_workers=3)
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Bedrock Runtime client with bearer token authentication."""
        if not self.settings.aws_bearer_token_bedrock:
            raise BedrockError("AWS_BEARER_TOKEN_BEDROCK is not configured.")

        if not self.settings.aws_region:
            raise BedrockError("AWS_REGION is not configured.")

        try:
            # Create Bedrock Runtime client with dummy credentials since we use bearer token auth
            self.client = boto3.client(
                "bedrock-runtime",
                region_name=self.settings.aws_region,
                aws_access_key_id="dummy",
                aws_secret_access_key="dummy",
            )

            # Configure bearer token authentication by modifying the client's auth handler
            self._configure_bearer_token_auth()

            logger.info(
                "Bedrock client initialized successfully with region=%s",
                self.settings.aws_region,
            )
        except Exception as exc:
            raise BedrockError(f"Failed to initialize Bedrock client: {exc}") from exc

    def _configure_bearer_token_auth(self) -> None:
        """Configure bearer token authentication for Bedrock API calls."""
        original_make_request = self.client._make_api_call

        def make_request_with_bearer_token(operation_name, api_params):
            # Intercept and add bearer token to the request
            try:
                result = original_make_request(operation_name, api_params)
                return result
            except Exception as exc:
                # If auth fails, try with bearer token in headers
                if "UnauthorizedException" in str(exc) or "AuthorizationException" in str(exc):
                    logger.debug("Retrying with bearer token authentication")
                raise

        # Add bearer token to the session headers
        if hasattr(self.client, "_session"):
            session = self.client._session
            session.user_agent_extra = f"bearer-token-auth"

        # Set up custom event handler for adding bearer token
        def add_bearer_token(request, **kwargs):
            request.headers["Authorization"] = f"Bearer {self.settings.aws_bearer_token_bedrock}"

        self.client.meta.events.register("before-send", add_bearer_token)

    def _models_to_try(self, primary: str) -> list[str]:
        """Get list of models to try, including fallback models."""
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
        """Log run to LangSmith if enabled."""
        if not self.langsmith.enabled:
            return
        run_name = f"Interview Intelligence: {operation or 'bedrock_invoke'}"
        inputs = {
            "model": model,
            "messages": messages,
            "response": content,
        }
        self.langsmith.create_run(run_name, inputs, run_type="llm")

    def _prepare_bedrock_messages(self, messages: list[dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Bedrock prompt format."""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n".join(prompt_parts)

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
        """Invoke Bedrock model with retry logic and timeout handling."""
        if not self.settings.aws_bearer_token_bedrock:
            raise BedrockError("AWS_BEARER_TOKEN_BEDROCK is not configured.")

        last_error: Exception | None = None

        for attempt_model in self._models_to_try(model):
            for retry in range(3):
                try:
                    # Prepare the prompt
                    prompt = self._prepare_bedrock_messages(messages)
                    if json_mode:
                        prompt += "\n\nReturn ONLY valid JSON."

                    # Prepare request body for Bedrock
                    body = json.dumps({
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "system": self._extract_system_prompt(messages),
                    })

                    # Run in executor to handle blocking I/O
                    loop = asyncio.get_event_loop()
                    response = await asyncio.wait_for(
                        loop.run_in_executor(
                            self._executor,
                            self._invoke_bedrock,
                            attempt_model,
                            body,
                        ),
                        timeout=120.0,
                    )

                    content = response
                    self._log_langsmith_run(operation, attempt_model, messages, content)
                    return content.strip()

                except asyncio.TimeoutError:
                    last_error = BedrockError(f"Request timeout for model {attempt_model}")
                    logger.warning(
                        "Bedrock request timeout model=%s retry=%s",
                        attempt_model,
                        retry,
                    )
                    continue

                except botocore.exceptions.BotoCoreError as exc:
                    last_error = exc
                    logger.warning(
                        "Bedrock request failed model=%s retry=%s: %s",
                        attempt_model,
                        retry,
                        exc,
                    )
                    continue

                except botocore.exceptions.ClientError as exc:
                    error_code = exc.response.get("Error", {}).get("Code", "Unknown")
                    if error_code == "ThrottlingException":
                        last_error = BedrockError("Rate limited by Bedrock.")
                        continue
                    if error_code in ["ServiceUnavailableException", "InternalServerError"]:
                        last_error = BedrockError(f"Bedrock server error: {error_code}")
                        continue
                    if error_code == "UnauthorizedException":
                        raise BedrockError(
                            f"Authentication failed. Check AWS_BEARER_TOKEN_BEDROCK and AWS_REGION: {error_code}"
                        ) from exc

                    # Other client errors
                    detail = str(exc)[:500]
                    raise BedrockError(f"Bedrock request failed: {detail}") from exc

                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        "Bedrock request error model=%s retry=%s: %s",
                        attempt_model,
                        retry,
                        exc,
                    )
                    continue

        raise BedrockError(f"All model attempts failed. Last error: {last_error}")

    def _invoke_bedrock(self, model: str, body: str) -> str:
        """Synchronous wrapper for Bedrock API call."""
        try:
            response = self.client.invoke_model(
                modelId=model,
                body=body,
                contentType="application/json",
                accept="application/json",
            )

            response_body = json.loads(response["body"].read().decode("utf-8"))

            # Extract content from response based on model type
            # Handle OpenAI-style format (choices array)
            if "choices" in response_body:
                choices = response_body["choices"]
                if isinstance(choices, list) and len(choices) > 0:
                    message = choices[0].get("message", {})
                    return message.get("content", "")
            # Handle Bedrock native format
            elif "content" in response_body:
                content = response_body["content"]
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get("text", "")
            elif "output" in response_body:
                return response_body["output"]
            elif "completion" in response_body:
                return response_body["completion"]
            elif "text" in response_body:
                return response_body["text"]

            # Fallback: convert entire response to string
            logger.warning("Unexpected Bedrock response format: %s", response_body)
            return json.dumps(response_body)

        except json.JSONDecodeError as exc:
            raise BedrockError(f"Failed to parse Bedrock response JSON: {exc}") from exc

    def _extract_system_prompt(self, messages: list[dict[str, str]]) -> str:
        """Extract system prompt from messages if present."""
        for msg in messages:
            if msg.get("role") == "system":
                return msg.get("content", "")
        return ""

    async def stream_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Stream completion from Bedrock model."""
        if not self.settings.aws_bearer_token_bedrock:
            raise BedrockError("AWS_BEARER_TOKEN_BEDROCK is not configured.")

        try:
            # Prepare the prompt
            prompt = self._prepare_bedrock_messages(messages)

            # Prepare request body for Bedrock streaming
            body = json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": self._extract_system_prompt(messages),
            })

            # Run streaming in executor
            loop = asyncio.get_event_loop()
            async for chunk in await asyncio.wait_for(
                loop.run_in_executor(
                    self._executor,
                    self._stream_bedrock,
                    model,
                    body,
                ),
                timeout=120.0,
            ):
                yield chunk

        except asyncio.TimeoutError:
            raise BedrockError("Stream request timeout")

    def _stream_bedrock(self, model: str, body: str) -> AsyncIterator[str]:
        """Synchronous wrapper for Bedrock streaming API call."""
        try:
            response = self.client.invoke_model_with_response_stream(
                modelId=model,
                body=body,
                contentType="application/json",
            )

            event_stream = response.get("body")
            for event in event_stream:
                if "chunk" in event:
                    chunk = json.loads(event["chunk"]["bytes"].decode("utf-8"))
                    if "content" in chunk:
                        content = chunk["content"]
                        if isinstance(content, list) and len(content) > 0:
                            yield content[0].get("text", "")
                    elif "output" in chunk:
                        yield chunk["output"]

        except Exception as exc:
            raise BedrockError(f"Stream failed: {exc}") from exc


def parse_json_response(text: str) -> dict[str, Any]:
    """Parse JSON response from model, handling markdown code blocks."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        ).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise BedrockError(f"Failed to parse JSON from model response: {exc}") from exc
