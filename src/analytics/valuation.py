import numpy as np
import pandas as pd

# -------------------------
# Load Data
# -------------------------

market_cap = pd.read_excel(
    "data/raw/market_cap.xlsx"
)

financial = pd.read_csv(
    "data/processed/financial_ratios_clean.csv"
)

sector = pd.read_csv(
    "data/processed/sectors_clean.csv"
)

companies = pd.read_csv(
    "data/processed/companies_clean.csv"
)

# -------------------------
# Standardize Year
# -------------------------

financial["year"] = (
    financial["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

# -------------------------
# Remove Duplicate Company-Year
# -------------------------

financial_unique = financial.drop_duplicates(
    subset=["company_id", "year"],
    keep="last"
)

# -------------------------
# 5-Year Median P/E
# -------------------------

latest_five = (
    market_cap
    .sort_values(["company_id", "year"])
    .groupby("company_id")
    .tail(5)
)

median_pe = (
    latest_five
    .groupby("company_id")["pe_ratio"]
    .median()
    .reset_index()
)

median_pe.rename(
    columns={
        "pe_ratio": "5yr_median_PE"
    },
    inplace=True
)

# -------------------------
# Merge Financial Data
# -------------------------

valuation = market_cap.merge(
    financial_unique[
        [
            "company_id",
            "year",
            "free_cash_flow_cr"
        ]
    ],
    on=["company_id", "year"],
    how="left"
)

# -------------------------
# Calculate FCF Yield
# -------------------------

valuation["fcf_yield_pct"] = (
    valuation["free_cash_flow_cr"]
    / valuation["market_cap_crore"]
) * 100

# -------------------------
# Merge Sector Data
# -------------------------

valuation = valuation.merge(
    sector[
        [
            "company_id",
            "broad_sector"
        ]
    ],
    on="company_id",
    how="left"
)

# -------------------------
# Latest Year
# -------------------------

latest = valuation[
    valuation["year"] == valuation["year"].max()
].copy()

# -------------------------
# Sector Median P/E
# -------------------------

sector_median = (
    latest
    .groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_median.rename(
    columns={
        "pe_ratio": "sector_median_pe"
    },
    inplace=True
)

# -------------------------
# Merge Sector Median
# -------------------------

valuation = valuation.merge(
    sector_median,
    on="broad_sector",
    how="left"
)

# -------------------------
# P/E vs Sector Median
# -------------------------

valuation["pe_vs_sector_median_pct"] = (
    valuation["pe_ratio"]
    / valuation["sector_median_pe"]
) * 100

# -------------------------
# Valuation Flags
# -------------------------

conditions = [
    valuation["pe_ratio"] > valuation["sector_median_pe"] * 1.5,
    valuation["pe_ratio"] < valuation["sector_median_pe"] * 0.7
]

choices = [
    "Caution",
    "Discount"
]

valuation["flag"] = np.select(
    conditions,
    choices,
    default="Fair"
)

# -------------------------
# Merge Company Names
# -------------------------

summary = valuation.merge(
    companies[
        [
            "id",
            "company_name"
        ]
    ],
    left_on="company_id",
    right_on="id",
    how="left"
)

summary = summary.merge(
    median_pe,
    on="company_id",
    how="left"
)

# Remove the extra id column if it exists
summary = summary.drop(
    columns=["id_x", "id_y"],
    errors="ignore"
)

print(summary.columns.tolist())

# -------------------------
# Select Final Columns
# -------------------------

summary = summary[
    [
        "company_id",
        "company_name",
        "year",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "fcf_yield_pct",
        "5yr_median_PE",
        "sector_median_pe",
        "pe_vs_sector_median_pct",
        "flag"
    ]
]

# -------------------------
# Save Outputs
# -------------------------

summary.to_excel(
    "output/valuation_summary.xlsx",
    index=False
)

flags = summary[
    summary["flag"] != "Fair"
]

flags.to_csv(
    "output/valuation_flags.csv",
    index=False
)

# -------------------------
# Verification
# -------------------------

print(summary.head())

print("\nShape:")
print(summary.shape)

print("\nFlag Counts:")
print(summary["flag"].value_counts())

print(
    summary[
        [
            "company_id",
            "5yr_median_PE"
        ]
    ].drop_duplicates().head(10)
)