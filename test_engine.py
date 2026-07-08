from src.screener.engine import ScreenerEngine

engine = ScreenerEngine(
    db_path="data/database/nifty100.db",
    config_path="config/screener_config.yaml"
)

filtered = engine.apply_filters("quality_compounder")

scored = engine.calculate_composite_score(filtered)

ranked = engine.rank_companies(
    scored,
    "composite_quality_score"
)

print(
    ranked[
        [
            "company_id",
            "year",
            "composite_quality_score"
        ]
    ].head(10)
)
