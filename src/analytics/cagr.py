"""
Financial Ratio Engine
Sprint 2 - Day 10

This module computes CAGR (Compound Annual Growth Rate)
for revenue, net profit and EPS.
"""



def calculate_cagr(
    beginning: float,
    ending: float,
    years: int,
    required_years: int = 5,
) -> tuple[float | None, str]:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Returns:
        A tuple containing:
        - CAGR value (or None)
        - Status flag
    """

    # Invalid number of years
    if years <= 0:
        return None, "INVALID_PERIOD"

    # Check if the number of years meets the requirement
    if years < required_years:
        return None, "INSUFFICIENT_DATA"

    # Beginning value cannot be zero
    if beginning == 0:
        return None, "ZERO_BASE"

    # Beginning positive, ending negative
    if beginning > 0 and ending < 0:
        return None, "DECLINE_TO_LOSS"

    # Beginning negative, ending positive
    if beginning < 0 and ending > 0:
        return None, "TURNAROUND"

    # Both values negative
    if beginning < 0 and ending < 0:
        return None, "BOTH_NEGATIVE"

    # Normal CAGR calculation
    cagr = ((ending / beginning) ** (1 / years) - 1) * 100
    return cagr, "NORMAL"

def revenue_cagr(
    beginning_revenue: float,
    ending_revenue: float,
    years: int,
) -> tuple[float | None, str]:
    """
    Calculate Revenue CAGR.
    """
    return calculate_cagr(beginning_revenue, ending_revenue, years)

def pat_cagr(
    beginning_pat: float,
    ending_pat: float,
    years: int,
) -> tuple[float | None, str]:
    """
    Calculate PAT (Net Profit) CAGR.
    """
    return calculate_cagr(beginning_pat, ending_pat, years)

def eps_cagr(
    beginning_eps: float,
    ending_eps: float,
    years: int,
) -> tuple[float | None, str]:
    """
    Calculate EPS CAGR.
    """
    return calculate_cagr(beginning_eps, ending_eps, years)



