import pandas as pd
import sqlite3

conn = sqlite3.connect("data/database/nifty100.db")
conn.execute("PRAGMA foreign_keys = ON")

print("Database Connected")

companies = pd.read_csv("data/processed/companies_clean.csv")
profitandloss = pd.read_csv("data/processed/profitandloss_clean.csv")
balancesheet = pd.read_csv("data/processed/balancesheet_clean.csv")
cashflow = pd.read_csv("data/processed/cashflow_clean.csv")
analysis = pd.read_csv("data/processed/analysis_clean.csv")
documents = pd.read_csv("data/processed/documents_clean.csv")
financial_ratios = pd.read_csv("data/processed/financial_ratios_clean.csv")
stock_prices = pd.read_csv("data/processed/stock_prices_clean.csv")
peer_groups = pd.read_csv("data/processed/peer_groups_clean.csv")
sectors = pd.read_csv("data/processed/sectors_clean.csv")
prosandcons = pd.read_csv("data/processed/prosandcons_clean.csv")
market_cap = pd.read_csv("data/processed/market_cap_clean.csv")

companies.to_sql(
    "companies",
    conn,
    if_exists="replace",
    index=False
)

print("Companies Loaded")

profitandloss.to_sql(
    "profitandloss",
    conn,
    if_exists="replace",
    index=False
)

balancesheet.to_sql(
    "balancesheet",
    conn,
    if_exists="replace",
    index=False
)

cashflow.to_sql(
    "cashflow",
    conn,
    if_exists="replace",
    index=False
)

analysis.to_sql(
    "analysis",
    conn,
    if_exists="replace",
    index=False
)

documents.to_sql(
    "documents",
    conn,
    if_exists="replace",
    index=False
)

financial_ratios.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

stock_prices.to_sql(
    "stock_prices",
    conn,
    if_exists="replace",
    index=False
)

peer_groups.to_sql(
    "peer_groups",
    conn,
    if_exists="replace",
    index=False
)

sectors.to_sql(
    "sectors",
    conn,
    if_exists="replace",
    index=False
)

prosandcons.to_sql(
    "prosandcons",
    conn,
    if_exists="replace",
    index=False
)

market_cap.to_sql(
    "market_cap",
    conn,
    if_exists="replace",
    index=False
)

print("All Tables Loaded")

print("\nRow Counts")

tables = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "financial_ratios",
    "stock_prices",
    "peer_groups",
    "sectors",
    "prosandcons",
    "market_cap"
]

for table in tables:

    count = pd.read_sql_query(
        f"SELECT COUNT(*) as count FROM {table}",
        conn
    )

    print(table, ":", count.iloc[0, 0])

    audit = []

for table in tables:

    count = pd.read_sql_query(
        f"SELECT COUNT(*) as count FROM {table}",
        conn
    ).iloc[0, 0]

    audit.append({
        "table_name": table,
        "row_count": count
    })

audit_df = pd.DataFrame(audit)

audit_df.to_csv(
    "reports/load_audit.csv",
    index=False
)

print("\nload_audit.csv generated!")

fk_check = pd.read_sql_query(
    "PRAGMA foreign_key_check;",
    conn
)

print("\nForeign Key Violations:")
print(len(fk_check))

