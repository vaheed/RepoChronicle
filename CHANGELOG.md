# Changelog

All notable changes are documented here.

## [0.1.0] - 2026-10-18

### Added
- English-only foundation repository and product positioning.
- Phased roadmap, system architecture, bootstrap/sync contract, security model, license policy and ADRs.
- Docker Compose foundation with PostgreSQL + pgvector, Valkey, API, MCP, worker and connector processes.
- Initial PostgreSQL schema and versioned migration runner.
- Health/readiness/status API endpoints.
- Bootstrap state machine, repository URL validation, evidence budget selection and chat payload normalizers.
- OpenAI-compatible chat/embedding adapters and a lazy local FastEmbed adapter.
- GitHub Actions quality, integration, security/license, and Compose workflows.

### Not yet implemented
- End-to-end GitHub/GitLab bootstrap or incremental ingestion.
- Semantic retrieval against the application database.
- Live Telegram/Discord connector sessions.
- Production authorization and authenticated MCP deployment.
- Fine-tuning job execution.
