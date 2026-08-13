"""
Financial Ratio Engine
Sprint 2 - Day 11

Cash Flow KPI calculations.
"""

def free_cash_flow(
    operating_activity: float,
    investing_activity: float
) -> float:
    """
    Calculate Free Cash Flow (FCF).

    Formula:
        Operating Cash Flow + Investing Cash Flow

    Note:
        Investing cash flow is usually negative.
        Negative FCF is allowed.
    """

    return operating_activity + investing_activity

from typing import Optional

def cfo_quality_score(
    cash_from_operations: float,
    net_profit: float
) -> tuple[Optional[float], str]:
    """
    Calculate CFO Quality Score.

    Formula:
        CFO / PAT

    Returns:
        (score, label)

    Labels:
        HIGH_QUALITY : score > 1.0
        MODERATE     : 0.5 <= score <= 1.0
        ACCRUAL_RISK : score < 0.5
        PAT_ZERO     : net_profit == 0
    """

    if net_profit == 0:
        return None, "PAT_ZERO"

    score = cash_from_operations / net_profit

    if score > 1:
        label = "HIGH_QUALITY"
    elif score >= 0.5:
        label = "MODERATE"
    else:
        label = "ACCRUAL_RISK"

    return score, label

from typing import Optional

def capex_intensity(
    investing_activity: float,
    sales: float
) -> tuple[Optional[float], str]:
    """
    Calculate CapEx Intensity.

    Formula:
        abs(Investing Activity) / Sales × 100

    Returns:
        (intensity, label)
    """

    if sales == 0:
        return None, "SALES_ZERO"

    intensity = (abs(investing_activity) / sales) * 100

    if intensity < 3:
        label = "ASSET_LIGHT"
    elif intensity <= 8:
        label = "MODERATE"
    else:
        label = "CAPITAL_INTENSIVE"

    return intensity, label

def fcf_conversion_rate(
    free_cash_flow: float,
    operating_profit: float
) -> Optional[float]:
    """
    Calculate FCF Conversion Rate.

    Formula:
        Free Cash Flow / Operating Profit × 100

    Returns:
        None if operating profit is zero.
    """

    if operating_profit == 0:
        return None

    return (free_cash_flow / operating_profit) * 100

def capital_allocation_pattern(
    operating_activity: float,
    investing_activity: float,
    financing_activity: float
) -> str:
    """
    Classify capital allocation pattern based on
    the signs of CFO, CFI and CFF.
    """

    cfo = operating_activity > 0
    cfi = investing_activity > 0
    cff = financing_activity > 0

    if cfo and not cfi and not cff:
        return "REINVESTOR"

    if cfo and cfi and not cff:
        return "SHAREHOLDER_RETURNS"

    if cfo and cfi and cff:
        return "CASH_ACCUMULATOR"

    if cfo and not cfi and cff:
        return "GROWTH_FUNDED_BY_DEBT"

    if not cfo and cfi and cff:
        return "DISTRESS_SIGNAL"

    if not cfo and not cfi and cff:
        return "PRE_REVENUE"

    if not cfo and cfi and not cff:
        return "LIQUIDATING_ASSETS"

    return "MIXED"

import pandas as pd
from pathlib import Path

CASHFLOW_FILE = "data/processed/cashflow_clean.csv"
FINANCIAL_FILE = "data/processed/financial_ratios_clean.csv"
COMPANIES_FILE = "data/processed/companies_clean.csv"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"
DISTRESS_FILE = OUTPUT_DIR / "distress_alerts.csv"
PATTERN_SUMMARY = OUTPUT_DIR / "capital_allocation_summary.csv"
PATTERN_CHANGES = OUTPUT_DIR / "pattern_changes.csv"

def load_data():

    cashflow = pd.read_csv(CASHFLOW_FILE)

    financial = pd.read_csv(FINANCIAL_FILE)

    companies = pd.read_csv(COMPANIES_FILE)

    return cashflow, financial, companies

def prepare_dataset():

    cashflow, financial, companies = load_data()

    cashflow["year"] = (
        cashflow["year"]
        .astype(str)
        .str.extract(r"(\d{2})")[0]
        .astype(int)
        + 2000
    )

    financial["year"] = (
        financial["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .astype(int)
    )

    financial = financial.drop_duplicates(
        subset=["company_id", "year"]
    )

    df = financial.merge(
        cashflow,
        on=["company_id", "year"],
        how="left"
    )

    df = df.merge(
        companies[
            [
                "id",
                "company_name",
                "roe_percentage",
                "roce_percentage"
            ]
        ],
        left_on="company_id",
        right_on="id",
        how="left"
    )

    df = df.drop(columns=["id_x", "id_y"], errors="ignore")

    return df

def generate():

    df = prepare_dataset()

    latest = (
        df.sort_values("year")
          .groupby("company_id")
          .tail(1)
          .copy()
    )

    print("\nUnique companies:", latest["company_id"].nunique())

    print("\nCompany IDs:")
    print(sorted(latest["company_id"].unique()))    

    results = []

    distress_rows = []

    for _, row in latest.iterrows():

        company = row["company_id"]

        # ----------------------------
        # CFO Quality
        # ----------------------------

        cfo_score, cfo_label = cfo_quality_score(
            row["cash_from_operations_cr"],
            row["net_profit_margin_pct"]
        )

        # ----------------------------
        # CapEx Intensity
        # ----------------------------

        capex_pct, capex_label = capex_intensity(
            row["capex_cr"],
            row["cash_from_operations_cr"]
        )

        # ----------------------------
        # Free Cash Flow
        # ----------------------------

        fcf = free_cash_flow(
            row["operating_activity"],
            row["investing_activity"]
        )

        fcf_conversion = fcf_conversion_rate(
            fcf,
            row["operating_profit_margin_pct"]
        )

        # ----------------------------
        # Distress
        # ----------------------------

        distress = (
            row["operating_activity"] < 0
            and
            row["financing_activity"] > 0
        )

        if distress:

            distress_rows.append({

                "company_id": company,

                "company_name": row["company_name"],

                "year": row["year"],

                "CFO": row["operating_activity"],

                "CFF": row["financing_activity"],

                "Net Cash Flow": row["net_cash_flow"]

            })

        # ----------------------------
        # Deleveraging
        # ----------------------------

        deleveraging = row["financing_activity"] < 0

        # ----------------------------
        # Capital Allocation
        # ----------------------------

        allocation = capital_allocation_pattern(

            row["operating_activity"],

            row["investing_activity"],

            row["financing_activity"]

        )

        results.append({

            "company_id": company,

            "company_name": row["company_name"],

            "year": row["year"],

            "cfo_quality_score": cfo_score,

            "cfo_quality_label": cfo_label,

            "capex_intensity_pct": capex_pct,

            "capex_label": capex_label,

            "fcf_conversion_pct": fcf_conversion,

            "distress_flag": distress,

            "deleveraging_flag": deleveraging,

            "capital_allocation_label": allocation

        })

        intelligence = pd.DataFrame(results)

        distress = pd.DataFrame(distress_rows)

        # =====================================================
        # Capital Allocation Summary
        # =====================================================

        distribution = (
            intelligence["capital_allocation_label"]
            .value_counts()
            .reset_index()
        )

        distribution.columns = [
            "capital_allocation_pattern",
            "company_count"
        ]

        distribution.to_csv(
            PATTERN_SUMMARY,
            index=False
        )

        # =====================================================
        # Pattern Changes
        # =====================================================

        changes = []

        for company, group in df.groupby("company_id"):

            group = group.sort_values("year")

            previous_pattern = None

            for _, row in group.iterrows():

                current_pattern = capital_allocation_pattern(
                    row["operating_activity"],
                    row["investing_activity"],
                    row["financing_activity"]
                )

                if (
                    previous_pattern is not None
                    and previous_pattern != current_pattern
                ):

                    changes.append({
                        "company_id": company,
                        "year": row["year"],
                        "from_pattern": previous_pattern,
                        "to_pattern": current_pattern
                    })

                previous_pattern = current_pattern

        changes_df = pd.DataFrame(changes)

        changes_df.to_csv(
            PATTERN_CHANGES,
            index=False
        )

        # =====================================================
        # Save Files
        # =====================================================

        intelligence.to_excel(
            OUTPUT_FILE,
            index=False
        )

        distress.to_csv(
            DISTRESS_FILE,
            index=False
        )

        print("=" * 60)
        print("Cash Flow Intelligence Generated")
        print("=" * 60)

        print("Companies :", len(intelligence))
        print("Distress Alerts :", len(distress))
        print("Pattern Changes :", len(changes_df))

        print(f"\nSaved -> {OUTPUT_FILE}")
        print(f"Saved -> {DISTRESS_FILE}")
        print(f"Saved -> {PATTERN_SUMMARY}")
        print(f"Saved -> {PATTERN_CHANGES}")

if __name__ == "__main__":
    generate()