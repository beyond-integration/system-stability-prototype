"""Near-commensurability diagnostics based on period-ratio proximity."""

from __future__ import annotations

import math
from typing import Any


def resonance_proximity(period_inner: float, period_outer: float, max_order: int = 12) -> dict[str, Any]:
    """Return nearest low-order resonance with the fractional offset from the observed period ratio.

    The function searches integer ratios p:q with 1 <= q < p <= max_order and reports
    the nearest candidate. It does not claim libration or resonance locking without
    resonant-angle information.
    """
    if period_inner <= 0 or period_outer <= 0:
        raise ValueError("Period values must be positive.")
    if period_outer <= period_inner:
        raise ValueError("Outer period must be larger than inner period.")

    r = period_outer / period_inner
    best = None
    best_offset = math.inf
    best_p = None
    best_q = None

    for q in range(1, max_order + 1):
        for p in range(q + 1, max_order + 1):
            ratio = p / q
            offset = abs(r / ratio - 1.0)
            if offset < best_offset:
                best_offset = offset
                best = ratio
                best_p = p
                best_q = q

    if best is None:
        return {
            "status": "INVALID",
            "value": None,
            "units": None,
            "method": "resonance_proximity",
            "warnings": ["No resonance candidates available."],
            "source": None,
        }

    return {
        "status": "VALID",
        "value": best_offset,
        "units": "fractional_offset",
        "method": "resonance_proximity",
        "assumptions": ["near_commensurability_only", "no_libration_proven"],
        "warnings": [],
        "source": None,
        "period_ratio": r,
        "nearest_resonance": best,
        "nearest_resonance_p": best_p,
        "nearest_resonance_q": best_q,
        "resonance_order": best_p - best_q,
        "fractional_offset": best_offset,
        "resonance_state": "NEAR_COMMENSURABILITY_RESONANCE_STATE_UNKNOWN",
    }
