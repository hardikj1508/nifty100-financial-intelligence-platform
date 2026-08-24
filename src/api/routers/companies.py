"""Company API endpoints."""

from pathlib import Path
import re
import sqlite3

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE = PROJECT_ROOT / "data" / "database" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = PROJECT_ROOT / "reports"


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    """Return a SQLite database connection."""
    return sqlite3.connect(DATABASE)


def rows_to_dicts(cursor):
    """Convert SQLite rows into dictionaries."""
    columns = [column[0] for column in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# ============================================================
# YEAR HELPERS
# ============================================================

def extract_year(value):
    """
    Extract four-digit year from project year labels.

    Examples:
        'Mar 2024' -> 2024
        'Mar 2019' -> 2019
    """
    if value is None:
        return None

    match = re.search(r"\d{4}", str(value))

    if match:
        return int(match.group())

    return None


def year_matches(
    year_value,
    from_year=None,
    to_year=None,
):
    """Check whether a project year falls inside the requested range."""

    year = extract_year(year_value)

    if year is None:
        return False

    if from_year is not None:
        if year < from_year:
            return False

    if to_year is not None:
        if year > to_year:
            return False

    return True


# ============================================================
# 1. GET ALL COMPANIES
# ============================================================

@router.get("")
def get_companies(
    sector: str | None = Query(
        default=None,
        description="Filter by broad sector",
    ),
    market_cap_category: str | None = Query(
        default=None,
        description="Filter by market-cap category",
    ),
    search: str | None = Query(
        default=None,
        description="Partial company name or ticker search",
    ),
):
    """
    Return all Nifty 100 companies with optional filters.
    """

    conn = get_connection()

    try:
        query = """
            SELECT
                c.id AS ticker,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                c.roe_percentage AS roe_pct,
                c.roce_percentage AS roce_pct,
                s.market_cap_category
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            WHERE 1 = 1
        """

        params = []

        # ----------------------------------------------------
        # Sector filter
        # ----------------------------------------------------

        if sector:
            query += """
                AND LOWER(s.broad_sector) = LOWER(?)
            """
            params.append(sector)

        # ----------------------------------------------------
        # Market-cap filter
        # ----------------------------------------------------

        if market_cap_category:
            query += """
                AND LOWER(s.market_cap_category) = LOWER(?)
            """
            params.append(market_cap_category)

        # ----------------------------------------------------
        # Search filter
        # ----------------------------------------------------

        if search:
            query += """
                AND (
                    LOWER(c.id) LIKE LOWER(?)
                    OR LOWER(c.company_name) LIKE LOWER(?)
                )
            """

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
            ])

        query += """
            ORDER BY c.id
        """

        cursor = conn.execute(query, params)

        return rows_to_dicts(cursor)

    finally:
        conn.close()


# ============================================================
# 2. GET COMPLETE COMPANY PROFILE
# ============================================================

@router.get("/{ticker}")
def get_company(ticker: str):
    """
    Return complete company profile with latest KPIs
    and sector information.
    """

    conn = get_connection()

    try:

        # ----------------------------------------------------
        # Company profile
        # ----------------------------------------------------

        company_cursor = conn.execute(
            """
            SELECT *
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

        company_columns = [
            column[0]
            for column in company_cursor.description
        ]

        company_data = dict(
            zip(company_columns, company)
        )

        # ----------------------------------------------------
        # Sector information
        # ----------------------------------------------------

        sector_cursor = conn.execute(
            """
            SELECT
                broad_sector,
                sub_sector,
                index_weight_pct,
                market_cap_category
            FROM sectors
            WHERE UPPER(company_id) = UPPER(?)
            LIMIT 1
            """,
            (ticker,),
        )

        sector_data = sector_cursor.fetchone()

        sector = None

        if sector_data is not None:
            sector_columns = [
                column[0]
                for column in sector_cursor.description
            ]

            sector = dict(
                zip(sector_columns, sector_data)
            )

        # ----------------------------------------------------
        # Latest financial ratios
        # ----------------------------------------------------

        ratio_cursor = conn.execute(
            """
            SELECT *
            FROM financial_ratios
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY CAST(
                substr(year, -4) AS INTEGER
            ) DESC
            LIMIT 1
            """,
            (ticker,),
        )

        latest_ratios = ratio_cursor.fetchone()

        ratios = None

        if latest_ratios is not None:
            ratio_columns = [
                column[0]
                for column in ratio_cursor.description
            ]

            ratios = dict(
                zip(ratio_columns, latest_ratios)
            )

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return {
            "company": company_data,
            "sector": sector,
            "latest_kpis": ratios,
        }

    finally:
        conn.close()


# ============================================================
# YEAR VALIDATION
# ============================================================

def validate_year_parameter(value, parameter_name):
    """
    Validate YYYY-MM format.

    Example:
        2024-03
    """

    if value is None:
        return None

    if not re.fullmatch(r"\d{4}-\d{2}", value):
        raise HTTPException(
            status_code=400,
            detail=(
                f"{parameter_name} must use "
                "YYYY-MM format"
            ),
        )

    return int(value[:4])


# ============================================================
# 3. PROFIT & LOSS
# ============================================================

@router.get("/{ticker}/pl")
def get_profit_loss(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None,
):
    """Return P&L history for a company."""

    from_year_int = validate_year_parameter(
        from_year,
        "from_year",
    )

    to_year_int = validate_year_parameter(
        to_year,
        "to_year",
    )

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT *
            FROM profitandloss
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY CAST(
                substr(year, -4) AS INTEGER
            )
            """,
            (ticker,),
        )

        rows = rows_to_dicts(cursor)

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No P&L data found for '{ticker}'",
            )

        filtered_rows = [
            row
            for row in rows
            if year_matches(
                row["year"],
                from_year_int,
                to_year_int,
            )
        ]

        return {
            "ticker": ticker.upper(),
            "from_year": from_year,
            "to_year": to_year,
            "history": filtered_rows,
        }

    finally:
        conn.close()


# ============================================================
# 4. BALANCE SHEET
# ============================================================

@router.get("/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None,
):
    """Return balance-sheet history for a company."""

    from_year_int = validate_year_parameter(
        from_year,
        "from_year",
    )

    to_year_int = validate_year_parameter(
        to_year,
        "to_year",
    )

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT *
            FROM balancesheet
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY CAST(
                substr(year, -4) AS INTEGER
            )
            """,
            (ticker,),
        )

        rows = rows_to_dicts(cursor)

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No balance-sheet data found "
                    f"for '{ticker}'"
                ),
            )

        filtered_rows = [
            row
            for row in rows
            if year_matches(
                row["year"],
                from_year_int,
                to_year_int,
            )
        ]

        return {
            "ticker": ticker.upper(),
            "from_year": from_year,
            "to_year": to_year,
            "history": filtered_rows,
        }

    finally:
        conn.close()


# ============================================================
# 5. CASH FLOW
# ============================================================

@router.get("/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None,
):
    """Return cash-flow history for a company."""

    from_year_int = validate_year_parameter(
        from_year,
        "from_year",
    )

    to_year_int = validate_year_parameter(
        to_year,
        "to_year",
    )

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT *
            FROM cashflow
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY CAST(
                substr(year, -4) AS INTEGER
            )
            """,
            (ticker,),
        )

        rows = rows_to_dicts(cursor)

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No cash-flow data found "
                    f"for '{ticker}'"
                ),
            )

        filtered_rows = [
            row
            for row in rows
            if year_matches(
                row["year"],
                from_year_int,
                to_year_int,
            )
        ]

        return {
            "ticker": ticker.upper(),
            "from_year": from_year,
            "to_year": to_year,
            "history": filtered_rows,
        }

    finally:
        conn.close()


# ============================================================
# 6. FINANCIAL RATIOS
# ============================================================

@router.get("/{ticker}/ratios")
def get_ratios(
    ticker: str,
    year: str | None = None,
):
    """
    Return computed financial ratios.

    If year is supplied, return only that year.
    """

    year_int = validate_year_parameter(
        year,
        "year",
    )

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT *
            FROM financial_ratios
            WHERE UPPER(company_id) = UPPER(?)
            ORDER BY CAST(
                substr(year, -4) AS INTEGER
            )
            """,
            (ticker,),
        )

        rows = rows_to_dicts(cursor)

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No financial-ratio data "
                    f"found for '{ticker}'"
                ),
            )

        if year_int is not None:
            rows = [
                row
                for row in rows
                if extract_year(row["year"]) == year_int
            ]

        return {
            "ticker": ticker.upper(),
            "year": year,
            "ratios": rows,
        }

    finally:
        conn.close()


# ============================================================
# 7. TEARSHEET PDF
# ============================================================

@router.get("/{ticker}/tearsheet")
def get_tearsheet(ticker: str):
    """
    Return the pre-generated tearsheet PDF.
    """

    ticker = ticker.upper()

    # --------------------------------------------------------
    # Search output first
    # --------------------------------------------------------

    candidates = list(
        OUTPUT_DIR.glob(f"{ticker}*.pdf")
    )

    # --------------------------------------------------------
    # Search reports if not found
    # --------------------------------------------------------

    if not candidates:
        candidates = list(
            REPORTS_DIR.glob(f"{ticker}*.pdf")
        )

    if not candidates:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Tearsheet PDF not found "
                f"for '{ticker}'"
            ),
        )

    pdf_file = candidates[0]

    return FileResponse(
        path=pdf_file,
        media_type="application/pdf",
        filename=pdf_file.name,
    )