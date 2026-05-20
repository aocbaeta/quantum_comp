from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
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


def add_all_qubit_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    measured = circuit.copy()
    measured.measure_all()
    return measured


def pauli_measurement_circuit(circuit: QuantumCircuit, label: str) -> QuantumCircuit:
    measured = circuit.copy()
    for qubit, symbol in enumerate(label):
        if symbol == "I" or symbol == "Z":
            continue
        if symbol == "X":
            measured.h(qubit)
        elif symbol == "Y":
            measured.sdg(qubit)
            measured.h(qubit)
        else:
            raise ValueError(f"unsupported Pauli symbol: {symbol}")
    measured.measure_all()
    return measured


def counts_pair_observables(counts: dict[str, int], n_qubits: int) -> dict[str, float]:
    shots = sum(counts.values())
    if shots <= 0:
        raise ValueError("counts must contain at least one shot")
    occupations = [0.0] * n_qubits
    for bitstring, count in counts.items():
        cleaned = bitstring.replace(" ", "")
        if len(cleaned) != n_qubits:
            raise ValueError(f"unexpected bitstring length: {bitstring}")
        for qubit in range(n_qubits):
            occupations[qubit] += count * int(cleaned[n_qubits - 1 - qubit])
    occupations = [value / shots for value in occupations]
    total_pairs = float(sum(occupations))
    result = {"shots": float(shots), "total_pair_number": total_pairs}
    for index, value in enumerate(occupations):
        result[f"n_{index}"] = float(value)
    return result


def pauli_expectation_from_counts(counts: dict[str, int], label: str) -> float:
    shots = sum(counts.values())
    if shots <= 0:
        raise ValueError("counts must contain at least one shot")
    n_qubits = len(label)
    total = 0.0
    for bitstring, count in counts.items():
        cleaned = bitstring.replace(" ", "")
        if len(cleaned) != n_qubits:
            raise ValueError(f"unexpected bitstring length: {bitstring}")
        eigenvalue = 1
        for qubit, symbol in enumerate(label):
            if symbol == "I":
                continue
            bit = int(cleaned[n_qubits - 1 - qubit])
            eigenvalue *= -1 if bit else 1
        total += count * eigenvalue
    return float(total / shots)


def estimate_pauli_energy_from_counts(
    term_counts: dict[str, dict[str, int]],
    terms: list[PauliMatrixTerm],
) -> dict[str, float]:
    energy = 0.0
    result: dict[str, float] = {}
    for index, term in enumerate(terms):
        expectation = pauli_expectation_from_counts(term_counts[term.label], term.label)
        contribution = float(term.coeff * expectation)
        result[f"term_{index}_{term.label}_expectation"] = expectation
        result[f"term_{index}_{term.label}_energy"] = contribution
        energy += contribution
    result["energy"] = float(energy)
    return result


def statevector_pair_observables(state: np.ndarray, n_qubits: int) -> dict[str, float]:
    probabilities = np.abs(np.asarray(state, dtype=complex)) ** 2
    occupations = [0.0] * n_qubits
    for basis_index, probability in enumerate(probabilities):
        bits = f"{basis_index:0{n_qubits}b}"
        for qubit in range(n_qubits):
            occupations[qubit] += float(probability) * int(bits[qubit])
    result = {"total_pair_number": float(sum(occupations))}
    for index, value in enumerate(occupations):
        result[f"n_{index}"] = float(value)
    return result


def statevector_pauli_energy(state: np.ndarray, terms: list[PauliMatrixTerm]) -> float:
    state_array = np.asarray(state, dtype=complex)
    return float(
        sum(
            np.real(np.vdot(state_array, term.matrix @ state_array))
            for term in terms
        )
    )


def depolarizing_noise_model(p1: float = 0.002, p2: float = 0.02) -> NoiseModel:
    noise_model = NoiseModel()
    one_qubit_error = depolarizing_error(p1, 1)
    two_qubit_error = depolarizing_error(p2, 2)
    noise_model.add_all_qubit_quantum_error(one_qubit_error, ["x", "sx", "rz"])
    noise_model.add_all_qubit_quantum_error(two_qubit_error, ["cx"])
    return noise_model


def run_counts(
    circuit: QuantumCircuit,
    shots: int,
    seed: int = 1234,
    noise_model: NoiseModel | None = None,
) -> dict[str, int]:
    simulator = AerSimulator(noise_model=noise_model, seed_simulator=seed)
    compiled = transpile(circuit, simulator, seed_transpiler=seed)
    result = simulator.run(compiled, shots=shots).result()
    return dict(result.get_counts())


def run_pauli_energy_shots(
    circuit: QuantumCircuit,
    terms: list[PauliMatrixTerm],
    shots: int,
    seed: int = 1234,
    noise_model: NoiseModel | None = None,
) -> dict[str, float]:
    term_counts = {}
    for offset, term in enumerate(terms):
        measured = pauli_measurement_circuit(circuit, term.label)
        term_counts[term.label] = run_counts(
            measured,
            shots=shots,
            seed=seed + offset,
            noise_model=noise_model,
        )
    result = estimate_pauli_energy_from_counts(term_counts, terms)
    result["shots"] = float(shots)
    return result
