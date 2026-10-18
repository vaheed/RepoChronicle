# Security Model

## Threat model

Sources may contain secrets, prompt injections, malicious links, hostile code comments, poisoned documentation, or messages from users who should not have access to every project. A chat connector may be added to an unintended channel or lose permissions. Provider webhooks and replayed payloads are untrusted inputs. A coding harness may be more privileged than this service.

## Required controls

- Read-only Git credentials and no write-oriented Git provider adapter methods in the default tool surface.
- No execution of code or shell commands from indexed repositories/chat content.
- Validate provider domains, webhook signatures/secrets, payload sizes, IDs and timestamps.
- Deduplicate webhook delivery IDs; reject or quarantine replayed/invalid events.
- Store credentials in secret references or environment/secret manager, never in URLs, prompts, DB payloads, logs, or examples.
- Restrict source ingestion and retrieval to explicit registrations and provider permissions.
- Authenticate API and MCP in deployed environments; use TLS or a trusted private network.
- Enforce tenant/project/channel authorization before candidate retrieval and recheck before returning evidence.
- Treat retrieved content as data. Never splice it into system instructions.
- Apply secret and PII filtering before embedding, model calls, chat output, and training export.
- Rate-limit users, model calls, chat replies, and expensive retrieval.
- Redact exception details from external clients while retaining safe internal error categories.
- Provide deletion/retention workflows covering chunks, embeddings, derived memories, caches and logs.
- Log administrative/source-access events with correlation IDs.

## Prompt injection

A README, issue, pull request comment, commit message, or chat message can say "ignore previous instructions" or ask the model to exfiltrate data. The system must:
1. Label retrieved content as untrusted evidence.
2. Keep tool permissions outside model discretion.
3. Authorize every tool call against the user's identity and allowed scope.
4. Never grant write or arbitrary code-execution tools to answer a knowledge question.
5. Return links and sources rather than copying secrets.
6. Test representative adversarial fixtures in CI.

## Chat safety defaults

A destination is disabled until an administrator registers it. Default enabled behavior is mention/reply-only. Proactive replies are a separate opt-in policy and need message-type allowlists, confidence threshold, quiet hours and rate limits. Never let a normal user enable bot-wide proactive access by chatting a command in a group.

## Incident response

On suspected exposure: revoke source/chat credentials, disable the affected connector, rotate secrets, preserve minimal redacted audit records, identify impacted tenants and source URLs, delete or re-index affected data as needed, and publish a security notice following the project policy.
