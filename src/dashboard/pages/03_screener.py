import streamlit as st

from src.dashboard.utils.db import *

st.title("📈 Stock Screener")

# Year selector
years = get_years()

year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years)-1
)

# Load data
df = get_screener_data(year)

st.subheader(f"Showing {len(df)} Companies")

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)