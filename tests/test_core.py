from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from algebra import X, Y, Z, anticommutator, commutator, is_hermitian, is_unitary
from fermions import verify_canonical_anticommutation
from hubbard import ground_state, two_site_bcs_matrix, two_site_spinless_hubbard_matrix
from propagator import exact_propagator
from spectral_stats import spacing_summary
from zeta_zeros import compute_zeta_zeros, normalized_spacings, riemann_von_mangoldt_count


def test_pauli_relations() -> None:
    assert np.allclose(commutator(X, Y), 2j * Z)
    assert np.allclose(anticommutator(X, Y), np.zeros((2, 2)))


def test_jordan_wigner_anticommutation() -> None:
    assert verify_canonical_anticommutation(3)["passed"] == 1.0


def test_propagator_is_unitary() -> None:
    assert is_unitary(exact_propagator(X + Z, time=0.5))


def test_hamiltonians_are_hermitian() -> None:
    hubbard = two_site_spinless_hubbard_matrix()
    bcs = two_site_bcs_matrix()
    assert is_hermitian(hubbard)
    assert is_hermitian(bcs)
    assert ground_state(hubbard)[0] <= 0.0


def test_first_riemann_zero() -> None:
    zero = compute_zeta_zeros(1)[0]
    assert abs(zero.real - 0.5) < 1e-12
    assert abs(zero.imag - 14.1347251417347) < 1e-12


def test_zeta_spacing_pipeline() -> None:
    zeros = compute_zeta_zeros(8)
    spacings = normalized_spacings(zeros)
    summary = spacing_summary(spacings)
    assert len(spacings) == 7
    assert abs(summary.mean - 1.0) < 1e-12
    assert riemann_von_mangoldt_count(zeros[-1].imag) > 0
