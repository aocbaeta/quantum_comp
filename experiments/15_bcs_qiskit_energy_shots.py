from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from bcs import computational_basis_state, exact_evolve_state, reduced_bcs_matrix, reduced_bcs_terms
from bcs_qiskit import (
    bcs_trotter_circuit,
    depolarizing_noise_model,
    run_pauli_energy_shots,
    simulate_bcs_trotter_circuit,
    statevector_pauli_energy,
)
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def write_rows(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_energy_values(rows: list[dict[str, float | str]], exact: float, statevector: float, path: Path) -> None:
    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for mode, color in [
        ("ideal_shots", QUANTUM_COLORS["qubit_cyan"]),
        ("noisy_shots", QUANTUM_COLORS["phase_red"]),
    ]:
        selected = [row for row in rows if row["mode"] == mode]
        ax.plot(
            [row["shots"] for row in selected],
            [row["energy"] for row in selected],
            marker="o",
            linewidth=2.0,
            color=color,
            label=mode,
        )
    ax.axhline(exact, color=QUANTUM_COLORS["cooper_gold"], linestyle="--", linewidth=2.0, label="exact")
    ax.axhline(statevector, color=QUANTUM_COLORS["fermion_green"], linestyle=":", linewidth=2.0, label="statevector")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("shots per Pauli term")
    ax.set_ylabel("energy estimate")
    ax.set_title("BCS energy from Pauli-term shot measurements")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_energy_errors(rows: list[dict[str, float | str]], path: Path) -> None:
    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for mode, color in [
        ("ideal_shots", QUANTUM_COLORS["qubit_cyan"]),
        ("noisy_shots", QUANTUM_COLORS["phase_red"]),
    ]:
        selected = [row for row in rows if row["mode"] == mode]
        ax.plot(
            [row["shots"] for row in selected],
            [row["abs_error_vs_statevector"] for row in selected],
            marker="o",
            linewidth=2.0,
            color=color,
            label=mode,
        )
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("shots per Pauli term")
    ax.set_ylabel("|E_shots - E_statevector|")
    ax.set_title("BCS shot-energy absolute error")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    g = 0.8
    occupied = [0, 1]
    time = 2.5
    steps = 8
    order = 2
    shots_values = [1024, 4096, 8192, 16384, 32768]
    seed = 20260521

    terms = reduced_bcs_terms(xi, g)
    hamiltonian = reduced_bcs_matrix(xi, g)
    initial = computational_basis_state(len(xi), occupied)
    exact_state = exact_evolve_state(hamiltonian, initial, time)
    exact_energy = statevector_pauli_energy(exact_state, terms)

    circuit = bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    qiskit_state = simulate_bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    statevector_energy = statevector_pauli_energy(qiskit_state, terms)
    noise_model = depolarizing_noise_model(p1=0.002, p2=0.02)

    rows: list[dict[str, float | str]] = []
    for shots in shots_values:
        for mode, noise in [("ideal_shots", None), ("noisy_shots", noise_model)]:
            estimate = run_pauli_energy_shots(
                circuit,
                terms,
                shots=shots,
                seed=seed + shots,
                noise_model=noise,
            )
            row = {
                "mode": mode,
                "shots": float(shots),
                "time": float(time),
                "steps": float(steps),
                "order": float(order),
                "exact_energy": exact_energy,
                "statevector_energy": statevector_energy,
                "energy": estimate["energy"],
                "abs_error_vs_exact": abs(estimate["energy"] - exact_energy),
                "abs_error_vs_statevector": abs(estimate["energy"] - statevector_energy),
            }
            rows.append(row)

    table_path = ROOT / "results" / "tables" / "bcs_qiskit_energy_shots.csv"
    write_rows(table_path, rows)

    figures_dir = ROOT / "results" / "figures"
    plot_energy_values(rows, exact_energy, statevector_energy, figures_dir / "bcs_qiskit_energy_shots_values.png")
    plot_energy_errors(rows, figures_dir / "bcs_qiskit_energy_shots_error.png")

    print(f"table:  {table_path}")
    print(f"figure: {figures_dir / 'bcs_qiskit_energy_shots_values.png'}")
    print(f"figure: {figures_dir / 'bcs_qiskit_energy_shots_error.png'}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
