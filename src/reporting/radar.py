import os
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATABASE = "data/database/nifty100.db"

METRIC_NAMES = {
    "return_on_equity_pct": "ROE",
    "net_profit_margin_pct": "NPM",
    "debt_to_equity": "D/E",
    "interest_coverage": "ICR",
    "asset_turnover": "Asset Turnover"
}

class RadarChartGenerator:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)


        self.percentile_df = pd.read_sql(
            "SELECT * FROM peer_percentiles",
            self.conn
        )

        self.peer_df = pd.read_sql(
            "SELECT * FROM peer_groups",
            self.conn
        )

        self.sector_df = pd.read_sql(
            "SELECT * FROM sectors",
            self.conn
        )

        print("Radar Chart Generator Loaded")

    def get_company_percentiles(self, company_id, year):

        return (
            self.percentile_df[
                (self.percentile_df["company_id"] == company_id) &
                (self.percentile_df["year"] == year)
            ]
            .sort_values("metric")
            .reset_index(drop=True)
        )
    
    def plot_radar_chart(self, company_id, year):

        df = self.get_company_percentiles(company_id, year)

        if df.empty:
            print(f"No data found for {company_id}")
            return
        
        peer_group = df.iloc[0]["peer_group_name"]

        peer_df = self.get_peer_average_percentiles(
            peer_group,
            year
        )

        # Align company metrics with peer metrics
        chart_df = (
            df.merge(
                peer_df,
                on="metric",
                how="inner",
                suffixes=("_company", "_peer")
            )
        )

        if chart_df.empty:
            print(f"No common metrics found for {company_id}")
            return
        
        labels = [
            METRIC_NAMES[m]
            for m in chart_df["metric"]
        ]

        values = chart_df["percentile_rank_company"].tolist()

        peer_values = chart_df["percentile_rank_peer"].tolist()

        # Close the polygon
        labels.append(labels[0])
        values.append(values[0])
        peer_values.append(peer_values[0])

        angles = np.linspace(
            0,
            2 * np.pi,
            len(labels),
            endpoint=True
        )

        _, ax = plt.subplots(
            figsize=(8, 8),
            subplot_kw={"polar": True}
        )

        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.plot(
            angles,
            peer_values,
            linestyle="--",
            linewidth=2,
            label="Peer Average"
        )

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels[:-1])

        ax.set_ylim(0, 100)

        ax.set_title(f"{company_id} ({year})")

        ax.legend(loc="upper right")

        os.makedirs("reports/radar_charts", exist_ok=True)

        filename = f"reports/radar_charts/{company_id}_{year}.png"

        plt.savefig(
            filename,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(f"Saved: {filename}")

    def get_peer_average_percentiles(self, peer_group_name, year):

        df = self.percentile_df[
            (self.percentile_df["peer_group_name"] == peer_group_name) &
            (self.percentile_df["year"] == year)
        ]

        return (
            df.groupby("metric")["percentile_rank"]
            .mean()
            .reset_index()
            .sort_values("metric")
            .reset_index(drop=True)
        )
    
    def generate_all_radar_charts(self, year):

        companies = (
            self.percentile_df["company_id"]
            .unique()
        )

        generated = 0

        for company in companies:

            try:
                self.plot_radar_chart(company, year)
                generated += 1

            except (ValueError, KeyError, TypeError) as e:
                print(f"Skipping {company}: {e}")

        print(f"{generated} radar charts generated.")