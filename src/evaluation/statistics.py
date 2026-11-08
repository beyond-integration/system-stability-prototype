"""Summary statistics and confidence intervals for screening performance."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.evaluation.metrics import binomial_confidence_interval


def summarise_method_stats(summary: pd.DataFrame) -> pd.DataFrame:
    """Append summary columns for confidence intervals and exact numerator/denominator reporting."""
    output = summary.copy()
    output["false_safe_rate_text"] = output.apply(
        lambda row: f"{row['fn']}/{row['fn'] + row['tn']} = {row['false_safe_rate'] * 100:.1f}%" if (row['fn'] + row['tn']) > 0 else "insufficient data",
        axis=1,
    )
    output["risk_capture_text"] = output.apply(
        lambda row: f"{row['tp']}/{row['tp'] + row['fn']} = {row['risk_capture'] * 100:.1f}%" if (row['tp'] + row['fn']) > 0 else "insufficient data",
        axis=1,
    )
    output["coverage_text"] = output.apply(
        lambda row: f"{row['tp'] + row['fp'] + row['tn'] + row['fn']}/{row['tp'] + row['fp'] + row['tn'] + row['fn'] + row['abstentions']} = {row['coverage'] * 100:.1f}%" if row['tp'] + row['fp'] + row['tn'] + row['fn'] + row['abstentions'] > 0 else "insufficient data",
        axis=1,
    )
    return output
