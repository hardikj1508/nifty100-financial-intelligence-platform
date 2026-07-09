import sqlite3
from sqlalchemy import column
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

        # Remove duplicate company-year records (temporary safeguard)
        financial_df = (
            financial_df
            .sort_values("id")
            .drop_duplicates(
                subset=["company_id", "year"],
                keep="first"
            )
            .reset_index(drop=True)
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
        sectors_df = pd.read_sql(
            "SELECT company_id, broad_sector FROM sectors",
            self.conn
        )      
        
        #Merge financial ratios with market cap
        merged_df = financial_df.merge(
            market_df,
            on = ["company_id","year"],
            how = "left"
        )

        merged_df = merged_df.merge(
            sectors_df,
            on="company_id",
            how="left"
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

                # Interest Coverage special handling
                if column == "interest_coverage":

                    debt_free = filtered_df[
                        filtered_df["debt_to_equity"] == 0
                    ]

                    others = filtered_df[
                        filtered_df["debt_to_equity"] != 0
                    ]

                    others = others[
                        others[column] >= condition["min"]
                    ]

                    filtered_df = pd.concat(
                        [debt_free, others],
                        ignore_index=True
                    )

                else:

                    filtered_df = filtered_df[
                        filtered_df[column] >= condition["min"]
                    ]

            if "max" in condition:

                # Skip Debt-to-Equity filter for Financials
                if column == "debt_to_equity":

                    financials = filtered_df[
                        filtered_df["broad_sector"] == "Financials"
                    ]

                    non_financials = filtered_df[
                        filtered_df["broad_sector"] != "Financials"
                    ]

                    non_financials = non_financials[
                        non_financials[column] <= condition["max"]
                    ]

                    filtered_df = pd.concat(
                        [financials, non_financials],
                        ignore_index=True
                    )

                else:

                    filtered_df = filtered_df[
                        filtered_df[column] <= condition["max"]
                    ]

        return filtered_df
    
    def calculate_composite_score(self, df):

        scored_df = df.copy()

        # Profitability
        roe_score = self.normalize_by_sector(
            scored_df,
            "return_on_equity_pct"
        )
        npm_score = self.normalize_by_sector(
            scored_df,
            "net_profit_margin_pct"
        )

        revenue_score = self.normalize_by_sector(
            scored_df,
            "compounded_sales_growth"
        )

        profit_score = self.normalize_by_sector(
            scored_df,
            "compounded_profit_growth"
        )

        debt_score = self.normalize_by_sector(
            scored_df,
            "debt_to_equity",
            inverse=True
        )

        interest_score = self.normalize_by_sector(
            scored_df,
            "interest_coverage"
        ) 

        # Composite Score (temporary version)
        scored_df["composite_quality_score"] = (
            roe_score * 0.25 +
            npm_score * 0.20 +
            revenue_score * 0.20 +
            profit_score * 0.20 +
            debt_score * 0.10 +
            interest_score * 0.05
        )

        return scored_df

    def normalize_score(self, series, inverse=False):
    
        series = pd.to_numeric(series, errors="coerce")

        valid = series.dropna()

        if valid.empty:
            return pd.Series(50, index=series.index)

        p10 = valid.quantile(0.10)
        p90 = valid.quantile(0.90)

        clipped = series.clip(lower=p10, upper=p90)

        min_val = clipped.min()
        max_val = clipped.max()

        if min_val == max_val:
            score = pd.Series(50, index=series.index)
        else:
            score = ((clipped - min_val) /
                     (max_val - min_val)) * 100

        if inverse:
            score = 100 - score

        return score
    
    def normalize_by_sector(self, df, column, inverse=False):
        """
        Normalize a metric separately within each broad sector.
        """

        normalized = pd.Series(index=df.index, dtype=float)

        for sector, group in df.groupby("broad_sector"):
            normalized.loc[group.index] = self.normalize_score(
                group[column],
                inverse=inverse
            )

        return normalized

    def rank_companies(self, df, score_column):
        return (
            df.sort_values(
                by=score_column,
                ascending=False
            )
            .reset_index(drop=True)
        )
    
    def get_top_companies(self, df, n=10):
        return df.head(n)
    
    def export_screener(self, output_path):

        presets = [
            "quality_compounder",
            "value_pick",
            "growth_accelerator",
            "dividend_champion",
            "debt_free_blue_chip",
            "turnaround_watch"
        ]

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

            for preset in presets:

                df = self.apply_filters(preset)

                df = self.calculate_composite_score(df)

                df = self.rank_companies(
                    df,
                    "composite_quality_score"
                )

                drop_cols = [
                    "id_x",
                    "id_y",
                    "id"
                ]

                df = df.drop(
                    columns=[c for c in drop_cols if c in df.columns]
                )
                
                df.to_excel(
                    writer,
                    sheet_name=preset[:31],
                    index=False
                )

        print(f"Screener exported to {output_path}")