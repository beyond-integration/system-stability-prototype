# Exoplanet Stability Screening

A reproducible scientific-computing prototype for screening compact exoplanet systems with analytical stability diagnostics and a finite-horizon REBOUND follow-up step.

## Project scope

This repository documents a compact exoplanet stability screening workflow with explicit assumptions, validation checks, and numerical follow-up. It is not a validated long-term stability predictor, not a replacement for established dynamical tools such as SPOCK, and not a machine-learning model.

The project currently demonstrates:
- data validation and provenance tracking for observed systems
- Kepler-consistency checks and unit handling
- mutual Hill-separation diagnostics
- AMD ratio and critical-AMD checks
- near-commensurability resonance diagnostics
- screening decisions with explicit assumptions and abstention logic
- finite-horizon REBOUND simulations for selected systems
- reproducible output tables, logs, and figures

The work is intentionally limited to a transparent prototype scope.

## Scientific question

Can a validity-aware screening workflow identify compact multi-planet systems that merit more expensive numerical follow-up, while clearly separating analytical diagnostics from finite-horizon numerical evidence?

## Actual project coverage

The repository contains processed tables for five observed systems:
- HD 219134
- Kepler-11
- Kepler-223
- Kepler-36
- TRAPPIST-1

All five were processed through the data-validation and screening workflow in the project outputs. The saved numerical simulation records in `outputs/simulations/` currently document finite-horizon REBOUND runs for:
- Kepler-36
- TRAPPIST-1

This distinction is important: the project data pipeline screens the full set of systems, but the numerical-integration records only cover the subset that received a simulation snapshot in this prototype release.

## Pipeline summary

```text
raw NASA archive CSVs
        ↓
processed system tables
        ↓
validation and unit checks
        ↓
Hill / AMD / resonance diagnostics
        ↓
decision logic (screen / investigate / abstain)
        ↓
selected finite-horizon REBOUND runs
        ↓
output tables, logs, and figures
```

## Repository structure

```text
Prototype_2/
├── README.md
├── LICENSE
├── requirements.txt
├── requirements-lock.txt
├── config.yaml
├── .gitignore
├── data/
│   ├── data_dictionary.md
│   ├── raw/
│   │   ├── literature/
│   │   └── nasa_archive/
│   ├── processed/
│   └── synthetic/
├── src/
│   ├── data/
│   ├── physics/
│   ├── screening/
│   ├── simulation/
│   ├── evaluation/
│   └── visualization/
├── tests/
├── outputs/
│   ├── figures/
│   ├── logs/
│   ├── simulations/
│   └── tables/
├── reports/
│   ├── experiment_log.md
│   ├── methods.md
│   └── limitations.md
└── .venv/                  # local-only; not part of the public repo
```

## Installation

Use a fresh Python environment outside the repository, then install dependencies from the declared requirement file.

PowerShell:

```powershell
python --version
python -m venv "$env:TEMP\exoplanet_release_venv"
& "$env:TEMP\exoplanet_release_venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

## Running the project

From the project root:

```powershell
python src/main.py
```

The project entry point first runs the required pytest gate and then executes the analysis pipeline if the tests pass.

## Testing

```powershell
python -m pytest -q
```

The current verified suite result in a clean external environment is 36 passing tests.

## Data provenance and sources

The data workflow preserves raw NASA Archive data and keeps it separate from processed values:
- raw NASA archive tables are stored in `data/raw/nasa_archive/`
- processed system tables are stored in `data/processed/`
- the synthetic grid is kept separate under `data/synthetic/`
- the dictionary file is `data/data_dictionary.md`

The raw archive files are not overwritten by the pipeline. The processed tables are derived values intended for the screening workflow and should be traced back to the original archive source and the selected reference parameters.

The project is deliberately careful about the scientific language:
- period-ratio proximity is not proof of resonance locking
- finite-horizon REBOUND runs are not proof of billion-year stability
- Hill and AMD diagnostics are conditional on the assumptions under which they are typically used

## Decision labels in the code

The screening logic uses the following labels explicitly:
- `ABSTAIN_INSUFFICIENT_INFORMATION`
- `NUMERICAL_FOLLOW_UP_REQUIRED`
- `SCREENABLE_UNDER_TESTED_CRITERIA`

The project stores these labels in the screening outputs and keeps the interpretation explicit in the report files.

## Outputs produced

The project writes its main results to:
- `outputs/tables/` for system validation, pair diagnostics, AMD metrics, screening decisions, simulation metadata and runtime summaries
- `outputs/simulations/` for structured JSON output from the finite-horizon numerical runs
- `outputs/figures/` for scientific plots
- `outputs/logs/` for execution logs

The generated figures are diagnostic outputs and are intended for inspection, not for claiming new physics.

## Actual results and limitation statements

The current repository includes a valid project pipeline and test suite, but it does not claim the following:
- universal long-term stability for all compact systems
- resonance proof from period-ratio proximity alone
- a mature astrophysical production tool
- a false claim that all five systems were numerically integrated when only selected systems have saved REBOUND runs

## Reproducibility notes

This prototype is intended to be transparent about:
- raw inputs retained separately from processed data
- project configuration in `config.yaml`
- deterministic seeds where used for synthetic or numerical runs
- saved outputs under `outputs/`
- scientific assumptions kept visible in the code and reports

## License

This project is distributed under the MIT License. See `LICENSE` for details.

## References and context

This prototype draws from standard analytical and numerical methods, including:
- Kepler’s third law
- mutual Hill-separation arguments
- AMD-based screening diagnostics
- near-commensurability proximity diagnostics
- finite-horizon REBOUND integration
