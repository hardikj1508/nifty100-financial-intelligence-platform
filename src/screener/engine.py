import sqlite3
import yaml
import pandas as pd


class ScreenerEngine:

    def __init__(self, db_path, config_path):
        self.conn = sqlite3.connect(db_path)

        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

        self.df = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )
    
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