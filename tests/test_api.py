"""Run from this directory with: python train.py, then python -m pytest -v."""
from fastapi.testclient import TestClient

from main import app

GOOD = {"amount_usd": 1500, "term_months": 12, "monthly_income_usd": 350.0, "previous_loans": 1, "late_payments": 0}


def test_health_reports_model_version(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["model_version"]  # "1.0.0" from the file, or a registry version such as "1"
    assert body["git_sha"]


def test_api_key_requires_missing_invalid_and_valid_credentials(client):
    with TestClient(app) as unauthenticated:
        assert unauthenticated.get("/api/v1/applications").status_code == 401
    assert client.get("/api/v1/applications", headers={"X-API-Key": "invalid"}).status_code == 401
    assert client.get("/api/v1/applications").status_code == 200


def test_missing_api_key_configuration_fails_closed(monkeypatch, api_key):
    monkeypatch.delenv("API_KEY", raising=False)
    with TestClient(app) as client_without_key:
        assert client_without_key.get("/health").status_code == 200
        response = client_without_key.get("/api/v1/applications", headers={"X-API-Key": api_key})
    assert response.status_code == 503


def test_health_and_docs_are_public():
    with TestClient(app) as unauthenticated:
        assert unauthenticated.get("/health").status_code == 200
        assert unauthenticated.get("/docs").status_code == 200


def test_prediction_is_a_probability(client):
    body = client.post("/api/v1/predictions", json=GOOD).json()
    assert 0 <= body["default_probability"] <= 1
    assert body["risk_band"] in {"low", "medium", "high"}


def test_amount_above_limit_is_rejected(client):
    assert client.post("/api/v1/predictions", json={**GOOD, "amount_usd": 9000}).status_code == 200
    assert client.post("/api/v1/predictions", json={**GOOD, "amount_usd": 10000}).status_code == 422


def test_create_and_read_application(client):
    created = client.post("/api/v1/applications", json={**GOOD, "borrower_id": 1042})
    assert created.status_code == 201
    app_id = created.json()["id"]
    assert client.get(f"/api/v1/applications/{app_id}").json()["borrower_id"] == 1042


def test_missing_application_is_404(client):
    assert client.get("/api/v1/applications/99999").status_code == 404
