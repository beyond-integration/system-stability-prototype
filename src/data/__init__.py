"""Data loading and validation package placeholder."""

from .units import (
    G,
    M_JUPITER,
    M_EARTH,
    DAYS_PER_YEAR,
    convert_mass_to_solar_mass,
    convert_period_to_years,
    convert_semimajor_axis_to_au,
    convert_to_internal_units,
)
from .load_system import load_planet_table, normalise_planet_table
from .validate_data import (
    REQUIRED_PLANET_COLUMNS,
    validate_planet_row,
    validate_system_table,
    collect_validation_failures,
)

__all__ = [
    "G",
    "M_JUPITER",
    "M_EARTH",
    "DAYS_PER_YEAR",
    "convert_mass_to_solar_mass",
    "convert_period_to_years",
    "convert_semimajor_axis_to_au",
    "convert_to_internal_units",
    "load_planet_table",
    "normalise_planet_table",
    "REQUIRED_PLANET_COLUMNS",
    "validate_planet_row",
    "validate_system_table",
    "collect_validation_failures",
]
