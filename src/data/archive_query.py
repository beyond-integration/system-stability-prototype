"""NASA Exoplanet Archive TAP helper for retrieving raw source tables."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib import parse, request


NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


def fetch_nasa_archive_table(
    table: str = "ps",
    columns: list[str] | None = None,
    where_clause: str | None = None,
    output_path: str | Path | None = None,
    max_rows: int | None = None,
) -> str | Path:
    """Query the NASA Exoplanet Archive TAP service and save the returned CSV.

    The output is deliberately minimal and explicit: it fetches raw archive tables without
    mutating or reinterpreting the data. The function is intended for initial raw-data
    collection, not for scientific stability decisions.
    """
    if columns is None:
        columns = [
            "hostname",
            "pl_name",
            "pl_orbper",
            "pl_orbpererr1",
            "pl_orbsmax",
            "pl_orbsmaxerr1",
            "pl_massj",
            "pl_massjerr1",
            "pl_eccen",
            "pl_eccenerr1",
            "st_mass",
            "st_masserr1",
            "source",
        ]

    column_text = ", ".join(columns)
    clauses = [f"SELECT {column_text} FROM {table}"]
    if where_clause:
        clauses.append(f"WHERE {where_clause}")
    if max_rows is not None:
        clauses.append(f"LIMIT {int(max_rows)}")
    query = " ".join(clauses)

    payload = parse.urlencode({"query": query})
    url = f"{NASA_TAP_URL}?{payload}"

    with request.urlopen(url, timeout=60) as response:
        csv_text = response.read().decode("utf-8", errors="replace")

    target = Path(output_path) if output_path is not None else Path("data/raw/nasa_archive") / f"{table}_raw.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(csv_text, encoding="utf-8")
    return target


def fetch_system_rows(
    system_name: str,
    table: str = "ps",
    output_dir: str | Path = "data/raw/nasa_archive",
) -> str | Path:
    """Fetch a single host-system table and save it under a system-aware filename."""
    safe_name = system_name.replace(" ", "_").replace("-", "_")
    output_path = Path(output_dir) / f"{safe_name.lower()}_raw.csv"
    where_clause = f"hostname = '{system_name}'"
    return fetch_nasa_archive_table(table=table, where_clause=where_clause, output_path=output_path)
