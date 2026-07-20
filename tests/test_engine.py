from src.screener.engine import ScreenerEngine

engine = ScreenerEngine(
    db_path="data/database/nifty100.db",
    config_path="config/screener_config.yaml"
)

engine.export_screener(
    "reports/screener_output.xlsx"
)