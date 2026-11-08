"""Figure generation for the stability-screening prototype using saved tables."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _format_axis_labels(ax: plt.Axes, labels: list[str], rotation: int = 35) -> None:
    """Rotate long labels to keep plots readable without overlap."""
    if not labels:
        return
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=rotation, ha="right")
    ax.tick_params(axis="x", labelsize=8)


def save_pair_hill_plot(df: pd.DataFrame, path: str | Path) -> None:
    """Plot adjacent pair Hill separations against the idealised threshold."""
    fig, ax = plt.subplots(figsize=(10, 6))
    threshold = 2.0 * 3.0 ** 0.5
    ax.axhline(threshold, color="black", linestyle="--", label=r"$2\sqrt{3}$")
    if not df.empty and "delta" in df.columns:
        pairs = df["pair"].tolist()
        deltas = df["delta"].tolist()
        ax.plot(range(len(pairs)), deltas, marker="o", linestyle="-", linewidth=1.5)
        _format_axis_labels(ax, pairs)
    ax.set_xlabel("Planet pair")
    ax.set_ylabel("Mutual Hill separation")
    ax.set_title("Mutual Hill separation for adjacent pairs")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_amd_plot(df: pd.DataFrame, path: str | Path) -> None:
    """Plot AMD ratios with the threshold at 1."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axhline(1.0, color="black", linestyle="--", label="AMD ratio = 1")
    if not df.empty and "amd_ratio" in df.columns:
        systems = df["system_name"].tolist()
        amd_ratios = df["amd_ratio"].tolist()
        ax.plot(range(len(systems)), amd_ratios, marker="o", linestyle="-", linewidth=1.5)
        _format_axis_labels(ax, systems)
    ax.set_xlabel("System")
    ax.set_ylabel("C / C_c")
    ax.set_title("Classical AMD ratio")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_resonance_plot(df: pd.DataFrame, path: str | Path) -> None:
    """Plot nearest-commensurability offsets for adjacent pairs."""
    fig, ax = plt.subplots(figsize=(10, 6))
    if not df.empty and "fractional_offset" in df.columns:
        pairs = df["pair"].tolist()
        offsets = df["fractional_offset"].tolist()
        ax.plot(range(len(pairs)), offsets, marker="o", linestyle="-", linewidth=1.5)
        _format_axis_labels(ax, pairs)
    ax.set_xlabel("Planet pair")
    ax.set_ylabel("Fractional offset")
    ax.set_title("Resonance proximity")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
