"""Embedding contracts and optional local/remote implementations."""

import asyncio
import math
import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import httpx


@dataclass(frozen=True, slots=True)
class EmbeddingBatch:
    model: str
    dimensions: int
    vectors: tuple[tuple[float, ...], ...]


class EmbeddingProvider(Protocol):
    @property
    def model_name(self) -> str: ...

    async def embed(self, texts: Sequence[str]) -> EmbeddingBatch: ...


class OpenAICompatibleEmbeddingProvider:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout_seconds: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not base_url or not model:
            raise ValueError("base_url and model are required")
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._client = client

    @property
    def model_name(self) -> str:
        return self._model

    async def embed(self, texts: Sequence[str]) -> EmbeddingBatch:
        if not texts:
            return EmbeddingBatch(self._model, 0, ())
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout)
        try:
            response = await client.post(
                f"{self._base_url}/embeddings",
                json={"model": self._model, "input": list(texts)},
                headers=headers,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.TimeoutException as exc:
            raise RuntimeError("embedding_timeout") from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"embedding_http_{exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError("embedding_transport_error") from exc
        except ValueError as exc:
            raise RuntimeError("embedding_invalid_json") from exc
        finally:
            if owns_client:
                await client.aclose()

        try:
            rows = body["data"]
            if not isinstance(rows, list):
                raise TypeError
            indexed_rows = [(row["index"], row["embedding"]) for row in rows]
            indexes = [index for index, _ in indexed_rows]
            if (
                len(indexes) != len(texts)
                or any(not isinstance(index, int) or isinstance(index, bool) for index in indexes)
                or sorted(indexes) != list(range(len(texts)))
            ):
                raise RuntimeError("embedding_response_indexes_invalid")
            ordered = sorted(indexed_rows, key=lambda row: row[0])
            vectors = tuple(tuple(float(value) for value in row[1]) for row in ordered)
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("embedding_response_schema_error") from exc
        if len(vectors) != len(texts):
            raise RuntimeError("embedding_count_mismatch")
        if any(not vector for vector in vectors):
            raise RuntimeError("embedding_dimensions_mismatch")
        if vectors and any(len(vector) != len(vectors[0]) for vector in vectors):
            raise RuntimeError("embedding_dimensions_mismatch")
        if any(not math.isfinite(value) for vector in vectors for value in vector):
            raise RuntimeError("embedding_values_invalid")
        return EmbeddingBatch(self._model, len(vectors[0]) if vectors else 0, vectors)


class LocalFastEmbedProvider:
    """Lazy local CPU embeddings. Requires the optional `local-embeddings` extra."""

    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self._model = model
        self._engine: Any | None = None
        self._initialization_lock = asyncio.Lock()
        self._inference_lock = asyncio.Lock()

    @property
    def model_name(self) -> str:
        return self._model

    async def embed(self, texts: Sequence[str]) -> EmbeddingBatch:
        if not texts:
            return EmbeddingBatch(self._model, 0, ())
        await self._ensure_engine()
        async with self._inference_lock:
            vectors = await asyncio.to_thread(self._embed_sync, list(texts))
        dimensions = len(vectors[0])
        if any(len(vector) != dimensions for vector in vectors):
            raise RuntimeError("embedding_dimensions_mismatch")
        if len(vectors) != len(texts):
            raise RuntimeError("embedding_count_mismatch")
        return EmbeddingBatch(self._model, dimensions, vectors)

    async def _ensure_engine(self) -> None:
        if self._engine is not None:
            return
        async with self._initialization_lock:
            if self._engine is None:
                self._engine = await asyncio.to_thread(self._create_engine)

    def _create_engine(self) -> Any:
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:
            raise RuntimeError(
                "Local embeddings require `pip install '.[local-embeddings]'`"
            ) from exc

        cache_dir = os.getenv("RC_MODEL_CACHE_DIR") or str(
            Path.home() / ".cache" / "repochronicle" / "models"
        )
        return TextEmbedding(model_name=self._model, cache_dir=cache_dir)

    def _embed_sync(self, texts: list[str]) -> tuple[tuple[float, ...], ...]:
        if self._engine is None:
            raise RuntimeError("embedding_engine_not_initialized")
        return tuple(
            tuple(float(value) for value in vector)
            for vector in self._engine.embed(texts)
        )
