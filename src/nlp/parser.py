import re
import pandas as pd
from pathlib import Path


# ==========================================================
# File Paths
# ==========================================================

INPUT_FILE = "data/processed/analysis_clean.csv"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "analysis_parsed.csv"
FAILURE_FILE = OUTPUT_DIR / "parse_failures.csv"


# ==========================================================
# Target Columns
# ==========================================================

TARGET_COLUMNS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe"
]


# ==========================================================
# Regex Pattern
# ==========================================================

PATTERN = re.compile(
    r"(?:(\d+)\s*Years?|Last\s*Year|TTM)\s*:?\s*(-?[\d.]+)%",
    flags=re.IGNORECASE
)


# ==========================================================
# Parse Single Metric
# ==========================================================

def parse_metric(text):
    """
    Extract period (years) and percentage value from text.

    Examples:
        10 Years: 21%
        5 Year: 14%
        Last Year: 18%
        TTM: 32%
    """

    if pd.isna(text):
        return None

    text = str(text).strip()

    match = PATTERN.search(text)

    if match is None:
        return None

    years = match.group(1)

    if years is None:

        if "TTM" in text.upper():
            years = 0
        else:
            years = 1

    value = float(match.group(2))

    return int(years), value


# ==========================================================
# Validation Hook
# ==========================================================

def validate_against_ratio_engine(parsed_df):
    """
    Placeholder for Ratio Engine validation.

    This will be connected once we identify the
    Ratio Engine output dataset.
    """

    print("\nRunning Ratio Engine validation...")

    # TODO
    # Load Ratio Engine output
    # Merge with parsed_df
    # Compare values
    # Flag divergence >5%

    print("Validation hook ready.")


# ==========================================================
# Main Parser
# ==========================================================

def parse_analysis():

    df = pd.read_csv(INPUT_FILE)

    parsed_rows = []
    failed_rows = []

    for _, row in df.iterrows():

        ticker = row["company_id"]

        for metric in TARGET_COLUMNS:

            result = parse_metric(row[metric])

            if result is None:

                failed_rows.append({

                    "company_id": ticker,
                    "metric_type": metric,
                    "raw_text": row[metric]

                })

            else:

                years, value = result

                parsed_rows.append({

                    "company_id": ticker,
                    "metric_type": metric,
                    "period_years": years,
                    "value_pct": value

                })

    parsed_df = pd.DataFrame(parsed_rows)
    failed_df = pd.DataFrame(failed_rows)

    parsed_df.to_csv(OUTPUT_FILE, index=False)
    failed_df.to_csv(FAILURE_FILE, index=False)

    validate_against_ratio_engine(parsed_df)

    print("=" * 60)
    print("Parsing Complete")
    print("=" * 60)
    print(f"Parsed Records : {len(parsed_df)}")
    print(f"Failed Records : {len(failed_df)}")
    print(f"\nSaved -> {OUTPUT_FILE}")
    print(f"Saved -> {FAILURE_FILE}")


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    parse_analysis()