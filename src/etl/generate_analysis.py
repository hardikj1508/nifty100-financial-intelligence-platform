import pandas as pd
from pathlib import Path


# ==========================================================
# File Paths
# ==========================================================

PANDL_FILE = "data/raw/profitandloss.xlsx"
RATIOS_FILE = "data/raw/financial_ratios.xlsx"
STOCK_FILE = "data/raw/stock_prices.xlsx"

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "analysis_derived.csv"


# ==========================================================
# CAGR Helper
# ==========================================================

def calculate_cagr(start_value, end_value, years):
    """
    Calculate CAGR as a percentage.

    CAGR = (End / Start)^(1 / years) - 1
    """

    if pd.isna(start_value) or pd.isna(end_value):
        return None

    if start_value <= 0 or end_value <= 0 or years <= 0:
        return None

    return ((end_value / start_value) ** (1 / years) - 1) * 100


# ==========================================================
# Load P&L
# ==========================================================

def load_pandl():
    df = pd.read_excel(
        PANDL_FILE,
        header=1
    )

    df["year"] = df["year"].astype(str)

    # Keep annual March records only.
    df = df[
        df["year"].str.contains("Mar", case=False, na=False)
    ].copy()

    df["year_num"] = (
        df["year"]
        .str.extract(r"(\d{4})")[0]
        .astype(int)
    )

    return df


# ==========================================================
# Calculate Growth Metrics
# ==========================================================

def calculate_growth_metrics(pandl):
    results = []

    for company_id, group in pandl.groupby("company_id"):

        group = (
            group
            .sort_values("year_num")
            .drop_duplicates("year_num", keep="last")
        )

        if group.empty:
            continue

        latest_year = group["year_num"].max()

        latest_rows = group[group["year_num"] == latest_year]

        if latest_rows.empty:
            continue

        latest = latest_rows.iloc[-1]

        result = {
            "company_id": company_id,
            "latest_year": latest_year,
        }

        # ------------------------------------------
        # Sales CAGR
        # ------------------------------------------

        for period in [10, 5, 3]:

            start_year = latest_year - period

            start_rows = group[
                group["year_num"] == start_year
            ]

            if start_rows.empty:
                result[f"sales_cagr_{period}y"] = None
            else:
                start = start_rows.iloc[-1]

                result[f"sales_cagr_{period}y"] = calculate_cagr(
                    start["sales"],
                    latest["sales"],
                    period
                )

        # ------------------------------------------
        # Profit Before Tax CAGR
        # ------------------------------------------

        for period in [10, 5, 3]:

            start_year = latest_year - period

            start_rows = group[
                group["year_num"] == start_year
            ]

            if start_rows.empty:
                result[f"profit_cagr_{period}y"] = None
            else:
                start = start_rows.iloc[-1]

                result[f"profit_cagr_{period}y"] = calculate_cagr(
                    start["profit_before_tax"],
                    latest["profit_before_tax"],
                    period
                )

        results.append(result)

    return pd.DataFrame(results)


# ==========================================================
# Load Financial Ratios
# ==========================================================

def load_latest_ratios():

    df = pd.read_excel(
        RATIOS_FILE,
        header=0
    )

    df["year_num"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
    )

    df["year_num"] = pd.to_numeric(
        df["year_num"],
        errors="coerce"
    )

    df = df.dropna(subset=["year_num"])

    df = (
        df
        .sort_values(["company_id", "year_num"])
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    return df[
        [
            "company_id",
            "year_num",
            "return_on_equity_pct",
        ]
    ].rename(
        columns={
            "year_num": "roe_year",
            "return_on_equity_pct": "roe",
        }
    )


# ==========================================================
# Calculate Stock Price CAGR
# ==========================================================

def calculate_stock_cagr():

    df = pd.read_excel(
        STOCK_FILE,
        header=0
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["adjusted_close"] = pd.to_numeric(
        df["adjusted_close"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "company_id",
            "date",
            "adjusted_close",
        ]
    )

    results = []

    for company_id, group in df.groupby("company_id"):

        group = group.sort_values("date")

        if len(group) < 2:
            continue

        first = group.iloc[0]
        last = group.iloc[-1]

        days = (
            last["date"] - first["date"]
        ).days

        years = days / 365.25

        if years <= 0:
            continue

        cagr = calculate_cagr(
            first["adjusted_close"],
            last["adjusted_close"],
            years
        )

        results.append(
            {
                "company_id": company_id,
                "stock_cagr": cagr,
                "stock_start_date": first["date"],
                "stock_end_date": last["date"],
            }
        )

    return pd.DataFrame(results)


# ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 60)
    print("Generating Derived Analysis Dataset")
    print("=" * 60)

    # ------------------------------------------
    # P&L
    # ------------------------------------------

    print("\nLoading P&L...")

    pandl = load_pandl()

    print(f"P&L rows: {len(pandl)}")
    print(f"P&L companies: {pandl['company_id'].nunique()}")

    growth = calculate_growth_metrics(pandl)

    print(
        f"Growth companies generated: "
        f"{growth['company_id'].nunique()}"
    )

    # ------------------------------------------
    # Financial Ratios
    # ------------------------------------------

    print("\nLoading financial ratios...")

    ratios = load_latest_ratios()

    print(
        f"Companies with latest ROE: "
        f"{ratios['company_id'].nunique()}"
    )

    # ------------------------------------------
    # Stock Prices
    # ------------------------------------------

    print("\nCalculating stock CAGR...")

    stock = calculate_stock_cagr()

    print(
        f"Companies with stock CAGR: "
        f"{stock['company_id'].nunique()}"
    )

    # ------------------------------------------
    # Merge
    # ------------------------------------------

    analysis = growth.merge(
        ratios,
        on="company_id",
        how="left"
    )

    analysis = analysis.merge(
        stock,
        on="company_id",
        how="left"
    )

    # ------------------------------------------
    # Primary screener metrics
    #
    # Existing screener expects:
    # compounded_sales_growth
    # compounded_profit_growth
    # stock_price_cagr
    # roe
    #
    # We use 5-year CAGR as the primary
    # compounded growth metric.
    # ------------------------------------------

    analysis["compounded_sales_growth"] = (
        analysis["sales_cagr_5y"]
    )

    analysis["compounded_profit_growth"] = (
        analysis["profit_cagr_5y"]
    )

    analysis["stock_price_cagr"] = (
        analysis["stock_cagr"]
    )

    # ------------------------------------------
    # Round values
    # ------------------------------------------

    numeric_columns = [
        "sales_cagr_10y",
        "sales_cagr_5y",
        "sales_cagr_3y",
        "profit_cagr_10y",
        "profit_cagr_5y",
        "profit_cagr_3y",
        "stock_cagr",
        "roe",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
    ]

    for column in numeric_columns:
        if column in analysis.columns:
            analysis[column] = analysis[column].round(4)

    # ------------------------------------------
    # Save
    # ------------------------------------------

    analysis = analysis.sort_values(
        "company_id"
    ).reset_index(drop=True)

    analysis.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 60)
    print("Analysis Generation Complete")
    print("=" * 60)

    print(f"Rows: {len(analysis)}")
    print(
        f"Companies: "
        f"{analysis['company_id'].nunique()}"
    )

    print("\nColumns:")
    print(analysis.columns.tolist())

    print("\nMissing values:")
    print(
        analysis[
            [
                "compounded_sales_growth",
                "compounded_profit_growth",
                "stock_price_cagr",
                "roe",
            ]
        ]
        .isna()
        .sum()
    )

    print("\nSample:")
    print(
        analysis[
            [
                "company_id",
                "latest_year",
                "compounded_sales_growth",
                "compounded_profit_growth",
                "stock_price_cagr",
                "roe",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print(f"\nSaved -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
