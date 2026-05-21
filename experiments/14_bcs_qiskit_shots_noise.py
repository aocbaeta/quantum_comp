from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from bcs import reduced_bcs_terms
from bcs_qiskit import (
    add_all_qubit_measurements,
    bcs_trotter_circuit,
    counts_pair_observables,
    depolarizing_noise_model,
    run_counts,
    simulate_bcs_trotter_circuit,
    statevector_pair_observables,
)
from quantum_colors import QUANTUM_COLORS, apply_quantum_style


def write_rows(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_total_pairs(rows: list[dict[str, float | str]], exact_total: float, path: Path) -> None:
    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for mode, color in [
        ("ideal_shots", QUANTUM_COLORS["qubit_cyan"]),
        ("noisy_shots", QUANTUM_COLORS["phase_red"]),
    ]:
        selected = [row for row in rows if row["mode"] == mode]
        ax.plot(
            [row["shots"] for row in selected],
            [row["total_pair_number"] for row in selected],
            marker="o",
            linewidth=2.0,
            color=color,
            label=mode,
        )
    ax.axhline(
        exact_total,
        color=QUANTUM_COLORS["cooper_gold"],
        linestyle="--",
        linewidth=2.0,
        label="statevector",
    )
    ax.set_xscale("log", base=2)
    ax.set_xlabel("shots")
    ax.set_ylabel("estimated total pair number")
    ax.set_title("BCS Qiskit measurement: ideal vs noisy shots")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_occupations(rows: list[dict[str, float | str]], exact: dict[str, float], path: Path) -> None:
    apply_quantum_style()
    shots = max(row["shots"] for row in rows if row["mode"] == "ideal_shots")
    selected = [row for row in rows if row["shots"] == shots]
    labels = [f"n_{index}" for index in range(4)]
    x = range(len(labels))
    width = 0.24
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.bar(
        [value - width for value in x],
        [exact[label] for label in labels],
        width=width,
        label="statevector",
        color=QUANTUM_COLORS["cooper_gold"],
    )
    for offset, mode, color in [
        (0.0, "ideal_shots", QUANTUM_COLORS["qubit_cyan"]),
        (width, "noisy_shots", QUANTUM_COLORS["phase_red"]),
    ]:
        row = next(item for item in selected if item["mode"] == mode)
        ax.bar(
            [value + offset for value in x],
            [row[label] for label in labels],
            width=width,
            label=f"{mode} {int(shots)}",
            color=color,
        )
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("pair occupation")
    ax.set_title("Measured BCS pair occupations")
    ax.grid(alpha=0.25, axis="y")
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
    seed = 20260520

    terms = reduced_bcs_terms(xi, g)
    circuit = bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    measured = add_all_qubit_measurements(circuit)
    state = simulate_bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    exact = statevector_pair_observables(state, len(xi))
    noise_model = depolarizing_noise_model(p1=0.002, p2=0.02)

    rows: list[dict[str, float | str]] = []
    for shots in shots_values:
        for mode, noise in [("ideal_shots", None), ("noisy_shots", noise_model)]:
            counts = run_counts(measured, shots=shots, seed=seed + shots, noise_model=noise)
            observed = counts_pair_observables(counts, len(xi))
            row = {
                "mode": mode,
                "shots": float(shots),
                "time": float(time),
                "steps": float(steps),
                "order": float(order),
                "exact_total_pair_number": exact["total_pair_number"],
                "total_pair_number": observed["total_pair_number"],
                "total_pair_error": abs(observed["total_pair_number"] - exact["total_pair_number"]),
            }
            for index in range(len(xi)):
                key = f"n_{index}"
                row[f"exact_{key}"] = exact[key]
                row[key] = observed[key]
                row[f"{key}_error"] = abs(observed[key] - exact[key])
            rows.append(row)

    table_path = ROOT / "results" / "tables" / "bcs_qiskit_shots_noise.csv"
    write_rows(table_path, rows)

    figures_dir = ROOT / "results" / "figures"
    plot_total_pairs(rows, exact["total_pair_number"], figures_dir / "bcs_qiskit_shots_noise_total_pairs.png")
    plot_occupations(rows, exact, figures_dir / "bcs_qiskit_shots_noise_occupations.png")

    print(f"table:  {table_path}")
    print(f"figure: {figures_dir / 'bcs_qiskit_shots_noise_total_pairs.png'}")
    print(f"figure: {figures_dir / 'bcs_qiskit_shots_noise_occupations.png'}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
