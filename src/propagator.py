from __future__ import annotations

import numpy as np
import scipy.linalg as la

from algebra import is_unitary

Array = np.ndarray


def exact_propagator(hamiltonian: Array, time: float, hbar: float = 1.0) -> Array:
    return la.expm(-1j * hamiltonian * time / hbar)


def first_order_trotter(terms: list[Array], time: float, steps: int) -> Array:
    if steps <= 0:
        raise ValueError("steps must be positive")
    dt = time / steps
    piece = np.eye(terms[0].shape[0], dtype=complex)
    for term in terms:
        piece = la.expm(-1j * term * dt) @ piece
    return np.linalg.matrix_power(piece, steps)


def propagator_error(exact: Array, approximate: Array) -> float:
    return float(np.linalg.norm(exact - approximate, ord=2))


def trotter_error_curve(terms: list[Array], time: float, steps_values: list[int]) -> list[dict[str, float]]:
    hamiltonian = sum(terms)
    exact = exact_propagator(hamiltonian, time)
    rows = []
    for steps in steps_values:
        approx = first_order_trotter(terms, time, steps)
        rows.append(
            {
                "steps": float(steps),
                "error": propagator_error(exact, approx),
                "unitary": float(is_unitary(approx)),
            }
        )
    return rows
