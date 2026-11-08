"""Event definitions and detection utilities for finite-horizon planetary integrations."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def _relative_state(sim: Any, planet_index: int, star_index: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Return the planet state relative to the stellar body."""
    star = sim.particles[star_index]
    planet = sim.particles[planet_index]
    r_rel = np.array(planet.xyz[:3], dtype=float) - np.array(star.xyz[:3], dtype=float)
    v_rel = np.array(planet.vxyz[:3], dtype=float) - np.array(star.vxyz[:3], dtype=float)
    return r_rel, v_rel


def mutual_hill_radius(a1: float, a2: float, m1: float, m2: float, m_star: float) -> float:
    """Return the mutual Hill radius for an adjacent pair in AU, Msun, and yr units."""
    if a1 <= 0 or a2 <= 0 or m1 <= 0 or m2 <= 0 or m_star <= 0:
        raise ValueError("All inputs for Hill radius must be positive.")
    return 0.5 * (a1 + a2) * ((m1 + m2) / (3.0 * m_star)) ** (1.0 / 3.0)


def pair_separation(pos1: np.ndarray, pos2: np.ndarray) -> float:
    """Return the Euclidean separation between two Cartesian position vectors."""
    return float(np.linalg.norm(pos1 - pos2))


def detect_close_encounter(sim: Any, threshold_pairs: list[tuple[int, int, float]] | None = None) -> dict[str, Any] | None:
    """Check whether any adjacent pair is within one mutual Hill radius of one another."""
    bodies = sim.particles
    if len(bodies) < 3:
        return None

    if threshold_pairs is None:
        threshold_pairs = []
        for i in range(1, len(bodies) - 1):
            j = i + 1
            a1 = bodies[i].a if hasattr(bodies[i], "a") else 1.0
            a2 = bodies[j].a if hasattr(bodies[j], "a") else 1.0
            m1 = bodies[i].m if hasattr(bodies[i], "m") else 1.0e-6
            m2 = bodies[j].m if hasattr(bodies[j], "m") else 1.0e-6
            m_star = bodies[0].m if hasattr(bodies[0], "m") else 1.0
            threshold_pairs.append((i, j, mutual_hill_radius(a1, a2, m1, m2, m_star)))

    for i, j, threshold in threshold_pairs:
        if i >= len(bodies) or j >= len(bodies):
            continue
        pos_i = np.array(bodies[i].xyz[:3], dtype=float)
        pos_j = np.array(bodies[j].xyz[:3], dtype=float)
        sep = pair_separation(pos_i, pos_j)
        if sep < threshold:
            return {
                "event_type": "close_encounter",
                "pair": (i, j),
                "separation": sep,
                "threshold": threshold,
                "time": sim.t,
            }
    return None


def detect_ejection(sim: Any, star_index: int = 0) -> dict[str, Any] | None:
    """Check whether a planet is unbound relative to the central star."""
    star = sim.particles[star_index]
    mu = 4.0 * math.pi**2 * star.m
    for idx in range(1, len(sim.particles)):
        p = sim.particles[idx]
        r_vec, v_vec = _relative_state(sim, idx, star_index)
        r = float(np.linalg.norm(r_vec))
        if r <= 0.0:
            continue
        specific_energy = 0.5 * float(np.dot(v_vec, v_vec)) - mu / r
        if specific_energy > 0.0:
            return {
                "event_type": "ejection",
                "planet_index": idx,
                "time": sim.t,
                "specific_energy": specific_energy,
                "reference_frame": "star-relative",
                "threshold": 0.0,
            }
    return None


def detect_stellar_collision(sim: Any, collision_radius: float | None = None, star_index: int = 0) -> dict[str, Any] | None:
    """Detect collision with the host star when a defensible stellar radius is available."""
    if collision_radius is None:
        return None
    star = sim.particles[star_index]
    for idx in range(1, len(sim.particles)):
        p = sim.particles[idx]
        r_vec, _ = _relative_state(sim, idx, star_index)
        r = float(np.linalg.norm(r_vec))
        if r <= collision_radius:
            return {
                "event_type": "stellar_collision",
                "planet_index": idx,
                "time": sim.t,
                "separation": r,
                "collision_radius": collision_radius,
                "reference_frame": "star-relative",
            }
    return None


def classify_event(sim: Any, collision_radius: float | None = None, star_index: int = 0) -> dict[str, Any] | None:
    """Return the first available event in a simulation snapshot."""
    event = detect_close_encounter(sim)
    if event is not None:
        return event
    event = detect_ejection(sim, star_index=star_index)
    if event is not None:
        return event
    return detect_stellar_collision(sim, collision_radius=collision_radius, star_index=star_index)
