from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import numpy as np

from bcs import green_spectral_density, pair_retarded_green_series
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def write_rows(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_green_time(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    times = [row["time"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.plot(times, [row["real"] for row in rows], label="Re G^R_00(t)", linewidth=2.0)
    ax.plot(
        times,
        [row["imag"] for row in rows],
        label="Im G^R_00(t)",
        linewidth=2.0,
        color=QUANTUM_COLORS["cooper_gold"],
    )
    ax.plot(
        times,
        [row["abs"] for row in rows],
        label="|G^R_00(t)|",
        linewidth=1.5,
        color=QUANTUM_COLORS["fermion_green"],
        alpha=0.85,
    )
    ax.set_xlabel("time")
    ax.set_ylabel("pair Green response")
    ax.set_title("Retarded pair Green function")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_spectral_density(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    selected = [row for row in rows if -8.0 <= row["omega"] <= 8.0]
    ax.plot(
        [row["omega"] for row in selected],
        [row["spectral_weight"] for row in selected],
        linewidth=2.0,
        color=QUANTUM_COLORS["phase_red"],
    )
    ax.axhline(0.0, color=QUANTUM_COLORS["silver_eigen"], linewidth=0.8, alpha=0.6)
    ax.set_xlabel("omega")
    ax.set_ylabel("-Im G^R(omega) / pi")
    ax.set_title("Approximate pair spectral density")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    g = 0.8
    occupied = [0, 1]
    eta = 0.04
    times = np.linspace(0.0, 18.0, 361)

    green_rows = pair_retarded_green_series(
        xi=xi,
        g=g,
        occupied=occupied,
        i=0,
        j=0,
        times=times,
        eta=eta,
    )
    values = [row["real"] + 1j * row["imag"] for row in green_rows]
    spectral_rows = green_spectral_density(times, values)

    green_path = ROOT / "results" / "tables" / "bcs_pair_green_retarded.csv"
    spectral_path = ROOT / "results" / "tables" / "bcs_pair_green_spectral_density.csv"
    write_rows(green_path, green_rows)
    write_rows(spectral_path, spectral_rows)

    figures_dir = ROOT / "results" / "figures"
    plot_green_time(green_rows, figures_dir / "bcs_pair_green_time.png")
    plot_spectral_density(spectral_rows, figures_dir / "bcs_pair_green_spectrum.png")

    peak = max(spectral_rows, key=lambda row: row["spectral_weight"])
    print(f"green:   {green_path}")
    print(f"spectrum:{spectral_path}")
    print(f"figure:  {figures_dir / 'bcs_pair_green_time.png'}")
    print(f"figure:  {figures_dir / 'bcs_pair_green_spectrum.png'}")
    print(f"peak:    {peak}")


if __name__ == "__main__":
    main()
