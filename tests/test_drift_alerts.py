import pytest

from drift_alerts import classify_consecutive_threshold, classify_income_psi


@pytest.mark.parametrize(
    ("value", "prior_count", "expected"),
    [
        (0.08, 0, ("stable", 0)),
        (0.1, 0, ("watch", 0)),
        (0.172, 0, ("watch", 0)),
        (0.2, 1, ("watch", 0)),
        (0.21, 0, ("watch", 1)),
        (0.22, 1, ("alert", 2)),
        (0.19, 1, ("watch", 0)),
    ],
)
def test_income_psi_alerts(value, prior_count, expected):
    assert classify_income_psi(value, prior_count) == expected


@pytest.mark.parametrize(
    ("value", "prior_count", "expected"),
    [
        (0.36, 0, ("stable", 0)),
        (0.4, 1, ("stable", 0)),
        (0.41, 0, ("watch", 1)),
        (0.42, 1, ("alert", 2)),
        (0.39, 1, ("stable", 0)),
    ],
)
def test_mean_risk_alerts(value, prior_count, expected):
    assert classify_consecutive_threshold(value, 0.40, prior_count) == expected


def test_non_finite_drift_values_are_rejected():
    with pytest.raises(ValueError, match="finite"):
        classify_consecutive_threshold(float("nan"), 0.40, 0)


def test_negative_income_psi_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        classify_income_psi(-0.01, 0)
