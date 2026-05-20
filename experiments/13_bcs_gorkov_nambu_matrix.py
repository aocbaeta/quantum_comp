from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import numpy as np

from bcs import gorkov_nambu_green_matrix_series, green_spectral_density
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def write_rows(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_nambu_channels(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    times = [row["time"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for key, color in [
        ("G_abs", QUANTUM_COLORS["qubit_cyan"]),
        ("F_abs", QUANTUM_COLORS["cooper_gold"]),
        ("Fdag_abs", QUANTUM_COLORS["fermion_green"]),
        ("Gdag_abs", QUANTUM_COLORS["phase_red"]),
    ]:
        ax.plot(times, [row[key] for row in rows], label=key.replace("_abs", ""), color=color, linewidth=2.0)
    ax.set_xlabel("time")
    ax.set_ylabel("channel magnitude")
    ax.set_title("Gorkov-Nambu retarded Green matrix channels")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_spectral_trace(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    selected = [row for row in rows if -8.0 <= row["omega"] <= 8.0]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.plot(
        [row["omega"] for row in selected],
        [row["spectral_weight"] for row in selected],
        color=QUANTUM_COLORS["bra_purple"],
        linewidth=2.0,
    )
    ax.axhline(0.0, color=QUANTUM_COLORS["silver_eigen"], linewidth=0.8, alpha=0.6)
    ax.set_xlabel("omega")
    ax.set_ylabel("-Im Tr G_Nambu(omega) / pi")
    ax.set_title("Approximate Gorkov-Nambu spectral trace")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    g = 0.8
    eta = 0.04
    times = np.linspace(0.0, 18.0, 361)

    theta = np.pi / 5
    u = [np.cos(theta)] * 4
    v = [
        np.sin(theta),
        np.sin(theta) * np.exp(0.25j),
        np.sin(theta) * np.exp(0.5j),
        np.sin(theta) * np.exp(0.75j),
    ]

    rows = gorkov_nambu_green_matrix_series(
        xi=xi,
        g=g,
        u=u,
        v=v,
        i=0,
        j=0,
        times=times,
        eta=eta,
    )
    trace_values = [row["trace_real"] + 1j * row["trace_imag"] for row in rows]
    spectral_rows = green_spectral_density(times, trace_values)

    table_path = ROOT / "results" / "tables" / "bcs_gorkov_nambu_time.csv"
    spectrum_path = ROOT / "results" / "tables" / "bcs_gorkov_nambu_spectral_trace.csv"
    write_rows(table_path, rows)
    write_rows(spectrum_path, spectral_rows)

    figures_dir = ROOT / "results" / "figures"
    plot_nambu_channels(rows, figures_dir / "bcs_gorkov_nambu_channels.png")
    plot_spectral_trace(spectral_rows, figures_dir / "bcs_gorkov_nambu_spectral_trace.png")

    peak = max(spectral_rows, key=lambda row: row["spectral_weight"])
    print(f"time:    {table_path}")
    print(f"spectrum:{spectrum_path}")
    print(f"figure:  {figures_dir / 'bcs_gorkov_nambu_channels.png'}")
    print(f"figure:  {figures_dir / 'bcs_gorkov_nambu_spectral_trace.png'}")
    print(f"peak:    {peak}")
    print(f"max |trace|: {max(row['trace_abs'] for row in rows)}")
    print(f"max |det|:   {max(row['det_abs'] for row in rows)}")


if __name__ == "__main__":
    main()
