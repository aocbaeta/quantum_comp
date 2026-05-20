from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from algebra import I2, X, Y, Z, commutator, is_hermitian, is_unitary, kron_all
from propagator import exact_propagator

Array = np.ndarray


@dataclass(frozen=True)
class PauliMatrixTerm:
    label: str
    coeff: float
    matrix: Array


def _single_site(n_qubits: int, index: int, op: Array) -> Array:
    return kron_all(*(op if q == index else I2 for q in range(n_qubits)))


def _two_site(n_qubits: int, i: int, j: int, op_i: Array, op_j: Array) -> Array:
    ops = []
    for q in range(n_qubits):
        if q == i:
            ops.append(op_i)
        elif q == j:
            ops.append(op_j)
        else:
            ops.append(I2)
    return kron_all(*ops)


def _label(n_qubits: int, mapping: dict[int, str]) -> str:
    return "".join(mapping.get(q, "I") for q in range(n_qubits))


def reduced_bcs_terms(xi: list[float] | Array, g: float) -> list[PauliMatrixTerm]:
    xi_array = np.asarray(xi, dtype=float)
    n_qubits = len(xi_array)
    terms: list[PauliMatrixTerm] = []

    for k, xi_k in enumerate(xi_array):
        terms.append(
            PauliMatrixTerm(
                label=_label(n_qubits, {k: "Z"}),
                coeff=float(xi_k),
                matrix=float(xi_k) * _single_site(n_qubits, k, Z),
            )
        )

    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            coeff = -float(g) / 2.0
            terms.append(
                PauliMatrixTerm(
                    label=_label(n_qubits, {i: "X", j: "X"}),
                    coeff=coeff,
                    matrix=coeff * _two_site(n_qubits, i, j, X, X),
                )
            )
            terms.append(
                PauliMatrixTerm(
                    label=_label(n_qubits, {i: "Y", j: "Y"}),
                    coeff=coeff,
                    matrix=coeff * _two_site(n_qubits, i, j, Y, Y),
                )
            )
    return terms


def reduced_bcs_matrix(xi: list[float] | Array, g: float) -> Array:
    terms = reduced_bcs_terms(xi, g)
    hamiltonian = sum((term.matrix for term in terms), np.zeros_like(terms[0].matrix))
    if not is_hermitian(hamiltonian):
        raise ValueError("BCS Hamiltonian must be Hermitian")
    return hamiltonian


def pair_number_operator(n_qubits: int, index: int) -> Array:
    return (_single_site(n_qubits, index, I2) - _single_site(n_qubits, index, Z)) / 2


def pair_annihilation_operator(n_qubits: int, index: int) -> Array:
    return _single_site(n_qubits, index, (X + 1j * Y) / 2)


def pair_creation_operator(n_qubits: int, index: int) -> Array:
    return _single_site(n_qubits, index, (X - 1j * Y) / 2)


def total_pair_number_operator(n_qubits: int) -> Array:
    return sum(
        (pair_number_operator(n_qubits, index) for index in range(n_qubits)),
        np.zeros((2**n_qubits, 2**n_qubits), dtype=complex),
    )


def computational_basis_state(n_qubits: int, occupied: list[int]) -> Array:
    bits = ["0"] * n_qubits
    for index in occupied:
        if index < 0 or index >= n_qubits:
            raise ValueError("occupied index out of range")
        bits[index] = "1"
    basis_index = int("".join(bits), 2)
    state = np.zeros(2**n_qubits, dtype=complex)
    state[basis_index] = 1.0
    return state


def bcs_product_state(
    u: list[complex] | Array,
    v: list[complex] | Array,
) -> Array:
    u_array = np.asarray(u, dtype=complex)
    v_array = np.asarray(v, dtype=complex)
    if len(u_array) != len(v_array):
        raise ValueError("u and v must have the same length")
    local_states = []
    for u_i, v_i in zip(u_array, v_array):
        norm = np.sqrt(abs(u_i) ** 2 + abs(v_i) ** 2)
        if norm == 0:
            raise ValueError("each local BCS factor must have nonzero norm")
        local_states.append(np.array([u_i / norm, v_i / norm], dtype=complex))
    return kron_all(*local_states)


def expectation(state: Array, operator: Array) -> complex:
    return np.vdot(state, operator @ state)


def fidelity(state_a: Array, state_b: Array) -> float:
    return float(abs(np.vdot(state_a, state_b)) ** 2)


def pair_occupations(state: Array, n_qubits: int) -> list[float]:
    return [
        float(np.real(expectation(state, pair_number_operator(n_qubits, index))))
        for index in range(n_qubits)
    ]


def pair_correlation_matrix(state: Array, n_qubits: int) -> Array:
    matrix = np.zeros((n_qubits, n_qubits), dtype=complex)
    creators = [pair_creation_operator(n_qubits, index) for index in range(n_qubits)]
    annihilators = [pair_annihilation_operator(n_qubits, index) for index in range(n_qubits)]
    for i in range(n_qubits):
        for j in range(n_qubits):
            matrix[i, j] = expectation(state, creators[i] @ annihilators[j])
    return matrix


def condensate_eigenvalue(state: Array, n_qubits: int) -> float:
    correlations = pair_correlation_matrix(state, n_qubits)
    eigenvalues = np.linalg.eigvalsh((correlations + correlations.conj().T) / 2)
    return float(np.max(np.real(eigenvalues)))


def effective_gap_proxy(state: Array, n_qubits: int, g: float) -> float:
    return float(abs(g) * np.sqrt(max(condensate_eigenvalue(state, n_qubits), 0.0)))


def apply_unitary_series(unitary_steps: list[Array], initial_state: Array) -> Array:
    state = np.asarray(initial_state, dtype=complex)
    for unitary in unitary_steps:
        state = unitary @ state
    return state


def first_order_trotter_step(terms: list[PauliMatrixTerm], dt: float) -> Array:
    dim = terms[0].matrix.shape[0]
    step = np.eye(dim, dtype=complex)
    for term in terms:
        step = exact_propagator(term.matrix, dt) @ step
    return step


def second_order_trotter_step(terms: list[PauliMatrixTerm], dt: float) -> Array:
    dim = terms[0].matrix.shape[0]
    step = np.eye(dim, dtype=complex)
    for term in terms:
        step = exact_propagator(term.matrix, dt / 2) @ step
    for term in reversed(terms):
        step = exact_propagator(term.matrix, dt / 2) @ step
    return step


def trotter_evolve_state(
    terms: list[PauliMatrixTerm],
    initial_state: Array,
    time: float,
    steps: int,
    order: int = 1,
) -> Array:
    if steps <= 0:
        raise ValueError("steps must be positive")
    if order == 1:
        step = first_order_trotter_step(terms, time / steps)
    elif order == 2:
        step = second_order_trotter_step(terms, time / steps)
    else:
        raise ValueError("only order 1 and 2 are supported")
    if not is_unitary(step, atol=1e-8):
        raise ValueError("Trotter step is not unitary")
    return np.linalg.matrix_power(step, steps) @ initial_state


def exact_evolve_state(hamiltonian: Array, initial_state: Array, time: float) -> Array:
    return exact_propagator(hamiltonian, time) @ initial_state


def heisenberg_operator(operator: Array, hamiltonian: Array, time: float) -> Array:
    unitary = exact_propagator(hamiltonian, time)
    return unitary.conj().T @ operator @ unitary


def pair_retarded_green_value(
    hamiltonian: Array,
    state: Array,
    i: int,
    j: int,
    time: float,
    eta: float = 0.0,
) -> complex:
    n_qubits = int(np.log2(hamiltonian.shape[0]))
    return retarded_green_value(
        hamiltonian=hamiltonian,
        state=state,
        operator_a=pair_annihilation_operator(n_qubits, i),
        operator_b=pair_creation_operator(n_qubits, j),
        time=time,
        eta=eta,
    )


def retarded_green_value(
    hamiltonian: Array,
    state: Array,
    operator_a: Array,
    operator_b: Array,
    time: float,
    eta: float = 0.0,
) -> complex:
    if time < 0:
        return 0.0j
    operator_a_t = heisenberg_operator(operator_a, hamiltonian, time)
    comm = operator_a_t @ operator_b - operator_b @ operator_a_t
    damping = np.exp(-float(eta) * float(time))
    return -1j * expectation(state, comm) * damping


def pair_retarded_green_series(
    xi: list[float] | Array,
    g: float,
    occupied: list[int],
    i: int,
    j: int,
    times: list[float] | Array,
    eta: float = 0.02,
) -> list[dict[str, float]]:
    hamiltonian = reduced_bcs_matrix(xi, g)
    state = computational_basis_state(len(xi), occupied)
    rows = []
    for time in np.asarray(times, dtype=float):
        value = pair_retarded_green_value(
            hamiltonian=hamiltonian,
            state=state,
            i=i,
            j=j,
            time=float(time),
            eta=eta,
        )
        rows.append(
            {
                "time": float(time),
                "i": float(i),
                "j": float(j),
                "real": float(np.real(value)),
                "imag": float(np.imag(value)),
                "abs": float(abs(value)),
            }
        )
    return rows


def anomalous_gorkov_green_series(
    xi: list[float] | Array,
    g: float,
    u: list[complex] | Array,
    v: list[complex] | Array,
    i: int,
    j: int,
    times: list[float] | Array,
    eta: float = 0.02,
) -> list[dict[str, float]]:
    hamiltonian = reduced_bcs_matrix(xi, g)
    state = bcs_product_state(u, v)
    n_qubits = len(xi)
    channels = {
        "F_ann_ann": (
            pair_annihilation_operator(n_qubits, i),
            pair_annihilation_operator(n_qubits, j),
        ),
        "Fdag_cre_cre": (
            pair_creation_operator(n_qubits, i),
            pair_creation_operator(n_qubits, j),
        ),
    }
    rows = []
    for time in np.asarray(times, dtype=float):
        row = {"time": float(time), "i": float(i), "j": float(j)}
        for name, (operator_a, operator_b) in channels.items():
            value = retarded_green_value(
                hamiltonian=hamiltonian,
                state=state,
                operator_a=operator_a,
                operator_b=operator_b,
                time=float(time),
                eta=eta,
            )
            row[f"{name}_real"] = float(np.real(value))
            row[f"{name}_imag"] = float(np.imag(value))
            row[f"{name}_abs"] = float(abs(value))
        rows.append(row)
    return rows


def gorkov_nambu_green_matrix_series(
    xi: list[float] | Array,
    g: float,
    u: list[complex] | Array,
    v: list[complex] | Array,
    i: int,
    j: int,
    times: list[float] | Array,
    eta: float = 0.02,
) -> list[dict[str, float]]:
    hamiltonian = reduced_bcs_matrix(xi, g)
    state = bcs_product_state(u, v)
    n_qubits = len(xi)
    annihilator_i = pair_annihilation_operator(n_qubits, i)
    annihilator_j = pair_annihilation_operator(n_qubits, j)
    creator_i = pair_creation_operator(n_qubits, i)
    creator_j = pair_creation_operator(n_qubits, j)
    channels = {
        "G": (annihilator_i, creator_j),
        "F": (annihilator_i, annihilator_j),
        "Fdag": (creator_i, creator_j),
        "Gdag": (creator_i, annihilator_j),
    }
    rows = []
    for time in np.asarray(times, dtype=float):
        values = {}
        for name, (operator_a, operator_b) in channels.items():
            values[name] = retarded_green_value(
                hamiltonian=hamiltonian,
                state=state,
                operator_a=operator_a,
                operator_b=operator_b,
                time=float(time),
                eta=eta,
            )
        nambu = np.array(
            [[values["G"], values["F"]], [values["Fdag"], values["Gdag"]]],
            dtype=complex,
        )
        row = {"time": float(time), "i": float(i), "j": float(j)}
        for name, value in values.items():
            row[f"{name}_real"] = float(np.real(value))
            row[f"{name}_imag"] = float(np.imag(value))
            row[f"{name}_abs"] = float(abs(value))
        trace = np.trace(nambu)
        determinant = np.linalg.det(nambu)
        row["trace_real"] = float(np.real(trace))
        row["trace_imag"] = float(np.imag(trace))
        row["trace_abs"] = float(abs(trace))
        row["det_real"] = float(np.real(determinant))
        row["det_imag"] = float(np.imag(determinant))
        row["det_abs"] = float(abs(determinant))
        rows.append(row)
    return rows


def green_spectral_density(
    times: list[float] | Array,
    values: list[complex] | Array,
) -> list[dict[str, float]]:
    times_array = np.asarray(times, dtype=float)
    values_array = np.asarray(values, dtype=complex)
    if len(times_array) < 2:
        raise ValueError("at least two times are required")
    dt = float(times_array[1] - times_array[0])
    if dt <= 0:
        raise ValueError("times must be increasing")
    spectrum = np.fft.fft(values_array) * dt
    frequencies = 2 * np.pi * np.fft.fftfreq(len(values_array), d=dt)
    order = np.argsort(frequencies)
    return [
        {
            "omega": float(frequencies[index]),
            "spectral_weight": float(-np.imag(spectrum[index]) / np.pi),
            "real_response": float(np.real(spectrum[index])),
            "imag_response": float(np.imag(spectrum[index])),
        }
        for index in order
    ]


def bcs_dynamics_row(
    xi: list[float] | Array,
    g: float,
    occupied: list[int],
    time: float,
    steps: int,
    order: int,
) -> dict[str, float]:
    terms = reduced_bcs_terms(xi, g)
    hamiltonian = reduced_bcs_matrix(xi, g)
    n_qubits = len(xi)
    initial = computational_basis_state(n_qubits, occupied)
    exact_state = exact_evolve_state(hamiltonian, initial, time)
    approx_state = trotter_evolve_state(terms, initial, time, steps, order=order)
    number = total_pair_number_operator(n_qubits)
    return {
        "time": float(time),
        "steps": float(steps),
        "order": float(order),
        "fidelity": fidelity(exact_state, approx_state),
        "state_error": float(np.linalg.norm(exact_state - approx_state)),
        "exact_energy": float(np.real(expectation(exact_state, hamiltonian))),
        "trotter_energy": float(np.real(expectation(approx_state, hamiltonian))),
        "exact_pair_number": float(np.real(expectation(exact_state, number))),
        "trotter_pair_number": float(np.real(expectation(approx_state, number))),
        "exact_condensate_eigenvalue": condensate_eigenvalue(exact_state, n_qubits),
        "trotter_condensate_eigenvalue": condensate_eigenvalue(approx_state, n_qubits),
        "exact_gap_proxy": effective_gap_proxy(exact_state, n_qubits, g),
        "trotter_gap_proxy": effective_gap_proxy(approx_state, n_qubits, g),
    }


def bcs_time_observables(
    xi: list[float] | Array,
    g: float,
    occupied: list[int],
    times: list[float] | Array,
    trotter_steps: int = 32,
    trotter_order: int = 2,
) -> list[dict[str, float]]:
    terms = reduced_bcs_terms(xi, g)
    hamiltonian = reduced_bcs_matrix(xi, g)
    n_qubits = len(xi)
    initial = computational_basis_state(n_qubits, occupied)
    number = total_pair_number_operator(n_qubits)
    rows = []
    for time in np.asarray(times, dtype=float):
        exact_state = exact_evolve_state(hamiltonian, initial, float(time))
        trotter_state = trotter_evolve_state(
            terms,
            initial,
            float(time),
            steps=trotter_steps,
            order=trotter_order,
        )
        exact_occupations = pair_occupations(exact_state, n_qubits)
        trotter_occupations = pair_occupations(trotter_state, n_qubits)
        row = {
            "time": float(time),
            "fidelity": fidelity(exact_state, trotter_state),
            "state_error": float(np.linalg.norm(exact_state - trotter_state)),
            "exact_energy": float(np.real(expectation(exact_state, hamiltonian))),
            "trotter_energy": float(np.real(expectation(trotter_state, hamiltonian))),
            "exact_pair_number": float(np.real(expectation(exact_state, number))),
            "trotter_pair_number": float(np.real(expectation(trotter_state, number))),
            "exact_condensate_eigenvalue": condensate_eigenvalue(exact_state, n_qubits),
            "trotter_condensate_eigenvalue": condensate_eigenvalue(trotter_state, n_qubits),
            "exact_gap_proxy": effective_gap_proxy(exact_state, n_qubits, g),
            "trotter_gap_proxy": effective_gap_proxy(trotter_state, n_qubits, g),
        }
        for index, occupation in enumerate(exact_occupations):
            row[f"exact_n_{index}"] = occupation
        for index, occupation in enumerate(trotter_occupations):
            row[f"trotter_n_{index}"] = occupation
        rows.append(row)
    return rows


def commutator_norm_table(terms: list[PauliMatrixTerm]) -> list[dict[str, float | str]]:
    rows = []
    for i, left in enumerate(terms):
        for j, right in enumerate(terms):
            if j <= i:
                continue
            norm = float(np.linalg.norm(commutator(left.matrix, right.matrix), ord=2))
            if norm > 1e-12:
                rows.append(
                    {
                        "left": left.label,
                        "right": right.label,
                        "left_coeff": left.coeff,
                        "right_coeff": right.coeff,
                        "commutator_norm": norm,
                    }
                )
    return rows
