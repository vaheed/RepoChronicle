# License and Artifact Policy

## Project license

RepoChronicle's original source code is licensed under Apache-2.0. Contributors must only submit material they have the right to license under Apache-2.0 and must preserve third-party notices where applicable.

A repository license does not relicense the models, data, containers, or external services used with the project.

## Dependency policy

Prefer permissive licenses compatible with commercial use and redistribution, including Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, PostgreSQL License, and similarly permissive licenses after review. A small number of unmodified transitive dependencies may use MPL-2.0; these are explicitly reviewed and must not be modified or vendored without satisfying that license’s source and notice requirements.

Do not introduce AGPL, SSPL, BUSL, source-available/non-OSI licenses, non-commercial terms, or an unknown license into a distributed runtime dependency without explicit maintainer approval and legal review. If a dependency has a dual or combined license, evaluate the exact selected license path, not just the most permissive option in a package page.

The CI script is intentionally fail-closed on unknown or unapproved dependency-license labels. Normalize scanner output when package metadata is ambiguous; do not simply add a broad exception to make CI green. CI currently audits the baseline runtime plus the channel and local-embedding extras. The optional training extra must be separately installed and audited as part of F6 because its transitive set is larger and not part of the default runtime.

## Initial technology/license review

The table records intended usage, not a substitute for checking the exact versions and transitive dependencies used in a release.

| Component | Purpose | Intended license / terms | Policy |
|---|---|---|---|
| Python 3.12 | Runtime | PSF License | Allowed |
| FastAPI | API | MIT | Allowed |
| Pydantic / pydantic-settings | Schemas/configuration | MIT | Allowed |
| HTTPX | HTTP client | BSD-3-Clause | Allowed |
| asyncpg | PostgreSQL driver | Apache-2.0 | Allowed |
| SQL migration scripts | Schema | Project-owned | Apache-2.0 |
| PostgreSQL | Relational store | PostgreSQL License | Allowed |
| pgvector extension/image | Vector storage | PostgreSQL License | Allowed |
| Valkey | Queue/cache protocol | BSD-3-Clause | Selected instead of Redis server to avoid Redis' current source-available licensing issues |
| redis-py client | Valkey/Redis protocol client | MIT | Allowed |
| MCP Python SDK | MCP tools/transports | MIT | Allowed |
| aiogram | Telegram Bot API | MIT | Optional connector dependency |
| discord.py | Discord API | MIT | Optional connector dependency |
| FastEmbed | Local embedding runtime | Apache-2.0 | Optional runtime; audit transitive deps |
| CodeGraph | Optional out-of-process code engine | Apache-2.0 upstream | Evaluate a pinned release in F3; not vendored or installed as a Python dependency |
| codesearch | Optional out-of-process code search engine | Apache-2.0 upstream | Evaluate a pinned release in F3; not vendored or installed as a Python dependency |
| Ollama | Optional local model runtime | MIT for Ollama software | Runtime license does not grant rights to the downloaded models |
| Transformers / TRL / PEFT | Optional future fine-tuning | Apache-2.0 for these projects | Planned optional training stack; each model/data source needs separate review |
| Any LLM/embedding weights | Inference artifact | Model-specific | Never bundled by default; require documented license/terms/privacy approval |
| OpenAI-compatible remote API | External service | Provider terms | Operator must assess price, retention, region and data-use terms |

## Container images

Pin production images by digest, generate an SBOM, and review image base distribution and package licenses. Tags in the development Compose file are convenience defaults and are not a production supply-chain guarantee.

## Model licenses and datasets

Before enabling a model:
- identify the exact repository and immutable model revision;
- save the model license and relevant terms in the deployment inventory;
- check commercial use, redistribution, attribution, acceptable-use, output and user-count limitations;
- check whether the model requires accepting a click-through agreement;
- confirm the intended deployment mode and jurisdiction;
- review training data rights for fine-tuning;
- record quantized/converted model provenance separately.

Do not call a model "open source" solely because its weights are downloadable or because its inference runtime is open source.

## License inventory

Every new dependency/extra/container/model must be added to `docs/DEPENDENCY_INVENTORY.md`. CI runs metadata-based license checks for installed Python distributions. Release CI should later attach an SBOM and a complete container/model manifest.
