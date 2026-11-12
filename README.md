# loan-api

## Train the model and run the tests

From PowerShell, run these commands from the `loan-api` directory:

```powershell
Set-Location .\loan-api
Remove-Item Env:MLFLOW_TRACKING_URI -ErrorAction SilentlyContinue
python train.py
python -m pytest -v
```

`Remove-Item Env:MLFLOW_TRACKING_URI` removes the variable for the current
PowerShell process, if it is set. Run the commands from this directory because
both `train.py` and the API modules are located here.

## Run the API

Set `API_KEY` to a newly generated secret of at least 32 characters before
starting the service. Keep it in your deployment provider's secret settings;
do not commit it. The health endpoint is public, while prediction and
application endpoints require the `X-API-Key` request header:

```powershell
$env:API_KEY = "<your-new-secret>"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

For example, send a request with
`Invoke-RestMethod -Headers @{ "X-API-Key" = $env:API_KEY }`.
The `/health` response includes `git_sha` so the deployment pipeline can
confirm which commit is running.

## Monitor model drift

With MLflow tracking configured and the `loan-default@champion` model
registered, run `python monitor.py` to process the 14 simulated monitoring
windows. The script logs PSI and alert-level metrics to the
`loan-default-monitoring` experiment and prints alerts to the console. It
watches monthly-income PSI from `0.1` through `0.2`, alerts when income PSI
exceeds `0.2` for two consecutive windows, and alerts when mean predicted
default exceeds `0.40` for two consecutive windows. This script currently
simulates windows; it is not a scheduled production alert service.

`python -m pytest -v tests/test_drift_alerts.py tests/test_prediction_values.py`
checks the consecutive-window thresholds and that API default probabilities
match the model output and preserve safe/risky score ordering.