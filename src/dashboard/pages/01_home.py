import streamlit as st

from src.dashboard.utils.db import *

st.title("🏠 Home Dashboard")

years = get_years()

year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years)-1
)

total_companies = get_total_companies()
avg_roe = get_average_roe(year)
median_de = get_median_de(year)
debt_free = get_debt_free_count(year)
median_npm = get_median_net_profit_margin(year)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Companies", total_companies)

with col2:
    st.metric("Average ROE", f"{avg_roe:.2f}%")

with col3:
    st.metric("Median D/E", f"{median_de:.2f}")

col4, col5 = st.columns(2)

with col4:
    st.metric("Debt-Free", debt_free)

with col5:
    st.metric("Median Net Profit Margin", f"{median_npm:.2f}%")

st.divider()

st.subheader("Sector Distribution")

sector_df = get_sector_breakdown()

st.bar_chart(
    sector_df.set_index("broad_sector")
)

st.divider()

st.subheader("Top 5 Companies")

top_df = get_top_companies(year)

st.dataframe(top_df, width="stretch")