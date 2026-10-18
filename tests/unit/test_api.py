from fastapi.testclient import TestClient

from repochronicle.api import app


def test_liveness_endpoint_does_not_need_external_services() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_endpoint_reports_scaffold_truthfully() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/status")
    body = response.json()
    assert response.status_code == 200
    assert body["phase"] == "F0"
    assert body["features"]["initial_repository_full_scan"] == "planned_F1"
    assert body["features"]["fine_tuning"] == "planned_optional_F6"
