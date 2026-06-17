# Dataset Analysis

## Total Datasets

12

### Core Datasets

1. companies.xlsx

* Master company information
* Primary Key: company_id

2. profitandloss.xlsx

* Revenue, expenses, profit metrics
* Primary Key: company_id + year

3. balancesheet.xlsx

* Assets, liabilities, borrowings
* Primary Key: company_id + year

4. cashflow.xlsx

* Operating, investing, financing cash flow
* Primary Key: company_id + year

5. analysis.xlsx

* Growth and trend metrics

6. documents.xlsx

* Annual report repository

7. prosandcons.xlsx

* Qualitative company insights

### Supporting Datasets

8. sectors.xlsx

* Sector mapping

9. stock_prices.xlsx

* Historical stock prices

10. market_cap.xlsx

* Valuation metrics

11. financial_ratios.xlsx

* KPI calculations

12. peer_groups.xlsx

* Industry peer mapping

## Data Flow

companies
├── profitandloss
├── balancesheet
├── cashflow
├── documents
└── analysis

profitandloss + balancesheet + cashflow
↓
financial_ratios
↓
Health Score
Screener
Sector Analytics
Peer Comparison
Dashboard
