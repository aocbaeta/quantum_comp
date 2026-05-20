#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PYTHONPATH = ROOT / "src"
sys.path.insert(0, str(PYTHONPATH))

from algebra import X, Y, Z, commutator

try:
    from qiskit.quantum_info import Operator
except ImportError:
    Operator = None

try:
    import cirq
except ImportError:
    cirq = None

try:
    import pennylane as qml
except ImportError:
    qml = None


def matrix_commutator(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def print_check(name: str, result: np.ndarray, expected: np.ndarray) -> None:
    print(f"== {name} ==")
    print(result)
    print("expected:")
    print(expected)
    print("match:", np.allclose(result, expected))
    print()


def python_commutator() -> None:
    print("Python direct commutator using src/algebra.py")
    comm = commutator(X, Y)
    print_check("[X,Y]", comm, 2j * Z)


def qiskit_commutator() -> None:
    if Operator is None:
        print("Qiskit is not installed.")
        return
    X_op = Operator.from_label("X").data
    Y_op = Operator.from_label("Y").data
    Z_op = Operator.from_label("Z").data
    comm = matrix_commutator(X_op, Y_op)
    print_check("Qiskit [X,Y]", comm, 2j * Z_op)


def cirq_commutator() -> None:
    if cirq is None:
        print("Cirq is not installed.")
        return
    X_op = cirq.unitary(cirq.X)
    Y_op = cirq.unitary(cirq.Y)
    Z_op = cirq.unitary(cirq.Z)
    comm = matrix_commutator(X_op, Y_op)
    print_check("Cirq [X,Y]", comm, 2j * Z_op)


def pennylane_commutator() -> None:
    if qml is None:
        print("PennyLane is not installed.")
        return
    X_op = np.array([[0, 1], [1, 0]], dtype=complex)
    Y_op = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z_op = np.array([[1, 0], [0, -1]], dtype=complex)
    comm = matrix_commutator(X_op, Y_op)
    print_check("PennyLane [X,Y]", comm, 2j * Z_op)


def main() -> None:
    python_commutator()
    qiskit_commutator()
    cirq_commutator()
    pennylane_commutator()


if __name__ == "__main__":
    main()
