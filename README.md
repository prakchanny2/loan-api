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