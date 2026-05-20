from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pennylane as qml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "tables" / "quantum_languages"


def save(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"pennylane_{name}.json").open("w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def amplitude_payload(state: np.ndarray, wires: int, circuit: str) -> dict:
    return {
        "circuit": circuit,
        "amplitudes": [
            {"basis": format(index, f"0{wires}b"), "amplitude": [float(a.real), float(a.imag)]}
            for index, a in enumerate(state)
            if abs(a) > 1e-10
        ],
    }


def bell() -> dict:
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    payload = amplitude_payload(np.asarray(circuit()), 2, "H(0); CNOT(0,1)")
    save("bell", payload)
    return payload


def deutsch_balanced() -> dict:
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit():
        qml.PauliX(1)
        qml.Hadamard(0)
        qml.Hadamard(1)
        qml.CNOT(wires=[0, 1])
        qml.Hadamard(0)
        return qml.probs(wires=[0])

    probs = np.asarray(circuit())
    payload = {"circuit": "X(1); H(0,1); CNOT(0,1); H(0)", "probs_wire_0": probs.tolist()}
    save("deutsch_balanced", payload)
    return payload


def grover_2q_mark_3() -> dict:
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(0)
        qml.Hadamard(1)
        qml.CZ(wires=[0, 1])
        qml.Hadamard(0)
        qml.Hadamard(1)
        qml.PauliX(0)
        qml.PauliX(1)
        qml.CZ(wires=[0, 1])
        qml.PauliX(0)
        qml.PauliX(1)
        qml.Hadamard(0)
        qml.Hadamard(1)
        return qml.state()

    payload = amplitude_payload(np.asarray(circuit()), 2, "2-qubit Grover marked |11>")
    save("grover_2q_mark_3", payload)
    return payload


def qft_3q_basis_3() -> dict:
    dev = qml.device("default.qubit", wires=3)

    @qml.qnode(dev)
    def circuit():
        qml.BasisState(np.array([0, 1, 1]), wires=[0, 1, 2])
        qml.QFT(wires=[0, 1, 2])
        return qml.state()

    payload = amplitude_payload(np.asarray(circuit()), 3, "Basis |011>; QFT")
    save("qft_3q_basis_3", payload)
    return payload


def diagonal_z_evolution(time: float = np.pi / 4) -> dict:
    dev = qml.device("default.qubit", wires=1)

    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(0)
        qml.RZ(2 * time, wires=0)
        return qml.state()

    payload = amplitude_payload(np.asarray(circuit()), 1, "H(0); RZ(2t)")
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
        print(f"\n== PennyLane: {name} ==")
        print(json.dumps(func(), indent=2)[:1400])


if __name__ == "__main__":
    main()
