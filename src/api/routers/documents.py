"""Company annual-report document API endpoints."""

import sqlite3

from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/companies",
    tags=["Documents"],
)


DATABASE = "data/database/nifty100.db"


@router.get("/{ticker}/documents")
def get_company_documents(ticker: str):
    """
    Return annual report links for a company.

    Each document includes an is_url_valid boolean flag.
    """

    conn = sqlite3.connect(DATABASE)

    try:

        # ====================================================
        # CHECK COMPANY
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
        # GET DOCUMENTS
        # ====================================================

        cursor = conn.execute(
            """
            SELECT
                year,
                annual_report
            FROM documents
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY year
            """,
            (company_ticker,),
        )

        rows = cursor.fetchall()

        # ====================================================
        # BUILD RESPONSE
        # ====================================================

        documents = []

        for year, annual_report in rows:

            is_url_valid = (
                isinstance(annual_report, str)
                and annual_report.startswith(
                    ("http://", "https://")
                )
            )

            documents.append(
                {
                    "year": year,
                    "annual_report": annual_report,
                    "is_url_valid": is_url_valid,
                }
            )

        return {
            "ticker": company_ticker,
            "company_name": company_name,
            "count": len(documents),
            "documents": documents,
        }

    finally:
        conn.close()