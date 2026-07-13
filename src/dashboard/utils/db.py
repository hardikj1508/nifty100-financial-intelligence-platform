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