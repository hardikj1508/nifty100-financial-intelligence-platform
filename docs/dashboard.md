# Nifty100 Financial Intelligence Platform — Dashboard Guide

## Overview
The Streamlit dashboard provides an interactive analyst interface over the Nifty100 financial intelligence data.

## Start
Run the API first:
```powershell
python -m uvicorn src.api.main:app --reload --port 8001
```
Then:
```powershell
streamlit run src/dashboard/app.py
```

The dashboard uses `NIFTY_API_BASE_URL` when supplied; otherwise it uses the local API base URL.

## Main Workflows
1. Company Profile — review profile, financial history, ratios and documents.
2. Screener — apply KPI thresholds or predefined presets.
3. Portfolio — review portfolio statistics and company metrics.
4. Sector Analysis — compare companies and metrics by sector.
5. Peer Analysis — inspect peer-group members.
6. Valuation — review available valuation metrics.
7. Market Capitalisation — inspect historical market-capitalisation data.

## Troubleshooting
If the dashboard cannot reach the API, verify port `8001` and confirm `NIFTY_API_BASE_URL` points to `/api/v1`.
