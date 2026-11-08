# Methods

## Objective

This prototype tests whether a validity-aware screening workflow can reduce expensive numerical integrations while retaining a low false-safe rate for compact multi-planet systems.

## Data sources

- Observed planetary systems are loaded from the project’s processed table set under `data/processed/`.
- Raw archive data are preserved under `data/raw/nasa_archive/` and are never overwritten during analysis.
- Synthetic systems are generated in `data/synthetic/` using fixed seeds so the screening workflow can be reproduced.

## Validation and preprocessing

- Each system is checked for complete planet records, physically meaningful semimajor axes, masses, and eccentricities.
- The code enforces explicit physical assumptions and returns warnings rather than silently zero-filling missing values.
- Systems are sorted by semimajor axis before analysis so pairwise diagnostics remain deterministic.

## Analytical screening

The project evaluates the following diagnostics:

1. Hill separation
   - Computes the mutual Hill radius and separation for adjacent planet pairs.
   - Uses the classical criterion $\Delta > 2\sqrt{3}$ as a warning threshold for idealised circular-coplanar systems.

2. AMD stability
   - Computes classical AMD and the critical AMD limit using the constrained minimisation structure described in the project specification.
   - Compares the system-level AMD ratio to the critical threshold.

3. Resonance proximity
   - Measures the nearest low-order resonant ratio and the fractional proximity to resonance.
   - Treats resonance proximity as a diagnostic, not proof of libration.

4. Validity assessment
   - Rejects or abstains from decisions when assumptions are violated, such as missing parameters, highly eccentric or inclined systems, or insufficient data quality.

## Numerical follow-up

- When the analytical screening indicates a need for confirmation, the project runs REBOUND simulations with a finite-horizon baseline.
- The numerical driver stores initial conditions, event summaries, and diagnostics with fixed seeds and explicit timescales.
- Energy and angular-momentum drift are recorded for auditability.

## Decision logic

The screening decision is a transparent choice among:

- `screen`: a system is classified as likely stable or unstable based on the analytical checks and applicability.
- `investigate`: the system is not yet decisive and merits numerical follow-up.
- `abstain`: the system is outside the safe applicability region for the analytical criteria.

## Reproducibility

The project uses a strict test gate before running the pipeline, and all generated outputs are saved to versioned directories under `outputs/`.
