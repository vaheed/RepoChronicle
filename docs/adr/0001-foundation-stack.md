# ADR 0001: Foundation Stack

- Status: Accepted for the starter; revisit only through a documented ADR.
- Date: 2026-10-18

## Context

The project needs self-hosting, permissive dependency licenses, read-only source ingestion, embeddings from the start, optional local/cloud models, a stable MCP interface, and one-command local startup.

## Decision

- Python 3.12 for API, orchestration and connectors.
- FastAPI for the HTTP control/query plane.
- PostgreSQL as durable source of truth; `pgvector` for vector data.
- Valkey for queue/cache primitives, avoiding reliance on the current Redis server license.
- Redis-protocol client (`redis-py`) for Valkey communication.
- Official MCP Python SDK behind a separate MCP service.
- `httpx` for provider adapters and OpenAI-compatible APIs.
- Local embeddings as a lazy, optional FastEmbed/ONNX adapter.
- OpenAI-compatible chat adapter to support OpenAI and compatible hosted/local endpoints.
- Docker Compose as the development/bootstrap deployment; services can be split horizontally later.

## Consequences

- One operational database initially, with vector storage in the same system.
- Optional model weights are not embedded in container images.
- Embedding spaces explicitly store model and dimensions; indexes are not shared across incompatible vectors.
- Provider logic does not belong in API route handlers.
- Fine-tuning requires an independent, opt-in training subsystem and is not in the request path.
