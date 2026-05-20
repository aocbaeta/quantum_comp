from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hubbard import ground_state, pauli_decompose_2q_matrix, two_site_spinless_hubbard_matrix
from vqe_runner import run_statevector_vqe


def main() -> None:
    matrix = two_site_spinless_hubbard_matrix(t=1.0, u=2.0)
    exact_energy, _ = ground_state(matrix)
    hamiltonian = pauli_decompose_2q_matrix(matrix)
    result = run_statevector_vqe(hamiltonian, exact_energy=exact_energy, reps=2, maxiter=250)

    out = ROOT / "results" / "tables" / "vqe_hubbard.csv"
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["exact_energy", "vqe_energy", "absolute_error"])
        writer.writeheader()
        writer.writerow(
            {
                "exact_energy": result.exact_energy,
                "vqe_energy": result.vqe_energy,
                "absolute_error": result.absolute_error,
            }
        )

    print(f"saved: {out}")
    print(f"Exact energy: {result.exact_energy:.10f}")
    print(f"VQE energy:   {result.vqe_energy:.10f}")
    print(f"Abs. error:   {result.absolute_error:.3e}")


if __name__ == "__main__":
    main()
