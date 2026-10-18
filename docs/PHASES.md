# Phase Contract and Definition of Done

Each milestone has its own feature flag/status, tests, documentation, and acceptance gate. The detailed task list is in [`../ROADMAP.md`](../ROADMAP.md).

| Phase | Shipped capability | Minimum proof |
|---|---|---|
| F0 | Repository foundation, Compose, migrations, contracts, bootstrap state machine | Unit suite, lint/type checks, config validation, fresh Compose smoke test |
| F1 | Repository registration and full first scan | End-to-end local Git fixture, pinned SHA, resumable stages, credentials tests |
| F2 | Incremental Git and code-host activity sync | Duplicate/out-of-order events, missed-webhook reconciliation, rename/delete tests |
| F3 | Code symbols, lexical/vector/hybrid retrieval | Postgres+pgvector integration tests, retrieval evaluation, dimension isolation |
| F4 | MCP, LLM routing, evidence answers | MCP protocol client tests, provider contract suite, context-budget and citation tests |
| F5 | Telegram/Discord conversation ingestion and replies | Mocked platform events, permission-denied, no-access, no-spam and dedupe tests |
| F6 | Durable knowledge and optional fine-tuning | Staleness/invalidation tests, training data redaction, evaluation gate, rollback test |
| F7 | Horizontal scaling and operations | Multiple worker/load tests, tenant-isolation test, backup/restore drill |
| F8 | Stable release and ecosystem | Clean install/upgrade/rollback, SBOM/license/security gate |

## Pull request checklist

- [ ] The pull request names its roadmap phase and acceptance criteria.
- [ ] Tests cover the new behavior and an important failure mode.
- [ ] If the change touches ingestion, it covers idempotency/retry/checkpoint semantics.
- [ ] If the change touches retrieval, it proves source provenance and context-budget behavior.
- [ ] If the change touches access control, there is a negative authorization test.
- [ ] If the change adds a dependency/model/container, the license inventory is updated.
- [ ] Documentation and feature status match actual behavior.
- [ ] Full CI passes.

## Test layers

- Unit: pure functions, schemas, state machines, ranking, token budgets, normalizers.
- Contract: provider interfaces with deterministic fake implementations.
- Integration: PostgreSQL/pgvector, Valkey streams, migration upgrades, repository fixture operations.
- Platform contract: captured synthetic Telegram/Discord/GitHub/GitLab API payloads plus mocked HTTP responses.
- End-to-end: Docker Compose fresh-volume test and actual MCP client request.
- Security: authorization-negative cases, webhook signatures/replay, prompt-injection fixtures, secret redaction.
- Retrieval evaluation: frozen synthetic and maintainer-approved datasets, with Recall@k/MRR, citation accuracy, stale evidence and latency metrics.
- Performance: reproducible repository fixtures at increasing sizes and event throughput.
