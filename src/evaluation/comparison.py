"""Comparison routines for the four analytical screening methods."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.evaluation.metrics import compute_method_metrics


def compare_screening_methods(results: list[dict[str, Any]]) -> pd.DataFrame:
    """Create a tabular summary for all screening methods using actual per-system classifications."""
    rows = []
    for method_name, entries in results:
        rows.append(compute_method_metrics(method_name, entries))
    return pd.DataFrame(rows)
