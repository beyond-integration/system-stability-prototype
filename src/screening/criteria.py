"""Criterion state generation for Hill, AMD, and resonance diagnostics."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.physics.amd import amd_ratio, critical_amd_pair, system_amd
from src.physics.hill import mutual_hill_separation
from src.physics.resonance import resonance_proximity


def evaluate_hill_for_system(df: pd.DataFrame) -> pd.DataFrame:
    """Compute pairwise Hill diagnostics for each adjacent pair in a system."""
    rows: list[dict[str, Any]] = []
    if df.empty:
        return pd.DataFrame(rows)

    for idx in range(len(df) - 1):
        inner = df.iloc[idx]
        outer = df.iloc[idx + 1]
        result = mutual_hill_separation(
            float(inner["semimajor_axis_au"]),
            float(outer["semimajor_axis_au"]),
            float(inner["mass_mj"]) * 9.54588e-4,
            float(outer["mass_mj"]) * 9.54588e-4,
            float(inner["stellar_mass_msun"]),
        )
        rows.append(
            {
                "pair": f"{inner['planet_name']}-{outer['planet_name']}",
                "inner_planet": inner["planet_name"],
                "outer_planet": outer["planet_name"],
                "delta": result["value"],
                "hill_radius": result["hill_radius"],
                "threshold": result["threshold"],
                "status": result["status"],
                "criterion_satisfied": result["idealised_hill_criterion_satisfied"],
                "source": inner["source"],
            }
        )
    return pd.DataFrame(rows)


def evaluate_amd_for_system(df: pd.DataFrame) -> dict[str, Any]:
    """Compute system-level AMD and critical AMD using the classical criterion."""
    if df.empty:
        return {
            "system_amd": 0.0,
            "critical_amd": 0.0,
            "amd_ratio": 0.0,
            "criterion_status": "VALID",
            "assumptions": ["classical_amd_criterion", "coplanar_baseline"],
            "pair_results": [],
        }

    planet_rows = [
        {
            "mass": float(row["mass_mj"]) * 9.54588e-4,
            "semimajor_axis": float(row["semimajor_axis_au"]),
            "eccentricity": float(row["eccentricity"]),
            "inclination_rad": float(row.get("inclination_deg", 0.0)) * 3.141592653589793 / 180.0,
        }
        for _, row in df.iterrows()
    ]
    star_mass = float(df["stellar_mass_msun"].iloc[0])
    system_amd_result = system_amd(planet_rows, star_mass)

    pair_results = []
    for idx in range(len(df) - 1):
        inner = df.iloc[idx]
        outer = df.iloc[idx + 1]
        pair_result = critical_amd_pair(
            float(inner["semimajor_axis_au"]),
            float(outer["semimajor_axis_au"]),
            float(inner["mass_mj"]) * 9.54588e-4,
            float(outer["mass_mj"]) * 9.54588e-4,
            float(inner["stellar_mass_msun"]),
        )
        pair_results.append(
            {
                "pair": f"{inner['planet_name']}-{outer['planet_name']}",
                "critical_amd": pair_result.get("value"),
                "convergence": pair_result.get("convergence", False),
                "status": pair_result["status"],
            }
        )

    valid_pair_values = [item["critical_amd"] for item in pair_results if item["critical_amd"] is not None]
    critical_value = min(valid_pair_values) if valid_pair_values else 1e-12
    ratio = amd_ratio(system_amd_result["value"], critical_value)
    return {
        "system_amd": system_amd_result["value"],
        "critical_amd": critical_value,
        "amd_ratio": ratio["value"],
        "criterion_status": "VALID" if ratio["value"] < 1.0 else "NUMERICAL_FOLLOW_UP",
        "assumptions": ["classical_amd_criterion", "coplanar_baseline"],
        "pair_results": pair_results,
    }


def evaluate_resonance_for_system(df: pd.DataFrame) -> pd.DataFrame:
    """Compute nearest-commensurability diagnostics for adjacent planet pairs."""
    rows: list[dict[str, Any]] = []
    if df.empty:
        return pd.DataFrame(rows)

    for idx in range(len(df) - 1):
        inner = df.iloc[idx]
        outer = df.iloc[idx + 1]
        result = resonance_proximity(float(inner["period_days"]), float(outer["period_days"]))
        rows.append(
            {
                "pair": f"{inner['planet_name']}-{outer['planet_name']}",
                "period_ratio": result["period_ratio"],
                "nearest_resonance": result["nearest_resonance"],
                "fractional_offset": result["fractional_offset"],
                "resonance_order": result["resonance_order"],
                "status": result["status"],
                "resonance_state": result["resonance_state"],
            }
        )
    return pd.DataFrame(rows)
