from repochronicle.training.contracts import TrainingJobRequest


def test_training_contract_has_no_implicit_approval() -> None:
    request = TrainingJobRequest(
        tenant_id="tenant-1",
        base_model_id="model-id",
        dataset_manifest_uri="file:///approved/manifest.json",
    )
    assert request.approved_by is None
    assert request.method == "lora_sft"
