# Architecture

## Goals

RepoChronicle is a self-hosted, multi-project knowledge service for code, engineering activity, and opt-in team conversations. It should scale by adding worker capacity and indexes, not by replacing the core data model.

Primary requirements:
- Read-only repository access.
- Full initial repository scan at a pinned commit; incremental updates afterward.
- Provider-independent Git, chat, LLM, embedding, vector, and MCP interfaces.
- Evidence provenance and honest freshness status.
- Retrieval that returns bounded context instead of whole repositories.
- Tenant-aware authorization across all ingested source material.
- Local models and OpenAI-compatible APIs.
- Optional fine-tuning which is never needed for normal operation.
- A single Docker Compose entry point for the baseline deployment.

## Logical components

### 1. Control plane API
Owns organizations, projects, sources, permissions, configuration, job requests, status, and administrative operations. It does not clone repositories or run long LLM jobs in request handlers.

### 2. Provider adapters
Implement source-specific operations behind contracts:
- Git providers: resolve revisions, fetch content, list events, consume webhooks, and reconcile cursors.
- Chat platforms: subscribe to authorized destinations, normalize messages, honor provider permissions, and send replies only after policy approval.
- LLM providers: chat/completion and optional tool-call semantics.
- Embedding providers: batch texts, return vectors plus model/dimension metadata.
- MCP: expose stable, read-only tools to external harnesses.

Adapters must return normalized domain events and source evidence. Provider-specific IDs are always retained alongside normalized IDs.

### 3. Durable job/event layer
Valkey is used as a Redis-protocol-compatible queue/cache backend under the permissive BSD-3-Clause Valkey license. PostgreSQL remains the durable source of truth. Queue messages are hints to work; job state, idempotency, checkpoints, and audit records are stored durably in PostgreSQL.

Job requirements:
- Stable idempotency key.
- Source/tenant scope.
- Lease and lease expiry.
- Retry count and categorized error.
- Checkpoint for last completed stage/cursor/SHA.
- Dead-letter reason and safe replay.
- Correlation ID and timestamps.

### 4. Repository ingestion and code intelligence
A repository source has a provider, canonical URL, selected branch/ref, and a recorded indexed SHA. The first scan is pinned to an explicit SHA. A source is not `ready` until required initial scan stages have completed and verification passes.

An initial scan creates:
- File manifest and stable content hashes.
- Language/file classifications and exclusion reasons.
- Chunks with repository, path, commit, line range, symbol, and content hash.
- Symbol/reference/dependency edges where a parser supports them.
- Text-search entries.
- Optional embeddings for each configured embedding space.
- Activity records for the available provider history window.

After bootstrap, sync fetches only changes since the last indexed SHA/cursor. Periodic reconciliation compares provider state against durable checkpoints to repair missed webhooks.

### 5. Knowledge storage
PostgreSQL stores tenancy, projects, registered sources, normalized activity, conversation messages, sync state, jobs, evidence references, memory facts, audit events, and retrieval metadata. `pgvector` stores embeddings.

Why Postgres + pgvector first:
- One operationally familiar durable data system.
- Relational filters for tenant and source ACLs can be applied before vector ranking.
- Lexical and relational queries can be combined with vector retrieval.
- Vector support is available at the first schema version without forcing every installation to run another database.

Vector storage uses **embedding spaces** keyed by provider, model/version, dimensions, distance metric, and normalization policy. Different models must not share an embedding space unless their vector dimensions and semantics are explicitly compatible. Dynamic per-space vector indexes can be created for the active dimensions; never cast arbitrary rows into the wrong dimension to satisfy an index.

A separate vector database adapter may be added later for measured reasons; it is not required for the baseline topology.

### 6. Retrieval and answer generation
The retrieval plan is query-dependent:
1. Resolve requester identity and authorized project/channel scope.
2. Classify query intent: exact symbol/file, semantic concept, time-bounded activity, architecture/dependency, conversation, or mixed.
3. Run lexical and/or dense search against the allowed scope.
4. Optionally expand through symbols/dependency graph or related Git/chat events.
5. Deduplicate and rank evidence; include revision/date/permissions/freshness metadata.
6. Fit evidence into a configured token/character budget.
7. Call the selected LLM with untrusted evidence clearly delimited.
8. Verify citations map to retrieved evidence and return an answer with sources and freshness.
9. Record a privacy-aware trace; do not retain prompts containing secrets by default.

A vector score is not proof. Exact symbol searches should retain lexical retrieval; time/history questions should start with relational event queries. Fine-tuning does not replace retrieval.

### 7. Shared MCP and chat interfaces
All external interfaces call the same authorization-aware application services. Telegram must not have a separate, weaker data access path than MCP. Chat destinations require explicit registration and opt-in. The bot can be configured as mention-only, reply-only, or proactive for selected types of event; proactive mode is not the default.

### 8. Model runtime
`LLMProvider` and `EmbeddingProvider` are separate contracts:
- Local chat: Ollama, vLLM, or llama.cpp server through an OpenAI-compatible API.
- Hosted chat: OpenAI or any compatible endpoint configured by the operator. API terms, prices, retention and regional processing remain provider-specific.
- Local embeddings: built-in adapter backed by FastEmbed/ONNX on CPU.
- Hosted embeddings: configurable OpenAI-compatible endpoint.
- Fine-tuning: optional training-job adapter, initially planned; not loaded at runtime unless explicitly promoted.

Model files are external artifacts, not source code dependencies. Each selected model must pass its own license/privacy/performance review.

## Deployment topology

Default Compose services:
- `db`: PostgreSQL with pgvector.
- `valkey`: queue/cache.
- `migrate`: one-shot schema upgrade.
- `api`: control/query API.
- `worker`: asynchronous ingestion/indexing jobs.
- `mcp`: Streamable HTTP MCP endpoint.
- `connectors`: Telegram/Discord event adapters, idle when no tokens are configured.

Optional `local-llm` profile starts Ollama. Model weights are not included. A production deployment should place API/MCP behind TLS and authenticated access; do not expose a bare MCP endpoint to the internet.

## Scaling boundaries

Scale horizontally by:
- Increasing worker replicas, with per-source leases and bounded provider concurrency.
- Partitioning queue workloads by tenant/source and job type.
- Separating CPU parsing/embedding tasks from I/O-heavy provider sync if metrics justify it.
- Adding database indexes, source/event partitioning and connection pooling.
- Adding object storage for large raw artifacts.
- Creating per-embedding-space HNSW/IVFFlat indexes or an external vector adapter if load tests justify it.
- Adding read replicas/caches for suitable read paths after correctness and freshness are proven.

Do not split services prematurely without workload measurements; do keep contracts independently replaceable from F0.

## Failure model

Provider timeouts, rate limits, partial permissions, invalid credentials, changed branches, malformed payloads, worker restarts, duplicate/out-of-order events, and model errors are routine cases. They must be represented in job status with retryability and last successful checkpoints. A failed embed operation must not mark the repository ready if embeddings are configured as required. If embeddings are disabled for a project, other indexes may still be ready but the feature status must say semantic search is disabled.

## Non-goals

- Writing to connected repositories.
- Automatically merging PRs, posting Git comments, or changing issues.
- Reading private chat channels without explicit installation/permissions.
- Replacing Git as the source of truth.
- Treating model-generated summaries as verified facts without provenance.
- Bundling arbitrary model weights under the software license.
