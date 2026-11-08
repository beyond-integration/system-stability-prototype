"""Tests for REBOUND simulation setup and event detection.

These checks cover the numerical-experiment gate required by the project: a minimal
valid one-planet orbit, reproducible seed-based initial conditions, and a multi-step
convergence comparison across three timesteps.
"""

from __future__ import annotations

import pandas as pd

from src.simulation.events import classify_event, mutual_hill_radius
from src.simulation.rebound_runner import (
    _build_simulation,
    compare_timestep_convergence,
    run_rebound_integration,
)


def test_mutual_hill_radius_increases_with_spacing():
    r_small = mutual_hill_radius(1.0, 1.5, 1e-4, 1e-4, 1.0)
    r_large = mutual_hill_radius(1.0, 2.0, 1e-4, 1e-4, 1.0)
    assert r_large > r_small


def test_rebound_integration_returns_valid_or_invalid_status():
    df = pd.DataFrame(
        [
            {
                "system_name": "Example",
                "planet_name": "b",
                "period_days": 365.25,
                "semimajor_axis_au": 1.0,
                "mass_mj": 1e-4,
                "eccentricity": 0.0,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
            {
                "system_name": "Example",
                "planet_name": "c",
                "period_days": 365.25 * (1.5 ** 1.5),
                "semimajor_axis_au": 1.5,
                "mass_mj": 1e-4,
                "eccentricity": 0.0,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
        ]
    )
    result = run_rebound_integration(df, seed=7, timestep=0.01, horizon=10.0)
    assert result.simulation_status in {"VALID", "INVALID"}
    assert result.energy_error is not None
    assert result.angular_momentum_error is not None


def test_one_star_one_planet_orbit_runs_and_stays_valid():
    df = pd.DataFrame(
        [
            {
                "system_name": "OnePlanet",
                "planet_name": "b",
                "period_days": 365.25,
                "semimajor_axis_au": 1.0,
                "mass_mj": 1e-6,
                "eccentricity": 0.0,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            }
        ]
    )
    result = run_rebound_integration(df, seed=1, timestep=0.05, horizon=5.0)
    assert result.simulation_status == "VALID"
    assert result.termination_reason == "completed"
    assert result.energy_error is not None


def test_fixed_seed_reproduces_identical_initial_conditions():
    df = pd.DataFrame(
        [
            {
                "system_name": "Seeded",
                "planet_name": "b",
                "period_days": 365.25,
                "semimajor_axis_au": 1.0,
                "mass_mj": 1e-4,
                "eccentricity": 0.1,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
            {
                "system_name": "Seeded",
                "planet_name": "c",
                "period_days": 730.5,
                "semimajor_axis_au": 1.5,
                "mass_mj": 1e-4,
                "eccentricity": 0.1,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
        ]
    )
    first = run_rebound_integration(df, seed=42, timestep=0.01, horizon=3.0).initial_conditions
    second = run_rebound_integration(df, seed=42, timestep=0.01, horizon=3.0).initial_conditions
    assert first == second


def test_timestep_convergence_comparison_has_three_configurations():
    df = pd.DataFrame(
        [
            {
                "system_name": "Conv",
                "planet_name": "b",
                "period_days": 365.25,
                "semimajor_axis_au": 1.0,
                "mass_mj": 1e-4,
                "eccentricity": 0.0,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
            {
                "system_name": "Conv",
                "planet_name": "c",
                "period_days": 365.25 * (1.5 ** 1.5),
                "semimajor_axis_au": 1.5,
                "mass_mj": 1e-4,
                "eccentricity": 0.0,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
        ]
    )
    table = compare_timestep_convergence(df, timestep_values=(0.04, 0.02, 0.01), horizon=10.0, seed=3)
    assert len(table) == 3
    assert set(table["timestep"]) == {0.04, 0.02, 0.01}


def test_close_encounter_event_classification_is_structured():
    df = pd.DataFrame(
        [
            {
                "system_name": "Close",
                "planet_name": "b",
                "period_days": 365.25,
                "semimajor_axis_au": 1.0,
                "mass_mj": 1e-4,
                "eccentricity": 0.0,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
            {
                "system_name": "Close",
                "planet_name": "c",
                "period_days": 365.25,
                "semimajor_axis_au": 1.01,
                "mass_mj": 1e-4,
                "eccentricity": 0.0,
                "stellar_mass_msun": 1.0,
                "source": "synthetic",
            },
        ]
    )
    sim = _build_simulation(df, seed=1, timestep=0.01, horizon=1.0)
    sim.integrate(1.0)
    event = classify_event(sim)
    assert event is None or event["event_type"] in {"close_encounter", "ejection", "stellar_collision"}
