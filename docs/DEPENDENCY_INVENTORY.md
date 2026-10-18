# Dependency and Artifact Inventory

This inventory describes the intended baseline. Exact resolved versions and transitive licenses must be reviewed in CI and before release.

## Runtime dependencies

| Dependency | Role | Intended license | Included in base runtime |
|---|---|---|---|
| FastAPI | HTTP API | MIT | Yes |
| Uvicorn | ASGI server | BSD-3-Clause | Yes |
| Pydantic / pydantic-settings | Validation and settings | MIT | Yes |
| HTTPX | Provider HTTP client | BSD-3-Clause | Yes |
| certifi (transitive) | CA bundle for HTTPS clients | MPL-2.0 | Transitive only; reviewed, do not modify or vendor without satisfying MPL notices/source requirements |
| asyncpg | Async PostgreSQL driver | Apache-2.0 | Yes |
| redis-py | Valkey protocol client | MIT | Yes |
| MCP Python SDK | MCP server | MIT | Yes |
| aiogram | Telegram Bot API | MIT | Optional `channels` extra |
| discord.py | Discord API | MIT | Optional `channels` extra |
| FastEmbed | Local embedding generation | Apache-2.0 | Optional `local-embeddings` extra |

## Infrastructure images

| Image | Purpose | Intended license notes |
|---|---|---|
| `pgvector/pgvector` | PostgreSQL plus pgvector extension | PostgreSQL License for PostgreSQL and pgvector; review OS image packages |
| `valkey/valkey` | Cache/job protocol backend | BSD-3-Clause |
| `ollama/ollama` | Optional local model server | MIT for the software; model weights have separate terms |

## Development/security tools

Ruff (MIT), pytest (MIT), mypy (MIT), Bandit (Apache-2.0), pip-audit (Apache-2.0), pip-licenses (MIT), and pytest-asyncio (Apache-2.0) are intended development-only dependencies. CI audits the baseline runtime plus channel and local-embedding extras. The optional `training` extra is a planned F6 dependency set and must receive its own full transitive license/security audit before that feature is enabled or distributed.

## Optional external code-intelligence engines

- [CodeGraph](https://github.com/codegraph-ai/CodeGraph), Apache-2.0 upstream; benchmark candidate, not bundled.
- [codesearch](https://github.com/flupkede/codesearch), Apache-2.0 upstream; benchmark candidate, not bundled.

Re-check the exact pinned revision and the licenses of any downloaded model weights before enabling either integration.

## Models

No model weights are included in this starter. The operator selects a model ID/revision and records its license before first use. No inference model should be silently downloaded during image build or repository bootstrap.
