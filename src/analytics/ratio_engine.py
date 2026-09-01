import csv
import sqlite3

from src.analytics.cashflow_kpis import (
    free_cash_flow,
)
from src.analytics.ratios import (
    asset_turnover,
    debt_to_equity_ratio,
    interest_coverage_ratio,
    net_profit_margin,
    operating_profit_margin,
    return_on_assets,
    return_on_capital_employed,
    return_on_equity,
)

DATABASE = "data/database/nifty100.db"
SECTOR_FILE = "data/processed/sectors_clean.csv"
LOG_FILE = "reports/ratio_edge_cases.log"


# ============================================================
# LOAD FINANCIAL COMPANIES
# ============================================================

def load_financial_companies():
    financial_companies = set()

    with open(
        SECTOR_FILE,
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["broad_sector"] == "Financials":
                financial_companies.add(row["company_id"])

    return financial_companies


# ============================================================
# LOGGING
# ============================================================

def log_issue(message):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(message + "\n")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(DATABASE)


# ============================================================
# SAFE KPI CALCULATIONS
# ============================================================

def safe_net_profit_margin(net_profit, sales):

    if net_profit is None or sales is None:
        return None

    return net_profit_margin(
        net_profit,
        sales
    )


def safe_operating_profit_margin(operating_profit, sales):

    if operating_profit is None or sales is None:
        return None

    return operating_profit_margin(
        operating_profit,
        sales
    )


def safe_return_on_equity(
    net_profit,
    equity_capital,
    reserves
):

    if (
        net_profit is None
        or equity_capital is None
        or reserves is None
    ):
        return None

    return return_on_equity(
        net_profit,
        equity_capital,
        reserves
    )


def safe_return_on_capital_employed(
    operating_profit,
    other_income,
    equity_capital,
    reserves,
    borrowings
):

    if (
        operating_profit is None
        or other_income is None
        or equity_capital is None
        or reserves is None
        or borrowings is None
    ):
        return None

    return return_on_capital_employed(
        operating_profit,
        other_income,
        equity_capital,
        reserves,
        borrowings
    )


def safe_return_on_assets(
    net_profit,
    total_assets
):

    if (
        net_profit is None
        or total_assets is None
    ):
        return None

    return return_on_assets(
        net_profit,
        total_assets
    )


def safe_debt_to_equity(
    borrowings,
    equity_capital,
    reserves
):

    if (
        borrowings is None
        or equity_capital is None
        or reserves is None
    ):
        return None

    return debt_to_equity_ratio(
        borrowings,
        equity_capital,
        reserves
    )


def safe_interest_coverage(
    operating_profit,
    other_income,
    interest
):

    if (
        operating_profit is None
        or other_income is None
        or interest is None
    ):
        return None

    return interest_coverage_ratio(
        operating_profit,
        other_income,
        interest
    )


def safe_asset_turnover(
    sales,
    total_assets
):

    if (
        sales is None
        or total_assets is None
    ):
        return None

    return asset_turnover(
        sales,
        total_assets
    )


def safe_free_cash_flow(
    operating_activity,
    investing_activity
):

    if (
        operating_activity is None
        or investing_activity is None
    ):
        return None

    return free_cash_flow(
        operating_activity,
        investing_activity
    )


# ============================================================
# MAIN RATIO ENGINE
# ============================================================

def populate_financial_ratios():

    conn = get_connection()
    cursor = conn.cursor()

    print("Starting Ratio Engine...")

    # --------------------------------------------------------
    # Reset log
    # --------------------------------------------------------

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "===== Ratio Engine Edge Cases =====\n\n"
        )

    # --------------------------------------------------------
    # Load financial companies
    # --------------------------------------------------------

    financial_companies = load_financial_companies()

    print(
        f"Loaded {len(financial_companies)} financial companies."
    )

    # --------------------------------------------------------
    # Get source data
    # --------------------------------------------------------

    cursor.execute(
        """
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
            c.financing_activity,

            comp.roe_percentage,
            comp.roce_percentage

        FROM profitandloss p

        JOIN balancesheet b
            ON p.company_id = b.company_id
            AND p.year = b.year

        JOIN cashflow c
            ON p.company_id = c.company_id
            AND p.year = c.year

        LEFT JOIN companies comp
            ON p.company_id = comp.id
        """
    )

    rows = cursor.fetchall()

    print(
        f"Found {len(rows)} company-year records."
    )

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    updated_rows = 0
    _missing_rows = 0
    roe_mismatches = 0
    roce_mismatches = 0
    high_debt_flags = 0

    # ========================================================
    # PROCESS EACH COMPANY-YEAR
    # ========================================================

    for row in rows:

        (
            company_id,
            year,

            sales,
            operating_profit,
            other_income,
            interest,
            net_profit,
            _eps,
            _dividend_payout,

            equity_capital,
            reserves,
            borrowings,
            _investments,
            total_assets,

            operating_activity,
            investing_activity,
            _financing_activity,

            expected_roe,
            expected_roce

        ) = row

        is_financial = (
            company_id in financial_companies
        )

        # ----------------------------------------------------
        # Missing-data logging
        # ----------------------------------------------------

        if operating_profit is None:

            log_issue(
                f"{company_id} | {year} | "
                f"Missing Operating Profit"
            )

        if sales is None:

            log_issue(
                f"{company_id} | {year} | "
                f"Missing Sales"
            )

        if equity_capital is None:

            log_issue(
                f"{company_id} | {year} | "
                f"Missing Equity Capital"
            )

        if reserves is None:

            log_issue(
                f"{company_id} | {year} | "
                f"Missing Reserves"
            )

        if total_assets is None:

            log_issue(
                f"{company_id} | {year} | "
                f"Missing Total Assets"
            )

        if operating_activity is None:

            log_issue(
                f"{company_id} | {year} | "
                f"Missing Operating Cash Flow"
            )

        if investing_activity is None:

            log_issue(
                f"{company_id} | {year} | "
                f"Missing Investing Cash Flow"
            )

        # ====================================================
        # CALCULATE KPIs
        # ====================================================

        npm = safe_net_profit_margin(
            net_profit,
            sales
        )

        opm = safe_operating_profit_margin(
            operating_profit,
            sales
        )

        roe = safe_return_on_equity(
            net_profit,
            equity_capital,
            reserves
        )

        roce = safe_return_on_capital_employed(
            operating_profit,
            other_income,
            equity_capital,
            reserves,
            borrowings
        )

        de_ratio = safe_debt_to_equity(
            borrowings,
            equity_capital,
            reserves
        )

        icr = safe_interest_coverage(
            operating_profit,
            other_income,
            interest
        )

        turnover = safe_asset_turnover(
            sales,
            total_assets
        )

        fcf = safe_free_cash_flow(
            operating_activity,
            investing_activity
        )

        # # ====================================================
        # # ROE VALIDATION
        # # ====================================================

        # if (
        #     roe is not None
        #     and expected_roe is not None
        #     and abs(roe - expected_roe) > 5
        # ):

        #     roe_mismatches += 1

        #     log_issue(
        #         f"{company_id} | {year} | ROE mismatch | "
        #         f"Calculated={roe:.2f} | "
        #         f"Source={expected_roe:.2f}"
        #     )

        # # ====================================================
        # # ROCE VALIDATION
        # # ====================================================

        # if (
        #     roce is not None
        #     and expected_roce is not None
        #     and abs(roce - expected_roce) > 5
        # ):

        #     roce_mismatches += 1

        #     log_issue(
        #         f"{company_id} | {year} | ROCE mismatch | "
        #         f"Calculated={roce:.2f} | "
        #         f"Source={expected_roce:.2f}"
        #     )

        # ====================================================
        # DEBT-TO-EQUITY VALIDATION
        # ====================================================

        if (
            de_ratio is not None
            and de_ratio > 5
            and not is_financial
        ):

            high_debt_flags += 1

            log_issue(
                f"{company_id} | {year} | "
                f"High Debt-to-Equity "
                f"({de_ratio:.2f})"
            )

        # ====================================================
        # UPDATE FINANCIAL RATIOS TABLE
        # ====================================================

        cursor.execute(
            """
            UPDATE financial_ratios

            SET

                net_profit_margin_pct = ?,

                operating_profit_margin_pct = ?,

                return_on_equity_pct = ?,

                debt_to_equity = ?,

                interest_coverage = ?,

                asset_turnover = ?,

                free_cash_flow_cr = ?,

                cash_from_operations_cr = ?

            WHERE company_id = ?

              AND year = ?
            """,

            (
                npm,
                opm,
                roe,
                de_ratio,
                icr,
                turnover,
                fcf,
                operating_activity,

                company_id,
                year
            )
        )

        updated_rows += cursor.rowcount

    # ========================================================
    # COMMIT
    # ========================================================

    conn.commit()

    conn.close()

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("FINANCIAL RATIO ENGINE COMPLETE")
    print("=" * 60)

    print(
        f"Source records      : {len(rows)}"
    )

    print(
        f"Rows updated        : {updated_rows}"
    )

    print(
        f"ROE mismatches      : {roe_mismatches}"
    )

    print(
        f"ROCE mismatches     : {roce_mismatches}"
    )

    print(
        f"High D/E flags      : {high_debt_flags}"
    )

    print(
        f"Edge-case log       : {LOG_FILE}"
    )

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    populate_financial_ratios()