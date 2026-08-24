"""
Nifty100 Financial Intelligence Platform
Sprint 6 - Day 36

KMeans financial clustering for all Nifty 100 companies.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


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

CLUSTER_FILE = OUTPUT_DIR / "cluster_labels.csv"
ELBOW_FILE = REPORTS_DIR / "elbow_plot.png"


# ============================================================
# CONFIGURATION
# ============================================================

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]

N_CLUSTERS = 5
RANDOM_STATE = 42


# ============================================================
# YEAR PARSER
# ============================================================

def parse_year(value):
    """Convert project year labels such as 'Mar 2024' to integer year."""
    value = str(value)

    match = pd.Series([value]).str.extract(r"(\d{4})")[0].iloc[0]

    if pd.isna(match):
        return None

    return int(match)


# ============================================================
# CAGR
# ============================================================

def calculate_positive_cagr(beginning, ending, years):
    """
    Calculate CAGR when beginning and ending values are positive.

    Returns NaN when CAGR cannot be meaningfully calculated.
    """

    if pd.isna(beginning) or pd.isna(ending):
        return float("nan")

    if years <= 0:
        return float("nan")

    if beginning <= 0 or ending <= 0:
        return float("nan")

    return ((ending / beginning) ** (1 / years) - 1) * 100


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """Load all datasets required for clustering."""

    financial = pd.read_csv(FINANCIAL_FILE)
    pandl = pd.read_csv(PANDL_FILE)
    cashflow = pd.read_csv(CASHFLOW_FILE)
    sectors = pd.read_csv(SECTOR_FILE)

    financial["parsed_year"] = financial["year"].apply(parse_year)
    pandl["parsed_year"] = pandl["year"].apply(parse_year)
    cashflow["parsed_year"] = cashflow["year"].apply(parse_year)

    return financial, pandl, cashflow, sectors


# ============================================================
# 5-YEAR CAGR FEATURES
# ============================================================

def calculate_company_cagr(df, value_column):
    """
    Calculate 5-year CAGR for every company.

    The latest available year is used as the ending year.
    A record approximately five years earlier is used as
    the beginning value.
    """

    results = []

    for company_id, group in df.groupby("company_id"):

        group = (
            group.dropna(subset=["parsed_year", value_column])
            .sort_values("parsed_year")
            .drop_duplicates("parsed_year")
        )

        if group.empty:
            results.append(
                {
                    "company_id": company_id,
                    "cagr": float("nan"),
                }
            )
            continue

        latest = group.iloc[-1]

        target_year = latest["parsed_year"] - 5

        candidates = group[group["parsed_year"] <= target_year]

        if candidates.empty:
            results.append(
                {
                    "company_id": company_id,
                    "cagr": float("nan"),
                }
            )
            continue

        beginning = candidates.iloc[-1]

        years = latest["parsed_year"] - beginning["parsed_year"]

        cagr = calculate_positive_cagr(
            beginning[value_column],
            latest[value_column],
            years,
        )

        results.append(
            {
                "company_id": company_id,
                "cagr": cagr,
            }
        )

    return pd.DataFrame(results)


# ============================================================
# BUILD CLUSTERING DATASET
# ============================================================

def build_feature_dataset(financial, pandl, cashflow, sectors):
    """Build one clustering feature row for every company."""

    # --------------------------------------------------------
    # Latest financial ratios
    # --------------------------------------------------------

    latest_financial = (
        financial
        .sort_values("parsed_year")
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    latest_financial = latest_financial[
        [
            "company_id",
            "return_on_equity_pct",
            "debt_to_equity",
            "operating_profit_margin_pct",
        ]
    ]

    # --------------------------------------------------------
    # Revenue CAGR
    # --------------------------------------------------------

    revenue_cagr = calculate_company_cagr(
        pandl,
        "sales",
    )

    revenue_cagr = revenue_cagr.rename(
        columns={"cagr": "revenue_cagr_5yr"}
    )

    # --------------------------------------------------------
    # FCF history
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
        columns={"cagr": "fcf_cagr_5yr"}
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
    # Merge everything
    # --------------------------------------------------------

    features = (
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

    return features


# ============================================================
# SECTOR MEDIAN IMPUTATION
# ============================================================

def impute_sector_medians(df):
    """Fill missing clustering features using sector medians."""

    df = df.copy()

    for feature in FEATURES:

        sector_medians = (
            df.groupby("broad_sector")[feature]
            .transform("median")
        )

        df[feature] = df[feature].fillna(sector_medians)

        # Fallback if an entire sector is missing the feature
        df[feature] = df[feature].fillna(
            df[feature].median()
        )

    return df


# ============================================================
# ELBOW PLOT
# ============================================================

def create_elbow_plot(X):
    """Generate elbow plot for k=2 through k=10."""

    k_values = range(2, 11)
    inertias = []

    for k in k_values:

        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=10,
        )

        model.fit(X)

        inertias.append(model.inertia_)

    plt.figure(figsize=(8, 5))

    plt.plot(
        list(k_values),
        inertias,
        marker="o",
    )

    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow Plot")

    plt.xticks(list(k_values))
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(ELBOW_FILE, dpi=200)
    plt.close()

    print(f"Elbow plot saved -> {ELBOW_FILE}")


# ============================================================
# CLUSTER NAMING
# ============================================================

def assign_cluster_names(df):
    """
    Assign descriptive names based on cluster financial profiles.

    Names are assigned according to relative cluster characteristics.
    """

    profile = (
        df.groupby("cluster_id")[FEATURES]
        .mean()
    )

    # Higher is generally better for ROE, revenue CAGR,
    # FCF CAGR and operating margin.
    # Lower debt-to-equity is generally better.

    quality_score = (
        profile["return_on_equity_pct"].rank()
        + profile["revenue_cagr_5yr"].rank()
        + profile["fcf_cagr_5yr"].rank()
        + profile["operating_profit_margin_pct"].rank()
        - profile["debt_to_equity"].rank()
    )

    ranked = quality_score.sort_values(ascending=False)

    names = [
        "High-Quality Compounders",
        "Emerging Growth",
        "Defensive Dividend Payers",
        "Value Cyclicals",
        "Distressed or Turnaround",
    ]

    cluster_names = {}

    for cluster_id, name in zip(ranked.index, names):
        cluster_names[cluster_id] = name

    return cluster_names, profile


# ============================================================
# MAIN CLUSTERING
# ============================================================

def run_clustering():
    """Run complete Day 36 clustering pipeline."""

    print("=" * 70)
    print("DAY 36 - KMEANS FINANCIAL CLUSTERING")
    print("=" * 70)

    financial, pandl, cashflow, sectors = load_data()

    print(f"Financial ratio rows : {len(financial)}")
    print(f"Companies in sectors : {sectors['company_id'].nunique()}")

    # --------------------------------------------------------
    # Build features
    # --------------------------------------------------------

    df = build_feature_dataset(
        financial,
        pandl,
        cashflow,
        sectors,
    )

    print(f"Companies before clustering : {df['company_id'].nunique()}")

    # --------------------------------------------------------
    # Imputation
    # --------------------------------------------------------

    df = impute_sector_medians(df)

    # --------------------------------------------------------
    # Final numeric check
    # --------------------------------------------------------

    missing = df[FEATURES].isna().sum()

    print("\nMissing values after sector median imputation:")
    print(missing)

    # --------------------------------------------------------
    # StandardScaler
    # --------------------------------------------------------

    scaler = StandardScaler()

    X = scaler.fit_transform(
        df[FEATURES]
    )

    # --------------------------------------------------------
    # Elbow plot
    # --------------------------------------------------------

    create_elbow_plot(X)

    # --------------------------------------------------------
    # KMeans
    # --------------------------------------------------------

    model = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=RANDOM_STATE,
        n_init=10,
    )

    cluster_ids = model.fit_predict(X)

    df["cluster_id"] = cluster_ids

    # --------------------------------------------------------
    # Distance from centroid
    # --------------------------------------------------------

    distances = model.transform(X)

    df["distance_from_centroid"] = [
        distances[i, cluster_ids[i]]
        for i in range(len(df))
    ]

    # --------------------------------------------------------
    # Cluster names
    # --------------------------------------------------------

    cluster_names, profile = assign_cluster_names(
        df
    )

    df["cluster_name"] = (
        df["cluster_id"]
        .map(cluster_names)
    )

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    output = df[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid",
        ]
    ].sort_values(
        ["cluster_id", "company_id"]
    )

    output.to_csv(
        CLUSTER_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CLUSTER SUMMARY")
    print("=" * 70)

    print(
        output.groupby(
            ["cluster_id", "cluster_name"]
        )
        .size()
        .to_string()
    )

    print("\nCluster profiles:")
    print(profile.round(2).to_string())

    print("\nTotal companies clustered:", len(output))
    print("Unique companies:", output["company_id"].nunique())

    print(f"\nCluster labels saved -> {CLUSTER_FILE}")
    print(f"Elbow plot saved -> {ELBOW_FILE}")

    print("\nDAY 36 COMPLETE")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_clustering()