# ADR 0005: Use an Existing Code Intelligence Engine Behind an Adapter

- Status: Accepted for evaluation; backend selection pending F3 benchmark
- Date: 2026-10-18

## Context

RepoChronicle needs language-aware search, symbols, call/dependency relationships, incremental indexing, and line-level evidence. Rebuilding all of those primitives would duplicate mature functionality and increase the number of parsers and indexes the project must maintain.

## Decision

- Expose a provider-neutral `CodeIntelligenceBackend` contract from F0.
- Benchmark CodeGraph and codesearch as Apache-2.0, out-of-process candidates; do not vendor their code.
- Keep PostgreSQL as the source of truth for tenants, source ACLs, event history, sync jobs, provenance, and project-to-project relationships.
- Treat the selected code engine's indexes as derived data. Every search response must be validated against the registered source and immutable commit SHA.
- Select a default only after the F3 benchmark; keep the provider replaceable without changing the MCP/API data model.

## Consequences

- F3 focuses on adapter integration, evidence normalization, authorization, and evaluation rather than immediately creating a new parser engine.
- Engine-specific language coverage, runtime, and model downloads remain explicit in deployment documentation.
- A native in-database fallback may remain for lexical search, but it is not required to duplicate the whole semantic graph.
