import sys
from pathlib import Path

import streamlit as st

# Streamlit executes pages from ``src/dashboard``. Add the project root so
# every page can consistently import modules with the ``src.`` prefix.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


st.set_page_config(
    page_title="Nifty100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Nifty100 Analytics Dashboard")

st.markdown("""
Welcome to the Nifty100 Financial Intelligence Platform.

Use the sidebar to navigate between the dashboard pages.
""")
