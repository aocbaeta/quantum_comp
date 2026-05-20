from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit.circuit.library import TwoLocal
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.quantum_info import SparsePauliOp


@dataclass(frozen=True)
class VQEResult:
    exact_energy: float
    vqe_energy: float
    absolute_error: float


def run_statevector_vqe(
    hamiltonian: SparsePauliOp,
    exact_energy: float,
    reps: int = 2,
    maxiter: int = 200,
    seed: int = 7,
) -> VQEResult:
    rng = np.random.default_rng(seed)
    ansatz = TwoLocal(
        num_qubits=hamiltonian.num_qubits,
        rotation_blocks="ry",
        entanglement_blocks="cz",
        reps=reps,
    )
    initial_point = rng.uniform(-0.1, 0.1, ansatz.num_parameters)
    optimizer = COBYLA(maxiter=maxiter)
    estimator = StatevectorEstimator()
    vqe = VQE(estimator, ansatz, optimizer, initial_point=initial_point)
    result = vqe.compute_minimum_eigenvalue(hamiltonian)
    vqe_energy = float(np.real(result.eigenvalue))
    return VQEResult(
        exact_energy=exact_energy,
        vqe_energy=vqe_energy,
        absolute_error=abs(vqe_energy - exact_energy),
    )
