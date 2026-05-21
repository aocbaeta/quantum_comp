from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import numpy as np

from bcs import (
    bcs_time_observables,
    computational_basis_state,
    exact_evolve_state,
    pair_correlation_matrix,
    reduced_bcs_matrix,
    reduced_bcs_terms,
    trotter_evolve_state,
)
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def write_rows(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_gap_and_condensate(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    times = [row["time"] for row in rows]
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 7.0), sharex=True)

    axes[0].plot(
        times,
        [row["exact_gap_proxy"] for row in rows],
        color=QUANTUM_COLORS["cooper_gold"],
        label="exact",
        linewidth=2.0,
    )
    axes[0].plot(
        times,
        [row["trotter_gap_proxy"] for row in rows],
        "--",
        color=QUANTUM_COLORS["qubit_cyan"],
        label="Trotter order 2",
        linewidth=2.0,
    )
    axes[0].set_ylabel("effective gap proxy")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    axes[1].plot(
        times,
        [row["exact_condensate_eigenvalue"] for row in rows],
        color=QUANTUM_COLORS["fermion_green"],
        label="exact",
        linewidth=2.0,
    )
    axes[1].plot(
        times,
        [row["trotter_condensate_eigenvalue"] for row in rows],
        "--",
        color=QUANTUM_COLORS["phase_red"],
        label="Trotter order 2",
        linewidth=2.0,
    )
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("largest pair-correlation eigenvalue")
    axes[1].legend()
    axes[1].grid(alpha=0.25)

    fig.suptitle("Reduced BCS observables for paper figures")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_pair_occupations(rows: list[dict[str, float]], path: Path) -> None:
    apply_quantum_style()
    times = [row["time"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for index in range(4):
        ax.plot(times, [row[f"exact_n_{index}"] for row in rows], label=f"mode {index}")
    ax.set_xlabel("time")
    ax.set_ylabel("pair occupation")
    ax.set_title("Exact pair occupations during BCS dynamics")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_correlation_heatmap(matrix: np.ndarray, path: Path, title: str) -> None:
    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(6.0, 5.2))
    image = ax.imshow(np.abs(matrix), cmap="viridis", origin="upper")
    ax.set_xlabel("annihilated pair mode j")
    ax.set_ylabel("created pair mode i")
    ax.set_title(title)
    ax.set_xticks(range(matrix.shape[0]))
    ax.set_yticks(range(matrix.shape[0]))
    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("|<b_i^dagger b_j>|")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    g = 0.8
    occupied = [0, 1]
    final_time = 6.0
    trotter_steps = 256
    times = np.linspace(0.0, final_time, 81)

    rows = bcs_time_observables(
        xi=xi,
        g=g,
        occupied=occupied,
        times=times,
        trotter_steps=trotter_steps,
        trotter_order=2,
    )

    table_path = ROOT / "results" / "tables" / "bcs_paper_observables.csv"
    write_rows(table_path, rows)

    figures_dir = ROOT / "results" / "figures"
    plot_gap_and_condensate(rows, figures_dir / "bcs_gap_condensate_time.png")
    plot_pair_occupations(rows, figures_dir / "bcs_pair_occupations_time.png")

    hamiltonian = reduced_bcs_matrix(xi, g)
    terms = reduced_bcs_terms(xi, g)
    initial = computational_basis_state(len(xi), occupied)
    exact_final = exact_evolve_state(hamiltonian, initial, final_time)
    trotter_final = trotter_evolve_state(terms, initial, final_time, trotter_steps, order=2)
    plot_correlation_heatmap(
        pair_correlation_matrix(exact_final, len(xi)),
        figures_dir / "bcs_pair_correlation_exact_final.png",
        "Exact final pair-correlation matrix",
    )
    plot_correlation_heatmap(
        pair_correlation_matrix(trotter_final, len(xi)),
        figures_dir / "bcs_pair_correlation_trotter_final.png",
        "Trotter final pair-correlation matrix",
    )

    print(f"table: {table_path}")
    print(f"figure: {figures_dir / 'bcs_gap_condensate_time.png'}")
    print(f"figure: {figures_dir / 'bcs_pair_occupations_time.png'}")
    print(f"figure: {figures_dir / 'bcs_pair_correlation_exact_final.png'}")
    print(f"figure: {figures_dir / 'bcs_pair_correlation_trotter_final.png'}")
    print("final row:")
    print(rows[-1])


if __name__ == "__main__":
    main()
