from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from algebra import X, Y, Z, anticommutator, commutator, is_hermitian, is_unitary
from bcs import (
    anomalous_gorkov_green_series,
    bcs_dynamics_row,
    bcs_product_state,
    bcs_time_observables,
    condensate_eigenvalue,
    computational_basis_state,
    expectation,
    fidelity,
    gorkov_nambu_green_matrix_series,
    green_spectral_density,
    pair_correlation_matrix,
    pair_retarded_green_series,
    pair_retarded_green_value,
    reduced_bcs_matrix,
    reduced_bcs_terms,
    total_pair_number_operator,
    trotter_evolve_state,
)
from bcs_qiskit import simulate_bcs_trotter_circuit
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


def test_reduced_bcs_hamiltonian_and_number_conservation() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    hamiltonian = reduced_bcs_matrix(xi, g=0.8)
    number = total_pair_number_operator(len(xi))
    assert is_hermitian(hamiltonian)
    assert np.linalg.norm(commutator(hamiltonian, number)) < 1e-10


def test_bcs_pair_correlations_are_physical() -> None:
    state = computational_basis_state(4, [0, 1])
    correlations = pair_correlation_matrix(state, 4)
    assert np.allclose(correlations, correlations.conj().T)
    assert np.allclose(np.diag(correlations), [1.0, 1.0, 0.0, 0.0])
    assert 0.0 <= condensate_eigenvalue(state, 4) <= 2.0


def test_bcs_time_observables_include_gap_proxy() -> None:
    rows = bcs_time_observables(
        xi=[-1.0, -0.35, 0.35, 1.0],
        g=0.8,
        occupied=[0, 1],
        times=[0.0, 0.5],
        trotter_steps=8,
    )
    assert len(rows) == 2
    assert rows[0]["exact_gap_proxy"] > 0.0
    assert rows[1]["fidelity"] > 0.9


def test_bcs_pair_retarded_green_function_is_causal() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    hamiltonian = reduced_bcs_matrix(xi, g=0.8)
    state = computational_basis_state(4, [0, 1])
    assert pair_retarded_green_value(hamiltonian, state, 0, 0, time=-0.1) == 0.0j
    assert np.isfinite(pair_retarded_green_value(hamiltonian, state, 0, 0, time=0.0))


def test_bcs_pair_green_spectrum_shape() -> None:
    rows = pair_retarded_green_series(
        xi=[-1.0, -0.35, 0.35, 1.0],
        g=0.8,
        occupied=[0, 1],
        i=0,
        j=0,
        times=[0.0, 0.1, 0.2, 0.3],
    )
    values = [row["real"] + 1j * row["imag"] for row in rows]
    spectrum = green_spectral_density([row["time"] for row in rows], values)
    assert len(spectrum) == 4
    assert spectrum[0]["omega"] < spectrum[-1]["omega"]


def test_bcs_product_state_and_anomalous_green_are_nontrivial() -> None:
    state = bcs_product_state([1.0, 1.0], [0.5, 0.25j])
    assert abs(np.vdot(state, state) - 1.0) < 1e-12
    rows = anomalous_gorkov_green_series(
        xi=[-1.0, -0.35],
        g=0.8,
        u=[1.0, 1.0],
        v=[0.5, 0.25j],
        i=0,
        j=0,
        times=[0.0, 0.2, 0.4],
    )
    assert max(row["F_ann_ann_abs"] for row in rows) > 1e-8


def test_gorkov_nambu_matrix_has_channels_and_invariants() -> None:
    rows = gorkov_nambu_green_matrix_series(
        xi=[-1.0, -0.35],
        g=0.8,
        u=[1.0, 1.0],
        v=[0.5, 0.25j],
        i=0,
        j=0,
        times=[0.0, 0.2],
    )
    assert len(rows) == 2
    for key in ["G_abs", "F_abs", "Fdag_abs", "Gdag_abs", "trace_abs", "det_abs"]:
        assert key in rows[0]
        assert np.isfinite(rows[0][key])
    assert max(row["F_abs"] for row in rows) > 1e-8


def test_bcs_trotter_improves_with_more_steps() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    row_1 = bcs_dynamics_row(xi, g=0.8, occupied=[0, 1], time=1.5, steps=1, order=1)
    row_16 = bcs_dynamics_row(xi, g=0.8, occupied=[0, 1], time=1.5, steps=16, order=1)
    assert row_16["state_error"] < row_1["state_error"]
    assert abs(row_16["exact_pair_number"] - row_16["trotter_pair_number"]) < 1e-8


def test_qiskit_trotter_matches_matrix_trotter() -> None:
    xi = [-1.0, -0.35, 0.35, 1.0]
    terms = reduced_bcs_terms(xi, g=0.8)
    initial = computational_basis_state(len(xi), [0, 1])
    matrix_state = trotter_evolve_state(terms, initial, time=0.7, steps=3, order=2)
    qiskit_state = simulate_bcs_trotter_circuit(terms, time=0.7, steps=3, order=2, occupied=[0, 1])
    assert fidelity(matrix_state, qiskit_state) > 1 - 1e-10
