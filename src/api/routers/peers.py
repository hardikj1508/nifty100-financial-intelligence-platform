"""Peer comparison API endpoints."""

import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/peers",
    tags=["Peers"],
)

DATABASE = "data/database/nifty100.db"


def percentile_rank(values, value):
    """Return percentile rank from 0 to 100."""
    if value is None or not values:
        return None

    valid_values = [
        float(v)
        for v in values
        if v is not None
    ]

    if not valid_values:
        return None

    value = float(value)

    less_than_or_equal = sum(
        1 for v in valid_values if v <= value
    )

    return round(
        (less_than_or_equal / len(valid_values)) * 100,
        2,
    )


@router.get("/{group_name}")
def get_peers(group_name: str):
    """
    Return all companies in a peer group with
    percentile ranks for 10 financial metrics.
    """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    try:
        # ========================================================
        # CHECK PEER GROUP
        # ========================================================

        group_check = conn.execute(
            """
            SELECT DISTINCT peer_group_name
            FROM peer_groups
            WHERE LOWER(peer_group_name) = LOWER(?)
            """,
            (group_name,),
        ).fetchone()

        if group_check is None:
            raise HTTPException(
                status_code=404,
                detail=f"Peer group '{group_name}' not found",
            )

        actual_group = group_check["peer_group_name"]

        # ========================================================
        # GET PEER COMPANIES
        # ========================================================

        query = """
            SELECT
                pg.company_id AS ticker,
                c.company_name,
                pg.is_benchmark,

                c.roe_percentage AS roce_roe_placeholder,
                c.roce_percentage AS roce_pct,

                fr.year,
                fr.net_profit_margin_pct,
                fr.operating_profit_margin_pct,
                fr.return_on_equity_pct,
                fr.debt_to_equity,
                fr.interest_coverage,
                fr.asset_turnover,
                fr.free_cash_flow_cr,

                mc.pe_ratio,
                mc.ev_ebitda

            FROM peer_groups pg

            INNER JOIN companies c
                ON c.id = pg.company_id

            LEFT JOIN financial_ratios fr
                ON fr.company_id = pg.company_id
                AND CAST(substr(fr.year, -4) AS INTEGER) = (
                    SELECT MAX(
                        CAST(substr(fr2.year, -4) AS INTEGER)
                    )
                    FROM financial_ratios fr2
                    WHERE fr2.company_id = pg.company_id
                )

            LEFT JOIN market_cap mc
                ON mc.company_id = pg.company_id
                AND mc.year = 2024

            WHERE LOWER(pg.peer_group_name) = LOWER(?)

            ORDER BY pg.is_benchmark DESC, pg.company_id
        """

        rows = conn.execute(
            query,
            (actual_group,),
        ).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Peer group '{actual_group}' not found",
            )

        # ========================================================
        # BUILD RAW METRIC ARRAYS
        # ========================================================

        metric_names = [
            "roe_pct",
            "roce_pct",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "pe_ratio",
            "ev_ebitda",
        ]

        metric_values = {
            metric: []
            for metric in metric_names
        }

        raw_companies = []

        for row in rows:

            company = {
                "ticker": row["ticker"],
                "company_name": row["company_name"],
                "is_benchmark": bool(row["is_benchmark"]),
                "year": row["year"],

                "metrics": {
                    "roe_pct": row["return_on_equity_pct"],
                    "roce_pct": row["roce_pct"],
                    "net_profit_margin_pct": row[
                        "net_profit_margin_pct"
                    ],
                    "operating_profit_margin_pct": row[
                        "operating_profit_margin_pct"
                    ],
                    "debt_to_equity": row[
                        "debt_to_equity"
                    ],
                    "interest_coverage": row[
                        "interest_coverage"
                    ],
                    "asset_turnover": row[
                        "asset_turnover"
                    ],
                    "free_cash_flow_cr": row[
                        "free_cash_flow_cr"
                    ],
                    "pe_ratio": row["pe_ratio"],
                    "ev_ebitda": row["ev_ebitda"],
                },
            }

            raw_companies.append(company)

            for metric in metric_names:
                value = company["metrics"][metric]

                if value is not None:
                    metric_values[metric].append(
                        float(value)
                    )

        # ========================================================
        # ADD PERCENTILE RANKS
        # ========================================================

        companies = []

        for company in raw_companies:

            percentile_ranks = {}

            for metric in metric_names:

                value = company["metrics"][metric]

                percentile_ranks[metric] = percentile_rank(
                    metric_values[metric],
                    value,
                )

            companies.append(
                {
                    "ticker": company["ticker"],
                    "company_name": company["company_name"],
                    "is_benchmark": company["is_benchmark"],
                    "year": company["year"],
                    "metrics": company["metrics"],
                    "percentile_rank": percentile_ranks,
                }
            )

        # ========================================================
        # RESPONSE
        # ========================================================

        return {
            "peer_group": actual_group,
            "count": len(companies),
            "companies": companies,
        }

    finally:
        conn.close()      
                    