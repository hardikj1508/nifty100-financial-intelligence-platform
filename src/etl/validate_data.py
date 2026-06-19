from matplotlib.pylab import rint
import pandas as pd

companies = pd.read_csv("data/processed/companies_clean.csv")
balancesheet = pd.read_csv("data/processed/balancesheet_clean.csv")
cashflow = pd.read_csv("data/processed/cashflow_clean.csv")
documents = pd.read_csv("data/processed/documents_clean.csv")
financial_ratios = pd.read_csv("data/processed/financial_ratios_clean.csv")
market_cap = pd.read_csv("data/processed/market_cap_clean.csv")
peer_groups = pd.read_csv("data/processed/peer_groups_clean.csv")
profitandloss = pd.read_csv("data/processed/profitandloss_clean.csv")
prosandcons = pd.read_csv("data/processed/prosandcons_clean.csv")
sectors = pd.read_csv("data/processed/sectors_clean.csv")
stock_prices = pd.read_csv("data/processed/stock_prices_clean.csv")
analysis = pd.read_csv("data/processed/analysis_clean.csv")
company_ids = set(companies["id"])
failures = []

print("Companies:", companies.shape)
print("Balance Sheet:", balancesheet.shape)
print("Cash Flow:", cashflow.shape)
print("Documents:", documents.shape)
print("Financial Ratios:", financial_ratios.shape)
print("Market Cap:", market_cap.shape)
print("Peer Groups:", peer_groups.shape)
print("Profit & Loss:", profitandloss.shape)
print("Pros & Cons:", prosandcons.shape)
print("Sectors:", sectors.shape)
print("Stock Prices:", stock_prices.shape)
print("Analysis:", analysis.shape)

child_tables = {
    "Balance Sheet": balancesheet,
    "Cash Flow": cashflow,
    "Documents": documents,
    "Financial Ratios": financial_ratios,
    "Market Cap": market_cap,
    "Peer Groups": peer_groups,
    "Profit & Loss": profitandloss,
    "Pros & Cons": prosandcons,
    "Sectors": sectors,
    "Stock Prices": stock_prices,
    "Analysis": analysis
}

datasets = {
    "Companies": companies,
    "Balance Sheet": balancesheet,
    "Cash Flow": cashflow,
    "Documents": documents,
    "Financial Ratios": financial_ratios,
    "Market Cap": market_cap,
    "Peer Groups": peer_groups,
    "Profit & Loss": profitandloss,
    "Pros & Cons": prosandcons,
    "Sectors": sectors,
    "Stock Prices": stock_prices,
    "Analysis": analysis
}

for name, df in datasets.items():
    print(f"\n{name}")
    print("-" * 30)

    print("Shape:", df.shape)

    print("\nMissing Values:")
    print(df.isnull().sum().sum())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

for name, df in datasets.items():

    if "id" in df.columns:

        bad_rows = df[df["id"].isnull()]

        for index, row in bad_rows.iterrows():

            failures.append({
                "table": name,
                "rule": "DQ_01",
                "row": index,
                "issue": "Missing Primary Key"
            })

for name, df in datasets.items():

    if "id" in df.columns:

        dup_rows = df[df["id"].duplicated()]

        for index, row in dup_rows.iterrows():

            failures.append({
                "table": name,
                "rule": "DQ_02",
                "row": index,
                "issue": "Duplicate Primary Key"
            })

# DQ-03 Foreign Key Validation

for table_name, df in child_tables.items():

    if "company_id" in df.columns:

        invalid_rows = df[~df["company_id"].isin(company_ids)]

        for index, row in invalid_rows.iterrows():

            failures.append({
                "table": table_name,
                "rule": "DQ_03",
                "row": index,
                "issue": f"Invalid company_id: {row['company_id']}"
            })
# DQ-04 : Year Validation
for table_name, df in child_tables.items():

    if "year" in df.columns:

        year_text = df["year"].astype(str)

        year_numeric = year_text.str.extract(r'(\d{2,4})')[0]

        year_numeric = pd.to_numeric(
            year_numeric,
            errors="coerce"
        )
        year_numeric = year_numeric.apply(
            lambda x: x + 2000 if pd.notna(x) and x < 100 else x
        )
        
        bad_rows = df[
            (year_numeric < 2000) |
            (year_numeric > 2025) |
            (year_numeric.isnull())
        ]

        for index, row in bad_rows.iterrows():

            failures.append({
                "table": table_name,
                "rule": "DQ_04",
                "row": index,
                "issue": f"Invalid year: {row['year']}"
            })

dq03_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_03"
)

print("\nDQ-03 Failures:", dq03_count)

dq04_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_04"
)

print("DQ-04 Failures:", dq04_count)

# DQ-05 : Negative Financial Values

check_columns = [
    "sales",
    "market_cap_crore"
]

for table_name, df in child_tables.items():

    for col in check_columns:

        if col in df.columns:

            values = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            bad_rows = df[values < 0]

            for index, row in bad_rows.iterrows():

                failures.append({
                    "table": table_name,
                    "rule": "DQ_05",
                    "row": index,
                    "issue": f"Negative value in {col}: {row[col]}"
                })

dq05_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_05"
)

print("DQ-05 Failures:", dq05_count)

# DQ-06 : Missing Critical Financial Values

critical_columns = [
    "sales",
    "net_profit",
    "market_cap_crore"
]

for table_name, df in child_tables.items():

    for col in critical_columns:

        if col in df.columns:

            bad_rows = df[df[col].isnull()]

            for index, row in bad_rows.iterrows():

                failures.append({
                    "table": table_name,
                    "rule": "DQ_06",
                    "row": index,
                    "issue": f"Missing value in {col}"
                })

dq06_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_06"
)

print("DQ-06 Failures:", dq06_count)

# DQ-07 : Assets vs Liabilities Validation

if "total_assets" in balancesheet.columns and "total_liabilities" in balancesheet.columns:

    assets = pd.to_numeric(
        balancesheet["total_assets"],
        errors="coerce"
    )

    liabilities = pd.to_numeric(
        balancesheet["total_liabilities"],
        errors="coerce"
    )

    bad_rows = balancesheet[
        abs(assets - liabilities) > 1
    ]

    for index, row in bad_rows.iterrows():

        failures.append({
            "table": "Balance Sheet",
            "rule": "DQ_07",
            "row": index,
            "issue": f"Assets ({row['total_assets']}) != Liabilities ({row['total_liabilities']})"
        })

dq07_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_07"
)

print("DQ-07 Failures:", dq07_count)

failure_df = pd.DataFrame(failures)

failure_df.to_csv(
    "reports/validation_failures.csv",
    index=False
)

print("\nValidation report generated!")

print(financial_ratios.columns)
print(financial_ratios.head())