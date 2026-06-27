"""
Financial Ratio Engine
Sprint 2 - Day 8

This module computes profitability ratios for companies.
"""

from typing import Optional

def net_profit_margin(
    net_profit: float,
    sales: float
) -> Optional[float]:
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

def operating_profit_margin(
    operating_profit: float,
    sales: float
) -> Optional[float]:
    """
    Calculate Operating Profit Margin (%)

    Formula:
        (Operating Profit / Sales) * 100

    Returns:
        None if sales is zero.
    """

    if sales == 0:
        return None

    return (operating_profit / sales) * 100

def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
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
) -> Optional[float]:
    """
    Calculate Return on Capital Employed (ROCE)

    Formula:
        EBIT / (Equity Capital + Reserves + Borrowings) * 100

    where:
        EBIT = Operating Profit + Other Income

    Returns:
        None if capital employed is less than or equal to zero.
    """

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
) -> Optional[float]:
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