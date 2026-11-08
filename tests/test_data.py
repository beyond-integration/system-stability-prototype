"""Placeholder tests for data-loading and validation modules."""

import pandas as pd

from src.data.validate_data import validate_planet_row, validate_system_table


def test_validate_planet_row_rejects_missing_required_column_data():
    row = {
        "system_name": "Example",
        "planet_name": "b",
        "period_days": 10.0,
        "period_unc_days": None,
        "semimajor_axis_au": 0.1,
        "semimajor_axis_unc_au": 0.001,
        "mass_mj": 0.05,
        "mass_unc_mj": 0.005,
        "eccentricity": 0.01,
        "ecc_unc": 0.005,
        "stellar_mass_msun": 1.0,
        "stellar_mass_unc_msun": 0.02,
        "source": "reference",
    }
    result = validate_planet_row(row)
    assert result["status"] == "INVALID"
    assert "period_unc_days" in result["missing"]


def test_validate_planet_row_rejects_negative_or_over_limit_eccentricity():
    row = {
        "system_name": "Example",
        "planet_name": "b",
        "period_days": 10.0,
        "period_unc_days": 0.01,
        "semimajor_axis_au": 0.1,
        "semimajor_axis_unc_au": 0.001,
        "mass_mj": 0.05,
        "mass_unc_mj": 0.005,
        "eccentricity": 1.2,
        "ecc_unc": 0.005,
        "stellar_mass_msun": 1.0,
        "stellar_mass_unc_msun": 0.02,
        "source": "reference",
    }
    result = validate_planet_row(row)
    assert "eccentricity must be less than 1" in result["errors"]


def test_validate_system_table_flags_duplicate_planets_and_unsorted_axes():
    df = pd.DataFrame(
        [
            {
                "system_name": "Example",
                "planet_name": "b",
                "period_days": 10.0,
                "period_unc_days": 0.01,
                "semimajor_axis_au": 0.3,
                "semimajor_axis_unc_au": 0.001,
                "mass_mj": 0.05,
                "mass_unc_mj": 0.005,
                "eccentricity": 0.01,
                "ecc_unc": 0.005,
                "stellar_mass_msun": 1.0,
                "stellar_mass_unc_msun": 0.02,
                "source": "reference",
            },
            {
                "system_name": "Example",
                "planet_name": "b",
                "period_days": 15.0,
                "period_unc_days": 0.02,
                "semimajor_axis_au": 0.1,
                "semimajor_axis_unc_au": 0.001,
                "mass_mj": 0.06,
                "mass_unc_mj": 0.006,
                "eccentricity": 0.02,
                "ecc_unc": 0.005,
                "stellar_mass_msun": 1.0,
                "stellar_mass_unc_msun": 0.02,
                "source": "reference",
            },
        ]
    )
    result = validate_system_table(df)
    assert result["status"] == "INVALID"
    assert any("duplicate planet_name" in issue for issue in result["invalid_fields"])
