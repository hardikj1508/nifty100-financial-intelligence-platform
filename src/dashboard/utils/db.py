import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "data/database/nifty100.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

@st.cache_data(ttl=600)
def get_companies():

    conn = get_connection()

    return pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

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

    except:

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