# Developer Guide

## Project Structure
- `src/etl/` — ingestion and transformation.
- `src/analytics/` — KPI, cash-flow, clustering and statistical analytics.
- `src/nlp/` — parsing and rule-based intelligence.
- `src/api/` — FastAPI application and routers.
- `src/dashboard/` — Streamlit interface.
- `src/reports/` — PDF and analytical report generation.
- `data/processed/` — processed datasets.
- `data/database/` — SQLite database.
- `reports/` — generated report artifacts.
- `docs/` — project documentation.

## Local Development
Activate the environment and run modules from the repository root. Keep API and dashboard ports consistent with the documentation.

## Validation
Use `pytest` for automated tests. Validate generated CSV/XLSX/PDF outputs separately.

## Data Integrity
Financial ratios are derived from processed financial statements. Investigate source-data anomalies before altering formulas. Preserve audit trails for exclusions and skipped companies.
