from __future__ import annotations

import numpy as np
from qiskit.quantum_info import SparsePauliOp

from fermions import (
    jordan_wigner_annihilation,
    jordan_wigner_creation,
    jordan_wigner_number,
)

Array = np.ndarray


def two_site_spinless_hubbard_matrix(t: float = 1.0, u: float = 2.0) -> Array:
    n_modes = 2
    c0 = jordan_wigner_annihilation(0, n_modes)
    c1 = jordan_wigner_annihilation(1, n_modes)
    cd0 = jordan_wigner_creation(0, n_modes)
    cd1 = jordan_wigner_creation(1, n_modes)
    n0 = jordan_wigner_number(0, n_modes)
    n1 = jordan_wigner_number(1, n_modes)
    return -t * (cd0 @ c1 + cd1 @ c0) + u * (n0 @ n1)


def two_site_bcs_matrix(epsilon: float = 1.0, delta: float = 0.4) -> Array:
    n_modes = 2
    c_up = jordan_wigner_annihilation(0, n_modes)
    c_down = jordan_wigner_annihilation(1, n_modes)
    cd_up = jordan_wigner_creation(0, n_modes)
    cd_down = jordan_wigner_creation(1, n_modes)
    n_up = jordan_wigner_number(0, n_modes)
    n_down = jordan_wigner_number(1, n_modes)
    pairing = cd_up @ cd_down + c_down @ c_up
    return epsilon * (n_up + n_down) - delta * pairing


def ground_state(hamiltonian: Array) -> tuple[float, Array]:
    values, vectors = np.linalg.eigh(hamiltonian)
    index = int(np.argmin(values))
    return float(values[index].real), vectors[:, index]


def pauli_decompose_2q_matrix(matrix: Array, atol: float = 1e-10) -> SparsePauliOp:
    paulis = ["I", "X", "Y", "Z"]
    labels: list[str] = []
    coeffs: list[complex] = []
    from algebra import pauli_string

    for left in paulis:
        for right in paulis:
            label = left + right
            basis = pauli_string(label)
            coeff = np.trace(basis.conj().T @ matrix) / 4
            if abs(coeff) > atol:
                labels.append(label)
                coeffs.append(coeff)
    return SparsePauliOp(labels, coeffs)
