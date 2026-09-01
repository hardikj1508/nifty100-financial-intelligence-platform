import pandas as pd

from src.dq.rules import (
    dq_01_missing_primary_keys,
    dq_02_duplicate_primary_keys,
    dq_03_invalid_company_ids,
    dq_04_balance_sheet_percent_mismatch,
    dq_05_negative_financial_values,
    dq_06_missing_critical_values,
    dq_07_balance_sheet_absolute_mismatch,
    dq_08_operating_profit_margin_mismatch,
    dq_09_invalid_sales,
    dq_10_invalid_market_cap,
    dq_11_missing_net_profit,
    dq_12_missing_eps,
    dq_13_invalid_market_cap_year,
    dq_14_duplicate_company_year,
)


def test_dq_01_missing_primary_key():
    assert dq_01_missing_primary_keys({"Companies": pd.DataFrame({"id": [1, None]})})[0]["rule"] == "DQ_01"


def test_dq_02_duplicate_primary_key():
    assert dq_02_duplicate_primary_keys({"Companies": pd.DataFrame({"id": [1, 1]})})[0]["rule"] == "DQ_02"


def test_dq_03_invalid_company_id():
    assert dq_03_invalid_company_ids({"Cash Flow": pd.DataFrame({"company_id": [9]})}, {1})[0]["rule"] == "DQ_03"


def test_dq_04_balance_sheet_percent_mismatch():
    assert dq_04_balance_sheet_percent_mismatch(pd.DataFrame({"total_assets": [100], "total_liabilities": [90]}))[0]["rule"] == "DQ_04"


def test_dq_05_negative_financial_value():
    assert dq_05_negative_financial_values({"Profit & Loss": pd.DataFrame({"sales": [-1]})})[0]["rule"] == "DQ_05"


def test_dq_06_missing_critical_value():
    assert dq_06_missing_critical_values({"Profit & Loss": pd.DataFrame({"net_profit": [None]})})[0]["rule"] == "DQ_06"


def test_dq_07_balance_sheet_absolute_mismatch():
    assert dq_07_balance_sheet_absolute_mismatch(pd.DataFrame({"total_assets": [100], "total_liabilities": [95]}))[0]["rule"] == "DQ_07"


def test_dq_08_operating_profit_margin_mismatch():
    source = pd.DataFrame({"company_id": [1], "year": [2024], "sales": [100], "operating_profit": [20]})
    ratios = pd.DataFrame({"company_id": [1], "year": [2024], "operating_profit_margin_pct": [10]})
    assert dq_08_operating_profit_margin_mismatch(source, ratios)[0]["rule"] == "DQ_08"


def test_dq_09_invalid_sales():
    assert dq_09_invalid_sales(pd.DataFrame({"sales": [0]}))[0]["rule"] == "DQ_09"


def test_dq_10_invalid_market_cap():
    assert dq_10_invalid_market_cap(pd.DataFrame({"market_cap_crore": [None]}))[0]["rule"] == "DQ_10"


def test_dq_11_missing_net_profit():
    assert dq_11_missing_net_profit(pd.DataFrame({"net_profit": [None]}))[0]["rule"] == "DQ_11"


def test_dq_12_missing_eps():
    assert dq_12_missing_eps(pd.DataFrame({"eps": [None]}))[0]["rule"] == "DQ_12"


def test_dq_13_invalid_market_cap_year():
    assert dq_13_invalid_market_cap_year(pd.DataFrame({"year": [1999]}))[0]["rule"] == "DQ_13"


def test_dq_14_duplicate_company_year():
    frame = pd.DataFrame({"company_id": [1, 1], "year": [2024, 2024]})
    assert dq_14_duplicate_company_year(frame)[0]["rule"] == "DQ_14"
