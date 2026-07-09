import numpy as np
import sqlite3
import pandas as pd

DATABASE = "data/database/nifty100.db"


class PeerEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

        self.peer_df = pd.read_sql(
            "SELECT * FROM peer_groups",
            self.conn
        )

        self.ratio_df = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        self.sector_df = pd.read_sql(
            "SELECT * FROM sectors",
            self.conn
        )

        print("Peer Engine Loaded")

    def get_peer_group(self, company_id):

        peer = self.peer_df[
            self.peer_df["company_id"] == company_id
        ]

        if peer.empty:
            return None

        return peer.iloc[0]["peer_group_name"]
    
    def get_peers(self, company_id):

        peer_group = self.get_peer_group(company_id)

        if peer_group is None:
            return pd.DataFrame()

        peers = self.peer_df[
            self.peer_df["peer_group_name"] == peer_group
        ]

        return peers
    
    def get_peer_financials(self, company_id):

        peers = self.get_peers(company_id)

        if peers.empty:
            return pd.DataFrame()

        peer_ids = peers["company_id"].tolist()

        financials = self.ratio_df[
            self.ratio_df["company_id"].isin(peer_ids)
        ]

        return financials
    
    def calculate_percentile_rank(self, company_id, metric, inverse=False):

        df = self.get_peer_financials(company_id).copy()

        if df.empty:
            return pd.DataFrame()

        # Remove rows where the metric is missing
        df = df.dropna(subset=[metric])

        if df.empty:
            return pd.DataFrame()

        if inverse:
            df["percentile_rank"] = (
                df.groupby("year")[metric]
                    .rank(
                        method="average",
                        pct=True,
                        ascending=False
                    )
                    * 100
            )
        else:
            df["percentile_rank"] = (
                df.groupby("year")[metric]
                    .rank(
                        method="average",
                        pct=True
                    )
                    * 100
                )

        return df[
            [
                "company_id",
                "year",
                metric,
                "percentile_rank"
            ]
        ].sort_values(
            "percentile_rank",
            ascending=False
        )
    
    def create_peer_percentiles_table(self):

        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peer_percentiles (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                company_id TEXT,

                peer_group_name TEXT,

                metric TEXT,

                value REAL,

                percentile_rank REAL,

                year TEXT

            )
        """)

        self.conn.commit()

        print("peer_percentiles table created.")

    def save_percentile_rank(self, df, metric, peer_group):

        if df.empty:
            print("Nothing to save.")
            return
        
        cursor = self.conn.cursor()

        cursor.execute(
            """
            DELETE FROM peer_percentiles
            WHERE peer_group_name = ?
            AND metric = ?
            """,
            (peer_group, metric)
        )

        for _, row in df.iterrows():

            cursor.execute(
                """
                INSERT INTO peer_percentiles
                (
                    company_id,
                    peer_group_name,
                    metric,
                    value,
                    percentile_rank,
                    year
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["company_id"],
                    peer_group,
                    metric,
                    round(row[metric], 2),
                    round(row["percentile_rank"], 2),
                    row["year"]
                )
            )

        self.conn.commit()

    def get_metrics(self):

        return [
            ("return_on_equity_pct", False),
            ("net_profit_margin_pct", False),
            ("debt_to_equity", True),
            ("interest_coverage", False),
            ("asset_turnover", False)
        ]
    
    def process_peer_group(self, company_id):

        peer_group = self.get_peer_group(company_id)

        if peer_group is None:
            print(f"{company_id}: No peer group assigned.")
            return

        print(f"Processing {peer_group}")

        for metric, inverse in self.get_metrics():

            print(metric)

            ranked = self.calculate_percentile_rank(
                company_id,
                metric,
                inverse=inverse
            )

            self.save_percentile_rank(
                ranked,
                metric,
                peer_group
            )

    def get_all_peer_groups(self):

        return self.peer_df["peer_group_name"].unique()   
    
    def process_all_peer_groups(self):

        for peer_group in self.get_all_peer_groups():

            company = (
                self.peer_df[
                    self.peer_df["peer_group_name"] == peer_group
                ]
                .iloc[0]["company_id"]
            )

            self.process_peer_group(company)

        print("All peer groups processed successfully.")