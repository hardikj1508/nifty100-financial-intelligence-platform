# Changelog

## Final Project Release
- Completed Nifty100 financial intelligence analytics pipeline.
- Added NLP parsing and rule-based pros/cons generation.
- Added cash-flow intelligence and distress detection.
- Added company, sector and portfolio reporting.
- Added KMeans company clustering and statistical profiling.
- Added FastAPI company, screener, portfolio, sector, peer, market-cap, valuation, document and health workflows.
- Added Streamlit dashboard workflows.
- Added OpenAPI and Postman documentation.
- Added analyst/developer documentation and performance notes.

## Data-quality notes
- Current processed sector classification contains 10 broad sectors.
- ATGL, JIOFIN and SBIN have insufficient history for the standard three-year tear-sheet policy and are logged as skipped.
- Some source financial statements require data-quality review before interpreting extreme ratios.
