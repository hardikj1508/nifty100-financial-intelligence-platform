import streamlit as st
import plotly.express as px
import pandas as pd

from src.dashboard.utils.db import *

st.title("Sector Analysis")

# -------------------------
# Get Available Sectors
# -------------------------

conn = get_connection()

sector_df = pd.read_sql(
    """
    SELECT DISTINCT broad_sector
    FROM sectors
    ORDER BY broad_sector
    """,
    conn
)

conn.close()

selected_sector = st.selectbox(
    "Select Sector",
    sector_df["broad_sector"]
)

# -------------------------
# Fetch Sector Data
# -------------------------

df = get_sector_data(selected_sector)

# Bubble size cannot be negative
df["bubble_size"] = df["free_cash_flow_cr"].abs()

# -------------------------
# Bubble Chart
# -------------------------

fig = px.scatter(
    df,
    x="return_on_equity_pct",
    y="net_profit_margin_pct",
    size="bubble_size",
    color="debt_to_equity",
    hover_name="company_name",
    hover_data={
        "return_on_equity_pct":":.2f",
        "net_profit_margin_pct":":.2f",
        "debt_to_equity":":.2f",
        "free_cash_flow_cr":":,.0f",
        "bubble_size":False
    },
    size_max=50,
    title="Sector Comparison"
)

fig.update_layout(
    height=600,
    xaxis_title="Return on Equity (%)",
    yaxis_title="Net Profit Margin (%)",
    legend_title="Debt to Equity"
)

st.plotly_chart(
    fig,
    width="stretch"
)

# -------------------------
# Sector Statistics
# -------------------------

st.subheader("Sector Statistics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Avg ROE",
    f"{df['return_on_equity_pct'].mean():.2f}%"
)

col2.metric(
    "Avg Margin",
    f"{df['net_profit_margin_pct'].mean():.2f}%"
)

col3.metric(
    "Avg Debt/Equity",
    f"{df['debt_to_equity'].mean():.2f}"
)

col4.metric(
    "Companies",
    len(df)
)