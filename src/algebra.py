from __future__ import annotations

import numpy as np

Array = np.ndarray

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

PAULI = {
    "I": I2,
    "X": X,
    "Y": Y,
    "Z": Z,
}


def commutator(a: Array, b: Array) -> Array:
    return a @ b - b @ a


def anticommutator(a: Array, b: Array) -> Array:
    return a @ b + b @ a


def dagger(a: Array) -> Array:
    return a.conj().T


def is_hermitian(a: Array, atol: float = 1e-10) -> bool:
    return np.allclose(a, dagger(a), atol=atol)


def is_unitary(a: Array, atol: float = 1e-10) -> bool:
    ident = np.eye(a.shape[0], dtype=complex)
    return np.allclose(dagger(a) @ a, ident, atol=atol)


def kron_all(*ops: Array) -> Array:
    if not ops:
        raise ValueError("kron_all requires at least one operator")
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out


def pauli_string(label: str) -> Array:
    try:
        return kron_all(*(PAULI[ch] for ch in label))
    except KeyError as exc:
        raise ValueError(f"Invalid Pauli label: {label}") from exc


def pretty_matrix(a: Array, digits: int = 4) -> str:
    return np.array2string(np.round(a, digits), suppress_small=True)
