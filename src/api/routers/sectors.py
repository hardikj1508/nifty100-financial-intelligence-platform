"""Sector API endpoints."""

import sqlite3
from statistics import median

from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/sectors",
    tags=["Sectors"],
)


DATABASE = "data/database/nifty100.db"


@router.get("")
def get_sectors():
    """
    Return sector-wise company information with
    company count and median financial KPIs.
    """

    conn = sqlite3.connect(DATABASE)

    try:
        # ========================================================
        # COMPANIES + SECTORS
        # ========================================================

        company_cursor = conn.execute(
            """
            SELECT
                s.broad_sector,
                s.sub_sector,
                s.market_cap_category,
                c.id AS ticker,
                c.company_name
            FROM sectors s
            INNER JOIN companies c
                ON c.id = s.company_id
            ORDER BY
                s.broad_sector,
                s.sub_sector,
                c.id
            """
        )

        company_rows = company_cursor.fetchall()

        # ========================================================
        # LATEST FINANCIAL RATIOS
        # ========================================================

        ratio_cursor = conn.execute(
            """
            SELECT
                fr.company_id,
                fr.return_on_equity_pct,
                fr.debt_to_equity
            FROM financial_ratios fr
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(CAST(substr(year, -4) AS INTEGER)) AS latest_year
                FROM financial_ratios
                GROUP BY company_id
            ) latest
                ON fr.company_id = latest.company_id
                AND CAST(substr(fr.year, -4) AS INTEGER)
                    = latest.latest_year
            """
        )

        ratio_rows = ratio_cursor.fetchall()

        ratios = {}

        for company_id, roe, debt_to_equity in ratio_rows:
            ratios[company_id] = {
                "roe": roe,
                "debt_to_equity": debt_to_equity,
            }

        # ========================================================
        # MARKET CAP DATA
        #
        # Use 2024 because that is the complete market-cap
        # dataset in this project.
        # ========================================================

        market_cursor = conn.execute(
            """
            SELECT
                company_id,
                pe_ratio
            FROM market_cap
            WHERE year = 2024
            """
        )

        market_rows = market_cursor.fetchall()

        market_data = {
            company_id: {
                "pe_ratio": pe_ratio,
            }
            for company_id, pe_ratio in market_rows
        }

        # ========================================================
        # BUILD SECTORS
        # ========================================================

        sectors = {}

        for (
            broad_sector,
            sub_sector,
            market_cap_category,
            ticker,
            company_name,
        ) in company_rows:

            if broad_sector not in sectors:
                sectors[broad_sector] = {
                    "sector": broad_sector,
                    "company_count": 0,
                    "median_roe": None,
                    "median_pe": None,
                    "median_de": None,
                    "companies": [],
                }

            sector = sectors[broad_sector]

            sector["company_count"] += 1

            sector["companies"].append(
                {
                    "ticker": ticker,
                    "company_name": company_name,
                    "sub_sector": sub_sector,
                    "market_cap_category": market_cap_category,
                }
            )

        # ========================================================
        # CALCULATE SECTOR MEDIANS
        # ========================================================

        for sector_name, sector in sectors.items():

            roe_values = []
            pe_values = []
            debt_values = []

            for company in sector["companies"]:

                ticker = company["ticker"]

                # Latest ROE + Debt/Equity
                ratio = ratios.get(ticker)

                if ratio is not None:

                    roe = ratio["roe"]

                    if roe is not None:
                        roe_values.append(float(roe))

                    debt_to_equity = ratio["debt_to_equity"]

                    if debt_to_equity is not None:
                        debt_values.append(
                            float(debt_to_equity)
                        )

                # 2024 P/E
                market = market_data.get(ticker)

                if market is not None:

                    pe_ratio = market["pe_ratio"]

                    if pe_ratio is not None:
                        pe_values.append(float(pe_ratio))

            if roe_values:
                sector["median_roe"] = median(roe_values)

            if pe_values:
                sector["median_pe"] = median(pe_values)

            if debt_values:
                sector["median_de"] = median(debt_values)

        # ========================================================
        # RESPONSE
        # ========================================================

        return {
            "count": len(sectors),
            "sectors": list(sectors.values()),
        }

    finally:
        conn.close()

@router.get("/{sector}/companies")
def get_sector_companies(sector: str):
    """
    Return all companies in a sector with their latest-year KPIs.
    Return HTTP 404 if the sector does not exist.
    """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        # ========================================================
        # CHECK THAT SECTOR EXISTS
        # ========================================================

        sector_check = conn.execute(
            """
            SELECT DISTINCT broad_sector
            FROM sectors
            WHERE LOWER(broad_sector) = LOWER(?)
            """,
            (sector,),
        ).fetchone()

        if sector_check is None:
            raise HTTPException(
                status_code=404,
                detail=f"Sector '{sector}' not found",
            )

        actual_sector = sector_check["broad_sector"]

        # ========================================================
        # GET COMPANIES + LATEST KPIs
        # ========================================================

        query = """
            SELECT
                c.id AS ticker,
                c.company_name,
                s.broad_sector AS sector,
                s.sub_sector,
                s.market_cap_category,
                f.year,
                f.return_on_equity_pct,
                f.net_profit_margin_pct,
                f.operating_profit_margin_pct,
                f.debt_to_equity,
                f.interest_coverage,
                f.asset_turnover
            FROM companies c

            INNER JOIN sectors s
                ON c.id = s.company_id

            INNER JOIN financial_ratios f
                ON c.id = f.company_id

            INNER JOIN (
                SELECT
                    company_id,
                    MAX(
                        CAST(substr(year, -4) AS INTEGER)
                    ) AS latest_year
                FROM financial_ratios
                GROUP BY company_id
            ) latest
                ON f.company_id = latest.company_id
                AND CAST(substr(f.year, -4) AS INTEGER)
                    = latest.latest_year

            WHERE LOWER(s.broad_sector) = LOWER(?)

            ORDER BY c.id
        """

        rows = conn.execute(
            query,
            (actual_sector,),
        ).fetchall()

        # ========================================================
        # BUILD RESPONSE
        # ========================================================

        companies = []

        for row in rows:
            companies.append(
                {
                    "ticker": row["ticker"],
                    "company_name": row["company_name"],
                    "sector": row["sector"],
                    "sub_sector": row["sub_sector"],
                    "market_cap_category": row["market_cap_category"],
                    "year": row["year"],
                    "kpis": {
                        "return_on_equity_pct": row[
                            "return_on_equity_pct"
                        ],
                        "net_profit_margin_pct": row[
                            "net_profit_margin_pct"
                        ],
                        "operating_profit_margin_pct": row[
                            "operating_profit_margin_pct"
                        ],
                        "debt_to_equity": row["debt_to_equity"],
                        "interest_coverage": row[
                            "interest_coverage"
                        ],
                        "asset_turnover": row["asset_turnover"],
                    },
                }
            )

        return {
            "sector": actual_sector,
            "count": len(companies),
            "companies": companies,
        }

    finally:
        conn.close()