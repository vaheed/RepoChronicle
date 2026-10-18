# AGENTS.md

This file is the repository-wide, harness-friendly entry point. The more detailed rules are in [`agent.md`](agent.md).

Before implementation, read:
1. `agent.md`
2. `ROADMAP.md`
3. `docs/ARCHITECTURE.md`
4. `docs/PHASES.md`
5. The relevant Architecture Decision Record under `docs/adr/`

Always distinguish implemented functionality from planned functionality. Work in small, phase-scoped changes. Preserve read-only repository permissions, evidence provenance, tenant isolation, context budgets, and the license gate. Add tests to CI for every behavior change.
