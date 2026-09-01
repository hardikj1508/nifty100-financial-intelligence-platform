import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

DATABASE = "data/database/nifty100.db"
OUTPUT_DIR = "reports/sector_reports"

REPORT_YEAR = "Mar 2024"

METRICS = {
    "return_on_equity_pct": "ROE (%)",
    "net_profit_margin_pct": "Net Profit Margin (%)",
    "operating_profit_margin_pct": "Operating Profit Margin (%)",
    "debt_to_equity": "Debt / Equity",
    "interest_coverage": "Interest Coverage",
    "asset_turnover": "Asset Turnover",
    "free_cash_flow_cr": "Free Cash Flow (₹ Cr)",
    "earnings_per_share": "EPS",
}

def get_sector_data(sector):
    """Fetch financial metrics for one broad sector."""

    conn = sqlite3.connect(DATABASE)

    query = """
        SELECT
            c.company_name,
            s.company_id,
            s.broad_sector,
            f.year,
            f.return_on_equity_pct,
            f.net_profit_margin_pct,
            f.operating_profit_margin_pct,
            f.debt_to_equity,
            f.interest_coverage,
            f.asset_turnover,
            f.free_cash_flow_cr,
            f.earnings_per_share
        FROM financial_ratios f
        JOIN companies c
            ON f.company_id = c.id
        Join sectors s
            ON c.id = s.company_id
        Where s.broad_sector = ?
            AND f.year = ?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[sector, REPORT_YEAR]
    )

    conn.close()

    return df

def calculate_sector_summary(df):
    """Calculate median values for sector metrics."""

    summary = {}

    for column, label in METRICS.items():
        if column in df.columns:
            values = pd.to_numeric(
                df[column],
                errors="coerce"
            ).dropna()

            if not values.empty:
                summary[label] = values.median()
            else:
                summary[label] = None
    return summary

def create_sector_report(sector):
    """Create a PDF report for one sector."""

    df = get_sector_data(sector)

    if df.empty:
        print(f"Skipping {sector}: no data found.")
        return False

    summary = calculate_sector_summary(df)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = os.path.join(
        OUTPUT_DIR,
        f"{sector.replace(' ', '_')}_sector_report.pdf"
    )

    with PdfPages(filename) as pdf:

        #Page 1 - SECTOR OVERVIEW

        fig = plt.figure(figsize=(11.69, 8.27))
        fig.patch.set_facecolor("white")

        fig.text(
            0.05,
            0.91,
            "NIFTY 100 FINANCIAL INTELLIGENCE PLATFORM",
            fontsize = 16,
            fontweight = "bold"
        )

        fig.text(
            0.05,
            0.84,
            f"Sector Analysis - {sector}",
            fontsize = 24,
            fontweight = "bold"
        )
        fig.text(
            0.05,
            0.79,
            f"Financial Period: {REPORT_YEAR}",
            fontsize = 11
        )
        fig.text(
            0.05,
            0.70,
            f"Companies in Sector: {len(df)}",
            fontsize=14
        )
        fig.text(
            0.05,
            0.63,
            "Sector Median KPIs",
            fontsize = 16, 
            fontweight = "bold"
        )

        y = 0.57

        for label, value in summary.items():

            if  value is None:
                display_value = "N/A"

            elif "Margin" in label or label == "ROE (%)":
                display_value = f"{value:,.2f}%"

            elif "Free Cash Flow" in label:
                display_value = f"{value:,.2f}"

            else:
                display_value = f"{value:.2f}"

            fig.text(
                0.08,
                y,
                f"{label}: {display_value}",
                fontsize=11
            )

            y -=0.045

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        #Page 2

        plot_df = df[
            [
                "company_name",
                "return_on_equity_pct",
                "net_profit_margin_pct"
            ]
        ].copy()

        plot_df["return_on_equity_pct"] = pd.to_numeric(
            plot_df["return_on_equity_pct"],
            errors="coerce"
        )

        plot_df["net_profit_margin_pct"] = pd.to_numeric(
            plot_df["net_profit_margin_pct"],
            errors="coerce"
        )

        plot_df = plot_df.dropna()

        if not plot_df.empty:

            fig,ax = plt.subplots(figsize=(11, 7))

            ax.scatter(
                plot_df["return_on_equity_pct"],
                plot_df["net_profit_margin_pct"],
                s=90,
                alpha=0.75
            )

            for _, row in plot_df.iterrows():

                ax.annotate(
                    row["company_name"],
                    (
                        row["return_on_equity_pct"],
                        row["net_profit_margin_pct"]
                    ),
                    fontsize=7,
                    xytext=(4, 4),
                    textcoords="offset points"
                )

            ax.set_title(
                f"{sector} - ROE vs Net Profit Margin",
                fontsize=16,
                fontweight = "bold"
            )

            ax.set_xlabel("Return on Equity (%)")
            ax.set_ylabel("Net Profit Margin (%)")

            ax.grid(alpha=0.25)

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        #PAGE 3 - METRIC COMPARISION

        available_metrics = []

        for column, label in METRICS.items():

            if column not in df.columns:
                continue

            values = pd.to_numeric(
                df[column],
                errors="coerce"
            ).dropna()

            if not values.empty:
                available_metrics.append(
                    (label, values.median())
                )

        if available_metrics:

            labels = [
                item[0]
                for item in available_metrics
            ]

            values = [
                item[1]
                for item in available_metrics
            ]

            fig, ax = plt.subplots(figsize=(11, 7))

            ax.barh(
                labels,
                values
            )

            ax.set_title(
                f"{sector} - Median Financial Metrics",
                fontsize = 16,
                fontweight = "bold"
            )

            ax.set_xlabel("Median Value")

            ax.grid(
                axis="x",
                alpha=0.25
            )

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        #Page 4 - COMPANY DATA TABLE

        table_columns = [
            "company_name",
            "return_on_equity_pct",
            "net_profit_margin_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover"
        ]

        table_df = df[
            [
                column
                for column in table_columns
                if column in df.columns
            ]
        ].copy()

        rename_map = {
            "company_name": "Company",
            "return_on_equity_pct": "ROE %",
            "net_profit_margin_pct": "NPM %",
            "debt_to_equity": "D/E",
            "interest_coverage": "ICR",
            "asset_turnover": "Asset Turnover"
        }

        table_df = table_df.rename(
            columns=rename_map
        )

        for column in table_df.columns:

            if column != "Company":

                table_df[column] = pd.to_numeric(
                    table_df[column],
                    errors="coerce"
                ).round(2)

        fig, ax = plt.subplots(
            figsize=(11.69, 8.27)
        )

        ax.axis("off")

        ax.set_title(
            f"{sector} - Company-Level Metrics",
            fontsize = 16,
            fontweight="bold",
            pad=20
        )

        table = ax.table(
            cellText=table_df.values,
            colLabels=table_df.columns,
            loc="center",
            cellLoc="center"
        )

        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.4)

        pdf.savefig(
            fig,
            bbox_inches="tight"
        )

        plt.close(fig)

    print(f"Created: {filename}")

    return True

def generate_all_sector_reports():

    conn = sqlite3.connect(DATABASE)

    sectors = pd.read_sql_query(
        """
        SELECT DISTINCT broad_sector
        FROM sectors
        ORDER BY broad_sector
        """,
        conn
    )

    conn.close()

    generated = 0
    skipped = 0

    print("=" * 60)
    print("DAY 34 - SECTOR REPORT GENERATION")
    print("=" * 60)

    for sector in sectors["broad_sector"]:

        try:

            success = create_sector_report(
                sector
            )

            if success:
                generated += 1
            else:
                skipped += 1

        except (ValueError, KeyError, TypeError) as e:

            skipped += 1
            print(f"FAILED: {sector} -> {e}")
            
            print()
    print("=" * 60)
    print("SECTOR REPORT GENERATION COMPLETE")
    print("=" * 60)

    print(
        f"Total sectors : {len(sectors)}"
    )

    print(
        f"Generated     : {generated}"
    )

    print(
        f"Skipped       : {skipped}"
    )

    print()
    print("Reports saved to:")
    print(OUTPUT_DIR)

if __name__ == "__main__":
    generate_all_sector_reports() 