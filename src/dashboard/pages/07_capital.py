import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import *

st.title("Capital Allocation")

# -------------------------
# Company Selection
# -------------------------

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    companies["id"],
    format_func=lambda x: companies.loc[
        companies["id"] == x,
        "company_name"
    ].iloc[0]
)

# -------------------------
# Fetch Data
# -------------------------

df = get_capital_data(selected_company)

# -------------------------
# Latest Year KPIs
# -------------------------

latest = df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Cash From Operations",
    f"{latest['cash_from_operations_cr']:.0f} Cr"
)

c2.metric(
    "Free Cash Flow",
    f"{latest['free_cash_flow_cr']:.0f} Cr"
)

c3.metric(
    "CAPEX",
    f"{latest['capex_cr']:.0f} Cr"
)

c4.metric(
    "Total Debt",
    f"{latest['total_debt_cr']:.0f} Cr"
)

# -------------------------
# Reshape Data
# -------------------------

capital_df = df.melt(
    id_vars="year",
    value_vars=[
        "cash_from_operations_cr",
        "free_cash_flow_cr",
        "capex_cr",
        "total_debt_cr"
    ],
    var_name="Metric",
    value_name="Value"
)

capital_df["Metric"] = capital_df["Metric"].replace({
    "cash_from_operations_cr": "Cash From Operations",
    "free_cash_flow_cr": "Free Cash Flow",
    "capex_cr": "CAPEX",
    "total_debt_cr": "Total Debt"
})

# -------------------------
# Chart
# -------------------------

fig = px.bar(
    capital_df,
    x="year",
    y="Value",
    color="Metric",
    barmode="group",
    title="Capital Allocation Trends"
)

fig.update_layout(
    height=600,
    xaxis_title="Year",
    yaxis_title="Amount (₹ Cr)",
    legend_title="Metric"
)

st.plotly_chart(
    fig,
    width="stretch"
)