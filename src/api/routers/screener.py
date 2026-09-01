"""Stock screener API endpoints."""

import math
import re
import sqlite3

import pandas as pd

from fastapi import APIRouter, HTTPException, Query

from src.screener.engine import ScreenerEngine

router = APIRouter(
    prefix="/screener",
    tags=["Screener"],
)


DATABASE = "data/database/nifty100.db"


def parse_number(value: str | None, parameter_name: str):
    """Convert a query parameter to float and return HTTP 400 on failure."""

    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail=f"{parameter_name} must be a valid number",
        )

    if math.isnan(number):
        raise HTTPException(
            status_code=400,
            detail=f"{parameter_name} must be a valid number"
        )

    return number


def extract_five_year_cagr(value):
    """
    Extract the 5-year CAGR percentage from analysis text.

    Example:
        '5 Years: 24%' -> 24.0
    """

    if value is None:
        return None

    match = re.search(
        r"5\s*Years:\s*(-?\d+(?:\.\d+)?)%",
        str(value),
        re.IGNORECASE,
    )

    if match:
        return float(match.group(1))

    return None


@router.get("")
def screen_companies(
    min_roe: str | None = Query(
        default=None,
        description="Minimum return on equity (%)",
    ),
    max_de: str | None = Query(
        default=None,
        description="Maximum debt-to-equity ratio",
    ),
    min_fcf: str | None = Query(
        default=None,
        description="Minimum free cash flow (? crore)",
    ),
    sector: str | None = Query(
        default=None,
        description="Broad sector",
    ),
    min_rev_cagr_5yr: str | None = Query(
        default=None,
        description="Minimum 5-year revenue CAGR (%)",
    ),
    min_pat_cagr_5yr: str | None = Query(
        default=None,
        description="Minimum 5-year PAT CAGR (%)",
    ),
    max_pe: str | None = Query(
        default=None,
        description="Maximum P/E ratio",
    ),
):
    """Return ranked companies matching screener filters."""

    # ========================================================
    # PARSE / VALIDATE PARAMETERS
    # ========================================================

    min_roe_value = parse_number(min_roe, "min_roe")
    max_de_value = parse_number(max_de, "max_de")
    min_fcf_value = parse_number(min_fcf, "min_fcf")
    min_rev_cagr_value = parse_number(
        min_rev_cagr_5yr,
        "min_rev_cagr_5yr",
    )
    min_pat_cagr_value = parse_number(
        min_pat_cagr_5yr,
        "min_pat_cagr_5yr",
    )
    max_pe_value = parse_number(max_pe, "max_pe")

    if max_de_value is not None and max_de_value < 0:
        raise HTTPException(
            status_code=400,
            detail="max_de cannot be negative",
        )

    if max_pe_value is not None and max_pe_value < 0:
        raise HTTPException(
            status_code=400,
            detail="max_pe cannot be negative",
        )

    if min_roe_value is not None and min_roe_value < -100:
        raise HTTPException(
            status_code=400,
            detail="min_roe is outside the valid range",
        )

    # ========================================================
    # DATABASE
    # ========================================================

    conn = sqlite3.connect(DATABASE)

    try:

        # ====================================================
        # GET ONE LATEST FINANCIAL-RATIO RECORD PER COMPANY
        # ====================================================

        ratio_query = """
            SELECT fr.*
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

        ratio_cursor = conn.execute(ratio_query)

        ratio_columns = [
            column[0]
            for column in ratio_cursor.description
        ]

        ratio_rows = [
            dict(zip(ratio_columns, row))
            for row in ratio_cursor.fetchall()
        ]

        # In the unlikely event of multiple records for the
        # same company/year, keep one record per company.
        latest_ratios = {}

        for row in ratio_rows:
            latest_ratios[row["company_id"]] = row

        # ====================================================
        # MARKET CAP
        #
        # 2024 contains all 92 companies.
        # ====================================================

        market_query = """
            SELECT *
            FROM market_cap
            WHERE year = 2024
        """

        market_cursor = conn.execute(market_query)

        market_columns = [
            column[0]
            for column in market_cursor.description
        ]

        market_rows = [
            dict(zip(market_columns, row))
            for row in market_cursor.fetchall()
        ]

        market_data = {
            row["company_id"]: row
            for row in market_rows
        }

        # ====================================================
        # ANALYSIS
        # ====================================================

        analysis_cursor = conn.execute(
            """
            SELECT
                company_id,
                compounded_sales_growth,
                compounded_profit_growth
            FROM analysis
            """
        )

        analysis_rows = analysis_cursor.fetchall()

        analysis_data = {}

        for row in analysis_rows:
            company_id = row[0]

            rev_cagr_5yr = extract_five_year_cagr(row[1])
            pat_cagr_5yr = extract_five_year_cagr(row[2])

            #Only keep rows containing 5-year CAGR values:
            if rev_cagr_5yr is not None or pat_cagr_5yr is not None:
                analysis_data[company_id] = {
                    "rev_cagr_5yr": rev_cagr_5yr,
                    "pat_cagr_5yr": pat_cagr_5yr,
                }

        # ====================================================
        # COMPANIES + SECTORS
        # ====================================================

        company_cursor = conn.execute(
            """
            SELECT
                c.id AS ticker,
                c.company_name,
                s.broad_sector,
                s.sub_sector
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            ORDER BY c.id
            """
        )

        companies = company_cursor.fetchall()

        results = []

        # ====================================================
        # BUILD ONE ROW PER COMPANY
        # ====================================================

        for ticker, company_name, broad_sector, sub_sector in companies:

            ratios = latest_ratios.get(ticker)
            market = market_data.get(ticker)
            analysis = analysis_data.get(
                ticker,
                {
                    "rev_cagr_5yr": None,
                    "pat_cagr_5yr": None,
                },
            )

            if ratios is None:
                roe = None
                debt_to_equity = None
                free_cash_flow = None
            else:
                roe = ratios.get("return_on_equity_pct")
                debt_to_equity = ratios.get("debt_to_equity")
                free_cash_flow = ratios.get("free_cash_flow_cr")

            pe_ratio = (
                market.get("pe_ratio")
                if market is not None
                else None
            )

            rev_cagr_5yr = analysis["rev_cagr_5yr"]
            pat_cagr_5yr = analysis["pat_cagr_5yr"]

            # =================================================
            # APPLY FILTERS
            # =================================================

            if (
                min_roe_value is not None
                and (
                    roe is None
                    or float(roe) < min_roe_value
                )
            ):
                continue

            if (
                max_de_value is not None
                and (
                    debt_to_equity is None
                    or float(debt_to_equity) > max_de_value
                )
            ):
                continue

            if (
                min_fcf_value is not None
                and (
                    free_cash_flow is None
                    or float(free_cash_flow) < min_fcf_value
                )
            ):
                continue

            if sector and (
                broad_sector is None
                or broad_sector.lower() != sector.lower()
            ):
                continue

            if (
                min_rev_cagr_value is not None
                and (
                    rev_cagr_5yr is None
                    or rev_cagr_5yr < min_rev_cagr_value
                )
            ):
                continue

            if (
                min_pat_cagr_value is not None
                and (
                    pat_cagr_5yr is None
                    or pat_cagr_5yr < min_pat_cagr_value
                )
            ):
                continue

            if (
                max_pe_value is not None
                and (
                    pe_ratio is None
                    or float(pe_ratio) > max_pe_value
                )
            ):
                continue

            # =================================================
            # RESULT
            # =================================================

            results.append(
                {
                    "ticker": ticker,
                    "company_name": company_name,
                    "sector": broad_sector,
                    "sub_sector": sub_sector,
                    "roe": roe,
                    "debt_to_equity": debt_to_equity,
                    "free_cash_flow": free_cash_flow,
                    "rev_cagr_5yr": rev_cagr_5yr,
                    "pat_cagr_5yr": pat_cagr_5yr,
                    "pe_ratio": pe_ratio,
                }
            )

        # ====================================================
        # RANKING
        #
        # Primary: ROE
        # Then PAT growth
        # Then revenue growth
        # Then FCF
        # Then lower debt
        # Then lower P/E
        # ====================================================

        def sort_key(row):
            return (
                row["roe"] if row["roe"] is not None else -999999,
                (
                    row["pat_cagr_5yr"]
                    if row["pat_cagr_5yr"] is not None
                    else -999999
                ),
                (
                    row["rev_cagr_5yr"]
                    if row["rev_cagr_5yr"] is not None
                    else -999999
                ),
                (
                    row["free_cash_flow"]
                    if row["free_cash_flow"] is not None
                    else -999999
                ),
                -(
                    row["debt_to_equity"]
                    if row["debt_to_equity"] is not None
                    else 999999
                ),
                -(
                    row["pe_ratio"]
                    if row["pe_ratio"] is not None
                    else 999999
                ),
            )

        results.sort(
            key=sort_key,
            reverse=True,
        )

        # ====================================================
        # ADD RANK
        # ====================================================

        for rank, row in enumerate(results, start=1):
            row["rank"] = rank

        # ====================================================
        # RESPONSE
        # ====================================================

        return {
            "count": len(results),
            "filters": {
                "min_roe": min_roe_value,
                "max_de": max_de_value,
                "min_fcf": min_fcf_value,
                "sector": sector,
                "min_rev_cagr_5yr": min_rev_cagr_value,
                "min_pat_cagr_5yr": min_pat_cagr_value,
                "max_pe": max_pe_value,
            },
            "companies": results,
        }

    finally:
        conn.close()

@router.get("/presets")
def screen_by_preset(
    preset: str = Query(
        default="growth_accelerator",
        description="Screener preset name",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of companies to return",
    ),
):
    """Run the validated ScreenerEngine using a configured preset."""

    engine = ScreenerEngine(
        "data/database/nifty100.db",
        "config/screener_config.yaml",
    )

    try:
        # Apply requested preset
        filtered_df = engine.apply_filters(preset)

        # Calculate sector-normalized composite score
        scored_df = engine.calculate_composite_score(
            filtered_df
        )

        # Rank by composite quality score
        ranked_df = engine.rank_companies(
            scored_df,
            "composite_quality_score",
        )

        # Return requested number of companies
        top_df = engine.get_top_companies(
            ranked_df,
            limit,
        )

        # Convert DataFrame to JSON-friendly records
        companies = []

        for rank, (_, row) in enumerate(
            top_df.iterrows(),
            start=1,
        ):
            companies.append(
                {
                    "rank": rank,
                    "ticker": row["company_id"],
                    "sector": row.get("broad_sector"),
                    "compounded_sales_growth": row.get(
                        "compounded_sales_growth"
                    ),
                    "compounded_profit_growth": row.get(
                        "compounded_profit_growth"
                    ),
                    "roe": row.get(
                        "return_on_equity_pct"
                    ),
                    "debt_to_equity": row.get(
                        "debt_to_equity"
                    ),
                    "interest_coverage": row.get(
                        "interest_coverage"
                    ),
                    "composite_quality_score": row.get(
                        "composite_quality_score"
                    ),
                }
            )

        # Convert NaN values to None
        for company in companies:
            for key, value in company.items():
                if pd.isna(value):
                    company[key] = None

        return {
            "preset": preset,
            "count": len(companies),
            "companies": companies,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        engine.conn.close()


