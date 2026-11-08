"""Mutual Hill radius and separation calculations with explicit assumptions."""

from __future__ import annotations

import math
from typing import Any


def mutual_hill_radius(a1: float, a2: float, m1: float, m2: float, m_star: float) -> float:
    """Return the mutual Hill radius R_H,m for an adjacent pair."""
    if a1 <= 0 or a2 <= 0:
        raise ValueError("Semimajor axes must be positive.")
    if m1 <= 0 or m2 <= 0 or m_star <= 0:
        raise ValueError("Masses must be positive.")
    if a2 <= a1:
        raise ValueError("The outer planet must have the larger semimajor axis.")
    return 0.5 * (a1 + a2) * ((m1 + m2) / (3.0 * m_star)) ** (1.0 / 3.0)


def mutual_hill_separation(a1: float, a2: float, m1: float, m2: float, m_star: float) -> dict[str, Any]:
    """Calculate the mutual Hill separation and return a structured result object."""
    try:
        rhm = mutual_hill_radius(a1, a2, m1, m2, m_star)
    except ValueError as exc:
        return {
            "status": "INVALID_INPUT",
            "value": None,
            "units": None,
            "method": "mutual_hill_separation",
            "assumptions": ["adjacent_pair"],
            "warnings": [str(exc)],
            "source": None,
        }

    delta = (a2 - a1) / rhm
    threshold = 2.0 * math.sqrt(3.0)
    satisfied = delta > threshold

    return {
        "status": "VALID",
        "value": delta,
        "units": "mutual_hill_radii",
        "method": "mutual_hill_separation",
        "assumptions": ["adjacent_pair", "coplanar_baseline", "circular_baseline"],
        "warnings": [],
        "source": None,
        "hill_radius": rhm,
        "threshold": threshold,
        "idealised_hill_criterion_satisfied": satisfied,
        "criterion_scope": (
            "Idealised two-planet circular coplanar Hill criterion; this is not a universal "
            "statement of long-term Lagrange stability for eccentric or multi-planet systems."
        ),
    }
