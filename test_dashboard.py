from src.dashboard.utils.db import get_connection
import pandas as pd

conn = get_connection()

df = pd.read_sql("""
SELECT company_id, COUNT(*) AS years
FROM financial_ratios
GROUP BY company_id
ORDER BY years ASC
""", conn)

print(df.head(20))

conn.close()