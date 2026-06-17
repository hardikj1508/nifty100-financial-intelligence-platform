import pandas as pd

df = pd.read_excel("data/raw/companies.xlsx")

print("\nColumns:")
print(df.columns)

print("\nShape:")
print(df.shape)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicates:")
print(df.duplicated().sum())

print("\nData Types:")
print(df.dtypes)

print("\nFirst 5 Rows:")
print(df.head())