#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from algebra import commutator, X, Y, Z


def python_commutator() -> str:
    return (
        "from algebra import X, Y, Z, commutator\n"
        "comm = commutator(X, Y)\n"
        "# comm == 2j * Z\n"
    )


def qiskit_commutator() -> str:
    return (
        "from qiskit.quantum_info import Operator\n"
        "X = Operator.from_label('X')\n"
        "Y = Operator.from_label('Y')\n"
        "Z = Operator.from_label('Z')\n"
        "comm = X @ Y - Y @ X\n"
        "# comm.data == 2j * Z.data\n"
    )


def cirq_commutator() -> str:
    return (
        "import cirq\n"
        "import numpy as np\n"
        "X = cirq.unitary(cirq.X)\n"
        "Y = cirq.unitary(cirq.Y)\n"
        "Z = cirq.unitary(cirq.Z)\n"
        "comm = X @ Y - Y @ X\n"
        "# comm == 2j * Z\n"
    )


def pennylane_commutator() -> str:
    return (
        "import numpy as np\n"
        "X = np.array([[0, 1], [1, 0]], dtype=complex)\n"
        "Y = np.array([[0, -1j], [1j, 0]], dtype=complex)\n"
        "Z = np.array([[1, 0], [0, -1]], dtype=complex)\n"
        "comm = X @ Y - Y @ X\n"
        "# comm == 2j * Z\n"
    )


def main() -> None:
    print("# Python commutator (src/algebra.py)")
    print(python_commutator())
    print("# Qiskit equivalent")
    print(qiskit_commutator())
    print("# Cirq equivalent")
    print(cirq_commutator())
    print("# PennyLane equivalent")
    print(pennylane_commutator())


if __name__ == "__main__":
    main()
