# Nifty100 Financial Intelligence Platform — Reports Guide

## Company Tear Sheets
Location: `reports/tearsheets/`

Tear sheets combine company identity, financial history, profitability/return metrics, balance-sheet information, cash-flow information and visual summaries.

Companies with fewer than three usable years are excluded from the standard tear-sheet batch and recorded in `output/skipped_tearsheets.csv`.

## Sector Reports
Location: `reports/sector_reports/`

Sector reports summarize companies and financial characteristics at sector level.

## Portfolio Summary
Location: `reports/portfolio/portfolio_summary.pdf`

The portfolio summary presents company-level KPI snapshots in alphabetical ticker order.

## Supporting Outputs
- `reports/peer_comparison.xlsx`
- `reports/screener_output.xlsx`
- `output/cashflow_intelligence.xlsx`
- `output/distress_alerts.csv`

## Reproducibility
Run the corresponding report-generation modules from the repository root and verify output directories before committing generated artifacts.
