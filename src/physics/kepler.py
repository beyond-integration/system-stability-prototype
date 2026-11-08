"""Kepler consistency checks and derived semimajor-axis calculations."""

from __future__ import annotations

import math
from typing import Any

from src.data.units import G


def kepler_period_from_a(a_au: float, stellar_mass_msun: float, planet_mass_msun: float = 0.0) -> float:
    """Return the orbital period in years for a circular orbit in AU, Msun, year units."""
    total_mass = stellar_mass_msun + planet_mass_msun
    if total_mass <= 0:
        raise ValueError("Total mass must be positive.")
    if a_au <= 0:
        raise ValueError("Semimajor axis must be positive.")
    return math.sqrt((a_au**3) / (G / (4.0 * math.pi**2) * total_mass))


def kepler_a_from_period(period_years: float, stellar_mass_msun: float, planet_mass_msun: float = 0.0) -> float:
    """Return the semimajor axis implied by a Keplerian period and mass."""
    total_mass = stellar_mass_msun + planet_mass_msun
    if total_mass <= 0:
        raise ValueError("Total mass must be positive.")
    if period_years <= 0:
        raise ValueError("Period must be positive.")
    return (total_mass * (period_years**2)) ** (1.0 / 3.0)


def check_kepler_consistency(
    period_days: float | None,
    semimajor_axis_au: float | None,
    stellar_mass_msun: float | None,
    planet_mass_msun: float | None = 0.0,
) -> dict[str, Any]:
    """Compare observed semimajor axis with the value implied by the period.

    Returns a structured result exposing status, value, units, warnings, and the
    relative fractional error.
    """
    if period_days is None or semimajor_axis_au is None or stellar_mass_msun is None:
        return {
            "status": "MISSING_REQUIRED_PARAMETER",
            "value": None,
            "units": None,
            "method": "kepler_consistency",
            "warnings": ["Required orbital inputs are missing."],
            "epsilon_a": None,
            "a_observed": semimajor_axis_au,
            "a_predicted": None,
        }

    period_years = period_days / 365.25
    a_predicted = kepler_a_from_period(period_years, stellar_mass_msun, planet_mass_msun)
    epsilon_a = abs(semimajor_axis_au - a_predicted) / a_predicted

    status = "VALID"
    warnings: list[str] = []
    if epsilon_a > 0.1:
        warnings.append("Observed semimajor axis differs materially from the Keplerian prediction.")
        status = "WARNING"

    return {
        "status": status,
        "value": epsilon_a,
        "units": "fractional_difference",
        "method": "kepler_consistency",
        "warnings": warnings,
        "epsilon_a": epsilon_a,
        "a_observed": semimajor_axis_au,
        "a_predicted": a_predicted,
    }
