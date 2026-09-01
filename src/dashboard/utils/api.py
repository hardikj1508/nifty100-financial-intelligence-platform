"""Small API adapter used by the Streamlit dashboard."""

import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

API_BASE_URL = os.getenv("NIFTY_API_BASE_URL", "http://127.0.0.1:8000/api/v1")


def fetch_screener(min_roe: float | None = None) -> dict:
    """Fetch screener results from the local FastAPI service."""
    parameters = {}
    if min_roe is not None:
        parameters["min_roe"] = min_roe

    url = f"{API_BASE_URL}/screener"
    if parameters:
        url = f"{url}?{urlencode(parameters)}"

    with urlopen(url, timeout=10) as response:
        return json.load(response)


def screener_dataframe(payload: dict) -> pd.DataFrame:
    """Convert the API payload into the table displayed in Streamlit."""
    return pd.DataFrame(payload["companies"])
