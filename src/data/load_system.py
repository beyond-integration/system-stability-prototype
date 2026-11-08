"""Load and normalise a planet table while preserving the original source data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .units import convert_to_internal_units


REQUIRED_COLUMNS = {
    "system_name",
    "planet_name",
    "period_days",
    "semimajor_axis_au",
    "mass_mj",
    "eccentricity",
    "stellar_mass_msun",
    "source",
}


def load_planet_table(path: str | Path) -> pd.DataFrame:
    """Load a CSV containing one row per planet. The raw data are preserved and never overwritten."""
    path = Path(path)
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Planet table is empty: {path}")
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required planet columns: {sorted(missing)}")
    return df


def normalise_planet_table(df: pd.DataFrame) -> pd.DataFrame:
    """Add internal-unit columns without overwriting the original source values."""
    normalised = df.copy()
    for _, row in normalised.iterrows():
        converted = convert_to_internal_units(row.to_dict())
        for key, value in converted.items():
            normalised.at[row.name, key] = value
    return normalised


def load_system(system_name: str, base_dir: str | Path) -> pd.DataFrame:
    """Load a processed system table by its system name from the processed-data directory."""
    base_dir = Path(base_dir)
    candidate = base_dir / f"{system_name}.csv"
    if not candidate.exists():
        raise FileNotFoundError(f"No processed system file found for {system_name!r} at {candidate}")
    return load_planet_table(candidate)
