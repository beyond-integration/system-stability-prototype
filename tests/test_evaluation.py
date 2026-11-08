"""Tests for evaluation metrics and screening comparisons."""

from __future__ import annotations

from src.evaluation.metrics import compute_method_metrics


def test_method_metrics_return_expected_counts():
    entries = [
        {"predicted": "follow_up", "actual": "event"},
        {"predicted": "follow_up", "actual": "no_event"},
        {"predicted": "screened", "actual": "event"},
        {"predicted": "screened", "actual": "no_event"},
    ]
    result = compute_method_metrics("test_method", entries)
    assert result["tp"] == 1
    assert result["fp"] == 1
    assert result["fn"] == 1
    assert result["tn"] == 1
    assert result["false_safe_rate"] == 1.0 / 2.0
    assert result["risk_capture"] == 1.0 / 2.0


def test_evaluation_metrics_include_real_sample_counts_in_text_fields():
    entries = [
        {"predicted": "follow_up", "actual": "event"},
        {"predicted": "follow_up", "actual": "event"},
        {"predicted": "screened", "actual": "event"},
        {"predicted": "screened", "actual": "no_event"},
    ]
    result = compute_method_metrics("risk_test", entries)
    assert result["tp"] == 2
    assert result["fn"] == 1
    assert result["tn"] == 1
    assert result["false_safe_rate"] == 1.0 / 2.0
    assert result["risk_capture"] == 2.0 / 3.0
