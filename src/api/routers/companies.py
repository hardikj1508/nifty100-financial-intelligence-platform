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

# ============================================================
# 6. FINANCIAL RATIOS
# ============================================================

@router.get("/{ticker}/ratios")
def get_ratios(
    ticker: str,
    year: str | None = None,
    from_year: str | None = None,
    to_year: str | None = None,
):
    """
    Return financial ratios for a company.

    Supports:
    - No filter: return all years
    - year: return one specific year
    - from_year + to_year: return a year range
    """

    # --------------------------------------------------------
    # Validate year parameters
    # --------------------------------------------------------

    year_int = validate_year_parameter(
        year,
        "year",
    )

    from_year_int = validate_year_parameter(
        from_year,
        "from_year",
    )

    to_year_int = validate_year_parameter(
        to_year,
        "to_year",
    )

    # --------------------------------------------------------
    # Make sure from_year is not greater than to_year
    # --------------------------------------------------------

    if (
        from_year_int is not None
        and to_year_int is not None
        and from_year_int > to_year_int
    ):
        raise HTTPException(
            status_code=400,
            detail="from_year must be less than or equal to to_year",
        )

    # --------------------------------------------------------
    # Connect to database
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # No data found
        # ----------------------------------------------------

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No financial-ratio data "
                    f"found for '{ticker}'"
                ),
            )

        # ----------------------------------------------------
        # Filter by one specific year
        # ----------------------------------------------------

        if year_int is not None:
            rows = [
                row
                for row in rows
                if extract_year(row["year"]) == year_int
            ]

        # ----------------------------------------------------
        # Filter by starting year
        # ----------------------------------------------------

        if from_year_int is not None:
            rows = [
                row
                for row in rows
                if extract_year(row["year"]) >= from_year_int
            ]

        # ----------------------------------------------------
        # Filter by ending year
        # ----------------------------------------------------

        if to_year_int is not None:
            rows = [
                row
                for row in rows
                if extract_year(row["year"]) <= to_year_int
            ]

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "ticker": ticker.upper(),
            "year": year,
            "from_year": from_year,
            "to_year": to_year,
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

# ============================================================
# 8. PEER COMPARISON
# ============================================================

@router.get("/{ticker}/peers/compare")
def compare_peers(ticker: str):
    """
    Return radar-comparison data for a company,
    its peer-group average, and benchmark company.
    """

    conn = get_connection()

    try:
        # ----------------------------------------------------
        # Find company
        # ----------------------------------------------------

        company_cursor = conn.execute(
            """
            SELECT
                c.id AS ticker,
                c.company_name
            FROM companies c
            WHERE UPPER(c.id) = UPPER(?)
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

        # ----------------------------------------------------
        # Find peer group
        # ----------------------------------------------------

        group_cursor = conn.execute(
            """
            SELECT
                pg.peer_group_name
            FROM peer_groups pg
            WHERE UPPER(pg.company_id) = UPPER(?)
            LIMIT 1
            """,
            (company_ticker,),
        )

        group = group_cursor.fetchone()

        if group is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No peer group found "
                    f"for '{company_ticker}'"
                ),
            )

        peer_group_name = group[0]

        # ----------------------------------------------------
        # Get all companies in peer group
        # ----------------------------------------------------

        peer_cursor = conn.execute(
            """
            SELECT
                pg.company_id,
                pg.is_benchmark,
                c.company_name
            FROM peer_groups pg
            INNER JOIN companies c
                ON c.id = pg.company_id
            WHERE pg.peer_group_name = ?
            ORDER BY c.id
            """,
            (peer_group_name,),
        )

        peer_rows = peer_cursor.fetchall()

        if not peer_rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No companies found in "
                    f"peer group '{peer_group_name}'"
                ),
            )

        # ----------------------------------------------------
        # Latest financial ratios
        # ----------------------------------------------------

        ratio_cursor = conn.execute(
            """
            SELECT
                fr.company_id,
                fr.return_on_equity_pct,
                fr.debt_to_equity,
                fr.interest_coverage,
                fr.asset_turnover,
                fr.free_cash_flow_cr
            FROM financial_ratios fr
            INNER JOIN (
                SELECT
                    company_id,
                    MAX(
                        CAST(substr(year, -4) AS INTEGER)
                    ) AS latest_year
                FROM financial_ratios
                GROUP BY company_id
            ) latest
                ON fr.company_id = latest.company_id
                AND CAST(substr(fr.year, -4) AS INTEGER)
                    = latest.latest_year
            """
        )

        ratio_rows = ratio_cursor.fetchall()

        ratios = {
            row[0]: {
                "roe_pct": row[1],
                "debt_to_equity": row[2],
                "interest_coverage": row[3],
                "asset_turnover": row[4],
                "free_cash_flow_cr": row[5],
            }
            for row in ratio_rows
        }

        # ----------------------------------------------------
        # Market data
        # ----------------------------------------------------

        market_cursor = conn.execute(
            """
            SELECT
                company_id,
                pe_ratio,
                pb_ratio,
                ev_ebitda
            FROM market_cap
            WHERE year = 2024
            """
        )

        market_rows = market_cursor.fetchall()

        market = {
            row[0]: {
                "pe_ratio": row[1],
                "pb_ratio": row[2],
                "ev_ebitda": row[3],
            }
            for row in market_rows
        }

        # ----------------------------------------------------
        # Build metric records
        # ----------------------------------------------------

        metric_names = [
            "roe_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "pe_ratio",
            "pb_ratio",
            "ev_ebitda",
        ]

        company_metrics = {}
        benchmark_ticker = None
        benchmark_name = None

        for peer_ticker, is_benchmark, peer_name in peer_rows:

            if is_benchmark:
                benchmark_ticker = peer_ticker
                benchmark_name = peer_name

            company_metrics[peer_ticker] = {}

            ratio = ratios.get(peer_ticker, {})
            market_data = market.get(peer_ticker, {})

            for metric in metric_names:

                if metric in ratio:
                    value = ratio.get(metric)
                else:
                    value = market_data.get(metric)

                company_metrics[peer_ticker][metric] = value

        # ----------------------------------------------------
        # Peer average
        # ----------------------------------------------------

        peer_average = {}

        for metric in metric_names:

            values = []

            for peer_ticker in company_metrics:

                value = company_metrics[
                    peer_ticker
                ].get(metric)

                if value is not None:
                    values.append(float(value))

            if values:
                peer_average[metric] = (
                    sum(values) / len(values)
                )
            else:
                peer_average[metric] = None

        # ----------------------------------------------------
        # Selected company
        # ----------------------------------------------------

        selected_metrics = company_metrics.get(
            company_ticker,
            {},
        )

        benchmark_metrics = {}

        if benchmark_ticker is not None:
            benchmark_metrics = company_metrics.get(
                benchmark_ticker,
                {},
            )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return {
            "ticker": company_ticker,
            "company_name": company_name,
            "peer_group": peer_group_name,
            "benchmark": {
                "ticker": benchmark_ticker,
                "company_name": benchmark_name,
                "metrics": benchmark_metrics,
            },
            "company": selected_metrics,
            "peer_average": peer_average,
            "metrics": metric_names,
        }

    finally:
        conn.close()