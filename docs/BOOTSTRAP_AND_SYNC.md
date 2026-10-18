# Repository Bootstrap and Incremental Sync

## Contract

The first connection of an existing repository must trigger a complete initial scan. `ready` is not set merely because credentials work or a clone has started.

After initial bootstrap, normal sync processes changes since durable checkpoints. Webhooks are the fast path; scheduled reconciliation is the recovery path.

## Bootstrap algorithm

1. **Register:** create tenant/project/source rows and bind credentials through a secret reference, not raw token text in the source URL.
2. **Validate:** allow only configured GitHub/GitLab hosts or explicitly approved self-hosted instances. Confirm repository visibility/read permissions.
3. **Pin:** resolve the configured default branch/ref to immutable commit SHA `S0`. Store branch name, `S0`, provider response metadata and bootstrap job ID.
4. **Schedule:** enqueue one idempotent job keyed by tenant + external source ID + bootstrap generation. Acquire a source-scoped lease.
5. **Fetch:** clone/fetch read-only content into an isolated workspace or bare repository. Never execute project scripts.
6. **Inventory:** enumerate files at `S0`; honor configured exclusions, `.gitignore`, size limits, binary detection, symlink rules and secret filtering.
7. **Index:** build text chunks, symbols/edges, lexical search entries, and embeddings for each enabled embedding space.
8. **Backfill activities:** request the provider's supported history, using stable pagination cursors and configured time windows/rate budgets.
9. **Verify:** validate expected stage counts and record indexed SHA `S0`. If the remote branch is now at `S1 != S0`, enqueue an incremental job from `S0` to `S1`.
10. **Ready:** set `ready` only after all required stages succeed. Optional stages such as embeddings may be disabled by explicit configuration; status must expose that state.

## Checkpointing

Every stage should be idempotent and persist:
- job ID, stage, lease owner/expiry;
- repository SHA or provider cursor;
- last completed unit (for example file path or page cursor);
- rows/items accepted, skipped and failed;
- retry count, next retry time and terminal failure reason;
- stage start/end and correlation ID.

A worker restart resumes from the last committed checkpoint. Database writes and checkpoint updates must share a transaction where possible. External side effects must have idempotency keys.

## Incremental Git sync

Given `last_indexed_sha` and the new target SHA:
- Fetch the commit graph read-only.
- Determine changed, added, deleted and renamed paths between those revisions.
- Re-index affected files/chunks/symbol edges; remove old searchable rows for deleted content.
- Recompute affected dependency/call relationships when the relevant symbol graph can be updated safely.
- Store the new SHA only after the required index writes are committed.
- If force-push rewrites ancestry or the old SHA is unavailable, enqueue a bounded full rescan and mark the source stale until it completes.

Never start a full scan on every webhook. Coalesce multiple queued events for a source and process the newest safe target SHA.

## Webhooks and reconciliation

Webhook handlers validate signatures/tokens before enqueueing payload references. Insert deliveries into a durable inbox with a unique provider delivery ID; duplicate deliveries are acknowledged without duplicate ingestion.

Scheduled reconciliation compares:
- remote branch HEAD to `last_indexed_sha`;
- provider activity windows to the last saved cursor/timestamp;
- outstanding webhook inbox IDs to completed event records;
- source permissions and default branch changes.

Reconciliation should use provider APIs rather than assuming webhook delivery is lossless. Use bounded concurrency and exponential backoff with jitter for rate limits and transient errors.

## Initial scan versus chat history

A newly registered Git repository can generally be fetched at its current permitted revision and indexed from scratch. Git-provider event-history backfill remains subject to API permissions, history APIs, pagination, retention and rate limits.

For standard Telegram bots, assume the bot starts receiving eligible updates after it is installed and authorized. Do not promise historical group backfill. Discord can support API history requests only for authorized channels and subject to its content-intent rules. Every connector must report its actual earliest available event time.

## Status contract

Expose `registered`, `validating`, `queued`, `fetching`, `inventorying`, `indexing`, `embedding`, `backfilling_activity`, `verifying`, `ready`, `stale`, `retrying`, `failed`, `disabled`, and `permission_limited` states as appropriate.

The status response must include:
- current and desired revision;
- last full scan time;
- last successful incremental sync;
- provider cursor/checkpoint;
- enabled indexing features;
- lag/staleness and reason;
- last error category without credential-bearing raw provider messages.
