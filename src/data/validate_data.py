"""Validate orbital data and return structured failure results."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

REQUIRED_PLANET_COLUMNS = {
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


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _check_numeric_range(name: str, value: Any, lower: float | None = None, upper: float | None = None) -> list[str]:
    errors: list[str] = []
    if value is None:
        return errors
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return [f"{name} is not numeric"]
    if math.isnan(numeric) or math.isinf(numeric):
        return [f"{name} is NaN or infinite"]
    if lower is not None and numeric < lower:
        errors.append(f"{name} below minimum {lower}")
    if upper is not None and numeric >= upper:
        errors.append(f"{name} at or above maximum {upper}")
    return errors


def validate_planet_row(row: dict[str, Any]) -> dict[str, Any]:
    """Validate a single planet row and return a structured status dictionary."""
    result: dict[str, Any] = {
        "status": "VALID",
        "errors": [],
        "missing": [],
        "warnings": [],
    }

    for required in REQUIRED_PLANET_COLUMNS:
        if required not in row or _is_missing(row.get(required)):
            result["missing"].append(required)

    for name in [
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
    ]:
        if name in row and not _is_missing(row.get(name)):
            if name in {"eccentricity", "ecc_unc"}:
                result["errors"].extend(_check_numeric_range(name, row[name], lower=0.0, upper=1.0))
            elif name in {"mass_mj", "mass_unc_mj", "stellar_mass_msun", "stellar_mass_unc_msun"}:
                result["errors"].extend(_check_numeric_range(name, row[name], lower=0.0))
            elif name in {"period_days", "period_unc_days", "semimajor_axis_au", "semimajor_axis_unc_au"}:
                result["errors"].extend(_check_numeric_range(name, row[name], lower=0.0))

    if row.get("eccentricity") is not None:
        try:
            ecc = float(row["eccentricity"])
        except (TypeError, ValueError):
            ecc = None
        if ecc is not None and ecc >= 1.0:
            result["errors"].append("eccentricity must be less than 1")
        if ecc is not None and ecc < 0.0:
            result["errors"].append("eccentricity must be non-negative")
    if row.get("mass_mj") is not None:
        try:
            mass = float(row["mass_mj"])
        except (TypeError, ValueError):
            mass = None
        if mass is not None and mass <= 0:
            result["errors"].append("mass_mj must be positive")
    if row.get("stellar_mass_msun") is not None:
        try:
            stellar_mass = float(row["stellar_mass_msun"])
        except (TypeError, ValueError):
            stellar_mass = None
        if stellar_mass is not None and stellar_mass <= 0:
            result["errors"].append("stellar_mass_msun must be positive")

    if result["missing"] or result["errors"]:
        result["status"] = "INVALID"
    return result


def collect_validation_failures(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Validate every row and return the row-specific results."""
    results: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        results.append({"planet_name": row.get("planet_name"), **validate_planet_row(row.to_dict())})
    return results


def validate_system_table(df: pd.DataFrame) -> dict[str, Any]:
    """Validate a full system table and summarise system-level issues."""
    validations = collect_validation_failures(df)
    all_missing = []
    all_errors = []
    for entry in validations:
        all_missing.extend(entry["missing"])
        all_errors.extend(entry["errors"])

    if "planet_name" in df.columns:
        duplicate_planets = df["planet_name"][df["planet_name"].duplicated()].tolist()
        if duplicate_planets:
            all_errors.extend([f"duplicate planet_name: {name}" for name in duplicate_planets])

    if {"period_days", "semimajor_axis_au"}.issubset(df.columns):
        try:
            periods = pd.to_numeric(df["period_days"], errors="coerce")
            axes = pd.to_numeric(df["semimajor_axis_au"], errors="coerce")
            if not periods.isna().all() and not axes.isna().all():
                sorted_axes = axes.sort_values().reset_index(drop=True)
                if not axes.reset_index(drop=True).equals(sorted_axes):
                    all_errors.append("semimajor_axis_au must be sorted in ascending order")
                if not periods.reset_index(drop=True).equals(periods.sort_values().reset_index(drop=True)):
                    all_errors.append("period_days must be sorted consistently with semimajor_axis_au")
        except Exception:
            all_errors.append("period_days and semimajor_axis_au ordering could not be validated")

    status = "VALID" if not all_missing and not all_errors else "INVALID"
    return {
        "status": status,
        "n_rows": len(df),
        "missing_fields": all_missing,
        "invalid_fields": all_errors,
        "row_results": validations,
    }
