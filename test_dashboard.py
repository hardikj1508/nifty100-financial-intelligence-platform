from src.dashboard.utils.db import *

conn = get_connection()

query = """
SELECT company_id,
       year,
       return_on_equity_pct
FROM financial_ratios
WHERE company_id IN ('ABB','BEL','HAL','LT')
AND year='Mar 2019'
"""

print(pd.read_sql(query, conn))

conn.close()