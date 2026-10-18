# RepoChronicle Roadmap

This roadmap is intentionally phased so each milestone leaves behind a testable, useful increment. The order is designed to avoid later architectural rewrites: provider adapters, event envelopes, tenant-aware IDs, embedding spaces, job checkpoints, and authorization are foundational contracts.

**Status key:** `[x]` included in the foundation scaffold; `[ ]` planned and not yet implemented. A checked item is not a claim that the entire product feature is complete.

## F0 — Repository foundation and executable contracts (current starter)

**Goal:** a clean, testable base repository that an AI coding harness can extend safely.

- [x] English-only documentation, README, agent.md and AGENTS.md.
- [x] Product architecture, data model, phase plan, ADRs, connector/provider contracts, and a replaceable code-intelligence backend contract.
- [x] Apache-2.0 project license and dependency/model license policy.
- [x] Docker Compose for API, MCP, worker, connector runtime, PostgreSQL + pgvector, and Valkey.
- [x] One-shot database migration service.
- [x] API liveness/readiness/status endpoints.
- [x] Bootstrap state machine and unit tests.
- [x] Context-budget selection utility and tests.
- [x] OpenAI-compatible provider abstraction and request client.
- [x] Telegram/Discord event normalization contracts.
- [x] GitHub Actions test, lint, security, license-policy and Compose validation jobs.
- [ ] Production GitHub/GitLab onboarding and source ingestion.

**Acceptance gate**
- Fresh clone passes `pip install -e ".[dev]"`, Ruff, mypy, and pytest.
- `docker compose config --quiet` succeeds.
- On fresh volumes, `docker compose up --build` reaches healthy DB/API/Valkey services.
- Health/readiness/status endpoints work.
- All planned-but-unimplemented capabilities are labeled accurately.

## F1 — Source registry and initial full scan

**Goal:** a user can add an existing repository after project creation and get a complete, reproducible first index.

- [ ] Organization, project, source, credential-reference, and source-permission APIs.
- [ ] GitHub and GitLab read-only connector implementations.
- [ ] Validate host/provider and test credential permissions without logging secrets.
- [ ] Clone/fetch at a pinned target SHA; record the source branch and target commit.
- [ ] Resumable bootstrap stages: validate → fetch → inventory → parse → chunk → embed → validate → ready.
- [ ] First-pass inventory with `.gitignore`-aware exclusions, configurable secret filtering, file hashes, size limits, binary detection, and symlink policy.
- [ ] Persist per-stage checkpoints; idempotency key prevents duplicate initialization.
- [ ] Compare current remote HEAD to target SHA at completion; queue a delta if it moved.
- [ ] Backfill commit and supported code-host activity history under rate and permission limits.
- [ ] Full-scan progress API, logs, metrics, cancellation, retry, and explicit failure reasons.

**Acceptance gate**
- Integration tests against local bare Git fixtures prove that a newly registered source is fully scanned at the requested SHA.
- A restart at every stage resumes without duplicate records.
- A branch move during bootstrap is detected and a follow-up delta is queued.
- Invalid credentials, inaccessible private repos, rate limits, and oversized/binary files fail safely.
- Secrets never appear in logs or database event payloads.
- GitHub Actions runs integration fixtures on every PR.

## F2 — Incremental code and activity synchronization

**Goal:** after bootstrap, process only changes and reliably recover missed webhooks.

- [ ] GitHub and GitLab webhook signature/token validation.
- [ ] Durable webhook inbox with unique delivery IDs and replay protection.
- [ ] Git commit-range processing from the recorded SHA; update changed/deleted/renamed files only.
- [ ] MR/PR, review, comment, issue, release, tag, and pipeline event ingestion.
- [ ] Provider pagination cursors, rate-limit backoff, jitter, retry classes, and dead-letter handling.
- [ ] Periodic reconciliation of branch HEAD, activity cursor, and webhook delivery windows.
- [ ] Per-source synchronization status: indexed SHA, last event cursor, last success, lag, and stale reason.
- [ ] Event deduplication and out-of-order event resolution.
- [ ] Retention and tombstones for deleted files, branches, messages, and permissions.

**Acceptance gate**
- Duplicate and out-of-order events result in one consistent final state.
- Dropped-webhook simulation is repaired by reconciliation.
- A single-file commit does not trigger a full repository re-index.
- Deletions and renames remove stale searchable content.
- Rate-limit and transient failure tests prove bounded retries.
- Sync status reports stale data truthfully.

## F3 — Code intelligence, embeddings, graph, and hybrid retrieval

**Goal:** reliable, evidence-backed retrieval with local embedding capability.

- [ ] Benchmark and integrate CodeGraph or codesearch behind `CodeIntelligenceBackend`; do not vendor their source.
- [ ] Normalize symbol, call/dependency, search and change-impact evidence to a source ID and immutable commit SHA.
- [ ] Keep a deterministic lexical fallback; implement in-house parsing only for gaps demonstrated by the benchmark.
- [ ] Built-in local embedding adapter (FastEmbed/ONNX CPU path) with user-selected model where the selected backend does not already provide a suitable embedding path.
- [ ] OpenAI-compatible remote embedding adapter and explicit model/dimension metadata.
- [ ] PostgreSQL + pgvector embedding storage with separate embedding spaces and per-space indexes.
- [ ] Lexical search (PostgreSQL full-text at baseline), dense vector search, hybrid rank fusion, optional reranking.
- [ ] Incremental re-embedding by content hash and embedding-space version.
- [ ] Secret and generated/binary content exclusion; allowlist/denylist configuration.
- [ ] Retrieval diagnostics and frozen evaluation datasets/metrics.
- [ ] Source/commit/file/line evidence attached to every returned chunk.

**Acceptance gate**
- Unit tests cover chunk boundaries, duplicate content, deletes, dimension mismatches, and embedding model changes.
- Integration tests exercise lexical, vector, and hybrid retrieval against Postgres + pgvector.
- Retrieval evaluation measures Recall@k/MRR on versioned fixtures.
- With local embedding mode, indexing and retrieval work without a paid API.
- Changing an embedding model creates a new embedding space instead of corrupting old vectors.
- Large-repository benchmarks record indexed bytes, chunks, duration, memory, and query latency.

## F4 — Project Brain API, MCP, LLM providers, and bounded context

**Goal:** provide a stable common knowledge interface for arbitrary coding harnesses.

- [ ] MCP tools: search code, inspect symbol, search activity, change impact, project status, service map, and sync status.
- [ ] MCP tool annotations are read-only; no repository mutation tools are exposed.
- [ ] OpenAI-compatible chat provider for cloud APIs, vLLM, Ollama and llama.cpp servers; optional native adapters where needed.
- [ ] Local LLM preset and provider health checks without auto-pulling model weights.
- [ ] Evidence-first answer generation with file/line/commit/activity/chat citations.
- [ ] Token/context budget estimation, result diversity, deduplication, and progressive expansion.
- [ ] Prompt-injection resistance: retrieved text is data, never instructions; tool allowlists and bounded calls.
- [ ] Authenticated MCP transport, short-lived tokens or reverse-proxy SSO, and project-level authorization.
- [ ] Retrieval/answer trace identifiers, redaction, timeouts, cancellation, and per-user quotas.

**Acceptance gate**
- MCP protocol tests run through an actual MCP client.
- Contract tests cover each tool schema and authorization failure.
- Context budget remains within the configured bound for oversized fixtures.
- A malicious repository README or chat message cannot invoke tools or override system policy.
- Answers include citations or explicitly state that evidence is insufficient.
- Both local and OpenAI-compatible mocked providers pass the same contract suite.

## F5 — Telegram and Discord team connectors

**Goal:** opt-in team conversations and useful, non-spammy assistance.

- [ ] Regular Telegram Bot API connector; Business connection remains optional.
- [ ] Discord bot connector with least-privilege server/channel permissions.
- [ ] Explicit destination registry and administrator opt-in per group, channel, thread, or forum.
- [ ] Telegram privacy-mode instructions and channel membership/administrator checks.
- [ ] Discord Message Content Intent status checks and Read Message History checks.
- [ ] Discord historical message backfill where platform permissions/API allow it; Telegram live ingestion begins when installed and authorized.
- [ ] Normalize edits, deletes, replies, threads, authors, timestamps, links, attachments metadata, and platform IDs.
- [ ] Deduplicate events, recover reconnect gaps where APIs allow, enforce provider rate limits, and handle deletion/retention events.
- [ ] Mention/reply-only mode, quiet mode, configurable proactive suggestions, anti-loop protections, and confidence thresholds.
- [ ] Unified access policy: users can only receive evidence from projects/channels they are authorized to access.

**Acceptance gate**
- Integration tests use mocked Telegram/Discord payloads and mocked API clients.
- Permission-denied and intent-disabled states are visible and fail closed.
- The bot cannot read an unregistered channel or answer using inaccessible source data.
- A group test proves the default mode does not unsolicitedly answer every message.
- Message deduplication and reconnect replay are tested.
- Documentation precisely describes platform history/backfill limits.

## F6 — Durable memory, decision records, summaries, and optional fine-tuning

**Goal:** keep verified knowledge current without bloating every prompt.

- [ ] Evidence-backed facts and architectural decisions with source, first/last valid revision, confidence, owner, and revalidation status.
- [ ] Distinguish verified facts, inferred summaries, unresolved hypotheses, and superseded facts.
- [ ] Time-aware summaries for project/day/week/release and conversation threads.
- [ ] Automatic invalidation/revalidation when source evidence changes or is deleted.
- [ ] Evaluation harness for answer quality, citation correctness, stale-memory rate, and hallucination rate.
- [ ] Optional training data export with PII/secrets filtering, explicit approval, and audit logs.
- [ ] Optional LoRA/SFT job adapter using permissively licensed training libraries (e.g. Transformers/TRL/PEFT) only after model/license review.
- [ ] Training jobs are isolated, reproducible, cancellable, and disabled by default.
- [ ] Compare fine-tuned models against retrieval-only baseline; promote only after evaluation thresholds pass.
- [ ] Model registry and rollback. RAG remains the source of truth; fine-tuning never replaces live data retrieval.

**Acceptance gate**
- Facts can be traced to sources and are invalidated when their evidence is removed.
- PII/secret redaction tests cover training exports.
- A fine-tuned model is never loaded automatically without explicit enablement and a successful evaluation report.
- If training extras/models are absent, core application tests and deployment still pass.
- Benchmark results prove improvement before a trained model is promoted.

## F7 — Scale, tenancy, operations, and resilience

**Goal:** scale by adding workers/partitions, not redesigning the system.

- [ ] Queue partitioning by tenant/source; horizontal worker scaling and leases.
- [ ] Tenant/project/channel isolation tests and database row-level policy review.
- [ ] Backpressure, per-provider concurrency limits, retry budgets, dead-letter replay UI/CLI.
- [ ] Postgres connection pooling, index tuning, retention/partitioning, backups, and restore drills.
- [ ] Multiple embedding spaces and model/provider routing per tenant/project.
- [ ] Object storage adapter for larger raw artifacts and snapshot manifests.
- [ ] OpenTelemetry traces/metrics, Prometheus metrics, structured logs, dashboards and SLOs.
- [ ] Production secret management, encryption at rest, key rotation, audit events and data deletion workflows.
- [ ] Load tests for many repos, high event volume, and multi-tenant retrieval.

**Acceptance gate**
- Horizontal workers do not process the same job concurrently without a valid lease.
- Restore drills reconstruct database state from documented backups.
- Cross-tenant negative tests never return data.
- Load tests define measured capacity and accepted backlogs.
- SLOs and resource/queue alerts have runbooks.

## F8 — Release readiness and ecosystem

- [ ] OpenAPI docs, MCP compatibility tests across common harnesses, and connector setup guides.
- [ ] Dependency/license inventory and SBOM generation attached to releases.
- [ ] Signed releases, pinned container images, reproducible dependency lock and release provenance.
- [ ] Upgrade/rollback instructions and schema compatibility policy.
- [ ] Architecture diagrams, demo fixtures with synthetic data, issue templates, release notes and contributor docs.
- [ ] Public benchmark suite and documented limitations.
- [ ] Project/organization installation guide and example deployments.

**Acceptance gate**
- Clean install, upgrade, rollback and recovery are exercised from scratch.
- Full CI, security, license and integration suites pass against release candidates.
- No credentials or real user/source data appear in demo fixtures or build artifacts.
- All product claims in README match the released code.

## Phase sequencing policy

- Each phase is a set of independently reviewable pull requests, not one giant merge.
- A phase is not complete merely because its code compiles; its acceptance gate must pass.
- Future-phase modules may define interfaces/contracts early, but their README/status must say `planned` until there are end-to-end tests.
- The architecture may evolve through ADRs, but any boundary change must be documented and tested.
