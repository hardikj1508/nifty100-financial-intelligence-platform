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