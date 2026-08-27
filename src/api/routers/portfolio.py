"""Portfolio API endpoints."""

import sqlite3

from fastapi import APIRouter, HTTPException, Query


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


DATABASE = "data/database/nifty100.db"


# ============================================================
# 1. GET ALL PORTFOLIO COMPANIES
# ============================================================

@router.get("")
def get_portfolio(
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
        description="Maximum number of companies to return",
    )
):
    """
    Return the latest March financial KPI data
    for NIFTY 100 companies.
    """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        query = """
            SELECT
                c.id AS ticker,
                c.company_name,
                s.broad_sector AS sector,
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
            INNER JOIN financial_ratios f
                ON c.id = f.company_id
            WHERE f.year = (
                SELECT MAX(f2.year)
                FROM financial_ratios f2
                WHERE f2.company_id = f.company_id
                  AND f2.year LIKE 'Mar %'
            )
            ORDER BY c.id
            LIMIT ?
        """

        rows = conn.execute(query, (limit,)).fetchall()

        portfolio = []

        for row in rows:
            portfolio.append(
                {
                    "ticker": row["ticker"],
                    "company_name": row["company_name"],
                    "sector": row["sector"],
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
            "count": len(portfolio),
            "portfolio": portfolio,
        }

    finally:
        conn.close()


# ============================================================
# 2. PORTFOLIO KPI PERCENTILES
# ============================================================

@router.get("/stats")
def get_portfolio_stats():
    """
    Return P10, P25, P50, P75 and P90 percentile
    statistics for 10 core KPIs across all companies.
    """

    conn = sqlite3.connect(DATABASE)

    try:

        query = """
            SELECT
                f.return_on_equity_pct,
                f.net_profit_margin_pct,
                f.operating_profit_margin_pct,
                f.debt_to_equity,
                f.interest_coverage,
                f.asset_turnover,
                f.free_cash_flow_cr,
                f.capex_cr,
                f.earnings_per_share,
                f.book_value_per_share
            FROM financial_ratios f
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
        """

        rows = conn.execute(query).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No financial-ratio data found",
            )

        # ====================================================
        # KPI NAMES
        # ====================================================

        kpi_names = [
            "return_on_equity_pct",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "capex_cr",
            "earnings_per_share",
            "book_value_per_share",
        ]

        # ====================================================
        # PERCENTILE FUNCTION
        # Linear interpolation
        # ====================================================

        def percentile(values, percentile_value):

            values = sorted(
                float(value)
                for value in values
                if value is not None
            )

            if not values:
                return None

            if len(values) == 1:
                return values[0]

            position = (
                (len(values) - 1)
                * percentile_value
                / 100
            )

            lower = int(position)
            upper = lower + 1

            if upper >= len(values):
                return values[-1]

            fraction = position - lower

            return (
                values[lower]
                + fraction
                * (values[upper] - values[lower])
            )

        # ====================================================
        # PERCENTILE LEVELS
        # ====================================================

        percentile_levels = [
            ("p10", 10),
            ("p25", 25),
            ("p50", 50),
            ("p75", 75),
            ("p90", 90),
        ]

        # ====================================================
        # CALCULATE STATS
        # ====================================================

        stats = {}

        for index, kpi in enumerate(kpi_names):

            values = [
                row[index]
                for row in rows
                if row[index] is not None
            ]

            stats[kpi] = {
                label: percentile(
                    values,
                    level,
                )
                for label, level in percentile_levels
            }

        # ====================================================
        # RESPONSE
        # ====================================================

        return {
            "company_count": len(rows),
            "kpi_count": len(kpi_names),
            "percentiles": [
                {
                    "percentile": label.upper(),
                    **{
                        kpi: stats[kpi][label]
                        for kpi in kpi_names
                    },
                }
                for label, _ in percentile_levels
            ],
        }

    finally:
        conn.close()


# ============================================================
# 3. GET ONE COMPANY'S PORTFOLIO DATA
# ============================================================

@router.get("/{ticker}")
def get_portfolio_company(ticker: str):
    """
    Return portfolio KPI information for one company.
    """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:

        query = """
            SELECT
                c.id AS ticker,
                c.company_name,
                s.broad_sector AS sector,
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
            INNER JOIN financial_ratios f
                ON c.id = f.company_id
            WHERE UPPER(c.id) = UPPER(?)
              AND f.year = (
                SELECT MAX(f2.year)
                FROM financial_ratios f2
                WHERE f2.company_id = f.company_id
                  AND f2.year LIKE 'Mar %'
            )
        """

        row = conn.execute(
            query,
            (ticker,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found",
            )

        return {
            "ticker": row["ticker"],
            "company_name": row["company_name"],
            "sector": row["sector"],
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

    finally:
        conn.close()