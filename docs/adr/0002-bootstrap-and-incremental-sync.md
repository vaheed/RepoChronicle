# ADR 0002: Bootstrap and Incremental Synchronization

- Status: Accepted
- Date: 2026-10-18

## Context

Sources can be added months or years after the product was created. The first connection must build a complete baseline; subsequent updates must not repeatedly rescan everything.

## Decision

For each newly registered code source, resolve and store a target SHA before scanning. Run a resumable full scan pinned to that SHA. Each stage has a durable checkpoint. Mark the source `ready` only after required stages and verification complete. If the branch moved during the scan, enqueue an incremental catch-up job.

After bootstrap, process webhooks incrementally from durable SHA/cursor checkpoints. Use periodic reconciliation to discover missed webhooks or permission changes. If ancestry/cursors cannot be trusted, mark stale and run a bounded rescan.

Chat connectors have source-specific history behavior: they begin live ingestion when authorized. Historical backfill is only used where the provider actually exposes it and the bot has required access.

## Consequences

- A source is never treated as initialized just because it was registered.
- Crashes are recoverable without repeating completed stages.
- Full scans and deltas are distinct job types.
- The product must expose indexed SHA, last sync, backfill boundary, and staleness in API/MCP answers.
