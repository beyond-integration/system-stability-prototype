"""Placeholder tests for resonance module."""

from src.physics.resonance import resonance_proximity


def test_exact_period_ratio_at_resonance_has_zero_offset():
    result = resonance_proximity(1.0, 4.0 / 3.0)
    assert result["fractional_offset"] == 0.0
    assert result["nearest_resonance"] == 4.0 / 3.0


def test_resonance_offset_is_small_for_nearby_ratio():
    result = resonance_proximity(1.0, 1.34)
    assert result["fractional_offset"] < 0.1
    assert result["resonance_state"] == "NEAR_COMMENSURABILITY_RESONANCE_STATE_UNKNOWN"
