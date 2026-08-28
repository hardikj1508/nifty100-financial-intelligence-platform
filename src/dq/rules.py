"""Import-safe data-quality rules for the processed financial datasets."""

from collections.abc import Mapping

import pandas as pd


def _failure(table: str, rule: str, row: int, issue: str) -> dict:
    return {"table": table, "rule": rule, "row": row, "issue": issue}


def dq_01_missing_primary_keys(datasets: Mapping[str, pd.DataFrame]) -> list[dict]:
    return [
        _failure(name, "DQ_01", row, "Missing Primary Key")
        for name, df in datasets.items() if "id" in df
        for row in df.index[df["id"].isna()]
    ]


def dq_02_duplicate_primary_keys(datasets: Mapping[str, pd.DataFrame]) -> list[dict]:
    return [
        _failure(name, "DQ_02", row, "Duplicate Primary Key")
        for name, df in datasets.items() if "id" in df
        for row in df.index[df["id"].duplicated()]
    ]


def dq_03_invalid_company_ids(child_tables: Mapping[str, pd.DataFrame], company_ids: set) -> list[dict]:
    return [
        _failure(name, "DQ_03", row, f"Invalid company_id: {df.at[row, 'company_id']}")
        for name, df in child_tables.items() if "company_id" in df
        for row in df.index[~df["company_id"].isin(company_ids)]
    ]


def dq_04_balance_sheet_percent_mismatch(balancesheet: pd.DataFrame, tolerance_pct: float = 1) -> list[dict]:
    assets = pd.to_numeric(balancesheet["total_assets"], errors="coerce")
    liabilities = pd.to_numeric(balancesheet["total_liabilities"], errors="coerce")
    mismatch = (assets - liabilities).abs() / assets.replace(0, pd.NA) * 100 > tolerance_pct
    return [_failure("Balance Sheet", "DQ_04", row, "Balance Sheet mismatch > 1%") for row in balancesheet.index[mismatch]]


def dq_05_negative_financial_values(child_tables: Mapping[str, pd.DataFrame], columns: tuple[str, ...] = ("sales", "market_cap_crore")) -> list[dict]:
    failures = []
    for name, df in child_tables.items():
        for column in columns:
            if column in df:
                for row in df.index[pd.to_numeric(df[column], errors="coerce") < 0]:
                    failures.append(_failure(name, "DQ_05", row, f"Negative value in {column}: {df.at[row, column]}"))
    return failures


def dq_06_missing_critical_values(child_tables: Mapping[str, pd.DataFrame], columns: tuple[str, ...] = ("sales", "net_profit", "market_cap_crore")) -> list[dict]:
    return [
        _failure(name, "DQ_06", row, f"Missing value in {column}")
        for name, df in child_tables.items() for column in columns if column in df
        for row in df.index[df[column].isna()]
    ]


def dq_07_balance_sheet_absolute_mismatch(balancesheet: pd.DataFrame, tolerance: float = 1) -> list[dict]:
    assets = pd.to_numeric(balancesheet["total_assets"], errors="coerce")
    liabilities = pd.to_numeric(balancesheet["total_liabilities"], errors="coerce")
    mismatch = (assets - liabilities).abs() > tolerance
    return [_failure("Balance Sheet", "DQ_07", row, "Assets and liabilities differ") for row in balancesheet.index[mismatch]]


def dq_08_operating_profit_margin_mismatch(profitandloss: pd.DataFrame, financial_ratios: pd.DataFrame, tolerance_pct: float = 1) -> list[dict]:
    source = profitandloss[["company_id", "year", "sales", "operating_profit"]]
    ratios = financial_ratios[["company_id", "year", "operating_profit_margin_pct"]]
    merged = source.merge(ratios, on=["company_id", "year"], how="inner")
    mismatch = ((merged["operating_profit"] / merged["sales"] * 100) - merged["operating_profit_margin_pct"]).abs() > tolerance_pct
    return [_failure("Financial Ratios", "DQ_08", row, "OPM mismatch") for row in merged.index[mismatch]]


def dq_09_invalid_sales(profitandloss: pd.DataFrame) -> list[dict]:
    sales = pd.to_numeric(profitandloss["sales"], errors="coerce")
    return [_failure("Profit & Loss", "DQ_09", row, "Invalid sales value") for row in profitandloss.index[(sales <= 0) | sales.isna()]]


def dq_10_invalid_market_cap(market_cap: pd.DataFrame) -> list[dict]:
    values = pd.to_numeric(market_cap["market_cap_crore"], errors="coerce")
    return [_failure("Market Cap", "DQ_10", row, "Invalid market cap") for row in market_cap.index[(values <= 0) | values.isna()]]


def dq_11_missing_net_profit(profitandloss: pd.DataFrame) -> list[dict]:
    return [_failure("Profit & Loss", "DQ_11", row, "Missing net profit") for row in profitandloss.index[profitandloss["net_profit"].isna()]]


def dq_12_missing_eps(profitandloss: pd.DataFrame) -> list[dict]:
    return [_failure("Profit & Loss", "DQ_12", row, "Missing EPS") for row in profitandloss.index[profitandloss["eps"].isna()]]


def dq_13_invalid_market_cap_year(market_cap: pd.DataFrame, minimum_year: int = 2000, maximum_year: int = 2025) -> list[dict]:
    years = pd.to_numeric(market_cap["year"], errors="coerce")
    invalid = (years < minimum_year) | (years > maximum_year) | years.isna()
    return [_failure("Market Cap", "DQ_13", row, "Invalid year") for row in market_cap.index[invalid]]


def dq_14_duplicate_company_year(profitandloss: pd.DataFrame) -> list[dict]:
    duplicates = profitandloss.duplicated(subset=["company_id", "year"])
    return [_failure("Profit & Loss", "DQ_14", row, "Duplicate company-year") for row in profitandloss.index[duplicates]]
