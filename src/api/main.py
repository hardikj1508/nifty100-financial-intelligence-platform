"""FastAPI application for the Nifty100 Financial Intelligence Platform."""

import sqlite3
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
    health,
)


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = "data/database/nifty100.db"
VERSION = "1.0.0"

START_TIME = time.monotonic()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create and return a SQLite database connection."""
    return sqlite3.connect(DATABASE)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Nifty100 Financial Intelligence Platform",
    description=(
        "Financial intelligence and analytics API "
        "for Nifty100 companies."
    ),
    version=VERSION,
)

# Store application-level configuration.
app.state.database = DATABASE
app.state.version = VERSION
app.state.start_time = START_TIME


# ============================================================
# CORS MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    """Log method, path, status code and response time."""

    start_time = time.perf_counter()

    response = await call_next(request)

    elapsed_ms = (
        time.perf_counter() - start_time
    ) * 1000

    print(
        f"{request.method} "
        f"{request.url.path} "
        f"{response.status_code} "
        f"{elapsed_ms:.2f} ms"
    )

    return response


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    companies.router,
    prefix="/api/v1",
)

app.include_router(
    screener.router,
    prefix="/api/v1",
)

app.include_router(
    sectors.router,
    prefix="/api/v1",
)

app.include_router(
    peers.router,
    prefix="/api/v1",
)

app.include_router(
    valuation.router,
    prefix="/api/v1",
)

app.include_router(
    portfolio.router,
    prefix="/api/v1",
)

app.include_router(
    documents.router,
    prefix="/api/v1",
)

app.include_router(
    health.router,
    prefix="/api/v1",
)