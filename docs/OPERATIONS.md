# Operations Guide

## Local development

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
docker compose logs -f api worker mcp connectors
```

## Readiness and status

- `GET http://localhost:8080/health/live` checks process liveness.
- `GET http://localhost:8080/health/ready` checks PostgreSQL and Valkey connectivity.
- `GET http://localhost:8080/v1/status` reports the current roadmap phase and feature flags/status.

The MCP service listens on port 8090 and exposes a Streamable HTTP endpoint. Configure authentication and network/TLS protection before any shared or production use. The scaffold must not be exposed directly to the public internet.

## Stop and reset

Stop the services but preserve local data:

```bash
docker compose down
```

Delete all local database, queue, and model data (destructive):

```bash
docker compose down -v
```

## Database migrations

Migrations are versioned SQL files in `migrations/`. The one-shot `migrate` service applies unapplied files and records them in `schema_migrations`. Migrations must be backwards-aware for rolling deployment once multiple versions run at once; until then, deploy one migration/app version at a time.

Never manually edit an already-applied migration. Add a new migration file and tests. Before releases, take a backup and rehearse restore.

## Model and embedding cache

No weights are in the repository. Model downloads can be large and model terms vary. Keep the model cache on a dedicated volume, record the exact revision and license, and do not share writable model volumes between untrusted tenants.

## Logs and diagnostics

Logs must use structured metadata, correlation IDs, safe error categories and timings. Do not log source contents, chat message bodies, full webhook payloads, API keys, authorization headers, model prompts or private repository URLs that may contain identifiers unless policy explicitly allows redacted forms.

## Production hardening before deployment

- Rotate the default local database password and use a secret manager.
- Bind services behind TLS/authentication and restrict inbound network access.
- Configure backups, restore tests, retention and deletion jobs.
- Use image digests and a dependency lock file.
- Enable dependency/license/security scans.
- Configure per-provider concurrency and rate limits.
- Set up health alerts, queue lag metrics and dead-letter recovery.
- Review each model's license and each remote provider's retention/data processing terms.


## Network exposure defaults

Compose binds host ports for the API, MCP, and optional Ollama to `127.0.0.1` by default. Keep that default on a single host. For remote team access, deploy an authenticated TLS reverse proxy with identity-aware access controls, then set `RC_API_BIND_HOST` and/or `RC_MCP_BIND_HOST` deliberately. Do not expose the scaffold MCP endpoint directly to the public internet: F0's status tool is minimal, and future source tools require per-user/project authorization before external exposure.
