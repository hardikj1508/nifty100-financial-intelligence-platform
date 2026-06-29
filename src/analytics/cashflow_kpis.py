"""
Financial Ratio Engine
Sprint 2 - Day 11

Cash Flow KPI calculations.
"""

def free_cash_flow(
    operating_activity: float,
    investing_activity: float
) -> float:
    """
    Calculate Free Cash Flow (FCF).

    Formula:
        Operating Cash Flow + Investing Cash Flow

    Note:
        Investing cash flow is usually negative.
        Negative FCF is allowed.
    """

    return operating_activity + investing_activity

from typing import Optional

def cfo_quality_score(
    cash_from_operations: float,
    net_profit: float
) -> tuple[Optional[float], str]:
    """
    Calculate CFO Quality Score.

    Formula:
        CFO / PAT

    Returns:
        (score, label)

    Labels:
        HIGH_QUALITY : score > 1.0
        MODERATE     : 0.5 <= score <= 1.0
        ACCRUAL_RISK : score < 0.5
        PAT_ZERO     : net_profit == 0
    """

    if net_profit == 0:
        return None, "PAT_ZERO"

    score = cash_from_operations / net_profit

    if score > 1:
        label = "HIGH_QUALITY"
    elif score >= 0.5:
        label = "MODERATE"
    else:
        label = "ACCRUAL_RISK"

    return score, label

from typing import Optional

def capex_intensity(
    investing_activity: float,
    sales: float
) -> tuple[Optional[float], str]:
    """
    Calculate CapEx Intensity.

    Formula:
        abs(Investing Activity) / Sales × 100

    Returns:
        (intensity, label)
    """

    if sales == 0:
        return None, "SALES_ZERO"

    intensity = (abs(investing_activity) / sales) * 100

    if intensity < 3:
        label = "ASSET_LIGHT"
    elif intensity <= 8:
        label = "MODERATE"
    else:
        label = "CAPITAL_INTENSIVE"

    return intensity, label

def fcf_conversion_rate(
    free_cash_flow: float,
    operating_profit: float
) -> Optional[float]:
    """
    Calculate FCF Conversion Rate.

    Formula:
        Free Cash Flow / Operating Profit × 100

    Returns:
        None if operating profit is zero.
    """

    if operating_profit == 0:
        return None

    return (free_cash_flow / operating_profit) * 100

def capital_allocation_pattern(
    operating_activity: float,
    investing_activity: float,
    financing_activity: float
) -> str:
    """
    Classify capital allocation pattern based on
    the signs of CFO, CFI and CFF.
    """

    cfo = operating_activity > 0
    cfi = investing_activity > 0
    cff = financing_activity > 0

    if cfo and not cfi and not cff:
        return "REINVESTOR"

    if cfo and cfi and not cff:
        return "SHAREHOLDER_RETURNS"

    if cfo and cfi and cff:
        return "CASH_ACCUMULATOR"

    if cfo and not cfi and cff:
        return "GROWTH_FUNDED_BY_DEBT"

    if not cfo and cfi and cff:
        return "DISTRESS_SIGNAL"

    if not cfo and not cfi and cff:
        return "PRE_REVENUE"

    if not cfo and cfi and not cff:
        return "LIQUIDATING_ASSETS"

    return "MIXED"