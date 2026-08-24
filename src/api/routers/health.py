"""Health and database status endpoints."""

import sqlite3
import time

from fastapi import APIRouter, Request


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


# ============================================================
# DATABASE TABLES
# ============================================================

TABLES = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios",
    "market_cap",
    "analysis",
    "documents",
    "peer_groups",
    "sectors",
]


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@router.get("")
def health_check(request: Request):
    """
    Return API health, database row counts,
    uptime and application version.
    """

    database = request.app.state.database
    version = request.app.state.version
    start_time = request.app.state.start_time

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    db_row_counts = {}

    for table in TABLES:
        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        db_row_counts[table] = cursor.fetchone()[0]

    conn.close()

    uptime_seconds = round(
        time.monotonic() - start_time,
        2,
    )

    return {
        "status": "ok",
        "db_row_counts": db_row_counts,
        "uptime_seconds": uptime_seconds,
        "version": version,
    }