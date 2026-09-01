import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import *

st.title("Financial Trends")

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    companies["id"],
    format_func=lambda x: companies.loc[
        companies["id"] == x,
        "company_name"
    ].iloc[0]
)

df = get_trend_data(selected_company)

metric_options = {
    "Net Profit Margin": "net_profit_margin_pct",
    "Operating Profit Margin": "operating_profit_margin_pct",
    "Return on Equity": "return_on_equity_pct",
    "Debt to Equity": "debt_to_equity",
    "Interest Coverage": "interest_coverage",
    "Asset Turnover": "asset_turnover",
    "Earnings Per Share": "earnings_per_share",
    "Book Value Per Share": "book_value_per_share"
}

selected_metrics = st.multiselect(
    "Select up to 3 metrics",
    options=list(metric_options.keys()),
    default=["Net Profit Margin"],
    max_selections=3
)

if selected_metrics:

    fig = px.line(
        df,
        x="year",
        y=[metric_options[m] for m in selected_metrics],
        markers=True
    )

    fig.update_layout(
        title="Financial Trends",
        xaxis_title="Year",
        yaxis_title="Value",
        legend_title="Metrics"
    )

    st.plotly_chart(fig, use_container_width=True)