import httpx
import pytest

from repochronicle.providers.embeddings import OpenAICompatibleEmbeddingProvider


@pytest.mark.asyncio
async def test_remote_embedding_provider_orders_vectors_by_index() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 1, "embedding": [0.3, 0.4]},
                    {"index": 0, "embedding": [0.1, 0.2]},
                ]
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://embeddings.example.test/v1",
        model="fixture-model",
        client=client,
    )
    result = await provider.embed(["first", "second"])
    await client.aclose()

    assert result.dimensions == 2
    assert result.vectors == ((0.1, 0.2), (0.3, 0.4))


@pytest.mark.asyncio
async def test_empty_embedding_batch_does_not_call_provider() -> None:
    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://embeddings.example.test/v1",
        model="fixture-model",
    )
    result = await provider.embed([])
    assert result.dimensions == 0
    assert result.vectors == ()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rows",
    [
        [{"index": 0, "embedding": [0.1]}, {"index": 0, "embedding": [0.2]}],
        [{"index": 1, "embedding": [0.1]}, {"index": 2, "embedding": [0.2]}],
    ],
)
async def test_remote_embedding_provider_rejects_duplicate_or_missing_indexes(rows) -> None:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"data": rows}))
    )
    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://embeddings.example.test/v1",
        model="fixture-model",
        client=client,
    )

    with pytest.raises(RuntimeError, match="embedding_response_indexes_invalid"):
        await provider.embed(["first", "second"])
    await client.aclose()


@pytest.mark.asyncio
async def test_remote_embedding_provider_rejects_non_finite_values() -> None:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
                lambda _: httpx.Response(
                    200,
                    content=b'{"data":[{"index":0,"embedding":[Infinity]}]}',
                    headers={"content-type": "application/json"},
                )
        )
    )
    provider = OpenAICompatibleEmbeddingProvider(
        base_url="https://embeddings.example.test/v1",
        model="fixture-model",
        client=client,
    )

    with pytest.raises(RuntimeError, match="embedding_values_invalid"):
        await provider.embed(["first"])
    await client.aclose()
