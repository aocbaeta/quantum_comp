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
    linear_zero_noise_extrapolation,
    run_pauli_energy_shots,
    scaled_depolarizing_noise_model,
    simulate_bcs_trotter_circuit,
    statevector_pauli_energy,
)
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def write_rows(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_zne(rows: list[dict[str, float | str]], summary: dict[str, float], path: Path) -> None:
    apply_quantum_style()
    x = [row["noise_scale"] for row in rows if row["mode"] == "scaled_noise"]
    y = [row["energy"] for row in rows if row["mode"] == "scaled_noise"]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.plot(x, y, "o", color=QUANTUM_COLORS["phase_red"], label="noisy shots")
    fit_x = [0.0, max(x)]
    fit_y = [summary["mitigated_energy"] + summary["noise_slope"] * value for value in fit_x]
    ax.plot(fit_x, fit_y, "--", color=QUANTUM_COLORS["qubit_cyan"], linewidth=2.0, label="linear ZNE fit")
    ax.axhline(summary["statevector_energy"], color=QUANTUM_COLORS["fermion_green"], linestyle=":", linewidth=2.0, label="statevector")
    ax.axhline(summary["exact_energy"], color=QUANTUM_COLORS["cooper_gold"], linestyle="-.", linewidth=2.0, label="exact")
    ax.scatter([0.0], [summary["mitigated_energy"]], color=QUANTUM_COLORS["bra_purple"], s=80, label="mitigated")
    ax.set_xlabel("noise scale")
    ax.set_ylabel("energy")
    ax.set_title("Zero-noise extrapolation for BCS Pauli-shot energy")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_error_bars(rows: list[dict[str, float | str]], summary: dict[str, float], path: Path) -> None:
    apply_quantum_style()
    labels = ["noisy x1", "mitigated"]
    noisy = next(row for row in rows if row["mode"] == "scaled_noise" and row["noise_scale"] == 1.0)
    errors = [
        noisy["abs_error_vs_statevector"],
        summary["mitigated_abs_error_vs_statevector"],
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.bar(labels, errors, color=[QUANTUM_COLORS["phase_red"], QUANTUM_COLORS["bra_purple"]])
    ax.set_ylabel("|E - E_statevector|")
    ax.set_title("Energy error before and after mitigation")
    ax.grid(alpha=0.25, axis="y")
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
    shots = 4096
    seed = 20260522
    noise_scales = [1.0, 2.0, 3.0]
    base_p1 = 0.0005
    base_p2 = 0.005

    terms = reduced_bcs_terms(xi, g)
    hamiltonian = reduced_bcs_matrix(xi, g)
    initial = computational_basis_state(len(xi), occupied)
    exact_state = exact_evolve_state(hamiltonian, initial, time)
    exact_energy = statevector_pauli_energy(exact_state, terms)

    circuit = bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    qiskit_state = simulate_bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    statevector_energy = statevector_pauli_energy(qiskit_state, terms)

    rows: list[dict[str, float | str]] = []
    for scale in noise_scales:
        noise_model = scaled_depolarizing_noise_model(scale, base_p1=base_p1, base_p2=base_p2)
        estimate = run_pauli_energy_shots(
            circuit,
            terms,
            shots=shots,
            seed=seed + int(scale * 100),
            noise_model=noise_model,
        )
        rows.append(
            {
                "mode": "scaled_noise",
                "noise_scale": float(scale),
                "shots": float(shots),
                "base_p1": base_p1,
                "base_p2": base_p2,
                "exact_energy": exact_energy,
                "statevector_energy": statevector_energy,
                "energy": estimate["energy"],
                "abs_error_vs_exact": abs(estimate["energy"] - exact_energy),
                "abs_error_vs_statevector": abs(estimate["energy"] - statevector_energy),
            }
        )

    zne = linear_zero_noise_extrapolation(
        [row["noise_scale"] for row in rows],
        [row["energy"] for row in rows],
    )
    summary = {
        "mode": "linear_zne",
        "noise_scale": 0.0,
        "shots": float(shots),
        "exact_energy": exact_energy,
        "statevector_energy": statevector_energy,
        "energy": zne["mitigated_energy"],
        "abs_error_vs_exact": abs(zne["mitigated_energy"] - exact_energy),
        "abs_error_vs_statevector": abs(zne["mitigated_energy"] - statevector_energy),
        "noise_slope": zne["noise_slope"],
        "fit_rmse": zne["fit_rmse"],
        "mitigated_energy": zne["mitigated_energy"],
        "mitigated_abs_error_vs_statevector": abs(zne["mitigated_energy"] - statevector_energy),
    }
    rows.append(summary)

    table_path = ROOT / "results" / "tables" / "bcs_qiskit_error_mitigation.csv"
    write_rows(table_path, rows)

    figures_dir = ROOT / "results" / "figures"
    plot_zne(rows, summary, figures_dir / "bcs_qiskit_error_mitigation_zne.png")
    plot_error_bars(rows, summary, figures_dir / "bcs_qiskit_error_mitigation_errors.png")

    print(f"table:  {table_path}")
    print(f"figure: {figures_dir / 'bcs_qiskit_error_mitigation_zne.png'}")
    print(f"figure: {figures_dir / 'bcs_qiskit_error_mitigation_errors.png'}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
