# Code Intelligence Backends

RepoChronicle must not reimplement a full language parser, call graph, vector index, and file watcher if a compatible open-source engine already solves that problem. The `CodeIntelligenceBackend` contract is an anti-corruption layer between the project knowledge service and an external code engine.

## Candidates reviewed on 2026-10-18

| Candidate | Upstream license | What it contributes | Use in RepoChronicle |
|---|---|---|---|
| [CodeGraph](https://github.com/codegraph-ai/CodeGraph) | Apache-2.0 | Semantic graph for symbols, imports, call chains, code search, persistent local index, MCP server | First candidate to benchmark for symbol/dependency and change-impact queries |
| [codesearch](https://github.com/flupkede/codesearch) | Apache-2.0 | Multi-repository Rust MCP server, tree-sitter chunking, local embeddings, hybrid BM25/vector search, incremental content hashing | First candidate to benchmark for repository-scale hybrid code search |

These are separately maintained programs, not Python dependencies. RepoChronicle does not vendor or copy their source into this repository. The operator pins a reviewed release/commit and deploys the selected engine behind the adapter. Re-check the upstream license, dependency inventory, runtime requirements, and model licenses at the exact revision used.

## Integration rules

- Keep a single adapter contract even if the selected engine exposes MCP or a CLI. Do not let platform-specific response fields leak into the domain API.
- Every returned result must be mapped to the registered source ID and a full commit SHA. Discard or mark stale any result whose revision does not match the requested/indexed revision.
- Apply tenant/source authorization before invoking the backend where possible, and re-check every returned source ID before returning evidence.
- Never expose a backend management tool that can register arbitrary filesystem roots through the public MCP endpoint.
- Keep the backend's own index as a derived cache; PostgreSQL remains authoritative for tenant policy, registered sources, sync checkpoints, activity, and audit state.
- Use RepoChronicle's lexical/provider-agnostic fallback only as needed. Do not maintain a second AST graph unless benchmarks prove a real gap.
- Embedding models downloaded by a backend have their own licenses; the backend's Apache-2.0 license does not license those weights.

## Benchmark gate before choosing a default

Evaluate both candidates with the same sanitized repository fixtures and frozen questions. Record language coverage, cold/warm indexing time, incremental update time, resident memory, disk size, query latency, Recall@k/MRR, file/line citation accuracy, stale-index detection, multi-repository isolation, license provenance, and Docker deployment effort. Select by measured fit instead of repository stars or one synthetic demo.

The F0 repository intentionally defines only the adapter contract. The F3 phase chooses and integrates a backend after these checks; it must not claim code intelligence is live before an end-to-end test passes.
