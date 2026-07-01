import csv
import sqlite3


from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity_ratio,
    interest_coverage_ratio,
    net_debt,
    asset_turnover,
)

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

DATABASE = "data/database/nifty100.db"
SECTOR_FILE = "data/processed/sectors_clean.csv"
LOG_FILE = "reports/ratio_edge_cases.log"

def load_financial_companies():
    financial_companies = set()

    with open(SECTOR_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["broad_sector"] == "Financials":
                financial_companies.add(row["company_id"])

    return financial_companies

def log_issue(message):
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(message + "\n")

def get_connection():
    return sqlite3.connect(DATABASE)

def populate_financial_ratios():
    conn = get_connection()
    cursor = conn.cursor()

    print("Starting Ratio Engine...")

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        file.write("===== Ratio Engine Edge Cases =====\n\n")

    financial_companies = load_financial_companies()

    print(f"Loaded {len(financial_companies)} financial companies:")

    cursor.execute("""
    SELECT DISTINCT
        p.company_id,
        p.year,

        p.sales,
        p.operating_profit,
        p.other_income,
        p.interest,
        p.net_profit,
        p.eps,
        p.dividend_payout,

        b.equity_capital,
        b.reserves,
        b.borrowings,
        b.investments,
        b.total_assets,

        c.operating_activity,
        c.investing_activity,
        c.financing_activity

    FROM profitandloss p

    JOIN balancesheet b
    ON p.company_id = b.company_id
    AND p.year = b.year

    JOIN cashflow c
    ON p.company_id = c.company_id
    AND p.year = c.year
    """)

    rows = cursor.fetchall()

    print(f"Found {len(rows)} company-year records.")

    for row in rows:
        (
            company_id,
            year,
            sales,
            operating_profit,
            other_income,
            interest,
            net_profit,
            eps,
            dividend_payout,
            equity_capital,
            reserves,
            borrowings,
            investments,
            total_assets,
            operating_activity,
            investing_activity,
            financing_activity,
        ) = row

        is_financial = company_id in financial_companies
        
        if operating_profit is None:
            log_issue(
                f"{company_id} | {year} | Missing Operating Profit"
            )

        if sales is None:
            log_issue(
                f"{company_id} | {year} | Missing Sales"
         )

        if equity_capital is None:
            log_issue(
                f"{company_id} | {year} | Missing Equity Capital"
            )

        if total_assets is None:
            log_issue(
                f"{company_id} | {year} | Missing Total Assets"
            )

        # Calculate KPIs
        
        npm = net_profit_margin(net_profit, sales)
        opm = operating_profit_margin(operating_profit, sales)
        roe = return_on_equity(net_profit, equity_capital, reserves)
        roa = return_on_assets(net_profit, total_assets)
        de_ratio = debt_to_equity_ratio(
            borrowings,
            equity_capital,
            reserves
            )
        if (
            de_ratio is not None
            and de_ratio > 5
            and not is_financial
        ):
            log_issue(
                f"{company_id} | {year} | High Debt-to-Equity ({de_ratio:.2f})"
            )

    # We'll write the logic here

    conn.commit()
    conn.close()

    print("Financial ratios updated successfully.")

if __name__ == "__main__":
    populate_financial_ratios()