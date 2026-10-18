import httpx
import pytest

from repochronicle.providers.llm import (
    ChatMessage,
    ChatRequest,
    OpenAICompatibleChatProvider,
    ProviderError,
)


@pytest.mark.asyncio
async def test_openai_compatible_chat_provider_parses_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-key"
        return httpx.Response(
            200,
            headers={"x-request-id": "req-test"},
            json={
                "model": "fixture-model",
                "choices": [{"message": {"role": "assistant", "content": "Grounded answer"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 4},
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleChatProvider(
        base_url="https://llm.example.test/v1",
        model="configured-model",
        api_key="test-key",
        client=client,
    )
    result = await provider.complete(
        ChatRequest(messages=[ChatMessage(role="user", content="Question")], model="ignored")
    )
    await client.aclose()

    assert result.content == "Grounded answer"
    assert result.model == "fixture-model"
    assert result.prompt_tokens == 12
    assert result.provider_request_id == "req-test"


@pytest.mark.asyncio
async def test_provider_error_does_not_expose_response_body() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="sensitive provider response and secret")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleChatProvider(
        base_url="https://llm.example.test/v1",
        model="fixture-model",
        api_key="not-logged",
        client=client,
    )
    with pytest.raises(ProviderError, match="llm_http_401") as exc_info:
        await provider.complete(
            ChatRequest(messages=[ChatMessage(role="user", content="Question")], model="fixture")
        )
    await client.aclose()

    assert "sensitive" not in str(exc_info.value)
    assert "not-logged" not in str(exc_info.value)
