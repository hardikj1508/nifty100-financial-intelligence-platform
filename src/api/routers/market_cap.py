"""Historical market-cap valuation API endpoints."""

import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/market-cap",
    tags=["Market Cap"],
)

DATABASE = "data/database/nifty100.db"


@router.get("/{ticker}")
def get_market_cap_history(ticker: str):
    """
    Return historical valuation multiples from 2019 to 2024.
    """

    conn = sqlite3.connect(DATABASE)

    try:
        # ========================================================
        # CHECK COMPANY
        # ========================================================

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

        # ========================================================
        # GET HISTORICAL VALUATION DATA
        # ========================================================

        cursor = conn.execute(
            """
            SELECT
                year,
                market_cap_crore,
                enterprise_value_crore,
                pe_ratio,
                pb_ratio,
                ev_ebitda,
                dividend_yield_pct
            FROM market_cap
            WHERE UPPER(company_id) = UPPER(?)
              AND year BETWEEN 2019 AND 2024
            ORDER BY year
            """,
            (company_ticker,),
        )

        rows = cursor.fetchall()

        # ========================================================
        # BUILD RESPONSE
        # ========================================================

        history = []

        for (
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct,
        ) in rows:

            history.append(
                {
                    "year": year,
                    "market_cap_crore": market_cap_crore,
                    "enterprise_value_crore": enterprise_value_crore,
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "ev_ebitda": ev_ebitda,
                    "dividend_yield_pct": dividend_yield_pct,
                }
            )

        return {
            "ticker": company_ticker,
            "company_name": company_name,
            "from_year": 2019,
            "to_year": 2024,
            "count": len(history),
            "history": history,
        }

    finally:
        conn.close()