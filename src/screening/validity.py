"""Validity checks for orbital-data quality and criterion applicability."""

from __future__ import annotations

from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {
    "system_name",
    "planet_name",
    "period_days",
    "period_unc_days",
    "semimajor_axis_au",
    "semimajor_axis_unc_au",
    "mass_mj",
    "mass_unc_mj",
    "eccentricity",
    "ecc_unc",
    "stellar_mass_msun",
    "stellar_mass_unc_msun",
    "source",
}


def validate_data_requirements(df: pd.DataFrame) -> dict[str, Any]:
    """Check whether a system table has the minimum data needed for analytical screening."""
    if df.empty:
        return {
            "status": "ABSTAIN",
            "required_parameters_valid": False,
            "assumptions_supported": False,
            "missing_fields": ["no_rows"],
            "warnings": ["The system table is empty."],
        }

    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        return {
            "status": "ABSTAIN",
            "required_parameters_valid": False,
            "assumptions_supported": False,
            "missing_fields": missing,
            "warnings": ["Required system columns are missing."],
        }

    warnings: list[str] = []
    issues: list[str] = []

    for col in ["period_days", "semimajor_axis_au", "mass_mj", "eccentricity", "stellar_mass_msun"]:
        ser = pd.to_numeric(df[col], errors="coerce")
        if ser.isna().any():
            issues.append(f"non_numeric_values:{col}")

    if df["stellar_mass_msun"].le(0).any():
        issues.append("nonpositive_stellar_mass")
    if df["mass_mj"].le(0).any():
        issues.append("nonpositive_planet_mass")
    if df["eccentricity"].ge(1.0).any():
        issues.append("eccentricity_at_or_above_one")
    if df["eccentricity"].lt(0).any():
        issues.append("negative_eccentricity")

    # Make the assumptions check stricter and explicit: the analytical conditions require
    # low-eccentricity and near-coplanar behaviour before classical Hill/AMD screening is valid.
    eccentricity_ok = df["eccentricity"].fillna(0.0).lt(0.3).all()
    coplanar_ok = df.get("inclination_deg", pd.Series(0.0, index=df.index)).fillna(0.0).le(5.0).all()
    stellar_mass_ok = df["stellar_mass_msun"].notna().all()
    mass_ok = df["mass_mj"].notna().all()
    assumptions_supported = bool(eccentricity_ok and coplanar_ok and stellar_mass_ok and mass_ok)

    if issues or not assumptions_supported:
        warnings.append("Criterion assumptions cannot be fully supported.")

    return {
        "status": "VALID" if not issues else "ABSTAIN",
        "required_parameters_valid": not issues,
        "assumptions_supported": assumptions_supported,
        "missing_fields": missing,
        "warnings": warnings,
    }


def check_assumptions(df: pd.DataFrame) -> dict[str, Any]:
    """Return an explicit assumptions report for the analytical screening engine."""
    if df.empty:
        return {"status": "ABSTAIN", "assumptions": [], "warnings": ["No system rows available."]}

    approx_coplanar = pd.to_numeric(df.get("inclination_deg", pd.Series(0.0, index=df.index)), errors="coerce").fillna(0.0)
    circular = df["eccentricity"].fillna(0.0) < 0.1
    assumptions = ["adjacent_pair_baseline", "coplanar_baseline", "circular_baseline"]
    warnings: list[str] = []

    if not approx_coplanar.le(5.0).all():
        assumptions.remove("coplanar_baseline")
        warnings.append("System is not close to coplanar; classical Hill/AMD assumptions may be weaker.")
    if not circular.all():
        assumptions.remove("circular_baseline")
        warnings.append("Non-negligible eccentricities mean the idealised Hill criterion is not definitive.")

    return {"status": "VALID", "assumptions": assumptions, "warnings": warnings}
