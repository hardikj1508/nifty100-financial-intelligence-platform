# Sprint 5 Retrospective

## Sprint Goal

Complete the final reporting and portfolio-summary layer of the Nifty 100 Financial Intelligence Platform and prepare the project for final review and demonstration.

## Completed Work

- Completed batch tearsheet generation for the Nifty 100 companies
- Added handling for companies with fewer than 3 years of available data
- Generated and maintained skipped-ticker reporting
- Completed sector-level report generation
- Generated sector reports for the available broad sectors
- Implemented portfolio summary PDF generation
- Generated one portfolio-summary page per company
- Included the top 6 financial KPIs for each company
- Added KPI trend indicators using up, down, and flat arrows
- Added special handling for Debt-to-Equity where a lower value represents improvement
- Ordered portfolio-summary pages alphabetically by company/ticker
- Fixed PDF layout issues for companies with long names
- Performed visual checks of generated PDF reports
- Prepared final demonstration deliverables

## Validation

- Portfolio summary PDF generated successfully
- Portfolio summary contains 92 company pages
- 89 companies have March financial data
- 3 companies without March data are handled separately
- Verified portfolio PDF opens successfully
- Visually checked generated pages for layout, blank pages, and table/chart rendering
- Verified sector report generation and output files
- Verified generated reporting outputs against the project requirements

## Challenges

- Some companies had insufficient historical data for reporting
- Generated outputs required handling of skipped companies
- Long company names caused PDF title-layout issues
- Database schema differences required adjustment of the portfolio-report query
- Generated output files required cleanup and Git-ignore handling
- Final output verification required checking both file counts and visual rendering

## Outcome

Sprint 5 completed successfully. The final reporting layer, sector reports, batch tearsheets, and portfolio summary have been generated and validated. The project is ready for final review and demonstration.