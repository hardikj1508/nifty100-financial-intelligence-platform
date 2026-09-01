"""
Financial Ratio Engine
Sprint 2 - Day 8

This module computes profitability ratios for companies.
"""



def net_profit_margin(
    net_profit: float,
    sales: float
) -> float | None:
    """
    Calculate Net Profit Margin (%)

    Formula:
        (Net Profit / Sales) * 100

    Returns:
        None if sales is zero.
    """

    if sales == 0:
        return None

    return (net_profit / sales) * 100

def operating_profit_margin(operating_profit, sales):
    if operating_profit is None or sales is None:
        return None

    if sales == 0:
        return None

    return (operating_profit / sales) * 100

def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> float | None:
    """
    Calculate Return on Equity (ROE)

    Formula:
        Net Profit / (Equity Capital + Reserves) * 100

    Returns:
        None if total equity is less than or equal to zero.
    """

    total_equity = equity_capital + reserves

    if total_equity <= 0:
        return None

    return (net_profit / total_equity) * 100

def return_on_capital_employed(
    operating_profit: float,
    other_income: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> float | None:
    """
    Calculate Return on Capital Employed (ROCE)

    Formula:
        EBIT / (Equity Capital + Reserves + Borrowings) * 100

    where:
        EBIT = Operating Profit + Other Income

    Returns:
        None if capital employed is less than or equal to zero.
    """


    if (
        operating_profit is None
        or other_income is None
        or equity_capital is None
        or reserves is None
        or borrowings is None
    ):
        return None

    ebit = operating_profit + other_income
    
    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100

def return_on_assets(
    net_profit: float,
    total_assets: float
) -> float | None:
    """
    Calculate Return on Assets (ROA)

    Formula:
        (Net Profit / Total Assets) * 100

    Returns:
        None if total assets is zero.
    """

    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100

def debt_to_equity_ratio(
    borrowings: float,
    equity_capital: float,
    reserves: float
) -> float | None:
    """
    Calculate Debt-to-Equity Ratio.

    Formula:
        Total Borrowings / (Equity Capital + Reserves)

    Returns:
        None if total equity is less than or equal to zero.
    """

    total_equity = equity_capital + reserves

    if total_equity <= 0:
        return None

    return borrowings / total_equity

def interest_coverage_ratio(
    operating_profit: float,
    other_income: float,
    interest: float
) -> float | None:
    """
    Calculate Interest Coverage Ratio (ICR).

    Formula:
        (Operating Profit + Other Income) / Interest

    Returns:
        None if interest is zero.
    """

    if interest == 0:
        return None

    ebit = operating_profit + other_income

    return ebit / interest

def net_debt(
    borrowings: float,
    investments: float
) -> float:
    """
    Calculate Net Debt.

    Formula:
        Borrowings - Investments

    Returns:
        Net Debt (can be negative).
    """

    return borrowings - investments

def asset_turnover(
    sales: float,
    total_assets: float
) -> float | None:
    """
    Calculate Asset Turnover Ratio.

    Formula:
        Sales / Total Assets

    Returns:
        None if total assets is zero.
    """

    if total_assets == 0:
        return None

    return sales / total_assets