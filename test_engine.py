from src.screener.engine import ScreenerEngine

engine = ScreenerEngine(
    db_path="data/database/nifty100.db",
    config_path="config/screener_config.yaml"
)

filtered = engine.apply_filters("quality_compounder")

scored = engine.calculate_composite_score(filtered)

print(scored[
    [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "debt_to_equity",
        "interest_coverage"
    ]
].isna().sum())

print(scored[
    [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "debt_to_equity",
        "interest_coverage"
    ]
].head())

