import pandas as pd

companies = pd.read_excel("data/raw/companies.xlsx")
profitandloss = pd.read_excel("data/raw/profitandloss.xlsx")
balancesheet = pd.read_excel("data/raw/balancesheet.xlsx")
cashflow = pd.read_excel("data/raw/cashflow.xlsx")

print("Companies:", companies.shape)
print("Profit & Loss:", profitandloss.shape)
print("Balance Sheet:", balancesheet.shape)
print("Cash Flow:", cashflow.shape)