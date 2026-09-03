# Nifty100 Financial Intelligence Platform — API Guide

## Overview
FastAPI REST API for company financial data, portfolio analytics, screening, sectors, peers, market capitalisation, valuation and documents.

**Base URL:** `http://127.0.0.1:8001/api/v1`

Interactive documentation: `/docs`; OpenAPI schema: `/openapi.json`.

## Company Endpoints
- `GET /companies` — list companies.
- `GET /companies/{ticker}` — company profile.
- `GET /companies/{ticker}/pl` — historical Profit & Loss.
- `GET /companies/{ticker}/bs` — historical Balance Sheet.
- `GET /companies/{ticker}/cf` — historical Cash Flow.
- `GET /companies/{ticker}/ratios` — financial ratios.
- `GET /companies/{ticker}/peers` — peer information.
- `GET /companies/{ticker}/documents` — generated documents.

## Screener
- `GET /screener` — apply screening criteria.
- `GET /screener/presets` — list predefined presets.

## Portfolio
- `GET /portfolio` — portfolio-level information.
- `GET /portfolio/{ticker}` — ticker-level information.
- `GET /portfolio/stats` — portfolio statistics.

## Sector and Peer Analysis
- `GET /sectors` — sector-level information and metrics.
- `GET /peers/{group_name}` — peer-group members.

## Market Capitalisation and Valuation
- `GET /market-cap/{ticker}` — historical market capitalisation.
- `GET /valuation/{ticker}` — valuation information.

## Health
- `GET /health` — API and dataset health information.

## Error Handling
`200` successful request; `400` invalid request parameters; `404` resource not found; `500` unexpected server error.

## Running the API
```powershell
python -m uvicorn src.api.main:app --reload --port 8001
```
