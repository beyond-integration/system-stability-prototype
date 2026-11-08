"""REBOUND integration driver for finite-horizon stability runs."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import rebound
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError("REBOUND is required for numerical simulation stage.") from exc

from src.simulation.events import classify_event


@dataclass
class SimulationResult:
    """Structured simulation result for one REBOUND run."""
    experiment_id: str
    system_name: str
    planet_names: list[str]
    dataset_version: str
    parameter_reference: str
    code_version: str
    python_version: str
    rebound_version: str
    integrator: str
    timestep: float
    integration_horizon: float
    random_seed: int
    initial_conditions: dict[str, Any]
    event_definition: str
    simulation_status: str
    energy_error: float | None
    angular_momentum_error: float | None
    wall_clock_time: float
    termination_reason: str
    event_type: str | None = None
    event_time: float | None = None
    event_details: dict[str, Any] | None = None


def _make_initial_conditions(df: pd.DataFrame, seed: int, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create deterministic, reproducible initial conditions in increasing semimajor-axis order."""
    config = config or {}
    rng = np.random.default_rng(seed)
    sorted_df = df.sort_values("semimajor_axis_au", kind="mergesort").reset_index(drop=True)
    mean_anomalies = rng.uniform(0.0, 2.0 * math.pi, size=len(sorted_df))
    output = {
        "seed": seed,
        "system_name": str(sorted_df["system_name"].iloc[0]) if not sorted_df.empty else "",
        "planet_names": sorted_df["planet_name"].tolist(),
        "semimajor_axes_au": sorted_df["semimajor_axis_au"].tolist(),
        "masses_msun": (sorted_df["mass_mj"] * 9.54588e-4).tolist(),
        "eccentricities": sorted_df["eccentricity"].fillna(0.0).tolist(),
        "arguments_of_periapsis": sorted_df.get("argument_of_periapsis_deg", pd.Series([0.0] * len(sorted_df))).tolist(),
        "angles_random": mean_anomalies.tolist(),
        "mean_anomalies": mean_anomalies.tolist(),
        "coplanar": True,
    }
    return output


def _build_simulation(df: pd.DataFrame, seed: int, timestep: float, horizon: float, integrator: str = "WHFast") -> Any:
    """Construct a REBOUND simulation from analytic planetary parameters."""
    sorted_df = df.sort_values("semimajor_axis_au", kind="mergesort").reset_index(drop=True)
    sim = rebound.Simulation()
    sim.G = 4.0 * math.pi**2
    sim.integrator = integrator
    sim.dt = timestep
    sim.t = 0.0
    sim.add(m=sorted_df["stellar_mass_msun"].iloc[0])
    for _, row in sorted_df.iterrows():
        a = float(row["semimajor_axis_au"])
        m = float(row["mass_mj"]) * 9.54588e-4
        e = float(row.get("eccentricity", 0.0) or 0.0)
        p = sim.particles[0]
        sim.add(m=m, a=a, e=e, primary=p)
    sim.move_to_com()
    return sim


def _total_energy(simulation: Any) -> float:
    """Return the system's total energy using the pairwise gravitational potential."""
    kinetic = 0.0
    potential = 0.0
    particles = simulation.particles
    for p in particles:
        kinetic += 0.5 * p.m * (p.vx**2 + p.vy**2 + p.vz**2)

    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            pi = particles[i]
            pj = particles[j]
            dx = pi.x - pj.x
            dy = pi.y - pj.y
            dz = pi.z - pj.z
            r = math.sqrt(dx**2 + dy**2 + dz**2)
            if r <= 0.0:
                continue
            potential -= simulation.G * pi.m * pj.m / r

    return kinetic + potential


def _total_angular_momentum(simulation: Any) -> np.ndarray:
    """Compute total angular momentum vector from the particle state."""
    total = np.zeros(3, dtype=float)
    for p in simulation.particles:
        r = np.array([p.x, p.y, p.z], dtype=float)
        v = np.array([p.vx, p.vy, p.vz], dtype=float)
        total += p.m * np.cross(r, v)
    return total


def run_rebound_integration(
    df: pd.DataFrame,
    seed: int = 1,
    integrator: str = "WHFast",
    timestep: float | None = None,
    horizon: float | None = None,
    experiment_id: str = "exp_001",
    dataset_version: str = "v1",
    parameter_reference: str = "processed_observed_systems.csv",
    code_version: str = "unknown",
    collision_radius: float | None = None,
) -> SimulationResult:
    """Run a REBOUND integration and return a structured result record."""
    if df.empty:
        raise ValueError("Simulation requires at least one row.")

    sorted_df = df.sort_values("semimajor_axis_au", kind="mergesort").reset_index(drop=True)
    p_min = float(sorted_df["period_days"].min()) / 365.25
    if timestep is None:
        timestep = p_min / 30.0
    if horizon is None:
        horizon = 1.0e4 * p_min

    initial_conditions = _make_initial_conditions(sorted_df, seed)
    sim = _build_simulation(sorted_df, seed, timestep, horizon, integrator)
    sim.dt = timestep
    sim.t = 0.0

    initial_energy = _total_energy(sim)
    initial_angular_momentum = _total_angular_momentum(sim)
    start = time.perf_counter()
    event = None
    termination_reason = "completed"

    try:
        sim.integrate(horizon, exact_finish_time=0)
    except Exception as exc:  # pragma: no cover - runtime failure path
        termination_reason = f"integration_failed:{type(exc).__name__}"

    wall_time = time.perf_counter() - start
    final_energy = _total_energy(sim)
    final_angular_momentum = _total_angular_momentum(sim)
    relative_energy_error = abs(final_energy - initial_energy) / abs(initial_energy) if abs(initial_energy) > 0 else None
    relative_angular_error = np.linalg.norm(final_angular_momentum - initial_angular_momentum) / np.linalg.norm(initial_angular_momentum) if np.linalg.norm(initial_angular_momentum) > 0 else None

    if termination_reason == "completed":
        event = classify_event(sim, collision_radius=collision_radius)
        if event is not None:
            termination_reason = "event_detected"
    else:
        event = None

    result = SimulationResult(
        experiment_id=experiment_id,
        system_name=str(sorted_df["system_name"].iloc[0]),
        planet_names=sorted_df["planet_name"].tolist(),
        dataset_version=dataset_version,
        parameter_reference=parameter_reference,
        code_version=code_version,
        python_version=str(__import__("sys").version.split()[0]),
        rebound_version=str(rebound.__version__),
        integrator=integrator,
        timestep=float(timestep),
        integration_horizon=float(horizon),
        random_seed=int(seed),
        initial_conditions=initial_conditions,
        event_definition="close_encounter or ejection or stellar_collision before horizon",
        simulation_status="VALID" if termination_reason in {"completed", "event_detected"} else "INVALID",
        energy_error=relative_energy_error,
        angular_momentum_error=relative_angular_error,
        wall_clock_time=float(wall_time),
        termination_reason=termination_reason,
        event_type=event["event_type"] if event else None,
        event_time=event["time"] if event else None,
        event_details=event,
    )
    return result


def save_simulation_outputs(result: SimulationResult, output_dir: str | Path) -> dict[str, str]:
    """Persist simulation metadata, initial conditions, and diagnostics to JSON files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    system_id = result.system_name
    seed_tag = f"{result.random_seed:03d}"
    prefix = f"{system_id}_seed_{seed_tag}"

    initial_path = output_dir / f"{prefix}_initial.json"
    final_path = output_dir / f"{prefix}_final.json"
    diagnostics_path = output_dir / f"{prefix}_diagnostics.json"

    initial_record = {
        "experiment_id": result.experiment_id,
        "system_name": result.system_name,
        "planet_names": result.planet_names,
        "dataset_version": result.dataset_version,
        "parameter_reference": result.parameter_reference,
        "code_version": result.code_version,
        "python_version": result.python_version,
        "rebound_version": result.rebound_version,
        "integrator": result.integrator,
        "timestep": result.timestep,
        "integration_horizon": result.integration_horizon,
        "random_seed": result.random_seed,
        "initial_conditions": result.initial_conditions,
        "event_definition": result.event_definition,
    }

    final_record = {
        "experiment_id": result.experiment_id,
        "system_name": result.system_name,
        "planet_names": result.planet_names,
        "simulation_status": result.simulation_status,
        "event_type": result.event_type,
        "event_time": result.event_time,
        "event_details": result.event_details,
    }

    diagnostics_record = {
        "experiment_id": result.experiment_id,
        "system_name": result.system_name,
        "simulation_status": result.simulation_status,
        "energy_error": result.energy_error,
        "angular_momentum_error": result.angular_momentum_error,
        "wall_clock_time": result.wall_clock_time,
        "termination_reason": result.termination_reason,
        "integrator": result.integrator,
        "timestep": result.timestep,
        "integration_horizon": result.integration_horizon,
        "random_seed": result.random_seed,
    }

    for path, record in [(initial_path, initial_record), (final_path, final_record), (diagnostics_path, diagnostics_record)]:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)

    return {
        "initial": str(initial_path),
        "final": str(final_path),
        "diagnostics": str(diagnostics_path),
    }


def compare_timestep_convergence(
    df: pd.DataFrame,
    timestep_values: list[float] | tuple[float, ...] | None = None,
    horizon: float = 20.0,
    seed: int = 7,
) -> pd.DataFrame:
    """Run the same system across multiple timesteps and report the diagnostic drift.

    This helper provides the explicit three-point convergence comparison required by the
    numerical experiment gate while keeping the simulation outputs reproducible and
    directly comparable across time steps.
    """
    if timestep_values is None:
        timestep_values = (0.04, 0.02, 0.01)
    rows: list[dict[str, Any]] = []
    for dt in timestep_values:
        result = run_rebound_integration(df, seed=seed, timestep=float(dt), horizon=float(horizon))
        rows.append(
            {
                "system_name": result.system_name,
                "seed": result.random_seed,
                "timestep": float(dt),
                "integration_horizon": float(horizon),
                "simulation_status": result.simulation_status,
                "termination_reason": result.termination_reason,
                "energy_error": result.energy_error,
                "angular_momentum_error": result.angular_momentum_error,
                "event_type": result.event_type,
                "event_time": result.event_time,
            }
        )
    return pd.DataFrame(rows)
