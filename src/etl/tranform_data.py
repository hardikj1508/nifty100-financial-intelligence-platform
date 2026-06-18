import pandas as pd
companies = pd.read_excel(
    "data/raw/companies.xlsx",
    header=1
)
companies.columns = (
    companies.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print(companies.columns)
print("\nMissing Values:")
print(companies.isnull().sum())
print("\nDuplicate Rows:")
print(companies.duplicated().sum())
print("\nShape:")
print(companies.shape)

companies.to_csv(
    "data/processed/companies_clean.csv",
    index=False
)

print("\nCleaned file saved successfully!")


financial_ratios = pd.read_excel(
    "data/raw/financial_ratios.xlsx"
)

financial_ratios.columns = (
    financial_ratios.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nFinancial Ratios:")
print(financial_ratios.head())
print("\nMissing Values:")
print(financial_ratios.isnull().sum())
print("\nDuplicate Rows:")
print(financial_ratios.duplicated().sum())
print("\nShape:")
print(financial_ratios.shape)

financial_ratios.to_csv(
    "data/processed/financial_ratios_clean.csv",
    index=False
)
print("\nFinancial Ratios cleaned file saved!")

balancesheet = pd.read_excel(
    "data/raw/balancesheet.xlsx",
    header=1
)
balancesheet.columns = (
    balancesheet.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nBalance Sheet:")
print(balancesheet.head())
print("\nMissing Values:")
print(balancesheet.isnull().sum())
print("\nDuplicate Rows:")
print(balancesheet.duplicated().sum())
print("\nShape:")
print(balancesheet.shape)

balancesheet.to_csv(
    "data/processed/balancesheet_clean.csv",
    index=False
)
print("\nBalance Sheet cleaned file saved!")


cashflow = pd.read_excel(
    "data/raw/cashflow.xlsx",
    header=1
)
cashflow.columns = (
    cashflow.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nCash Flow:")
print(cashflow.head())
print("\nMissing Values:")
print(cashflow.isnull().sum())
print("\nDuplicate Rows:")
print(cashflow.duplicated().sum())
print("\nShape:")
print(cashflow.shape)

cashflow.to_csv(
    "data/processed/cashflow_clean.csv",
    index=False
)
print("\nCash Flow cleaned file saved!")

market_cap = pd.read_excel(
    "data/raw/market_cap.xlsx")
market_cap.columns = (
    market_cap.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nMarket Cap:")
print(market_cap.head())
print("\nMissing Values:")
print(market_cap.isnull().sum())
print("\nDuplicate Rows:")
print(market_cap.duplicated().sum())
print("\nShape:")
print(market_cap.shape)

market_cap.to_csv(
    "data/processed/market_cap_clean.csv",
    index=False
)
print("\nMarket Cap cleaned file saved!")


profitandloss = pd.read_excel(
    "data/raw/profitandloss.xlsx",
    header=1
)
profitandloss.columns = (
    profitandloss.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nProfit and Loss:")
print(profitandloss.head())
print("\nMissing Values:")
print(profitandloss.isnull().sum())
print("\nDuplicate Rows:")
print(profitandloss.duplicated().sum())
print("\nShape:")
print(profitandloss.shape)

profitandloss.to_csv(
    "data/processed/profitandloss_clean.csv",
    index=False
)
print("\nProfit and Loss cleaned file saved!")  


analysis = pd.read_excel(
    "data/raw/analysis.xlsx",
    header=1
)
analysis.columns = (
    analysis.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nAnalysis:")
print(analysis.head())
print("\nMissing Values:")
print(analysis.isnull().sum())
print("\nDuplicate Rows:")
print(analysis.duplicated().sum())
print("\nShape:")
print(analysis.shape)

analysis.to_csv(
    "data/processed/analysis_clean.csv",
    index=False
)
print("\nAnalysis cleaned file saved!")

documents = pd.read_excel(
    "data/raw/documents.xlsx",
    header=1
)
documents.columns = (
    documents.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nDocuments:")
print(documents.head())
print("\nMissing Values:")
print(documents.isnull().sum())
print("\nDuplicate Rows:")
print(documents.duplicated().sum())
print("\nShape:")
print(documents.shape)

documents.to_csv(
    "data/processed/documents_clean.csv",
    index=False
)
print("\nDocuments cleaned file saved!")

peer_groups = pd.read_excel(
    "data/raw/peer_groups.xlsx")
peer_groups.columns = (
    peer_groups.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nPeer Groups:")
print(peer_groups.head())
print("\nMissing Values:")
print(peer_groups.isnull().sum())
print("\nDuplicate Rows:")
print(peer_groups.duplicated().sum())
print("\nShape:")
print(peer_groups.shape)

peer_groups.to_csv(
    "data/processed/peer_groups_clean.csv",
    index=False
)
print("\nPeer Groups cleaned file saved!")

prosandcons = pd.read_excel(
    "data/raw/prosandcons.xlsx",
    header=1
)
prosandcons.columns = (
    prosandcons.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

print("\nPros and Cons:")
print(prosandcons.head())
print("\nMissing Values:")
print(prosandcons.isnull().sum())
print("\nDuplicate Rows:")
print(prosandcons.duplicated().sum())
print("\nShape:")
print(prosandcons.shape)

prosandcons.to_csv(
    "data/processed/prosandcons_clean.csv",
    index=False
)
print("\nPros and Cons cleaned file saved!")


sectors = pd.read_excel(
    "data/raw/sectors.xlsx"
)
sectors.columns = (
    sectors.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)
print("\nSectors:")
print(sectors.head())
print("\nMissing Values:")
print(sectors.isnull().sum())
print("\nDuplicate Rows:")
print(sectors.duplicated().sum())
print("\nShape:")
print(sectors.shape)

sectors.to_csv(
    "data/processed/sectors_clean.csv",
    index=False
)
print("\nSectors cleaned file saved!")


stock_prices = pd.read_excel(
    "data/raw/stock_prices.xlsx")
stock_prices.columns = (
    stock_prices.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)
print("\nStock Prices:")
print(stock_prices.head())
print("\nMissing Values:")
print(stock_prices.isnull().sum())
print("\nDuplicate Rows:")
print(stock_prices.duplicated().sum())
print("\nShape:")
print(stock_prices.shape)
stock_prices.to_csv(
    "data/processed/stock_prices_clean.csv",
    index=False
)
print("\nStock Prices cleaned file saved!")