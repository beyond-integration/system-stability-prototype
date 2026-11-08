"""Generate the controlled synthetic system grid used for the screening prototype."""

from __future__ import annotations

from pathlib import Path

from src.simulation.initial_conditions import generate_synthetic_csv


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    output = root / "data" / "synthetic" / "synthetic_grid.csv"
    generate_synthetic_csv(output)
    print(f"Synthetic grid written to {output}")
