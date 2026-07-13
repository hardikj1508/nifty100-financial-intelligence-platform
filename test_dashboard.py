from src.dashboard.utils.db import *

print(get_years())
print(get_total_companies())
print(get_average_roe("Mar 2024"))
print(get_median_de("Mar 2024"))
print(get_debt_free_count("Mar 2024"))
print(get_median_net_profit_margin("Mar 2024"))

print(get_sector_breakdown().head())
print(get_top_companies("Mar 2024").head())