from __future__ import annotations

import numpy as np

from algebra import I2, X, Y, Z, dagger, kron_all

Array = np.ndarray


def annihilation_single() -> Array:
    return np.array([[0, 1], [0, 0]], dtype=complex)


def creation_single() -> Array:
    return dagger(annihilation_single())


def number_single() -> Array:
    c = annihilation_single()
    return dagger(c) @ c


def jordan_wigner_annihilation(mode: int, n_modes: int) -> Array:
    if mode < 0 or mode >= n_modes:
        raise ValueError("mode must satisfy 0 <= mode < n_modes")
    sigma_minus = (X + 1j * Y) / 2
    ops = []
    for index in range(n_modes):
        if index < mode:
            ops.append(Z)
        elif index == mode:
            ops.append(sigma_minus)
        else:
            ops.append(I2)
    return kron_all(*ops)


def jordan_wigner_creation(mode: int, n_modes: int) -> Array:
    return dagger(jordan_wigner_annihilation(mode, n_modes))


def jordan_wigner_number(mode: int, n_modes: int) -> Array:
    c = jordan_wigner_annihilation(mode, n_modes)
    return dagger(c) @ c


def verify_canonical_anticommutation(n_modes: int, atol: float = 1e-10) -> dict[str, float]:
    ident = np.eye(2**n_modes, dtype=complex)
    max_create_annihilate_error = 0.0
    max_annihilate_error = 0.0
    max_create_error = 0.0

    annihilators = [jordan_wigner_annihilation(i, n_modes) for i in range(n_modes)]
    creators = [dagger(c) for c in annihilators]

    for i in range(n_modes):
        for j in range(n_modes):
            delta = ident if i == j else np.zeros_like(ident)
            ca = annihilators[i] @ creators[j] + creators[j] @ annihilators[i]
            aa = annihilators[i] @ annihilators[j] + annihilators[j] @ annihilators[i]
            cc = creators[i] @ creators[j] + creators[j] @ creators[i]
            max_create_annihilate_error = max(
                max_create_annihilate_error, float(np.linalg.norm(ca - delta))
            )
            max_annihilate_error = max(max_annihilate_error, float(np.linalg.norm(aa)))
            max_create_error = max(max_create_error, float(np.linalg.norm(cc)))

    return {
        "creator_annihilator": max_create_annihilate_error,
        "annihilator_annihilator": max_annihilate_error,
        "creator_creator": max_create_error,
        "passed": float(
            max_create_annihilate_error < atol
            and max_annihilate_error < atol
            and max_create_error < atol
        ),
    }
