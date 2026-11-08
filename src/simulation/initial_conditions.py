"""Synthetic and observed-system initial-condition generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def solve_outer_separation(a1: float, delta: float, m1: float, m2: float, m_star: float) -> float:
    """Solve for the outer semimajor axis corresponding to a target mutual Hill separation."""
    def f(a2: float) -> float:
        rh = 0.5 * (a1 + a2) * ((m1 + m2) / (3.0 * m_star)) ** (1.0 / 3.0)
        return (a2 - a1) / rh - delta

    lo = a1 * 1.01
    hi = a1 * 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def generate_synthetic_grid() -> pd.DataFrame:
    """Generate a controlled two-planet synthetic dataset matching the project specification."""
    rng = np.random.default_rng(20261105)
    records: list[dict[str, Any]] = []
    mass_levels = [1e-5, 1e-4]
    deltas = [2.8, 3.2, 3.46, 3.7, 4.0, 5.0, 8.0, 12.0]
    eccentricities = [0.0, 0.05]

    for mass in mass_levels:
        for delta in deltas:
            for ecc in eccentricities:
                a1 = 1.0
                a2 = solve_outer_separation(a1, delta, mass, mass, 1.0)
                for realization in range(3):
                    angle = rng.uniform(0.0, 2.0 * np.pi)
                    records.append(
                        {
                            "system_name": f"synthetic_delta_{delta}_m_{mass}_e_{ecc}",
                            "planet_name": "b",
                            "period_days": ((a1 ** 3) / 1.0) ** 0.5 * 365.25,
                            "period_unc_days": 0.0,
                            "semimajor_axis_au": a1,
                            "semimajor_axis_unc_au": 0.0,
                            "mass_mj": mass / 9.54588e-4,
                            "mass_unc_mj": 0.0,
                            "eccentricity": ecc,
                            "ecc_unc": 0.0,
                            "stellar_mass_msun": 1.0,
                            "stellar_mass_unc_msun": 0.0,
                            "source": "synthetic_grid",
                            "realization": realization,
                            "angle_seed": angle,
                        }
                    )
                    records.append(
                        {
                            "system_name": f"synthetic_delta_{delta}_m_{mass}_e_{ecc}",
                            "planet_name": "c",
                            "period_days": ((a2 ** 3) / 1.0) ** 0.5 * 365.25,
                            "period_unc_days": 0.0,
                            "semimajor_axis_au": a2,
                            "semimajor_axis_unc_au": 0.0,
                            "mass_mj": mass / 9.54588e-4,
                            "mass_unc_mj": 0.0,
                            "eccentricity": ecc,
                            "ecc_unc": 0.0,
                            "stellar_mass_msun": 1.0,
                            "stellar_mass_unc_msun": 0.0,
                            "source": "synthetic_grid",
                            "realization": realization,
                            "angle_seed": angle + np.pi / 2.0,
                        }
                    )
    return pd.DataFrame(records)


def write_initial_conditions_json(path: str | Path, payload: dict[str, Any]) -> None:
    """Write a JSON record of a simulation initial condition in the project format."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def generate_synthetic_csv(output_path: str | Path) -> None:
    """Write the synthetic grid CSV to disk."""
    df = generate_synthetic_grid()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return None
