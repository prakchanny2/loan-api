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