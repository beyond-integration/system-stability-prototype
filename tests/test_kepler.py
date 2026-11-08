"""Placeholder tests for kepler module."""

import pytest
import pandas as pd

from src.physics.amd import system_amd
from src.physics.hill import mutual_hill_separation
from src.physics.kepler import check_kepler_consistency, kepler_a_from_period


def test_kepler_a_from_period_matches_earth_like_orbit():
    a = kepler_a_from_period(1.0, 1.0, 0.0)
    assert a == pytest.approx(1.0)


def test_kepler_consistency_valid_case():
    result = check_kepler_consistency(365.25, 1.0, 1.0, 0.0)
    assert result["status"] in {"VALID", "WARNING"}
    assert result["a_predicted"] == pytest.approx(1.0)
    assert result["epsilon_a"] == pytest.approx(0.0, abs=1e-12)


def test_kepler_consistency_missing_inputs():
    result = check_kepler_consistency(None, 1.0, 1.0, 0.0)
    assert result["status"] == "MISSING_REQUIRED_PARAMETER"


def test_kepler_consistency_warns_on_large_difference():
    result = check_kepler_consistency(365.25, 2.0, 1.0, 0.0)
    assert result["status"] == "WARNING"
    assert result["epsilon_a"] > 0.1


def test_hd_219134_bc_delta_matches_expected_reference():
    df = pd.read_csv("data/processed/hd_219134.csv")
    b = df.iloc[0]
    c = df.iloc[1]
    result = mutual_hill_separation(
        float(b["semimajor_axis_au"]),
        float(c["semimajor_axis_au"]),
        float(b["mass_mj"]) * 9.54588e-4,
        float(c["mass_mj"]) * 9.54588e-4,
        float(b["stellar_mass_msun"]),
    )
    assert result["value"] == pytest.approx(22.73, abs=0.2)


def test_kepler_223_bc_ratio_is_about_4_3():
    df = pd.read_csv("data/processed/kepler_223.csv")
    ratio = float(df.iloc[1]["period_days"]) / float(df.iloc[0]["period_days"])
    assert ratio == pytest.approx(9.84564 / 7.38449, rel=0.02)


def test_data_missing_produces_explicit_unavailable_status():
    result = check_kepler_consistency(None, None, 1.0, 0.0)
    assert result["status"] == "MISSING_REQUIRED_PARAMETER"


def test_increasing_separation_increases_hill_delta():
    low = mutual_hill_separation(1.0, 1.2, 1e-5, 1e-5, 1.0)
    high = mutual_hill_separation(1.0, 1.5, 1e-5, 1e-5, 1.0)
    assert low["value"] < high["value"]


def test_increasing_eccentricity_increases_amd_when_other_params_fixed():
    circular = [{"mass": 1e-5, "semimajor_axis": 1.0, "eccentricity": 0.0, "inclination_rad": 0.0}]
    eccentric = [{"mass": 1e-5, "semimajor_axis": 1.0, "eccentricity": 0.5, "inclination_rad": 0.0}]
    assert system_amd(eccentric, 1.0)["value"] > system_amd(circular, 1.0)["value"]
