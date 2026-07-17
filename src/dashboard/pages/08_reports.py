import streamlit as st

from src.dashboard.utils.db import *

st.title("Reports & Resources")

# -------------------------
# Company Selection
# -------------------------

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    companies["id"],
    format_func=lambda x:
        companies.loc[
            companies["id"] == x,
            "company_name"
        ].iloc[0]
)

# -------------------------
# Fetch Report Data
# -------------------------

df = get_company_reports(selected_company)

report = df.iloc[0]

# -------------------------
# Company Information
# -------------------------

st.subheader(report["company_name"])

st.write("### Useful Links")

col1, col2, col3 = st.columns(3)

with col1:
    st.link_button(
        "🌐 Company Website",
        report["website"]
    )

with col2:
    st.link_button(
        "📈 NSE Profile",
        report["nse_profile"]
    )

with col3:
    st.link_button(
        "📊 BSE Profile",
        report["bse_profile"]
    )

# -------------------------
# Information
# -------------------------

st.info(
    """
These links provide quick access to:

• Official Company Website

• NSE Company Profile

• BSE Company Profile

You can use these resources to access annual reports,
financial statements, investor presentations and other
company disclosures.
"""
)