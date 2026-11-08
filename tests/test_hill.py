"""Placeholder tests for hill module."""

import pytest

from src.physics.hill import mutual_hill_separation


def test_hill_separation_increases_with_wider_spacing():
    low = mutual_hill_separation(1.0, 1.2, 1e-5, 1e-5, 1.0)
    high = mutual_hill_separation(1.0, 1.5, 1e-5, 1e-5, 1.0)
    assert low["value"] < high["value"]


def test_hill_separation_decreases_with_more_mass():
    small = mutual_hill_separation(1.0, 1.2, 1e-5, 1e-5, 1.0)
    large = mutual_hill_separation(1.0, 1.2, 1e-4, 1e-4, 1.0)
    assert large["value"] < small["value"]


def test_hill_invalid_input_rejected():
    result = mutual_hill_separation(-1.0, 1.2, 1e-5, 1e-5, 1.0)
    assert result["status"] == "INVALID_INPUT"
