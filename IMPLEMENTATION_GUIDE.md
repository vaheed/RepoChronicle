# Implementation Guide for Coding Harnesses

This repository is prepared to be implemented incrementally by Codex, OpenCode, Claude Code, or another harness.

## First session

1. Read `agent.md`, `AGENTS.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, and `docs/PHASES.md`.
2. Run the current checks locally and note any environment-specific failures:
   `ruff check .`, `ruff format --check .`, `mypy src`, `pytest -q`, `docker compose config --quiet`.
3. Do not start F1 until F0 acceptance criteria pass in CI.
4. Pick one F1 vertical slice: create a source record, validate read-only Git credentials, resolve a pinned SHA, and enqueue a bootstrap job.
5. Implement through contracts, migration, provider adapter, API, worker stage, and tests together.
6. Continue stage by stage until a real private/public test repository can be fully scanned at the pinned SHA and resumes correctly after a worker restart.

## Recommended first coding issue: F1-001

**Title:** Implement source registration and bootstrap job creation.

Acceptance criteria:
- API endpoint registers a GitHub/GitLab repository only for an authenticated tenant.
- The server validates the canonical URL against configured host allowlists and disallows credentials/query tokens in URLs.
- Credentials are passed through a secret reference; raw tokens are never returned or logged.
- A stable idempotency key prevents duplicate sources/bootstrap jobs.
- Source status moves through validation and queued states; a status endpoint exposes the current job.
- The job records the target branch and target SHA when the provider supports lookup.
- Tests cover valid URL, unauthorized tenant, denied credentials, duplicate registration, malformed payload, and provider unavailable.
- The feature status in README/API is updated only after the vertical slice works end to end.

## Do not do this

- Do not create a "complete scan" endpoint that only returns success without processing files.
- Do not mark a source ready before all configured required stages finish.
- Do not dump an entire repository into an LLM context.
- Do not add multiple embedding/vector systems without benchmark evidence.
- Do not run fine-tuning against live project discussions by default.
