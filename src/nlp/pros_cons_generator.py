import pandas as pd
from pathlib import Path

from src.nlp.rules import PRO_RULES, CON_RULES

# ==========================================================
# File Paths
# ==========================================================

FINANCIAL_FILE = "data/processed/financial_ratios_clean.csv"
ANALYSIS_FILE = "data/processed/analysis_clean.csv"
COMPANIES_FILE = "data/processed/companies_clean.csv"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "pros_cons_generated.csv"

PARSED_ANALYSIS = "output/analysis_parsed.csv"

# ==========================================================
# Load Data
# ==========================================================

def load_data():

    financial = pd.read_csv(FINANCIAL_FILE)
    analysis = pd.read_csv(ANALYSIS_FILE)
    companies = pd.read_csv(COMPANIES_FILE)
    parsed = pd.read_csv(PARSED_ANALYSIS)

    return financial, analysis, companies, parsed


# ==========================================================
# Prepare Dataset
# ==========================================================

def prepare_dataset():

    financial, analysis, companies, parsed = load_data()

    print("Financial Columns:")
    print(financial.columns.tolist())

    print("\nAnalysis Columns:")
    print(analysis.columns.tolist())

    print("\nCompanies Columns:")
    print(companies.columns.tolist())

    # -----------------------------------------
    # Convert parsed analysis to wide format
    # -----------------------------------------

    parsed = parsed.pivot_table(
        index="company_id",
        columns="metric_type",
        values="value_pct",
        aggfunc="first"
    ).reset_index()

    # -----------------------------------------
    # Merge financial ratios with parsed metrics
    # -----------------------------------------

    df = financial.merge(
        parsed,
        on="company_id",
        how="left"
    )

    return df


# ==========================================================
# Helper Function
# ==========================================================

def add_result(results, company_id, rule, rule_type):
    """
    Append a Pro or Con rule to the output.
    """

    results.append({

        "company_id": company_id,
        "type": rule_type,
        "rule_id": rule["id"],
        "text": rule["text"],
        "confidence_pct": rule["confidence"]

    })


# ==========================================================
# Main Generator
# ==========================================================

def generate():

    df = prepare_dataset()

    print("=" * 60)
    print("Pros / Cons Generator")
    print("=" * 60)

    print(f"Rows Loaded : {len(df)}")
    print(f"Companies   : {df.company_id.nunique()}")

    latest = (
        df.sort_values("year")
          .groupby("company_id")
          .tail(1)
          .copy()
    )

    print(f"Latest Records : {len(latest)}")

    results = []

    # ======================================================
    # Evaluate Rules
    # ======================================================

    for _, row in latest.iterrows():

        company = row["company_id"]

        # ---------------------------------------------
        # P1 : ROE > 20%
        # ---------------------------------------------

        if pd.notna(row["return_on_equity_pct"]):

            if row["return_on_equity_pct"] > 20:

                add_result(
                    results,
                    company,
                    PRO_RULES[0],
                    "pro"
                )
        # P2 : Positive Free Cash Flow

        if pd.notna(row["free_cash_flow_cr"]):

            if row["free_cash_flow_cr"] > 0:

                add_result(
                    results,
                    company,
                    PRO_RULES[1],
                    "pro"
                )

        # P3 : Debt Free

        if pd.notna(row["debt_to_equity"]):

            if row["debt_to_equity"] == 0:

                add_result(
                    results,
                    company,
                    PRO_RULES[2],
                    "pro"
                )

        # -------------------------------------------------
        # P4 : Revenue CAGR
        # -------------------------------------------------

        if pd.notna(row["compounded_sales_growth"]):
            if row["compounded_sales_growth"] > 15:

                add_result(
                    results,
                    company,
                    PRO_RULES[3],
                    "pro"
                )

        # -------------------------------------------------
        # P5 : Operating Profit Margin
        # -------------------------------------------------

        if pd.notna(row["operating_profit_margin_pct"]):
            if row["operating_profit_margin_pct"] > 25:

                add_result(
                    results,
                    company,
                    PRO_RULES[4],
                    "pro"
                )               

        # -------------------------------------------------
        # P6 : Profit CAGR
        # -------------------------------------------------

        if pd.notna(row["compounded_profit_growth"]):
            if row["compounded_profit_growth"] > 20:

                add_result(
                    results,
                    company,
                    PRO_RULES[5],
                    "pro"
                )

        # -------------------------------------------------
        # P7 : High Interest Coverage
        # -------------------------------------------------

        if pd.notna(row["interest_coverage"]):
            if row["interest_coverage"] > 10:

                add_result(
                    results,
                    company,
                    PRO_RULES[6],
                    "pro"
                )

        # -------------------------------------------------
        # P8 : Dividend Payout
        # -------------------------------------------------

        if pd.notna(row["dividend_payout_ratio_pct"]):
            if row["dividend_payout_ratio_pct"] > 20:

                add_result(
                    results,
                    company,
                    PRO_RULES[7],
                    "pro"
                )

        # -------------------------------------------------
        # P9 : Positive EPS
        # -------------------------------------------------

        if pd.notna(row["earnings_per_share"]):
            if row["earnings_per_share"] > 0:

                add_result(
                    results,
                    company,
                    PRO_RULES[8],
                    "pro"
                )

        # -------------------------------------------------
        # P10 : High ROE
        # -------------------------------------------------

        if pd.notna(row["return_on_equity_pct"]):
            if row["return_on_equity_pct"] > 20:

                add_result(
                    results,
                    company,
                    PRO_RULES[9],
                    "pro"
                )

        if pd.notna(row["asset_turnover"]):
            if row["asset_turnover"] > 1:
                add_result(results, company, PRO_RULES[10], "pro")

        if pd.notna(row["debt_to_equity"]):
            if row["debt_to_equity"] < 0.5:
                add_result(results, company, PRO_RULES[11], "pro")

        # -------------------------------------------------
        # C1 : High Debt
        # -------------------------------------------------

        if pd.notna(row["debt_to_equity"]):
            if row["debt_to_equity"] > 2:

                add_result(
                    results,
                    company,
                    CON_RULES[0],
                    "con"
                )

        # -------------------------------------------------
        # C2 : Negative Free Cash Flow
        # -------------------------------------------------

        if pd.notna(row["free_cash_flow_cr"]):
            if row["free_cash_flow_cr"] < 0:

                add_result(
                    results,
                    company,
                    CON_RULES[1],
                    "con"
                )

        # -------------------------------------------------
        # C3 : Low Operating Margin
        # -------------------------------------------------

        if pd.notna(row["operating_profit_margin_pct"]):
            if row["operating_profit_margin_pct"] < 10:

                add_result(
                    results,
                    company,
                    CON_RULES[2],
                    "con"
                )

        # -------------------------------------------------
        # C4 : Negative Net Profit
        # -------------------------------------------------

        if pd.notna(row["net_profit_margin_pct"]):
            if row["net_profit_margin_pct"] < 0:

                add_result(
                    results,
                    company,
                    CON_RULES[3],
                    "con"
                )
                
        # -------------------------------------------------
        # C5 : Low Revenue Growth
        # -------------------------------------------------

        if pd.notna(row["compounded_sales_growth"]):
            if row["compounded_sales_growth"] < 5:

                add_result(
                    results,
                    company,
                    CON_RULES[4],
                    "con"
                )

        # -------------------------------------------------
        # C6 : Low Interest Coverage
        # -------------------------------------------------

        if pd.notna(row["interest_coverage"]):
            if row["interest_coverage"] < 1.5:

                add_result(
                    results,
                    company,
                    CON_RULES[5],
                    "con"
                )

        # -------------------------------------------------
        # C7 : Excessive Dividend Payout
        # -------------------------------------------------

        if pd.notna(row["dividend_payout_ratio_pct"]):
            if row["dividend_payout_ratio_pct"] > 100:

                add_result(
                    results,
                    company,
                    CON_RULES[6],
                    "con"
                )

        # -------------------------------------------------
        # C8 : Very High Debt
        # -------------------------------------------------

        if pd.notna(row["debt_to_equity"]):
            if row["debt_to_equity"] > 3:

                add_result(
                    results,
                    company,
                    CON_RULES[7],
                    "con"
                )

        # -------------------------------------------------
        # C9 : Low ROE
        # -------------------------------------------------

        if pd.notna(row["return_on_equity_pct"]):
            if row["return_on_equity_pct"] < 10:

                add_result(
                    results,
                    company,
                    CON_RULES[8],
                    "con"
                )

        # -------------------------------------------------
        # C10 : Low Asset Turnover
        # -------------------------------------------------

        if pd.notna(row["asset_turnover"]):
            if row["asset_turnover"] < 0.5:

                add_result(
                    results,
                    company,
                    CON_RULES[9],
                    "con"
                )

        # -------------------------------------------------
        # C11 : Extremely High Debt
        # -------------------------------------------------

        if pd.notna(row["debt_to_equity"]):
            if row["debt_to_equity"] > 5:

                add_result(
                    results,
                    company,
                    CON_RULES[10],
                    "con"
                )

        # -------------------------------------------------
        # C12 : Weak Profit Growth
        # -------------------------------------------------

        if pd.notna(row["compounded_profit_growth"]):
            if row["compounded_profit_growth"] < 5:

                add_result(
                    results,
                    company,
                    CON_RULES[11],
                    "con"
                )

        # C13 : Low Dividend Payout

        if pd.notna(row["dividend_payout_ratio_pct"]):
            if row["dividend_payout_ratio_pct"] < 20:

                add_result(
                    results,
                    company,
                    CON_RULES[12],
                    "con"
                )

        # C14 : Low Asset Utilization

        if pd.notna(row["asset_turnover"]):
            if row["asset_turnover"] < 1:

                add_result(
                    results,
                    company,
                    CON_RULES[13],
                    "con"
                )

        # C15 : Low Book Value

        if pd.notna(row["book_value_per_share"]):
            if row["book_value_per_share"] < 100:

                add_result(
                    results,
                    company,
                    CON_RULES[14],
                    "con"
                )

    # ======================================================
    # Save Results
    # ======================================================

    # -----------------------------------------
    # Validation
    # -----------------------------------------

    results_df = pd.DataFrame(results)

    pro_count = (
        results_df[results_df["type"] == "pro"]
        .groupby("company_id")
        .size()
    )

    con_count = (
        results_df[results_df["type"] == "con"]
        .groupby("company_id")
        .size()
    )

    missing_pro = set(latest["company_id"]) - set(pro_count.index)

    missing_con = set(latest["company_id"]) - set(con_count.index)

    print("\nValidation")
    print("=" * 60)
    print(f"Companies Missing Pro : {len(missing_pro)}")
    print(f"Companies Missing Con : {len(missing_con)}")

    if missing_pro:
        print("Missing Pro:", sorted(missing_pro))

    if missing_con:
        print("Missing Con:", sorted(missing_con))

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print(f"Rules Generated : {len(results_df)}")
    print(f"Saved -> {OUTPUT_FILE}")


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    generate()