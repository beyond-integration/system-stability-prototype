# Experiment log

## Project status

- Prototype: stability screening workflow
- Validation gate: required pytest suite executed before pipeline execution
- Current status: repository tests pass in the active project environment

## Execution notes

- Raw NASA archive tables are preserved under `data/raw/nasa_archive/`.
- Processed system tables are generated under `data/processed/`.
- Analytical screening diagnostics are computed on validated systems only.
- REBOUND simulations are generated under `outputs/simulations/` and summarised in `outputs/tables/`.

## Scientific audit trail

- Data validation and unit checks are performed before any screening decision.
- Hill, AMD, and resonance diagnostics are reported separately rather than combined without traceability.
- Decision outputs can be traced to the underlying assumptions and warnings.

## Reproducibility

The project is designed to be rerun from a clean environment by installing dependencies from `requirements.txt` and executing the project entry point in `src/main.py`.
