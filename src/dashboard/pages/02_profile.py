import streamlit as st

from src.dashboard.utils.db import *

st.title("🏢 Company Profile")


# Company list
companies = get_companies()

company = st.selectbox(
    "Select Company",
    companies["company_name"]
)

# Year selector
years = get_years()

year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years)-1
)

profile = get_company_profile(company)

profile = get_company_profile(company)

if profile.empty:
    st.error("Company data not found.")
    st.stop()

company_data = profile.iloc[0]

st.image(company_data["company_logo"], width=120)

st.subheader(company_data["company_name"])

st.write("**About Company**")
st.write(company_data["about_company"])

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.write("### Company Links")

    st.link_button(
        "🌐 Company Website",
        company_data["website"]
    )

    st.link_button(
        "📈 NSE Profile",
        company_data["nse_profile"]
    )

    st.link_button(
        "📊 BSE Profile",
        company_data["bse_profile"]
    )


with col2:
    st.metric("Face Value", company_data["face_value"])
    st.metric("Book Value", company_data["book_value"])
    st.metric("ROE", f"{company_data['roe_percentage']}%")
    st.metric("ROCE", f"{company_data['roce_percentage']}%")
