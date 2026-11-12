"""Simulate 14 days of traffic and log PSI and mean-risk drift alerts to MLflow."""
import mlflow

from data import FEATURES, make_data
from drift_alerts import classify_consecutive_threshold, classify_income_psi
from psi import psi

ALERT_LEVELS = {"stable": 0, "watch": 1, "alert": 2}


def _report_alert(metric: str, value: float, level: str, previous_level: str, threshold: float) -> None:
    if level == "watch" and previous_level != "watch":
        print(f"[WATCH] {metric}={value:.3f}; threshold is {threshold:.3f}")
    elif level == "alert" and previous_level != "alert":
        print(f"[ALERT] {metric}={value:.3f} exceeded {threshold:.3f} for 2 consecutive windows")
    elif previous_level == "alert" and level != "alert":
        print(f"[RESOLVED] {metric}={value:.3f} is no longer above {threshold:.3f}")


def run_monitor() -> None:
    reference = make_data(n=5000, seed=42)
    model = mlflow.pyfunc.load_model("models:/loan-default@champion")
    income_high_windows = 0
    risk_high_windows = 0
    previous_income_level = "stable"
    previous_risk_level = "stable"

    mlflow.set_experiment("loan-default-monitoring")
    with mlflow.start_run(run_name="daily-drift-check"):
        mlflow.set_tag("income_psi_watch", "0.1 <= PSI <= 0.2")
        mlflow.set_tag("income_psi_alert", "PSI > 0.2 for 2 consecutive windows")
        mlflow.set_tag("mean_predicted_default_alert", "> 0.40 for 2 consecutive windows")

        for day in range(1, 15):
            # Incomes slowly fall and loan sizes rise over two simulated weeks.
            today = make_data(n=400, seed=100 + day, income_mean=400 - 8 * day, amount_high=5001)
            income_psi = psi(reference["monthly_income_usd"], today["monthly_income_usd"])
            income_level, income_high_windows = classify_income_psi(
                income_psi, income_high_windows
            )
            mean_risk = float(model.predict(today[FEATURES])[:, 1].mean())
            risk_level, risk_high_windows = classify_consecutive_threshold(
                mean_risk, 0.40, risk_high_windows
            )

            for feature in ["monthly_income_usd", "amount_usd", "late_payments"]:
                mlflow.log_metric(
                    f"psi_{feature}",
                    income_psi if feature == "monthly_income_usd"
                    else psi(reference[feature], today[feature]),
                    step=day,
                )
            mlflow.log_metric("mean_predicted_default", mean_risk, step=day)
            mlflow.log_metric("actual_default_rate", float(today.defaulted.mean()), step=day)
            mlflow.log_metric("income_psi_alert_level", ALERT_LEVELS[income_level], step=day)
            mlflow.log_metric("income_psi_high_windows", income_high_windows, step=day)
            mlflow.log_metric("mean_risk_alert_level", ALERT_LEVELS[risk_level], step=day)
            mlflow.log_metric("mean_risk_high_windows", risk_high_windows, step=day)
            mlflow.set_tag("latest_income_psi_alert", income_level)
            mlflow.set_tag("latest_mean_risk_alert", risk_level)

            _report_alert("income PSI", income_psi, income_level, previous_income_level, 0.2)
            _report_alert("mean predicted default", mean_risk, risk_level, previous_risk_level, 0.40)
            previous_income_level = income_level
            previous_risk_level = risk_level
            print(f"day {day:>2}: income PSI={income_psi:.3f}  mean risk={mean_risk:.3f}")


if __name__ == "__main__":
    run_monitor()