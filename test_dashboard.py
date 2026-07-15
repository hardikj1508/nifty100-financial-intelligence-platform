from src.dashboard.utils.db import *
import pandas as pd

conn = get_connection()

query = """
SELECT *
FROM financial_ratios
WHERE company_id='ABB'
AND year='Mar 2024'
"""

df = pd.read_sql(query, conn)

print(df)

conn.close()