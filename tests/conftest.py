"""Ensure the project root is importable during pytest collection.

This is required because the code is organised as a src-based package in a
workspace folder without an installed editable package yet.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
