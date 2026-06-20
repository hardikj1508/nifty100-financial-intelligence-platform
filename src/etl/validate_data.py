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

dq01_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_01"
)

print("DQ-01 Failures:", dq01_count)

dq02_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_02"
)

print("DQ-02 Failures:", dq02_count)

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

dq03_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_03"
)

print("DQ-03 Failures:", dq03_count)

# DQ-04 : BS Balance <1%

assets = pd.to_numeric(
    balancesheet["total_assets"],
    errors="coerce"
)

liabilities = pd.to_numeric(
    balancesheet["total_liabilities"],
    errors="coerce"
)

difference_pct = (
    abs(assets - liabilities)
    / assets.replace(0, pd.NA)
) * 100

bad_rows = balancesheet[
    difference_pct > 1
]

for index, row in bad_rows.iterrows():

    failures.append({
        "table": "Balance Sheet",
        "rule": "DQ_04",
        "row": index,
        "issue": "Balance Sheet mismatch > 1%"
    })

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

# DQ-08 : OPM Cross Check

pl_opm = profitandloss[
    ["company_id", "year", "sales", "operating_profit"]
].copy()

ratio_opm = financial_ratios[
    ["company_id", "year", "operating_profit_margin_pct"]
].copy()

merged = pd.merge(
    pl_opm,
    ratio_opm,
    on=["company_id", "year"],
    how="inner"
)

merged["calculated_opm"] = (
    merged["operating_profit"] /
    merged["sales"]
) * 100

bad_rows = merged[
    abs(
        merged["calculated_opm"] -
        merged["operating_profit_margin_pct"]
    ) > 1
]

for index, row in bad_rows.iterrows():

    failures.append({
        "table": "Financial Ratios",
        "rule": "DQ_08",
        "row": index,
        "issue": "OPM mismatch"
    })

dq08_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_08"
)

print("DQ-08 Failures:", dq08_count)

# DQ-09 : Positive Sales Check

if "sales" in profitandloss.columns:

    sales_numeric = pd.to_numeric(
        profitandloss["sales"],
        errors="coerce"
    )

    bad_rows = profitandloss[
        (sales_numeric <= 0)
        | (sales_numeric.isnull())
    ]

    for index, row in bad_rows.iterrows():

        failures.append({
            "table": "Profit & Loss",
            "rule": "DQ_09",
            "row": index,
            "issue": f"Invalid sales value: {row['sales']}"
        })

dq09_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_09"
)

print("DQ-09 Failures:", dq09_count)

# DQ-10 : Positive Market Cap

if "market_cap_crore" in market_cap.columns:

    market_cap_numeric = pd.to_numeric(
        market_cap["market_cap_crore"],
        errors="coerce"
    )

    bad_rows = market_cap[
        (market_cap_numeric <= 0)
        | (market_cap_numeric.isnull())
    ]

    for index, row in bad_rows.iterrows():

        failures.append({
            "table": "Market Cap",
            "rule": "DQ_10",
            "row": index,
            "issue": f"Invalid market cap: {row['market_cap_crore']}"
        })

dq10_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_10"
)

print("DQ-10 Failures:", dq10_count)

# DQ-11 : Net Profit Not Null

if "net_profit" in profitandloss.columns:

    bad_rows = profitandloss[
        profitandloss["net_profit"].isnull()
    ]

    for index, row in bad_rows.iterrows():

        failures.append({
            "table": "Profit & Loss",
            "rule": "DQ_11",
            "row": index,
            "issue": "Missing net profit"
        })

dq11_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_11"
)

print("DQ-11 Failures:", dq11_count)

# DQ-12 : EPS Not Null

if "eps" in profitandloss.columns:

    bad_rows = profitandloss[
        profitandloss["eps"].isnull()
    ]

    for index, row in bad_rows.iterrows():

        failures.append({
            "table": "Profit & Loss",
            "rule": "DQ_12",
            "row": index,
            "issue": "Missing EPS"
        })

dq12_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_12"
)

print("DQ-12 Failures:", dq12_count)

# DQ-13 : Market Cap Year Validity

if "year" in market_cap.columns:

    year_numeric = pd.to_numeric(
        market_cap["year"],
        errors="coerce"
    )

    bad_rows = market_cap[
        (year_numeric < 2000)
        | (year_numeric > 2025)
        | (year_numeric.isnull())
    ]

    for index, row in bad_rows.iterrows():

        failures.append({
            "table": "Market Cap",
            "rule": "DQ_13",
            "row": index,
            "issue": f"Invalid year: {row['year']}"
        })

dq13_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_13"
)

print("DQ-13 Failures:", dq13_count)

# DQ-14 : Duplicate Company-Year

if "company_id" in profitandloss.columns and "year" in profitandloss.columns:

    dup_rows = profitandloss[
        profitandloss.duplicated(
            subset=["company_id", "year"]
        )
    ]

    for index, row in dup_rows.iterrows():

        failures.append({
            "table": "Profit & Loss",
            "rule": "DQ_14",
            "row": index,
            "issue": "Duplicate company-year"
        })

dq14_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_14"
)

print("DQ-14 Failures:", dq14_count)

# DQ-15 : Dividend Payout Check

if "dividend_payout" in profitandloss.columns:

    payout_numeric = pd.to_numeric(
        profitandloss["dividend_payout"],
        errors="coerce"
    )

    bad_rows = profitandloss[
        payout_numeric < 0
    ]

    for index, row in bad_rows.iterrows():

        failures.append({
            "table": "Profit & Loss",
            "rule": "DQ_15",
            "row": index,
            "issue": "Negative dividend payout"
        })

dq15_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_15"
)

print("DQ-15 Failures:", dq15_count)

# DQ-16 : Company Exists In Master

master_companies = set(
    companies["id"].astype(str)
)

bad_rows = companies[
    ~companies["id"].astype(str).isin(master_companies)
]

for index, row in bad_rows.iterrows():

    failures.append({
        "table": "Companies",
        "rule": "DQ_16",
        "row": index,
        "issue": "Company missing from master"
    })

dq16_count = sum(
    1 for x in failures
    if x["rule"] == "DQ_16"
)

print("DQ-16 Failures:", dq16_count)

failure_df = pd.DataFrame(failures)

failure_df.to_csv(
    "reports/validation_failures.csv",
    index=False
)

print("\nValidation report generated!")

print("\nCompanies")
print(companies.columns)

print("\nProfit & Loss")
print(profitandloss.columns)

print("\nBalance Sheet")
print(balancesheet.columns)

print("\nCash Flow")
print(cashflow.columns)

print("\nAnalysis")
print(analysis.columns)

print("\nDocuments")
print(documents.columns)

print("\nFinancial Ratios")
print(financial_ratios.columns)

print("\nStock Prices")
print(stock_prices.columns)

print("\nPeer Groups")
print(peer_groups.columns)

print("\nSectors")
print(sectors.columns)

print("\nPros and Cons")
print(prosandcons.columns)

print("\nMarket Cap")
print(market_cap.columns)
