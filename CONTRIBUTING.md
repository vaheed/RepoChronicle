# Contributing

Thank you for helping build RepoChronicle.

## Before opening a pull request

1. Read `agent.md`, `AGENTS.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, and the relevant ADR.
2. State the roadmap phase and acceptance criteria in the PR description.
3. Keep each PR focused and independently testable.
4. Add tests for normal, failure, retry, and authorization-denied paths as relevant.
5. Update docs and `docs/DEPENDENCY_INVENTORY.md` when behavior or dependencies change.
6. Run the complete local check suite.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev,channels,local-embeddings]"
cp .env.example .env
```

Run the checks:

```bash
ruff check .
ruff format --check .
mypy src
pytest -q
docker compose config --quiet
```

## Code and architecture rules

- New providers implement an existing interface or introduce an ADR explaining why the contract must change.
- Keep the core source of truth in PostgreSQL. Cache/job messages do not replace durable state.
- Repository and chat connections are read-only unless an independently reviewed future ADR changes that guarantee.
- Do not execute scripts from connected repositories.
- Every retrieval result must retain source provenance and apply authorization before content is returned.
- Keep embeddings and LLM providers separate and record every embedding space's dimension and model revision.
- Do not bundle model weights or add unclear-license dependencies.
- Do not enable fine-tuning without a redacted dataset, evaluation suite, human promotion gate, and rollback procedure.

## Pull request title examples

- `F1: add GitHub bootstrap adapter`
- `F2: reconcile missed webhook deliveries`
- `F3: add per-space pgvector index manager`
- `F5: enforce Discord destination authorization`

## License

By contributing, you agree that your contribution is made under the Apache-2.0 license used by the project, unless a separate signed agreement explicitly states otherwise.
