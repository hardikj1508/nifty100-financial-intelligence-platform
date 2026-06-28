from src.analytics.cagr import (
    calculate_cagr,
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)

def test_normal_cagr():
    value, flag = calculate_cagr(100, 200, 5)

    assert round(value, 2) == 14.87
    assert flag == "NORMAL"


def test_zero_base():
    value, flag = calculate_cagr(0, 200, 5)

    assert value is None
    assert flag == "ZERO_BASE"


def test_turnaround():
    value, flag = calculate_cagr(-100, 200, 5)

    assert value is None
    assert flag == "TURNAROUND"


def test_decline_to_loss():
    value, flag = calculate_cagr(100, -50, 5)

    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():
    value, flag = calculate_cagr(-100, -50, 5)

    assert value is None
    assert flag == "BOTH_NEGATIVE"


def test_invalid_period():
    value, flag = calculate_cagr(100, 200, 0)

    assert value is None
    assert flag == "INVALID_PERIOD"

def test_revenue_cagr():
    value, flag = revenue_cagr(100, 200, 5)

    assert round(value, 2) == 14.87
    assert flag == "NORMAL"


def test_pat_cagr():
    value, flag = pat_cagr(80, 160, 5)

    assert round(value, 2) == 14.87
    assert flag == "NORMAL"


def test_eps_cagr():
    value, flag = eps_cagr(10, 20, 5)

    assert round(value, 2) == 14.87
    assert flag == "NORMAL"

def test_insufficient_data():
    value, flag = calculate_cagr(100, 150, 3)

    assert value is None
    assert flag == "INSUFFICIENT_DATA"