from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import numpy as np

from bcs import anomalous_gorkov_green_series, green_spectral_density
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def write_rows(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_anomalous_time(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    times = [row["time"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.plot(
        times,
        [row["F_ann_ann_real"] for row in rows],
        label="Re F^R_00(t)",
        linewidth=2.0,
        color=QUANTUM_COLORS["qubit_cyan"],
    )
    ax.plot(
        times,
        [row["F_ann_ann_imag"] for row in rows],
        label="Im F^R_00(t)",
        linewidth=2.0,
        color=QUANTUM_COLORS["cooper_gold"],
    )
    ax.plot(
        times,
        [row["F_ann_ann_abs"] for row in rows],
        label="|F^R_00(t)|",
        linewidth=1.4,
        color=QUANTUM_COLORS["fermion_green"],
        alpha=0.85,
    )
    ax.set_xlabel("time")
    ax.set_ylabel("anomalous pair response")
    ax.set_title("Gorkov anomalous retarded Green function")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_anomalous_spectrum(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    selected = [row for row in rows if -8.0 <= row["omega"] <= 8.0]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.plot(
        [row["omega"] for row in selected],
        [row["spectral_weight"] for row in selected],
        linewidth=2.0,
        color=QUANTUM_COLORS["bra_purple"],
    )
    ax.axhline(0.0, color=QUANTUM_COLORS["silver_eigen"], linewidth=0.8, alpha=0.6)
    ax.set_xlabel("omega")
    ax.set_ylabel("-Im F^R(omega) / pi")
    ax.set_title("Approximate anomalous spectral density")
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

    rows = anomalous_gorkov_green_series(
        xi=xi,
        g=g,
        u=u,
        v=v,
        i=0,
        j=0,
        times=times,
        eta=eta,
    )
    values = [row["F_ann_ann_real"] + 1j * row["F_ann_ann_imag"] for row in rows]
    spectrum = green_spectral_density(times, values)

    table_path = ROOT / "results" / "tables" / "bcs_gorkov_anomalous_time.csv"
    spectrum_path = ROOT / "results" / "tables" / "bcs_gorkov_anomalous_spectrum.csv"
    write_rows(table_path, rows)
    write_rows(spectrum_path, spectrum)

    figures_dir = ROOT / "results" / "figures"
    plot_anomalous_time(rows, figures_dir / "bcs_gorkov_anomalous_time.png")
    plot_anomalous_spectrum(spectrum, figures_dir / "bcs_gorkov_anomalous_spectrum.png")

    peak = max(spectrum, key=lambda row: row["spectral_weight"])
    print(f"time:    {table_path}")
    print(f"spectrum:{spectrum_path}")
    print(f"figure:  {figures_dir / 'bcs_gorkov_anomalous_time.png'}")
    print(f"figure:  {figures_dir / 'bcs_gorkov_anomalous_spectrum.png'}")
    print(f"peak:    {peak}")
    print(f"max |F|: {max(row['F_ann_ann_abs'] for row in rows)}")


if __name__ == "__main__":
    main()
