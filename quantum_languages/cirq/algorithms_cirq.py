from __future__ import annotations

import json
from pathlib import Path

import cirq
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "tables" / "quantum_languages"


def save(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"cirq_{name}.json").open("w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def state_payload(circuit: cirq.Circuit, qubits: list[cirq.Qid]) -> dict:
    result = cirq.Simulator(seed=7).simulate(circuit, qubit_order=qubits)
    state = result.final_state_vector
    return {
        "circuit": str(circuit),
        "amplitudes": [
            {"basis": format(index, f"0{len(qubits)}b"), "amplitude": [float(a.real), float(a.imag)]}
            for index, a in enumerate(state)
            if abs(a) > 1e-10
        ],
    }


def bell() -> dict:
    q = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.H(q[0]), cirq.CNOT(q[0], q[1]))
    payload = state_payload(circuit, q)
    save("bell", payload)
    return payload


def deutsch_balanced() -> dict:
    q = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.X(q[1]),
        cirq.H(q[0]),
        cirq.H(q[1]),
        cirq.CNOT(q[0], q[1]),
        cirq.H(q[0]),
        cirq.measure(q[0], key="answer"),
    )
    result = cirq.Simulator(seed=7).run(circuit, repetitions=256)
    payload = {"circuit": str(circuit), "histogram": result.histogram(key="answer")}
    payload["histogram"] = {str(k): int(v) for k, v in payload["histogram"].items()}
    save("deutsch_balanced", payload)
    return payload


def grover_2q_mark_3() -> dict:
    q = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H.on_each(*q),
        cirq.CZ(q[0], q[1]),
        cirq.H.on_each(*q),
        cirq.X.on_each(*q),
        cirq.CZ(q[0], q[1]),
        cirq.X.on_each(*q),
        cirq.H.on_each(*q),
    )
    payload = state_payload(circuit, q)
    save("grover_2q_mark_3", payload)
    return payload


def qft_3q_basis_3() -> dict:
    q = cirq.LineQubit.range(3)
    circuit = cirq.Circuit(cirq.X(q[0]), cirq.X(q[1]))
    for target in range(3):
        circuit.append(cirq.H(q[target]))
        for control in range(target + 1, 3):
            circuit.append(cirq.CZPowGate(exponent=1 / 2 ** (control - target))(q[control], q[target]))
    circuit.append(cirq.SWAP(q[0], q[2]))
    payload = state_payload(circuit, q)
    save("qft_3q_basis_3", payload)
    return payload


def diagonal_z_evolution(time: float = np.pi / 4) -> dict:
    q = cirq.LineQubit.range(1)
    circuit = cirq.Circuit(cirq.H(q[0]), cirq.rz(2 * time)(q[0]))
    payload = state_payload(circuit, q)
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
        print(f"\n== Cirq: {name} ==")
        print(json.dumps(func(), indent=2)[:1400])


if __name__ == "__main__":
    main()
