"""
Nifty100 Financial Intelligence Platform
Sprint 6 - Day 37
Cluster Profiling, Correlation, Outliers & Portfolio Statistics
"""

from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = PROJECT_ROOT / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


FINANCIAL_FILE = DATA_DIR / "financial_ratios_clean.csv"
PANDL_FILE = DATA_DIR / "profitandloss_clean.csv"
CASHFLOW_FILE = DATA_DIR / "cashflow_clean.csv"
SECTOR_FILE = DATA_DIR / "sectors_clean.csv"

CORRELATION_FILE = REPORTS_DIR / "correlation_heatmap.png"
OUTLIER_FILE = OUTPUT_DIR / "outlier_report.csv"
PORTFOLIO_FILE = OUTPUT_DIR / "portfolio_stats.csv"


# ============================================================
# KPI CONFIGURATION
# ============================================================

KPI_COLUMNS = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "cash_from_operations_cr",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
]


# ============================================================
# YEAR PARSER
# ============================================================

def parse_year(value):
    """Convert labels such as 'Mar 2024' into integer year."""

    value = str(value)

    match = pd.Series([value]).str.extract(
        r"(\d{4})"
    )[0].iloc[0]

    if pd.isna(match):
        return None

    return int(match)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    financial = pd.read_csv(FINANCIAL_FILE)
    pandl = pd.read_csv(PANDL_FILE)
    cashflow = pd.read_csv(CASHFLOW_FILE)
    sectors = pd.read_csv(SECTOR_FILE)

    financial["parsed_year"] = financial["year"].apply(parse_year)
    pandl["parsed_year"] = pandl["year"].apply(parse_year)
    cashflow["parsed_year"] = cashflow["year"].apply(parse_year)

    return financial, pandl, cashflow, sectors


# ============================================================
# POSITIVE CAGR
# ============================================================

def calculate_positive_cagr(beginning, ending, years):

    if pd.isna(beginning) or pd.isna(ending):
        return np.nan

    if years <= 0:
        return np.nan

    if beginning <= 0 or ending <= 0:
        return np.nan

    return (
        ((ending / beginning) ** (1 / years) - 1)
        * 100
    )


# ============================================================
# COMPANY CAGR
# ============================================================

def calculate_company_cagr(df, value_column):

    results = []

    for company_id, group in df.groupby("company_id"):

        group = (
            group
            .dropna(
                subset=[
                    "parsed_year",
                    value_column,
                ]
            )
            .sort_values("parsed_year")
            .drop_duplicates("parsed_year")
        )

        if group.empty:

            results.append({
                "company_id": company_id,
                "cagr": np.nan,
            })

            continue

        latest = group.iloc[-1]

        target_year = latest["parsed_year"] - 5

        candidates = group[
            group["parsed_year"] <= target_year
        ]

        if candidates.empty:

            results.append({
                "company_id": company_id,
                "cagr": np.nan,
            })

            continue

        beginning = candidates.iloc[-1]

        years = (
            latest["parsed_year"]
            - beginning["parsed_year"]
        )

        cagr = calculate_positive_cagr(
            beginning[value_column],
            latest[value_column],
            years,
        )

        results.append({
            "company_id": company_id,
            "cagr": cagr,
        })

    return pd.DataFrame(results)


# ============================================================
# BUILD LATEST KPI DATASET
# ============================================================

def build_latest_dataset(
    financial,
    pandl,
    cashflow,
    sectors,
):
    """
    Build one latest-year KPI observation per company.

    Financial ratio KPIs already calculated by the Ratio Engine
    are taken directly from financial_ratios_clean.csv.

    CAGR metrics are calculated separately from historical
    P&L and cash-flow data.
    """

    # --------------------------------------------------------
    # Latest financial-ratio observation
    # --------------------------------------------------------

    latest_financial = (
        financial
        .sort_values("parsed_year")
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    # --------------------------------------------------------
    # Revenue CAGR
    # --------------------------------------------------------

    revenue_cagr = calculate_company_cagr(
        pandl,
        "sales",
    )

    revenue_cagr = revenue_cagr.rename(
        columns={
            "cagr": "revenue_cagr_5yr"
        }
    )

    # --------------------------------------------------------
    # Build Free Cash Flow history
    #
    # FCF = Operating Activity + Investing Activity
    # --------------------------------------------------------

    cashflow = cashflow.copy()

    cashflow["free_cash_flow"] = (
        pd.to_numeric(
            cashflow["operating_activity"],
            errors="coerce",
        )
        +
        pd.to_numeric(
            cashflow["investing_activity"],
            errors="coerce",
        )
    )

    # --------------------------------------------------------
    # FCF CAGR
    # --------------------------------------------------------

    fcf_cagr = calculate_company_cagr(
        cashflow,
        "free_cash_flow",
    )

    fcf_cagr = fcf_cagr.rename(
        columns={
            "cagr": "fcf_cagr_5yr"
        }
    )

    # --------------------------------------------------------
    # Sector information
    # --------------------------------------------------------

    sector_data = sectors[
        [
            "company_id",
            "broad_sector",
            "sub_sector",
        ]
    ].drop_duplicates("company_id")

    # --------------------------------------------------------
    # Merge
    #
    # IMPORTANT:
    # free_cash_flow_cr and cash_from_operations_cr
    # already exist in financial_ratios_clean.csv.
    #
    # Therefore we DO NOT merge another copy from cashflow.
    # --------------------------------------------------------

    latest = (
        latest_financial
        .merge(
            revenue_cagr,
            on="company_id",
            how="left",
        )
        .merge(
            fcf_cagr,
            on="company_id",
            how="left",
        )
        .merge(
            sector_data,
            on="company_id",
            how="left",
        )
    )

    return latest


# ============================================================
# CORRELATION HEATMAP
# ============================================================

def create_correlation_heatmap(df):

    correlation = (
        df[KPI_COLUMNS]
        .corr(method="pearson")
    )

    plt.figure(
        figsize=(14, 11)
    )

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
    )

    plt.title(
        "Nifty 100 Financial KPI Correlation Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        CORRELATION_FILE,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Correlation heatmap saved -> "
        f"{CORRELATION_FILE}"
    )

    return correlation


# ============================================================
# SECTOR-WISE OUTLIER DETECTION
# ============================================================

def detect_sector_outliers(df):

    records = []

    for sector, group in df.groupby(
        "broad_sector"
    ):

        group = group.copy()

        for metric in KPI_COLUMNS:

            values = pd.to_numeric(
                group[metric],
                errors="coerce",
            )

            mean = values.mean()
            std = values.std()

            # Avoid division by zero
            if pd.isna(std) or std == 0:
                continue

            z_scores = (
                (values - mean)
                / std
            )

            for index, z_score in z_scores.items():

                if pd.isna(z_score):
                    continue

                if abs(z_score) > 3:

                    records.append({

                        "company_id":
                            group.loc[
                                index,
                                "company_id"
                            ],

                        "broad_sector":
                            sector,

                        "metric":
                            metric,

                        "value":
                            group.loc[
                                index,
                                metric
                            ],

                        "sector_mean":
                            mean,

                        "sector_std":
                            std,

                        "z_score":
                            z_score,

                        "absolute_z_score":
                            abs(z_score),

                    })

    outliers = pd.DataFrame(records)

    if not outliers.empty:

        outliers = outliers.sort_values(
            "absolute_z_score",
            ascending=False,
        )

    outliers.to_csv(
        OUTLIER_FILE,
        index=False,
    )

    print(
        f"Outlier report saved -> "
        f"{OUTLIER_FILE}"
    )

    print(
        f"Total outlier observations: "
        f"{len(outliers)}"
    )

    return outliers


# ============================================================
# PORTFOLIO STATISTICS
# ============================================================

def create_portfolio_statistics(df):

    statistics = []

    for metric in KPI_COLUMNS:

        values = pd.to_numeric(
            df[metric],
            errors="coerce",
        ).dropna()

        statistics.append({

            "kpi": metric,

            "P10":
                values.quantile(0.10),

            "P25":
                values.quantile(0.25),

            "P50":
                values.quantile(0.50),

            "P75":
                values.quantile(0.75),

            "P90":
                values.quantile(0.90),

            "Mean":
                values.mean(),

            "Std":
                values.std(),

            "Count":
                values.count(),

        })

    portfolio_stats = pd.DataFrame(
        statistics
    )

    portfolio_stats.to_csv(
        PORTFOLIO_FILE,
        index=False,
    )

    print(
        f"Portfolio statistics saved -> "
        f"{PORTFOLIO_FILE}"
    )

    return portfolio_stats


# ============================================================
# MAIN
# ============================================================

def run_day37():

    print("=" * 70)
    print("DAY 37 - CLUSTER PROFILING & STATISTICS")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    financial, pandl, cashflow, sectors = (
        load_data()
    )

    print(
        f"Financial ratio rows : "
        f"{len(financial)}"
    )

    # --------------------------------------------------------
    # Build latest dataset
    # --------------------------------------------------------

    df = build_latest_dataset(
        financial,
        pandl,
        cashflow,
        sectors,
    )

    print(
        f"Latest company observations : "
        f"{len(df)}"
    )

    print(
        f"Unique companies : "
        f"{df['company_id'].nunique()}"
    )

    # --------------------------------------------------------
    # Check KPIs
    # --------------------------------------------------------

    print("\nKPI columns:")

    for kpi in KPI_COLUMNS:

        print(
            f"{kpi:<35} "
            f"{df[kpi].notna().sum()} values"
        )

    # --------------------------------------------------------
    # Correlation
    # --------------------------------------------------------

    print(
        "\nGenerating correlation heatmap..."
    )

    correlation = create_correlation_heatmap(
        df
    )

    print("\nCorrelation matrix:")

    print(
        correlation.round(2).to_string()
    )

    # --------------------------------------------------------
    # Outliers
    # --------------------------------------------------------

    print(
        "\nRunning sector-wise outlier detection..."
    )

    outliers = detect_sector_outliers(
        df
    )

    # --------------------------------------------------------
    # Portfolio statistics
    # --------------------------------------------------------

    print(
        "\nGenerating portfolio statistics..."
    )

    portfolio_stats = (
        create_portfolio_statistics(df)
    )

    print(
        "\nPortfolio statistics:"
    )

    print(
        portfolio_stats.round(2).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DAY 37 COMPLETE")
    print("=" * 70)

    print(
        f"\nCompanies analysed : "
        f"{df['company_id'].nunique()}"
    )

    print(
        f"Correlation heatmap : "
        f"{CORRELATION_FILE.exists()}"
    )

    print(
        f"Outlier report : "
        f"{OUTLIER_FILE.exists()}"
    )

    print(
        f"Portfolio statistics : "
        f"{PORTFOLIO_FILE.exists()}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_day37()

