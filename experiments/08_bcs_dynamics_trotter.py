from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from bcs import bcs_dynamics_row, commutator_norm_table, reduced_bcs_terms
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def main() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    g = 0.8
    occupied = [0, 1]
    time = 2.5
    steps_values = [1, 2, 4, 8, 16, 32, 64]

    rows = []
    for order in [1, 2]:
        for steps in steps_values:
            rows.append(
                bcs_dynamics_row(
                    xi=xi,
                    g=g,
                    occupied=occupied,
                    time=time,
                    steps=steps,
                    order=order,
                )
            )

    table_path = ROOT / "results" / "tables" / "bcs_dynamics_trotter.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    comm_rows = commutator_norm_table(reduced_bcs_terms(xi, g))
    comm_path = ROOT / "results" / "tables" / "bcs_commutator_norms.csv"
    with comm_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["left", "right", "left_coeff", "right_coeff", "commutator_norm"],
        )
        writer.writeheader()
        writer.writerows(comm_rows)

    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for order, color in [(1, QUANTUM_COLORS["phase_red"]), (2, QUANTUM_COLORS["qubit_cyan"])]:
        selected = [row for row in rows if int(row["order"]) == order]
        ax.loglog(
            [row["steps"] for row in selected],
            [row["state_error"] for row in selected],
            marker="o",
            color=color,
            label=f"Trotter order {order}",
        )
    ax.set_xlabel("Trotter steps")
    ax.set_ylabel("state vector error")
    ax.set_title("Reduced BCS dynamics: exact vs Trotter")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    figure_path = ROOT / "results" / "figures" / "bcs_trotter_error.png"
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    print(f"table:       {table_path}")
    print(f"commutators: {comm_path}")
    print(f"figure:      {figure_path}")
    print("best rows:")
    for row in rows[-2:]:
        print(row)


if __name__ == "__main__":
    main()
