# ADR 0003: Retrieval and Embedding Spaces

- Status: Accepted
- Date: 2026-10-18

## Context

Different models emit different dimensions and represent text/code differently. The system must be able to change model providers and enable or disable embeddings without a schema redesign.

## Decision

- Keep `EmbeddingProvider` separate from `LLMProvider`.
- Store one metadata record per embedding space: provider/model revision, dimensions, normalization, chunker version, distance metric and license review.
- Store vectors keyed by both chunk and embedding-space ID.
- Build/query an index only for a dimension-compatible embedding space. Use safe per-space indexes or partitions.
- Keep lexical search available when embeddings are disabled or a provider fails.
- Treat model changes as a new space and re-embed in the background; promote only after retrieval evaluation.

## Consequences

- No implicit mixing of vectors from different models.
- Model selection does not become a hard-coded application dependency.
- Production must measure index build and recall before enabling new spaces.
