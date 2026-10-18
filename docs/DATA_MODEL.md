# Data Model

The initial migration is intentionally small enough to review and designed around tenant scoping, source provenance, event idempotency, checkpoints, and optional retrieval modalities.

## Core entities

- **tenant**: isolation boundary, policy and configuration.
- **project**: logical software system; can span many repositories.
- **source**: one code-host repository, issue tracker, or authorized chat destination.
- **provider_installation**: secret reference, provider account and permission status; never plaintext token values.
- **sync_job / sync_checkpoint**: durable stage, cursor, revision, lease and retry metadata.
- **webhook_inbox**: provider delivery ID, payload hash, processed timestamp and failure category.
- **activity_event**: commit, PR/MR, issue, review, release or CI event with provider ID and source URL.
- **conversation_message**: normalized message/thread/event with platform IDs and retention status.
- **repository_file / code_chunk**: revision-aware source provenance, path, content hash, line span, language, chunker version.
- **code_symbol / graph_edge**: definitions, references, imports, calls and dependency relationships, scoped to a revision or validity interval.
- **embedding_space**: provider, model/version, dimensions, distance metric, normalization, tokenizer/chunker compatibility and license-review reference.
- **chunk_embedding**: one vector per chunk per embedding space, never mixing dimensions/models in the same search space.
- **knowledge_fact / decision_record**: verified or inferred claims, evidence references, valid-from/replaced-by revisions, confidence, owner, and revalidation status.
- **access_policy / source_membership**: user, role and platform-destination scope. Enforce authorization before search results are returned.
- **audit_event**: access to sensitive source data, admin changes, exports, training-data generation and deletions.

## Multi-tenancy

Every tenant-owned row must carry `tenant_id` or be reachable only through a foreign-key path with tenant-aware query constraints. API handlers derive tenant identity from authentication; they must not trust a `tenant_id` supplied by an untrusted MCP argument.

Negative authorization tests are mandatory. Filtering by tenant only after vector ranking is not sufficient; unauthorized rows must not enter the candidate set.

## Vector dimension and model isolation

Use one `embedding_space` row per model/version/configuration. `chunk_embedding` stores its space ID and dimension. A vector index is created for a compatible space/dimension only. Changing model or dimensions creates a new space and re-embeds in the background; old indexes remain queryable until the new space passes evaluation and is promoted.

Keep embedding source text, chunker version, model revision and normalized-input hash so embeddings can be rebuilt reproducibly.

## Retention and deletion

The system must distinguish source deletion from temporary provider unavailability. When a file/message is deleted upstream, mark or delete its active searchable record according to policy, remove related embeddings/derived facts, and retain only minimum audit/tombstone information required for consistency. Retention policies are configurable per tenant and connector.

## Data minimization

Do not store full chat payloads or repository file copies in logs. Persist only fields required for sync, source evidence, and configured retention. Model request traces should store IDs, token counts and timing by default; prompt/content capture is opt-in and redacted.
