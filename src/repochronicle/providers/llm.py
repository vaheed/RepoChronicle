"""OpenAI-compatible chat provider with bounded timeout and safe errors."""

from typing import Any

import httpx
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float = Field(default=0.1, ge=0, le=2)
    max_tokens: int = Field(default=1200, ge=1, le=32000)


class ChatResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    provider_request_id: str | None = None


class ProviderError(RuntimeError):
    """Safe provider-facing failure category without request secrets or raw payloads."""


class OpenAICompatibleChatProvider:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout_seconds: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        if not model:
            raise ValueError("model is required")
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._client = client

    async def complete(self, request: ChatRequest) -> ChatResponse:
        payload = request.model_dump()
        payload["model"] = self._model
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            body: dict[str, Any] = response.json()
        except httpx.TimeoutException as exc:
            raise ProviderError("llm_timeout") from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"llm_http_{exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise ProviderError("llm_transport_error") from exc
        except ValueError as exc:
            raise ProviderError("llm_invalid_json") from exc
        finally:
            if owns_client:
                await client.aclose()

        try:
            choice = body["choices"][0]
            content = choice["message"]["content"]
            usage = body.get("usage", {})
            return ChatResponse(
                content=content if isinstance(content, str) else str(content),
                model=str(body.get("model", self._model)),
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                provider_request_id=response.headers.get("x-request-id"),
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("llm_response_schema_error") from exc
