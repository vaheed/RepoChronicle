# Test Strategy and GitHub Actions

## Local required checks

```bash
ruff check .
ruff format --check .
mypy src
pytest -q
docker compose config --quiet
```

## CI layers

1. **Static quality:** Ruff lint/format, mypy, import checks.
2. **Unit suite:** state transitions, URL validation, event normalization, token/context budgets, evidence citations and failure classification.
3. **Integration:** PostgreSQL + pgvector migration/app query tests and Valkey stream/lease tests.
4. **Provider contracts:** fake GitHub/GitLab/Telegram/Discord/LLM/embedding providers with realistic sanitized payloads.
5. **Security:** dependency advisory scan, license policy, secret scan, webhook replay tests, tenant-isolation and prompt-injection cases.
6. **Container:** Compose config validation, Docker build, startup and health checks.
7. **Retrieval evaluation:** versioned fixture queries with expected evidence IDs. Track Recall@k/MRR, citation accuracy, stale evidence and latency.
8. **Resilience/performance:** stage restarts, duplicate/out-of-order deliveries, provider rate limits, backfills and increasing repository/event volumes.

## CI policy

The `ci.yml` workflow runs on pushes and pull requests. `security.yml` runs dependency audit and license policy checks. `compose.yml` validates the stack and builds the container. External services must be pinned to tested versions for release candidates.

No phase is accepted with tests that only assert a happy path. Ingestion changes need retry/idempotency tests; retrieval changes need citation/context tests; connector changes need authorization-denied tests; migrations need upgrade/re-run tests.

## Test data policy

Use synthetic source code, fake repository URLs, fake chat users/messages, and generated event IDs. Never commit proprietary repository snapshots, real access tokens, private chat exports, real email addresses, or production logs.
