# Loan API Verification Checklist

## Run the loan API container and open `/docs`

Command run (using the locally available image `loan-api:1.0`):

```powershell
docker run --rm -d --name loan-api-docs -p 8000:8000 loan-api:1.0
```

Output:

```text
171ebdcfde72bf8a74e6dbf050f175e7637f29d0fa57ec022081420f60465ad3
```

Opened `http://localhost:8000/docs` in the browser. The page title was
`Loan Application Service - Swagger UI`.

## Submit a prediction and verify HTTP 200

Command run in PowerShell:

```powershell
$body = @{ amount_usd = 1500; term_months = 12; monthly_income_usd = 350.0; previous_loans = 1; late_payments = 0 } | ConvertTo-Json -Compress
$response = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:8000/api/v1/predictions' -Method Post -ContentType 'application/json' -Body $body
"PREDICTION STATUS: $([int]$response.StatusCode)"
"PREDICTION BODY: $($response.Content)"
```

Output:

```text
PREDICTION STATUS: 200
PREDICTION BODY: {"default_probability":0.095,"risk_band":"low","model_version":"1.0.0"}
```

The same prediction was submitted from Swagger UI at `/docs`; its server
response showed status `200` and the response body above.
