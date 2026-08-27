"""Valuation API endpoints."""

import sqlite3

from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/valuation",
    tags=["Valuation"],
)


DATABASE = "data/database/nifty100.db"


@router.get("/{ticker}")
def get_valuation(ticker: str):
    """
    Return valuation, profitability, and financial-strength
    metrics for a company.
    """

    conn = sqlite3.connect(DATABASE)

    try:

        # ====================================================
        # COMPANY
        # ====================================================

        company_cursor = conn.execute(
            """
            SELECT
                id,
                company_name
            FROM companies
            WHERE UPPER(id) = UPPER(?)
            """,
            (ticker,),
        )

        company = company_cursor.fetchone()

        if company is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found",
            )

        company_ticker = company[0]
        company_name = company[1]

        # ====================================================
        # MARKET VALUATION
        # ====================================================

        market_cursor = conn.execute(
            """
            SELECT
                year,
                market_cap_crore,
                enterprise_value_crore,
                pb_ratio,
                pe_ratio,
                dividend_yield_pct
            FROM market_cap
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY year DESC
            LIMIT 1
            """,
            (ticker,),
        )

        market = market_cursor.fetchone()

        # ====================================================
        # FINANCIAL RATIOS
        # ====================================================

        ratio_cursor = conn.execute(
            """
            SELECT
                year,
                net_profit_margin_pct,
                operating_profit_margin_pct,
                return_on_equity_pct,
                debt_to_equity,
                interest_coverage,
                asset_turnover,
                free_cash_flow_cr,
                capex_cr,
                earnings_per_share,
                book_value_per_share,
                dividend_payout_ratio_pct,
                total_debt_cr,
                cash_from_operations_cr
            FROM financial_ratios
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY CAST(substr(year, -4) AS INTEGER) DESC
            LIMIT 1
            """,
            (ticker,),
        )

        ratios = ratio_cursor.fetchone()

        # ====================================================
        # RESPONSE
        # ====================================================

        return {
            "ticker": company_ticker,
            "company_name": company_name,

            "valuation": (
                {
                    "year": market[0],
                    "market_cap_crore": market[1],
                    "enterprise_value_crore": market[2],
                    "pb_ratio": market[3],
                    "pe_ratio": market[4],
                    "dividend_yield_pct": market[5],
                }
                if market
                else None
            ),

            "profitability": (
                {
                    "year": ratios[0],
                    "net_profit_margin_pct": ratios[1],
                    "operating_profit_margin_pct": ratios[2],
                    "return_on_equity_pct": ratios[3],
                }
                if ratios
                else None
            ),

            "financial_strength": (
                {
                    "debt_to_equity": ratios[4],
                    "interest_coverage": ratios[5],
                    "asset_turnover": ratios[6],
                    "free_cash_flow_cr": ratios[7],
                    "capex_cr": ratios[8],
                    "total_debt_cr": ratios[12],
                    "cash_from_operations_cr": ratios[13],
                }
                if ratios
                else None
            ),

            "per_share": (
                {
                    "earnings_per_share": ratios[9],
                    "book_value_per_share": ratios[10],
                    "dividend_payout_ratio_pct": ratios[11],
                }
                if ratios
                else None
            ),
        }

    finally:
        conn.close()

