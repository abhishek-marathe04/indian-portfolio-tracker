from datetime import date

from services.xirr import xirr


def test_xirr_simple_one_year_ten_percent_return():
    # Invest 1000 today, worth 1100 exactly one year later -> ~10% XIRR.
    cash_flows = [-1000.0, 1100.0]
    dates = [date(2025, 1, 1), date(2026, 1, 1)]
    result = xirr(cash_flows, dates)
    assert result is not None
    assert abs(result - 0.10) < 0.005


def test_xirr_multiple_sips_plus_terminal_value():
    # Three monthly SIPs of 1000 each, current value comfortably above total
    # invested -> a positive, finite return.
    cash_flows = [-1000.0, -1000.0, -1000.0, 3200.0]
    dates = [date(2025, 1, 1), date(2025, 2, 1), date(2025, 3, 1), date(2026, 1, 1)]
    result = xirr(cash_flows, dates)
    assert result is not None
    assert result > 0


def test_xirr_returns_none_for_negative_return():
    cash_flows = [-1000.0, 800.0]
    dates = [date(2025, 1, 1), date(2026, 1, 1)]
    result = xirr(cash_flows, dates)
    assert result is not None
    assert result < 0


def test_xirr_returns_none_with_fewer_than_two_cash_flows():
    assert xirr([1000.0], [date(2025, 1, 1)]) is None
    assert xirr([], []) is None


def test_xirr_returns_none_on_mismatched_lengths():
    assert xirr([1.0, 2.0], [date(2025, 1, 1)]) is None


def test_xirr_returns_none_when_no_root_in_bracket():
    # Tiny recent outflows against a huge terminal value implies an
    # astronomically large annualized rate outside the solver's bracket —
    # this must fail gracefully (None), not raise.
    cash_flows = [-100.0, -100.0, 2_000_000.0]
    dates = [date(2026, 7, 1), date(2026, 7, 1), date(2026, 8, 1)]
    assert xirr(cash_flows, dates) is None
