# Nifty100 Financial Intelligence Platform — Troubleshooting

## API does not start
```powershell
python -m uvicorn src.api.main:app --reload --port 8001
```
If port 8001 is occupied, stop the previous Uvicorn process or use another port consistently.

## Dashboard cannot connect
Verify `http://127.0.0.1:8001/docs`. If required, set `NIFTY_API_BASE_URL` to `http://127.0.0.1:8001/api/v1`.

## Missing report
Check the output directory and confirm sufficient source observations. Standard tear-sheet generation skips companies with insufficient history and records them in `output/skipped_tearsheets.csv`.

## Unexpected ratio
Inspect the source company-year balance-sheet and P&L values before changing calculation formulas.

## Tests
```powershell
pytest
```
Review the test summary before final sign-off.
