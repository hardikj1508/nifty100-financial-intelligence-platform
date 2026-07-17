from src.dashboard.utils.db import *

df = get_company_reports("ABB")

print(df)

print(df.columns.tolist())