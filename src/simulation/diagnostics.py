"""Scientific diagnostics helpers for stability simulations."""

from __future__ import annotations

from typing import Any

import numpy as np


def compute_convergence_summary(simulation_data: dict[str, Any]) -> dict[str, Any]:
    """Summarise numerical convergence diagnostics from a simulation result.

    The function is intentionally light-weight and deterministic: it checks the energy and
    angular-momentum drift, the time-step scale, and whether the integration ended normally.
    """
    status = simulation_data.get("status", "unknown")
    diagnostics = simulation_data.get("diagnostics", {})

    energy_drift = float(diagnostics.get("energy_drift", np.nan))
    angular_momentum_drift = float(diagnostics.get("angular_momentum_drift", np.nan))
    time_step = float(diagnostics.get("time_step", np.nan))
    relative_duration = float(diagnostics.get("relative_duration", np.nan))

    return {
        "status": status,
        "energy_drift": energy_drift,
        "angular_momentum_drift": angular_momentum_drift,
        "time_step": time_step,
        "relative_duration": relative_duration,
        "stable": status in {"stable", "long_term_stable"},
        "warning": bool(np.isnan(energy_drift) or np.isnan(angular_momentum_drift)),
    }


def summarise_event_counts(events: list[dict[str, Any]] | None) -> dict[str, int]:
    """Count event classes for reporting."""
    counts = {"close_encounter": 0, "ejection": 0, "stellar_collision": 0, "other": 0}
    if not events:
        return counts

    for event in events:
        kind = str(event.get("type", "other")).strip().lower()
        if kind in counts:
            counts[kind] += 1
        else:
            counts["other"] += 1
    return counts


def validate_step_convergence(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Check whether a sequence of simulations converges on a consistent outcome."""
    if not results:
        return {"n_runs": 0, "all_consistent": False, "status_counts": {}}

    outcomes = [str(item.get("status", "unknown")).lower() for item in results]
    status_counts = {}
    for status in outcomes:
        status_counts[status] = status_counts.get(status, 0) + 1

    dominant_status, dominant_count = max(status_counts.items(), key=lambda pair: pair[1])
    return {
        "n_runs": len(results),
        "all_consistent": len(set(outcomes)) <= 1,
        "status_counts": status_counts,
        "dominant_status": dominant_status,
        "dominant_fraction": dominant_count / len(results),
    }
