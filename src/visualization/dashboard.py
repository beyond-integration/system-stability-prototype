"""Simple dashboard/reporting module for project outputs.

This intentionally does not recalculate physics independently; it reads the saved result tables
and presents them in a compact, auditable format.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def render_dashboard(output_dir: str | Path) -> dict[str, Any]:
    """Load the saved result tables and return a compact dashboard summary."""
    output_dir = Path(output_dir)
    tables = {
        "system_validation": output_dir / "tables" / "system_validation.csv",
        "pair_diagnostics": output_dir / "tables" / "pair_diagnostics.csv",
        "amd_diagnostics": output_dir / "tables" / "amd_diagnostics.csv",
        "screening_decisions": output_dir / "tables" / "screening_decisions.csv",
        "simulation_runs": output_dir / "tables" / "simulation_runs.csv",
    }

    dashboard = {}
    for name, path in tables.items():
        if path.exists():
            dashboard[name] = pd.read_csv(path)
        else:
            dashboard[name] = pd.DataFrame()

    summary = {
        "system_count": len(dashboard["system_validation"]),
        "pair_count": len(dashboard["pair_diagnostics"]),
        "amd_count": len(dashboard["amd_diagnostics"]),
        "decision_count": len(dashboard["screening_decisions"]),
        "simulation_count": len(dashboard["simulation_runs"]),
    }
    return summary
