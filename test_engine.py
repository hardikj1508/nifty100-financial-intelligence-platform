from src.screener.engine import ScreenerEngine

engine = ScreenerEngine(
    db_path="data/database/nifty100.db",
    config_path="config/screener_config.yaml"
)

presets = [
    "quality_compounder",
    "value_pick",
    "growth_accelerator",
    "dividend_champion",
    "debt_free_blue_chip",
    "turnaround_watch"
]

for preset in presets:
    result = engine.apply_filters(preset)
    print(f"{preset}: {result.shape[0]} companies")