"""Unit conversion routines and documented physical constants for the project.

All calculations are performed in the project's internal units:
- Distance: AU
- Mass: solar masses
- Time: years
- Angles: radians
"""

from __future__ import annotations

import math
from typing import Any

G = 4.0 * math.pi**2

# Mass conversion constants in solar masses.
M_JUPITER = 9.54588e-4
M_EARTH = 3.0035e-6
DAYS_PER_YEAR = 365.25


def convert_mass_to_solar_mass(value: float, unit: str | None = None) -> float:
    """Convert a mass value to solar masses.

    Supported units are explicitly recognised to avoid silent defaults.
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise ValueError("Mass value cannot be None or NaN.")

    if unit is None:
        unit = "Msun"

    unit_norm = unit.strip().lower()
    if unit_norm in {"msun", "solarmass", "m_sun", "sunmass"}:
        return float(value)
    if unit_norm in {"mj", "mjup", "m_jup", "jupiter_mass"}:
        return float(value) * M_JUPITER
    if unit_norm in {"me", "mearth", "m_earth", "earth_mass"}:
        return float(value) * M_EARTH
    if unit_norm in {"kg", "kilogram", "kilograms"}:
        # Conversion factor: 1 Msun = 1.98847e30 kg
        return float(value) / 1.98847e30
    raise ValueError(f"Unsupported mass unit: {unit!r}")


def convert_period_to_years(value: float, unit: str | None = None) -> float:
    """Convert a period to years."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise ValueError("Period value cannot be None or NaN.")

    if unit is None:
        unit = "days"

    unit_norm = unit.strip().lower()
    if unit_norm in {"yr", "year", "years", "y"}:
        return float(value)
    if unit_norm in {"day", "days", "d"}:
        return float(value) / DAYS_PER_YEAR
    if unit_norm in {"hour", "hours", "h"}:
        return float(value) / (24.0 * DAYS_PER_YEAR)
    if unit_norm in {"s", "sec", "second", "seconds"}:
        return float(value) / (86400.0 * DAYS_PER_YEAR)
    raise ValueError(f"Unsupported period unit: {unit!r}")


def convert_semimajor_axis_to_au(value: float, unit: str | None = None) -> float:
    """Convert a semimajor axis to AU."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise ValueError("Semimajor axis value cannot be None or NaN.")

    if unit is None:
        unit = "AU"

    unit_norm = unit.strip().lower()
    if unit_norm in {"au", "astronomicalunit", "astronomical_unit"}:
        return float(value)
    if unit_norm in {"m", "meter", "meters", "metre", "metres"}:
        return float(value) / 1.495978707e11
    if unit_norm in {"km", "kilometer", "kilometres", "kilometres"}:
        return float(value) / 1.495978707e8
    if unit_norm in {"pc", "parsec", "parsecs"}:
        return float(value) * 206264.806247
    raise ValueError(f"Unsupported semimajor-axis unit: {unit!r}")


def convert_to_internal_units(row: dict[str, Any]) -> dict[str, Any]:
    """Convert a row of orbital data to the internal project units.

    The function keeps the original source values and only adds internal-unit fields,
    while preserving the raw inputs in their original units.
    """
    converted = dict(row)

    # Keep original values as provided; only add converted copies.
    if "mass_mj" in row and row["mass_mj"] is not None:
        converted["mass_msun"] = convert_mass_to_solar_mass(float(row["mass_mj"]), "MJ")
    if "stellar_mass_msun" in row and row["stellar_mass_msun"] is not None:
        converted["stellar_mass_msun_internal"] = float(row["stellar_mass_msun"])
    if "period_days" in row and row["period_days"] is not None:
        converted["period_years"] = convert_period_to_years(float(row["period_days"]), "days")
    if "semimajor_axis_au" in row and row["semimajor_axis_au"] is not None:
        converted["semimajor_axis_au_internal"] = float(row["semimajor_axis_au"])
    if "eccentricity" in row and row["eccentricity"] is not None:
        converted["eccentricity_internal"] = float(row["eccentricity"])
    if "inclination_deg" in row and row["inclination_deg"] is not None:
        converted["inclination_rad"] = math.radians(float(row["inclination_deg"]))
    if "longitude_node_deg" in row and row["longitude_node_deg"] is not None:
        converted["longitude_node_rad"] = math.radians(float(row["longitude_node_deg"]))
    if "argument_of_periapsis_deg" in row and row["argument_of_periapsis_deg"] is not None:
        converted["argument_of_periapsis_rad"] = math.radians(float(row["argument_of_periapsis_deg"]))
    if "mean_anomaly_deg" in row and row["mean_anomaly_deg"] is not None:
        converted["mean_anomaly_rad"] = math.radians(float(row["mean_anomaly_deg"]))

    return converted
