"""
Financial Ratio Engine
Sprint 2 - Day 10

This module computes CAGR (Compound Annual Growth Rate)
for revenue, net profit and EPS.
"""

from typing import Optional

def calculate_cagr(
    beginning: float,
    ending: float,
    years: int,
) -> tuple[Optional[float], str]:
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



