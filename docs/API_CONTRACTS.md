# API and Event Contracts

These are target contracts for the planned phases. The F0 API implements only health and status endpoints; do not assume these routes already exist.

## Source registration

`POST /v1/sources`

```json
{
  "project_id": "uuid",
  "provider": "github",
  "source_kind": "git_repository",
  "canonical_url": "https://github.com/owner/repository",
  "default_branch": "main",
  "credential_ref": "secret://repochronicle/tenant/repo-reader",
  "options": {
    "full_scan": true,
    "index_embeddings": true,
    "backfill_activity_days": 365
  }
}
```

The `tenant_id` is derived from authenticated identity, not trusted from the body. A successful request should return a source ID and a bootstrap job ID, normally with HTTP 202. A duplicate request with the same idempotency key should return the original resource, not create a second scan.

## Source status

`GET /v1/sources/{source_id}/status`

Must return:
- source state and enabled modalities;
- target branch/SHA, indexed SHA and any revision lag;
- current bootstrap/incremental stage;
- last successful full scan and incremental sync times;
- activity backfill boundary and provider cursor where supported;
- last safe error category;
- next planned reconciliation time.

The API must not return secret values, raw provider authorization responses, raw message bodies, or data outside the requester scope.

## Normalized activity event

```json
{
  "event_id": "provider-stable-id",
  "tenant_id": "server-derived",
  "source_id": "uuid",
  "provider": "github",
  "event_type": "pull_request.merged",
  "actor_id": "provider-user-id",
  "occurred_at": "2026-10-18T14:00:00Z",
  "source_url": "https://github.com/owner/repository/pull/123",
  "commit_sha": "immutable-sha-or-null",
  "related_id": "123",
  "metadata": {
    "schema_version": 1
  }
}
```

Normalize and validate payloads before persistence. Keep provider IDs for deduplication. Event metadata should be minimal and avoid complete raw payloads.

## Evidence object

```json
{
  "evidence_id": "stable-evidence-id",
  "tenant_id": "server-derived",
  "project_id": "uuid",
  "source_id": "uuid",
  "source_kind": "code_chunk",
  "source_url": "https://github.com/owner/repository/blob/<sha>/src/file.py#L20-L35",
  "revision": "immutable-sha",
  "path": "src/file.py",
  "start_line": 20,
  "end_line": 35,
  "occurred_at": null,
  "indexed_at": "2026-10-18T14:00:00Z",
  "score": 0.87,
  "text": "bounded excerpt"
}
```

The result layer must authorize the source before the evidence object is exposed. Search APIs should apply hard result-count and token/character limits.
