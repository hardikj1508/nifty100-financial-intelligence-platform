from src.screener.engine import ScreenerEngine

engine = ScreenerEngine(
    db_path="data/database/nifty100.db",
    config_path="config/screener_config.yaml"
)

filtered = engine.apply_filters("quality_compounder")

print(filtered.head())

print("\nFiltered Shape:")
print(filtered.shape)

print("\nVerification")

print("Minimum ROE:",
      filtered["return_on_equity_pct"].min())

print("Maximum Debt/Equity:",
      filtered["debt_to_equity"].max())

print("Minimum Free Cash Flow:",
      filtered["free_cash_flow_cr"].min())