from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)
def test_free_cash_flow():
    assert free_cash_flow(800, -300) == 500

def test_free_cash_flow_negative():
    assert free_cash_flow(600, -900) == -300

def test_cfo_quality_high():
    score, label = cfo_quality_score(1200, 1000)

    assert score == 1.2
    assert label == "HIGH_QUALITY"


def test_cfo_quality_moderate():
    score, label = cfo_quality_score(700, 1000)

    assert score == 0.7
    assert label == "MODERATE"


def test_cfo_quality_accrual_risk():
    score, label = cfo_quality_score(300, 1000)

    assert score == 0.3
    assert label == "ACCRUAL_RISK"


def test_cfo_quality_pat_zero():
    score, label = cfo_quality_score(500, 0)

    assert score is None
    assert label == "PAT_ZERO"

def test_capex_asset_light():
    value, label = capex_intensity(-200, 10000)

    assert value == 2.0
    assert label == "ASSET_LIGHT"


def test_capex_moderate():
    value, label = capex_intensity(-500, 10000)

    assert value == 5.0
    assert label == "MODERATE"


def test_capex_capital_intensive():
    value, label = capex_intensity(-1500, 10000)

    assert value == 15.0
    assert label == "CAPITAL_INTENSIVE"


def test_capex_sales_zero():
    value, label = capex_intensity(-500, 0)

    assert value is None
    assert label == "SALES_ZERO"

def test_fcf_conversion_rate():
    assert fcf_conversion_rate(500, 1000) == 50.0


def test_fcf_conversion_rate_zero_profit():
    assert fcf_conversion_rate(500, 0) is None

def test_pattern_reinvestor():
    assert capital_allocation_pattern(100, -50, -20) == "REINVESTOR"


def test_pattern_shareholder_returns():
    assert capital_allocation_pattern(100, 50, -20) == "SHAREHOLDER_RETURNS"


def test_pattern_cash_accumulator():
    assert capital_allocation_pattern(100, 50, 20) == "CASH_ACCUMULATOR"


def test_pattern_growth_by_debt():
    assert capital_allocation_pattern(100, -50, 20) == "GROWTH_FUNDED_BY_DEBT"


def test_pattern_distress():
    assert capital_allocation_pattern(-100, 50, 20) == "DISTRESS_SIGNAL"


def test_pattern_pre_revenue():
    assert capital_allocation_pattern(-100, -50, 20) == "PRE_REVENUE"


def test_pattern_liquidating_assets():
    assert capital_allocation_pattern(-100, 50, -20) == "LIQUIDATING_ASSETS"


def test_pattern_mixed():
    assert capital_allocation_pattern(-100, -50, -20) == "MIXED"