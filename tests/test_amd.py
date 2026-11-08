"""Placeholder tests for amd module."""

import math

import pytest

from src.physics.amd import system_amd


def test_amd_zero_for_circular_coplanar_system():
    planets = [
        {"mass": 1e-5, "semimajor_axis": 1.0, "eccentricity": 0.0, "inclination_rad": 0.0},
        {"mass": 1e-5, "semimajor_axis": 1.5, "eccentricity": 0.0, "inclination_rad": 0.0},
    ]
    result = system_amd(planets, 1.0)
    assert result["value"] == pytest.approx(0.0, abs=1e-12)


def test_amd_increases_with_eccentricity():
    circular = [
        {"mass": 1e-5, "semimajor_axis": 1.0, "eccentricity": 0.0, "inclination_rad": 0.0},
    ]
    eccentric = [
        {"mass": 1e-5, "semimajor_axis": 1.0, "eccentricity": 0.5, "inclination_rad": 0.0},
    ]
    assert system_amd(eccentric, 1.0)["value"] > system_amd(circular, 1.0)["value"]


def test_amd_rejects_invalid_eccentricity():
    planets = [{"mass": 1e-5, "semimajor_axis": 1.0, "eccentricity": 1.0, "inclination_rad": 0.0}]
    with pytest.raises(ValueError):
        system_amd(planets, 1.0)
