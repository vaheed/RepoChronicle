# Optional Fine-Tuning Design

Fine-tuning is an optional capability planned for F6. It must not be necessary for the system to answer project questions. Retrieval remains the only source of current truth.

## Why it is not enabled by default

Project code and engineering conversations change continuously. Fine-tuning is poor as the only mechanism for current repository facts, and it can introduce stale knowledge or memorization/privacy risks. The base architecture therefore uses retrieval and evidence citations first.

Fine-tuning may later improve stable behaviors such as answer format, tool selection, organization terminology, or domain-specific classification. It must not be used to "teach" private source code to a model without an explicit, reviewed data and model policy.

## Planned interfaces

- `TrainingDatasetBuilder`: exports approved, redacted examples with source lineage.
- `TrainingBackend`: starts/cancels/observes a training job.
- `ModelArtifactRegistry`: stores immutable artifact metadata and license/provenance.
- `ModelEvaluator`: runs a frozen evaluation suite against baseline and candidate.
- `ModelPromoter`: explicit human approval before deployment.

## Candidate training stack

Transformers, TRL and PEFT are permissively licensed software projects (Apache-2.0 at time of initial review). They may be used as optional dependencies after version-specific review. The selected base model, training data and output artifact each have separate licensing and privacy considerations.

## Promotion gate

A training artifact stays inactive until:
- secret/PII filtering passes;
- data lineage and permission checks pass;
- the evaluation set is frozen and versioned;
- citation correctness, hallucination, stale-memory and refusal metrics do not regress;
- the candidate shows a measurable improvement on an explicitly selected task;
- a maintainer approves the deployment;
- rollback to the last approved model is tested.

The `training` extra and worker are not implemented in the foundation scaffold. Do not add a Docker service that appears production-ready before these controls exist.
