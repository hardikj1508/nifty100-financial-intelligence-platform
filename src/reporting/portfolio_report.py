import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


DATABASE = "data/database/nifty100.db"
OUTPUT_DIR = "reports/portfolio"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "portfolio_summary.pdf")


# Day 35: Top 6 KPIs
KPIS = {
    "return_on_equity_pct": ("ROE (%)", "higher"),
    "net_profit_margin_pct": ("Net Profit Margin (%)", "higher"),
    "operating_profit_margin_pct": ("Operating Profit Margin (%)", "higher"),
    "debt_to_equity": ("Debt / Equity", "lower"),
    "interest_coverage": ("Interest Coverage", "higher"),
    "asset_turnover": ("Asset Turnover", "higher"),
}


def get_portfolio_data():
    conn = sqlite3.connect(DATABASE)

    query = """
    SELECT
        c.id AS company_id,
        c.company_name,
        s.broad_sector,
        f.year,
        f.return_on_equity_pct,
        f.net_profit_margin_pct,
        f.operating_profit_margin_pct,
        f.debt_to_equity,
        f.interest_coverage,
        f.asset_turnover
    FROM companies c
    LEFT JOIN sectors s
        ON c.id = s.company_id
    LEFT JOIN financial_ratios f
        ON c.id = f.company_id
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def get_march_records(df):
    """Keep annual March records only."""

    df = df[df["year"].astype(str).str.startswith("Mar ")].copy()

    def year_number(value):
        try:
            return int(str(value).split()[-1])
        except (ValueError, IndexError):
            return None

    df["year_number"] = df["year"].apply(year_number)
    df = df.dropna(subset=["year_number"])

    return df.sort_values(
        ["company_id", "year_number"]
    )


def trend_symbol(current, previous, direction):
    """
    Determine trend.

    Right arrow = change within ±2%.
    Up/down depends on whether higher or lower is better.
    """

    if pd.isna(current) or pd.isna(previous):
        return "—"

    if previous == 0:
        if current == 0:
            return "→"
        return "↑" if direction == "higher" else "↓"

    change_pct = ((current - previous) / abs(previous)) * 100

    if abs(change_pct) <= 2:
        return "→"

    if direction == "higher":
        return "↑" if change_pct > 0 else "↓"

    return "↓" if change_pct > 0 else "↑"


def format_value(value):
    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}"


def prepare_company_data(df):
    companies = []

    for ticker, group in df.groupby("company_id"):
        group = group.sort_values("year_number")

        latest = group.iloc[-1]

        if len(group) >= 2:
            previous = group.iloc[-2]
        else:
            previous = None

        companies.append({
            "ticker": ticker,
            "company_name": latest["company_name"],
            "sector": latest["broad_sector"] or "Unknown",
            "latest_year": latest["year"],
            "previous_year": (
                previous["year"] if previous is not None else None
            ),
            "latest": latest,
            "previous": previous,
        })

    return sorted(
        companies,
        key=lambda x: str(x["ticker"]).upper()
    )


def create_company_page(pdf, company):
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ticker = company["ticker"]
    company_name = company["company_name"]
    sector = company["sector"]
    latest_year = company["latest_year"]
    previous_year = company["previous_year"]

    # Title — wrap long company names cleanly
    import textwrap

    company_title = textwrap.fill(
        str(company_name),
        width=42
    )

    title_lines = company_title.count("\n") + 1

    ax.text(
        0.06,
        0.92,
        company_title,
        fontsize=20,
        fontweight="bold",
        va="top",
        linespacing=1.15,
    )

    # Move subtitle down depending on title length
    subtitle_y = 0.92 - (0.045 * title_lines) - 0.015

    ax.text(
        0.06,
        subtitle_y,
        f"{ticker}   |   {sector}",
        fontsize=12,
        va="top",
    )

    report_y = subtitle_y - 0.05

    ax.text(
        0.06,
        report_y,
        f"Portfolio Financial Summary — {latest_year}",
        fontsize=11,
        va="top",
    )

    # Table
    columns = ["KPI", "Latest", "Trend"]

    table_data = []

    latest = company["latest"]
    previous = company["previous"]

    for column, (label, direction) in KPIS.items():

        current_value = latest[column]

        previous_value = (
            previous[column]
            if previous is not None
            else None
        )

        trend = trend_symbol(
            current_value,
            previous_value,
            direction,
        )

        table_data.append([
            label,
            format_value(current_value),
            trend,
        ])

    table = ax.table(
        cellText=table_data,
        colLabels=columns,
        colWidths=[0.50, 0.20, 0.15],
        cellLoc="left",
        colLoc="left",
        bbox=[0.06, 0.37, 0.85, 0.37],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)

    # Header
    for cell in table.get_celld().values():
        cell.set_linewidth(0.5)

    for col in range(3):
        table[(0, col)].set_text_props(
            fontweight="bold"
        )

    # Trend legend
    ax.text(
        0.06,
        0.29,
        "Trend:",
        fontsize=11,
        fontweight="bold",
    )

    ax.text(
        0.14,
        0.29,
        "↑ Improved",
        fontsize=10,
    )

    ax.text(
        0.27,
        0.29,
        "↓ Declined",
        fontsize=10,
    )

    ax.text(
        0.42,
        0.29,
        "→ Flat (within ±2%)",
        fontsize=10,
    )

    ax.text(
        0.06,
        0.23,
        f"Comparison: {previous_year or 'N/A'} → {latest_year}",
        fontsize=10,
    )

    ax.text(
        0.06,
        0.16,
        "Note: For Debt / Equity, a decrease is treated as an improvement.",
        fontsize=9,
    )

    ax.text(
        0.06,
        0.08,
        "Nifty 100 Financial Intelligence Platform",
        fontsize=8,
    )

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def create_missing_data_page(pdf, company_id, company_name):
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(
        0.06,
        0.90,
        str(company_name),
        fontsize=22,
        fontweight="bold",
        va="top",
    )

    ax.text(
        0.06,
        0.84,
        str(company_id),
        fontsize=12,
    )

    ax.text(
        0.06,
        0.65,
        "Annual financial data unavailable",
        fontsize=18,
        fontweight="bold",
    )

    ax.text(
        0.06,
        0.57,
        "No March financial-ratio record was found for this company.",
        fontsize=11,
    )

    ax.text(
        0.06,
        0.08,
        "Nifty 100 Financial Intelligence Platform",
        fontsize=8,
    )

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw_df = get_portfolio_data()

    march_df = get_march_records(raw_df)

    companies = prepare_company_data(march_df)

    # Companies with no March data
    all_companies = (
        raw_df[
            ["company_id", "company_name", "broad_sector"]
        ]
        .drop_duplicates("company_id")
        .sort_values("company_id")
    )

    companies_with_march = set(
        march_df["company_id"].unique()
    )

    missing = all_companies[
        ~all_companies["company_id"].isin(companies_with_march)
    ]

    with PdfPages(OUTPUT_FILE) as pdf:

        for company in companies:
            create_company_page(pdf, company)

        for _, row in missing.iterrows():
            create_missing_data_page(
                pdf,
                row["company_id"],
                row["company_name"],
            )

    print("=" * 60)
    print("DAY 35 PORTFOLIO REPORT GENERATED")
    print("=" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print(f"Companies with March data: {len(companies)}")
    print(f"Companies without March data: {len(missing)}")
    print(f"Total pages: {len(companies) + len(missing)}")
    print("=" * 60)


if __name__ == "__main__":
    main()