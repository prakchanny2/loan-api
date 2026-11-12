"""Regression tests for the meaning and direction of default probabilities."""
import pandas as pd

from main import FEATURES, ml

GOOD = {
    "amount_usd": 1500,
    "term_months": 12,
    "monthly_income_usd": 350.0,
    "previous_loans": 1,
    "late_payments": 0,
}


def test_prediction_equals_model_default_probability(client):
    expected = round(
        float(ml["predict_proba"](pd.DataFrame([GOOD])[FEATURES])[0, 1]),
        3,
    )

    response = client.post("/api/v1/predictions", json=GOOD)

    assert response.status_code == 200
    assert response.json()["default_probability"] == expected


def test_safe_applicant_scores_low_and_risky_applicant_scores_high(client):
    safe_applicant = {
        "amount_usd": 100,
        "term_months": 24,
        "monthly_income_usd": 2000.0,
        "previous_loans": 5,
        "late_payments": 0,
    }
    risky_applicant = {
        "amount_usd": 9000,
        "term_months": 3,
        "monthly_income_usd": 80.0,
        "previous_loans": 0,
        "late_payments": 5,
    }

    safe_response = client.post("/api/v1/predictions", json=safe_applicant)
    risky_response = client.post("/api/v1/predictions", json=risky_applicant)

    assert safe_response.status_code == 200
    assert risky_response.status_code == 200
    assert safe_response.json()["risk_band"] == "low"
    assert risky_response.json()["risk_band"] == "high"
    assert safe_response.json()["default_probability"] < risky_response.json()["default_probability"]
