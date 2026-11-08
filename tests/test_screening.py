"""Tests for the screening decision engine."""

from __future__ import annotations

from src.screening.decision import decide_screening


def test_decide_screening_abstains_for_invalid_inputs():
    result = decide_screening({"required_parameters_valid": False, "warnings": ["missing mass"]})
    assert result["decision"] == "ABSTAIN_INSUFFICIENT_INFORMATION"
    assert result["status"] == "ABSTAIN"


def test_decide_screening_follows_up_when_hill_or_amd_fail():
    hill = {"criterion_satisfied": False}
    amd = {"criterion_status": "NUMERICAL_FOLLOW_UP"}
    result = decide_screening({"required_parameters_valid": True}, hill=hill, amd=amd, resonance={"fractional_offset": 0.5})
    assert result["decision"] == "NUMERICAL_FOLLOW_UP_REQUIRED"
    assert result["status"] == "INVESTIGATE"


def test_decide_screening_screenable_when_checks_pass():
    result = decide_screening({"required_parameters_valid": True}, hill={"criterion_satisfied": True}, amd={"criterion_status": "VALID"}, resonance={"fractional_offset": 0.12})
    assert result["decision"] == "SCREENABLE_UNDER_TESTED_CRITERIA"
    assert result["status"] == "VALID"


def test_decide_screening_records_reason_traceability():
    result = decide_screening(
        {"required_parameters_valid": True},
        hill={"criterion_satisfied": False},
        amd={"criterion_status": "VALID"},
        resonance={"fractional_offset": 0.02},
    )
    assert "hill_threshold_breach" in result["reasons"] or "near_commensurability" in result["reasons"]
    assert result["details"]
