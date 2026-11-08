"""Classical AMD and critical-AMD calculations with explicit assumptions."""

from __future__ import annotations

import math
from typing import Any

from scipy.optimize import minimize


def lambda_i(m_i: float, m_star: float, a_i: float, G: float = 4.0 * math.pi**2) -> float:
    """Return the specific angular momentum scale Lambda_i = m_i * sqrt(G M_star a_i)."""
    if m_i <= 0 or m_star <= 0 or a_i <= 0:
        raise ValueError("m_i, m_star, and a_i must be positive.")
    return m_i * math.sqrt(G * m_star * a_i)


def system_amd(planet_data: list[dict[str, float]], m_star: float, G: float = 4.0 * math.pi**2) -> dict[str, Any]:
    """Compute the classical system AMD for coplanar systems.

    The function accepts a list of dictionaries with keys: mass, semimajor_axis,
    eccentricity, inclination_rad. All values are in internal units.
    """
    if m_star <= 0:
        raise ValueError("Stellar mass must be positive.")

    total_amd = 0.0
    for planet in planet_data:
        m_i = float(planet["mass"])
        a_i = float(planet["semimajor_axis"])
        e_i = float(planet["eccentricity"])
        inc_i = float(planet.get("inclination_rad", 0.0))
        if m_i <= 0 or a_i <= 0:
            raise ValueError("Planet mass and semimajor axis must be positive.")
        if not 0.0 <= e_i < 1.0:
            raise ValueError("Eccentricity must satisfy 0 <= e < 1.")
        lam = lambda_i(m_i, m_star, a_i, G)
        total_amd += lam * (1.0 - math.sqrt(1.0 - e_i**2) * math.cos(inc_i))

    return {
        "status": "VALID",
        "value": total_amd,
        "units": "angular_momentum_deficit",
        "method": "classical_amd",
        "assumptions": ["coplanar_baseline"],
        "warnings": [],
        "source": None,
    }


def critical_amd_pair(a1: float, a2: float, m1: float, m2: float, m_star: float) -> dict[str, Any]:
    """Compute the critical AMD for a pair by minimising the AMD required for orbit crossing."""
    if a1 <= 0 or a2 <= 0 or a2 <= a1:
        raise ValueError("The inner and outer semimajor axes must satisfy 0 < a1 < a2.")
    if m1 <= 0 or m2 <= 0 or m_star <= 0:
        raise ValueError("All masses must be positive.")

    lam1 = lambda_i(m1, m_star, a1)
    lam2 = lambda_i(m2, m_star, a2)

    def objective(x):
        e1, e2 = x
        if e1 < 0 or e2 < 0 or e1 >= 1 or e2 >= 1:
            return 1e12
        return lam1 * (1.0 - math.sqrt(1.0 - e1**2)) + lam2 * (1.0 - math.sqrt(1.0 - e2**2))

    def constraint(x):
        e1, e2 = x
        return a1 * (1.0 + e1) - a2 * (1.0 - e2)

    result = minimize(
        objective,
        x0=[0.1, 0.1],
        constraints=[{"type": "eq", "fun": constraint}],
        bounds=[(0.0, 1.0 - 1e-12), (0.0, 1.0 - 1e-12)],
        method="SLSQP",
    )

    if not result.success:
        return {
            "status": "OPTIMISATION_FAILED",
            "value": None,
            "units": "angular_momentum_deficit",
            "method": "critical_amd_pair",
            "assumptions": ["adjacent_pair", "coplanar_baseline"],
            "warnings": [f"Critical AMD optimisation failed: {result.message}"],
            "source": None,
            "convergence": False,
        }

    e1_opt, e2_opt = result.x
    critical_amd = objective(result.x)
    return {
        "status": "VALID",
        "value": critical_amd,
        "units": "angular_momentum_deficit",
        "method": "critical_amd_pair",
        "assumptions": ["adjacent_pair", "coplanar_baseline"],
        "warnings": [],
        "source": None,
        "convergence": True,
        "optimal_eccentricities": {"e1": e1_opt, "e2": e2_opt},
    }


def amd_ratio(system_amd_value: float, critical_amd_value: float) -> dict[str, Any]:
    """Return the AMD ratio A = C / C_c for a system or pair."""
    if critical_amd_value <= 0:
        raise ValueError("Critical AMD must be positive.")
    ratio = system_amd_value / critical_amd_value
    return {
        "status": "VALID",
        "value": ratio,
        "units": "dimensionless",
        "method": "amd_ratio",
        "assumptions": ["classical_amd_criterion"],
        "warnings": [],
        "source": None,
        "threshold": 1.0,
    }
