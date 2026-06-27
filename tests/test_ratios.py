from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity_ratio,
    interest_coverage_ratio,
    net_debt,
    asset_turnover,
)


def test_net_profit_margin():
    result = net_profit_margin(200, 1000)

    assert result == 20

def test_net_profit_margin_zero_sales():
    result = net_profit_margin(200, 0)

    assert result is None

def test_operating_profit_margin():
    result = operating_profit_margin(150, 600)

    assert result == 25

def test_operating_profit_margin_zero_sales():
    result = operating_profit_margin(150, 0)

    assert result is None

def test_return_on_equity():
    result = return_on_equity(
        net_profit=100,
        equity_capital=400,
        reserves=100
    )

    assert result == 20

def test_return_on_equity_negative_equity():
    result = return_on_equity(
        net_profit=100,
        equity_capital=-50,
        reserves=25
    )

    assert result is None

def test_return_on_capital_employed():
    result = return_on_capital_employed(
        operating_profit=100,
        other_income=20,
        equity_capital=400,
        reserves=100,
        borrowings=100
    )

    assert result == 20

def test_return_on_assets():
    result = return_on_assets(
        net_profit=150,
        total_assets=750
    )

    assert result == 20

def test_debt_to_equity_ratio():
    assert debt_to_equity_ratio(500, 1000, 1000) == 0.25

def test_debt_to_equity_ratio_negative_equity():
    assert debt_to_equity_ratio(500, -1000, 500) is None

def test_interest_coverage_ratio():
    assert interest_coverage_ratio(600, 100, 140) == 5.0

def test_interest_coverage_ratio_zero_interest():
    assert interest_coverage_ratio(600, 100, 0) is None

def test_net_debt():
    assert net_debt(500, 120) == 380

def test_net_debt_negative():
    assert net_debt(300, 450) == -150

def test_asset_turnover():
    assert asset_turnover(10000, 5000) == 2.0

def test_asset_turnover_zero_assets():
    assert asset_turnover(10000, 0) is None


    