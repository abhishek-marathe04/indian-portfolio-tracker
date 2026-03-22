"""XIRR calculation using Newton-Raphson method.

Phase 1 stub — full implementation in Phase 3.
"""
from __future__ import annotations

from datetime import date
from typing import Sequence


def xirr(cash_flows: Sequence[float], dates: Sequence[date]) -> float | None:
    """Compute the Extended Internal Rate of Return.

    Args:
        cash_flows: Negative for investments (outflows), positive for redemptions / current value.
        dates:      Corresponding dates for each cash flow.

    Returns:
        XIRR as a decimal (e.g. 0.14 for 14%) or None if it cannot converge.
    """
    if len(cash_flows) != len(dates) or len(cash_flows) < 2:
        return None

    try:
        from scipy.optimize import brentq

        base = dates[0]

        def npv(rate: float) -> float:
            return sum(
                cf / (1 + rate) ** ((d - base).days / 365.0)
                for cf, d in zip(cash_flows, dates)
            )

        return brentq(npv, -0.999, 100.0, maxiter=1000)
    except Exception:
        return None
