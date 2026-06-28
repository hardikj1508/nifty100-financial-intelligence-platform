from src.analytics.cagr import calculate_cagr

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