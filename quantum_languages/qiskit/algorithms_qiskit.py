from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "tables" / "quantum_languages"


def save(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"qiskit_{name}.json").open("w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def state_payload(circuit: QuantumCircuit) -> dict:
    state = Statevector.from_instruction(circuit)
    return {
        "circuit": circuit.draw(output="text").single_string(),
        "amplitudes": [
            {"basis": format(index, f"0{circuit.num_qubits}b"), "amplitude": [float(a.real), float(a.imag)]}
            for index, a in enumerate(state.data)
            if abs(a) > 1e-10
        ],
    }


def bell() -> dict:
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    payload = state_payload(qc)
    save("bell", payload)
    return payload


def deutsch_balanced() -> dict:
    qc = QuantumCircuit(2, 1)
    qc.x(1)
    qc.h([0, 1])
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    counts = simulator.run(compiled, shots=256, seed_simulator=7).result().get_counts()
    payload = {"circuit": qc.draw(output="text").single_string(), "counts": counts}
    save("deutsch_balanced", payload)
    return payload


def grover_2q_mark_3() -> dict:
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    payload = state_payload(qc)
    save("grover_2q_mark_3", payload)
    return payload


def qft_3q_basis_3() -> dict:
    qc = QuantumCircuit(3)
    qc.x([0, 1])
    for target in range(3):
        qc.h(target)
        for control in range(target + 1, 3):
            qc.cp(np.pi / 2 ** (control - target), control, target)
    qc.swap(0, 2)
    payload = state_payload(qc)
    save("qft_3q_basis_3", payload)
    return payload


def diagonal_z_evolution(time: float = np.pi / 4) -> dict:
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.rz(2 * time, 0)
    payload = state_payload(qc)
    save("diagonal_z_evolution", payload)
    return payload


def main() -> None:
    for name, func in [
        ("bell", bell),
        ("deutsch_balanced", deutsch_balanced),
        ("grover_2q_mark_3", grover_2q_mark_3),
        ("qft_3q_basis_3", qft_3q_basis_3),
        ("diagonal_z_evolution", diagonal_z_evolution),
    ]:
        print(f"\n== Qiskit: {name} ==")
        print(json.dumps(func(), indent=2)[:1400])


if __name__ == "__main__":
    main()
