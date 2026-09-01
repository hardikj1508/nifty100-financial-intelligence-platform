import sqlite3

import pandas as pd
import streamlit as st

DB_PATH = "data/database/nifty100.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

@st.cache_data(ttl=600)
def get_companies():

    conn = get_connection()

    query = """
    SELECT
        id,
        company_name
    FROM companies
    ORDER BY company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_ratios(company_id, year=None):

    conn = get_connection()

    query = """
    SELECT *
    FROM financial_ratios
    WHERE company_id=?
    """

    params = [company_id]

    if year:
        query += " AND year=?"
        params.append(year)

    return pd.read_sql(
        query,
        conn,
        params=params
    )

@st.cache_data(ttl=600)
def get_pl(company_id):

    conn = get_connection()

    return pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id=?
        """,
        conn,
        params=[company_id]
    )

@st.cache_data(ttl=600)
def get_bs(company_id):

    conn = get_connection()

    return pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id=?
        """,
        conn,
        params=[company_id]
    )

@st.cache_data(ttl=600)
def get_cf(company_id):

    conn = get_connection()

    return pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id=?
        """,
        conn,
        params=[company_id]
    )

@st.cache_data(ttl=600)
def get_sectors():

    conn = get_connection()

    return pd.read_sql(
        "SELECT * FROM sectors",
        conn
    )

@st.cache_data(ttl=600)
def get_peers(peer_group):

    conn = get_connection()

    return pd.read_sql(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name=?
        """,
        conn,
        params=[peer_group]
    )

@st.cache_data(ttl=600)
def get_valuation(company_id):

    try:

        conn = get_connection()

        return pd.read_sql(
            """
            SELECT *
            FROM valuation_summary
            WHERE company_id=?
            """,
            conn,
            params=[company_id]
        )

    except sqlite3.Error:
        return pd.DataFrame()
    
@st.cache_data(ttl=600)
def get_years():
    conn = get_connection()

    query = """
    SELECT DISTINCT year
    FROM financial_ratios
    ORDER BY year
    """

    return pd.read_sql(query, conn)["year"].tolist()


@st.cache_data(ttl=600)
def get_sector_counts():
    conn = get_connection()

    query = """
    SELECT broad_sector, COUNT(*) AS companies
    FROM sectors
    GROUP BY broad_sector
    ORDER BY companies DESC
    """

    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_total_companies():
    conn = get_connection()

    query = """
    SELECT COUNT(*) AS total
    FROM companies
    """

    return pd.read_sql(query, conn).iloc[0]["total"]

@st.cache_data(ttl=600)
def get_average_roe(year):
    conn = get_connection()

    query = """
    SELECT AVG(return_on_equity_pct) AS avg_roe
    FROM financial_ratios
    WHERE year = ?
    """

    df = pd.read_sql(query, conn, params=[year])

    return df.iloc[0]["avg_roe"]

@st.cache_data(ttl=600)
def get_median_de(year):
    conn = get_connection()

    query = """
    SELECT debt_to_equity
    FROM financial_ratios
    WHERE year = ?
    """

    df = pd.read_sql(query, conn, params=[year])

    return df["debt_to_equity"].median()

@st.cache_data(ttl=600)
def get_debt_free_count(year):
    conn = get_connection()

    query = """
    SELECT COUNT(*) AS total
    FROM financial_ratios
    WHERE year = ?
    AND debt_to_equity = 0
    """

    df = pd.read_sql(query, conn, params=[year])

    return df.iloc[0]["total"]

@st.cache_data(ttl=600)
def get_median_net_profit_margin(year):

    conn = get_connection()

    query = """
    SELECT net_profit_margin_pct
    FROM financial_ratios
    WHERE year = ?
    """

    df = pd.read_sql(query, conn, params=[year])

    conn.close()

    return df["net_profit_margin_pct"].median()

@st.cache_data(ttl=600)
def get_sector_breakdown():

    conn = get_connection()

    query = """
    SELECT broad_sector,
           COUNT(*) AS companies
    FROM sectors
    GROUP BY broad_sector
    ORDER BY companies DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_top_companies(year):

    conn = get_connection()

    query = """
    SELECT
        c.company_name,
        f.return_on_equity_pct,
        f.net_profit_margin_pct
    FROM financial_ratios f
    JOIN companies c
        ON f.company_id = c.id
    WHERE f.year = ?
    ORDER BY f.return_on_equity_pct DESC
    LIMIT 5
    """

    df = pd.read_sql(query, conn, params=[year])

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_company_profile(company_name):

    conn = get_connection()

    query = """
    SELECT *
    FROM companies
    WHERE company_name = ?
    """

    df = pd.read_sql(query, conn, params=[company_name])

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_screener_data(year):

    conn = get_connection()

    query = """
    SELECT
        c.company_name,
        s.broad_sector,
        f.return_on_equity_pct,
        f.debt_to_equity,
        f.net_profit_margin_pct
    FROM financial_ratios f
    JOIN companies c
        ON f.company_id = c.id
    LEFT JOIN sectors s
        ON c.id = s.company_id
    WHERE f.year = ?
    """

    df = pd.read_sql(query, conn, params=[year])

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_peer_comparison(company_name, year):

    conn = get_connection()

    query = """
    SELECT
        c.company_name,
        s.broad_sector,
        f.return_on_equity_pct,
        f.debt_to_equity,
        f.net_profit_margin_pct,
        f.earnings_per_share

    FROM financial_ratios f

    JOIN companies c
    ON f.company_id = c.id

    LEFT JOIN sectors s
    ON c.id = s.company_id

    WHERE
    s.broad_sector = (

        SELECT broad_sector
        FROM sectors
        WHERE company_id = ?

    )

    AND f.year = ?

    ORDER BY return_on_equity_pct DESC
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_name, year]
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_peer_average(company_id, year):

    conn = get_connection()

    query = """
    SELECT
        AVG(f.return_on_equity_pct) AS return_on_equity_pct,
        AVG(f.debt_to_equity) AS debt_to_equity,
        AVG(f.net_profit_margin_pct) AS net_profit_margin_pct,
        AVG(f.earnings_per_share) AS earnings_per_share

    FROM financial_ratios f

    JOIN sectors s
        ON f.company_id = s.company_id

    WHERE
        s.broad_sector = (
            SELECT broad_sector
            FROM sectors
            WHERE company_id = ?
        )

        AND f.year = ?
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id, year]
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_trend_data(company_id):

    conn = get_connection()

    query = """
    SELECT
        year,
        net_profit_margin_pct,
        operating_profit_margin_pct,
        return_on_equity_pct,
        debt_to_equity,
        interest_coverage,
        asset_turnover,
        earnings_per_share,
        book_value_per_share
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id]
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_sector_data(sector):

    conn = get_connection()

    query = """
    SELECT
        c.company_name,
        s.broad_sector,
        f.return_on_equity_pct,
        f.net_profit_margin_pct,
        f.debt_to_equity,
        f.free_cash_flow_cr
    FROM financial_ratios f

    JOIN companies c
        ON f.company_id = c.id

    JOIN sectors s
        ON c.id = s.company_id

    WHERE s.broad_sector = ?
      AND f.year = 'Mar 2024'
    """

    df = pd.read_sql(
        query,
        conn,
        params=[sector]
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_capital_data(company_id):

    conn = get_connection()

    query = """
    SELECT
        year,
        cash_from_operations_cr,
        free_cash_flow_cr,
        capex_cr,
        total_debt_cr
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id]
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_company_reports(company_id):

    conn = get_connection()

    query = """
    SELECT
        company_name,
        website,
        nse_profile,
        bse_profile
    FROM companies
    WHERE id = ?
    """

    df = pd.read_sql(
        query,
        conn,
        params=[company_id]
    )

    conn.close()

    return df