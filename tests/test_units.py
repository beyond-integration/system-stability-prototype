"""Placeholder tests for units module."""

import math

import pytest

from src.data.units import (
    DAYS_PER_YEAR,
    G,
    M_EARTH,
    M_JUPITER,
    convert_mass_to_solar_mass,
    convert_period_to_years,
    convert_semimajor_axis_to_au,
)


def test_constants_are_documented():
    assert G == 4.0 * math.pi**2
    assert M_JUPITER == pytest.approx(9.54588e-4)
    assert M_EARTH == pytest.approx(3.0035e-6)
    assert DAYS_PER_YEAR == pytest.approx(365.25)


def test_mass_conversion_known_values():
    assert convert_mass_to_solar_mass(1.0, "MJ") == pytest.approx(M_JUPITER)
    assert convert_mass_to_solar_mass(1.0, "ME") == pytest.approx(M_EARTH)
    assert convert_mass_to_solar_mass(1.0, "Msun") == pytest.approx(1.0)


def test_time_and_distance_conversions():
    assert convert_period_to_years(365.25, "days") == pytest.approx(1.0)
    assert convert_semimajor_axis_to_au(1.0, "AU") == pytest.approx(1.0)


def test_invalid_mass_unit_raises_value_error():
    with pytest.raises(ValueError):
        convert_mass_to_solar_mass(1.0, "lbs")
