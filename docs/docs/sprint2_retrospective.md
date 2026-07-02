# Sprint 2 Retrospective

## Sprint Goal
Build the Financial Ratio Engine and KPI computation pipeline.

## Completed Work
- Implemented profitability ratio calculations
- Implemented leverage ratios
- Implemented efficiency ratios
- Implemented CAGR calculations
- Implemented Cash Flow KPIs
- Added financial sector handling for Debt-to-Equity
- Added ROE and ROCE validation
- Added ratio edge case logging
- Populated financial_ratios SQLite table

## Validation
- 46/46 pytest tests passed
- financial_ratios table contains 1184 records
- KPI values verified using SQLite queries
- Edge cases reviewed and documented

## Challenges
- Duplicate source records
- Missing operating profit values
- Financial company Debt-to-Equity exceptions
- Source ROE/ROCE inconsistencies

## Outcome
Sprint 2 completed successfully and ready for Sprint 3.