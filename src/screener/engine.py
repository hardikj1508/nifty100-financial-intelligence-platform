import sqlite3
import yaml
import pandas as pd


class ScreenerEngine:

    def __init__(self, db_path, config_path):
        self.conn = sqlite3.connect(db_path)

        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

        #Load financial ratios
        financial_df = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        financial_df["year"] = financial_df["year"].astype(str)
        financial_df["year"] = financial_df["year"].str.extract(r'(\d{4})')

        #Load market cap
        market_df = pd.read_sql(
            "SELECT * FROM market_cap",
            self.conn
        )

        #Load analysis
        analysis_df = pd.read_sql(
            "SELECT * FROM analysis",
            self.conn
        )

        financial_df["year"] = financial_df["year"].astype(str)
        market_df["year"] = market_df["year"].astype(str)      
        
        #Merge financial ratios with market cap
        merged_df = financial_df.merge(
            market_df,
            on = ["company_id","year"],
            how = "left"
        )

        #Merge analysis
        merged_df = merged_df.merge(
            analysis_df,
            on = "company_id",
            how = "left"
        )

        # Convert analysis columns from TEXT to numeric
        numeric_cols = [
            "compounded_sales_growth",
            "compounded_profit_growth",
            "stock_price_cagr",
            "roe"
        ]

        for col in numeric_cols:
            merged_df[col] = pd.to_numeric(
                merged_df[col],
                errors="coerce"
            )

        self.df = merged_df

    
    def apply_filters(self, preset_name):

        filtered_df = self.df.copy()

        preset = self.config.get(preset_name)

        if preset is None:
            raise ValueError(
                f"Preset '{preset_name}' not found in configuration."
            )

        for column, condition in preset.items():

            if "min" in condition:
                filtered_df = filtered_df[
                    filtered_df[column] >= condition["min"]
            ]

            if "max" in condition:
                filtered_df = filtered_df[
                    filtered_df[column] <= condition["max"]
                ]

        return filtered_df