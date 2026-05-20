from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPERIMENTS = [
    "01_algebra_fermions.py",
    "02_propagator_trotter.py",
    "03_hubbard_bcs.py",
    "04_vqe_hubbard.py",
    "05_zeta_zeros_statistics.py",
    "06_zeta_critical_line_scan.py",
    "08_bcs_dynamics_trotter.py",
    "09_bcs_qiskit_trotter_circuit.py",
    "10_bcs_paper_observables.py",
    "11_bcs_pair_green_function.py",
    "12_bcs_gorkov_anomalous_green.py",
    "13_bcs_gorkov_nambu_matrix.py",
    "14_bcs_qiskit_shots_noise.py",
]


def main() -> None:
    for experiment in EXPERIMENTS:
        path = ROOT / "experiments" / experiment
        print(f"\n== {experiment} ==", flush=True)
        subprocess.run([sys.executable, str(path)], check=True)


if __name__ == "__main__":
    main()
