from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import RXXGate, RYYGate
from qiskit.quantum_info import Statevector

from bcs import PauliMatrixTerm


def _active_qubits(label: str) -> list[int]:
    return [index for index, symbol in enumerate(label) if symbol != "I"]


def append_pauli_evolution(circuit: QuantumCircuit, term: PauliMatrixTerm, dt: float) -> None:
    active = _active_qubits(term.label)
    theta = 2.0 * term.coeff * dt
    if len(active) == 1 and term.label[active[0]] == "Z":
        circuit.rz(theta, active[0])
        return
    if len(active) == 2:
        a, b = active
        symbols = term.label[a] + term.label[b]
        if symbols == "XX":
            circuit.append(RXXGate(theta), [a, b])
            return
        if symbols == "YY":
            circuit.append(RYYGate(theta), [a, b])
            return
    raise ValueError(f"Unsupported Pauli evolution term: {term.label}")


def bcs_trotter_circuit(
    terms: list[PauliMatrixTerm],
    time: float,
    steps: int,
    order: int = 1,
    occupied: list[int] | None = None,
) -> QuantumCircuit:
    if steps <= 0:
        raise ValueError("steps must be positive")
    n_qubits = len(terms[0].label)
    circuit = QuantumCircuit(n_qubits)
    for index in occupied or []:
        circuit.x(index)

    dt = time / steps
    for _ in range(steps):
        if order == 1:
            for term in terms:
                append_pauli_evolution(circuit, term, dt)
        elif order == 2:
            for term in terms:
                append_pauli_evolution(circuit, term, dt / 2)
            for term in reversed(terms):
                append_pauli_evolution(circuit, term, dt / 2)
        else:
            raise ValueError("only order 1 and 2 are supported")
    return circuit


def qiskit_state_to_matrix_order(state: np.ndarray, n_qubits: int) -> np.ndarray:
    converted = np.zeros_like(state, dtype=complex)
    for qiskit_index, amplitude in enumerate(state):
        bits_qiskit = [(qiskit_index >> bit) & 1 for bit in range(n_qubits)]
        matrix_index = int("".join(str(bit) for bit in bits_qiskit), 2)
        converted[matrix_index] = amplitude
    return converted


def simulate_bcs_trotter_circuit(
    terms: list[PauliMatrixTerm],
    time: float,
    steps: int,
    order: int,
    occupied: list[int],
) -> np.ndarray:
    circuit = bcs_trotter_circuit(terms, time=time, steps=steps, order=order, occupied=occupied)
    state = np.asarray(Statevector.from_instruction(circuit).data, dtype=complex)
    return qiskit_state_to_matrix_order(state, len(terms[0].label))
