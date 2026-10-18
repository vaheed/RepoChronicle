"""Training interfaces kept out of the online inference path."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class TrainingJobRequest:
    tenant_id: str
    base_model_id: str
    dataset_manifest_uri: str
    method: str = "lora_sft"
    approved_by: str | None = None


@dataclass(frozen=True, slots=True)
class TrainingJobResult:
    job_id: str
    status: str
    artifact_uri: str | None = None
    evaluation_report_uri: str | None = None


class TrainingBackend(Protocol):
    """Pluggable backend for an explicitly approved, optional training job."""

    async def submit(self, request: TrainingJobRequest) -> TrainingJobResult: ...

    async def cancel(self, job_id: str) -> None: ...
