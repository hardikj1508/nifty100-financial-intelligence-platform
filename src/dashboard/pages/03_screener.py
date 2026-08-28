import streamlit as st

from src.dashboard.utils.api import fetch_screener, screener_dataframe

st.title("📈 Stock Screener")

min_roe = st.sidebar.number_input(
    "Minimum ROE (%)",
    min_value=0.0,
    value=0.0,
    step=1.0,
)

try:
    payload = fetch_screener(min_roe=min_roe or None)
    dataframe = screener_dataframe(payload)

    st.subheader(f"Showing {payload['count']} Companies")
    st.dataframe(dataframe, width="stretch", hide_index=True)
except OSError:
    st.error(
        "The API is unavailable. Start it with: "
        "uvicorn src.api.main:app --reload --port 8001"
    )
