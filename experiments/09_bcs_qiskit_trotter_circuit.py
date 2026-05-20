from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from bcs import fidelity, reduced_bcs_terms, trotter_evolve_state, computational_basis_state
from bcs_qiskit import bcs_trotter_circuit, simulate_bcs_trotter_circuit


def main() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    g = 0.8
    occupied = [0, 1]
    time = 2.5
    steps = 8
    order = 2
    terms = reduced_bcs_terms(xi, g)
    n_qubits = len(xi)
    initial = computational_basis_state(n_qubits, occupied)
    matrix_state = trotter_evolve_state(terms, initial, time=time, steps=steps, order=order)
    qiskit_state = simulate_bcs_trotter_circuit(
        terms,
        time=time,
        steps=steps,
        order=order,
        occupied=occupied,
    )

    circuit = bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    rows = [
        {
            "time": time,
            "steps": steps,
            "order": order,
            "n_qubits": n_qubits,
            "depth": circuit.depth(),
            "size": circuit.size(),
            "matrix_qiskit_fidelity": fidelity(matrix_state, qiskit_state),
            "state_error": float(np.linalg.norm(matrix_state - qiskit_state)),
        }
    ]
    table_path = ROOT / "results" / "tables" / "bcs_qiskit_trotter_circuit.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    circuit_path = ROOT / "results" / "tables" / "bcs_qiskit_trotter_circuit.txt"
    circuit_path.write_text(circuit.draw(output="text").single_string())

    print(f"table:   {table_path}")
    print(f"circuit: {circuit_path}")
    print(rows[0])


if __name__ == "__main__":
    main()
