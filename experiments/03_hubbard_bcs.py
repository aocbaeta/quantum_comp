from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from hubbard import ground_state, pauli_decompose_2q_matrix, two_site_bcs_matrix, two_site_spinless_hubbard_matrix


def summarize(name: str, matrix: np.ndarray) -> dict[str, float | str]:
    energy, _state = ground_state(matrix)
    pauli = pauli_decompose_2q_matrix(matrix)
    return {
        "model": name,
        "ground_energy": energy,
        "pauli_terms": len(pauli),
        "pauli_sum": str(pauli),
    }


def main() -> None:
    rows = [
        summarize("spinless_hubbard_2site", two_site_spinless_hubbard_matrix(t=1.0, u=2.0)),
        summarize("bcs_pair_2mode", two_site_bcs_matrix(epsilon=1.0, delta=0.4)),
    ]
    out = ROOT / "results" / "tables" / "hubbard_bcs_summary.csv"
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["model", "ground_energy", "pauli_terms", "pauli_sum"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved: {out}")
    for row in rows:
        print(f"{row['model']}: E0={row['ground_energy']:.8f}, terms={row['pauli_terms']}")
        print(row["pauli_sum"])


if __name__ == "__main__":
    main()
