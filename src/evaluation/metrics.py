"""Evaluation metrics and summaries for screening-method comparison."""

from __future__ import annotations

import math
from typing import Any


def binomial_confidence_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """Return a conservative binomial confidence interval for a proportion."""
    if trials <= 0:
        return (0.0, 1.0)
    if successes < 0 or successes > trials:
        raise ValueError("successes must be between 0 and trials")

    alpha = 1.0 - confidence
    p = successes / trials
    q = 1.0 - p
    if successes == 0:
        lower = 0.0
    else:
        lower = max(0.0, p - 1.96 * math.sqrt(p * q / trials))
    if successes == trials:
        upper = 1.0
    else:
        upper = min(1.0, p + 1.96 * math.sqrt(p * q / trials))
    return (lower, upper)


def confusion_matrix_summary(tp: int, fp: int, fn: int, tn: int) -> dict[str, float]:
    """Return basic confusion-matrix derived metrics."""
    total = tp + fp + fn + tn
    false_safe_rate = (fn / (fn + tn)) if (fn + tn) > 0 else float("nan")
    risk_capture = (tp / (tp + fn)) if (tp + fn) > 0 else float("nan")
    coverage = ((tp + fp + tn + fn) / total) if total > 0 else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "false_safe_rate": false_safe_rate,
        "risk_capture": risk_capture,
        "coverage": coverage,
    }


def compute_method_metrics(method_name: str, class_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarise a screening method using recorded per-system outcomes."""
    tp = sum(1 for item in class_results if item.get("predicted") == "follow_up" and item.get("actual") == "event")
    fp = sum(1 for item in class_results if item.get("predicted") == "follow_up" and item.get("actual") == "no_event")
    fn = sum(1 for item in class_results if item.get("predicted") == "screened" and item.get("actual") == "event")
    tn = sum(1 for item in class_results if item.get("predicted") == "screened" and item.get("actual") == "no_event")
    abstentions = sum(1 for item in class_results if item.get("predicted") == "abstain")
    total = len(class_results)
    classified = total - abstentions
    false_safe_rate = (fn / (fn + tn)) if (fn + tn) > 0 else float("nan")
    risk_capture = (tp / (tp + fn)) if (tp + fn) > 0 else float("nan")
    coverage = (classified / total) if total > 0 else 0.0
    workload_saved = (1.0 - (tp + fp + fn + tn) / total) if total > 0 else 0.0

    ci = binomial_confidence_interval(fn, fn + tn) if (fn + tn) > 0 else (float("nan"), float("nan"))
    return {
        "method": method_name,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "abstentions": abstentions,
        "coverage": coverage,
        "false_safe_rate": false_safe_rate,
        "risk_capture": risk_capture,
        "workload_saved": workload_saved,
        "confidence_interval_95": ci,
    }
