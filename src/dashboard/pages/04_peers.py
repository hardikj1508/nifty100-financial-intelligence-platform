import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils.db import *

st.title("Peer Comparison")

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    companies["id"],
    format_func=lambda x: companies.loc[
        companies["id"] == x,
        "company_name"
    ].iloc[0]
)

year = st.selectbox(
    "Year",
    [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024"
    ]
)

df = get_peer_comparison(selected_company, year)

st.dataframe(df, use_container_width=True)

company = df[df["company_name"] ==
    companies.loc[
        companies["id"] == selected_company,
        "company_name"
    ].iloc[0]
]

peer_avg = get_peer_average(
    selected_company,
    year
)

metrics = [
    "return_on_equity_pct",
    "debt_to_equity",
    "net_profit_margin_pct",
    "earnings_per_share"
]

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company[metrics].iloc[0],
        theta=metrics,
        fill="toself",
        name="Selected Company"
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_avg[metrics].iloc[0],
        theta=metrics,
        fill="toself",
        name="Peer Average"
    )
)

fig.update_layout(
    title="Company vs Peer Average",
    polar={
        "radialaxis": {
            "visible":True
        }
    },
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

