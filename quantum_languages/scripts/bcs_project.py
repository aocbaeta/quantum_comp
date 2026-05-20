#!/usr/bin/env python3
from __future__ import annotations

import argparse
from types import SimpleNamespace
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp, Statevector
import pennylane as qml
import cirq

I = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def produto_tensorial(lista_operadores):
    resultado = lista_operadores[0]
    for operador in lista_operadores[1:]:
        resultado = np.kron(resultado, operador)
    return resultado


def operador_local(n_qubits, indice, operador):
    lista = []
    for q in range(n_qubits):
        lista.append(operador if q == indice else I)
    return produto_tensorial(lista)


def operador_dois_corpos(n_qubits, i, j, operador_i, operador_j):
    lista = []
    for q in range(n_qubits):
        if q == i:
            lista.append(operador_i)
        elif q == j:
            lista.append(operador_j)
        else:
            lista.append(I)
    return produto_tensorial(lista)


def construir_hamiltoniano_bcs_matriz(xi, g):
    n_qubits = len(xi)
    dimensao = 2 ** n_qubits
    H = np.zeros((dimensao, dimensao), dtype=complex)

    for k, xi_k in enumerate(xi):
        H += xi_k * operador_local(n_qubits, k, Z)

    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            H += -(g / 2.0) * operador_dois_corpos(n_qubits, i, j, X, X)
            H += -(g / 2.0) * operador_dois_corpos(n_qubits, i, j, Y, Y)

    return H


def energia_exata_classica(xi, g):
    H = construir_hamiltoniano_bcs_matriz(xi, g)
    autovalores = np.linalg.eigvalsh(H)
    return float(np.min(np.real(autovalores)))


def string_pauli_qiskit(n_qubits, operadores):
    paulis = ["I"] * n_qubits
    for indice, simbolo in operadores.items():
        paulis[n_qubits - 1 - indice] = simbolo
    return "".join(paulis)


def construir_hamiltoniano_bcs_qiskit(xi, g):
    n_qubits = len(xi)
    termos = []

    for k, xi_k in enumerate(xi):
        pauli = string_pauli_qiskit(n_qubits, {k: "Z"})
        termos.append((pauli, float(xi_k)))

    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            pauli_xx = string_pauli_qiskit(n_qubits, {i: "X", j: "X"})
            pauli_yy = string_pauli_qiskit(n_qubits, {i: "Y", j: "Y"})
            termos.append((pauli_xx, -g / 2.0))
            termos.append((pauli_yy, -g / 2.0))

    return SparsePauliOp.from_list(termos)


def construir_ansatz_qiskit(n_qubits, parametros):
    circuito = QuantumCircuit(n_qubits)
    for layer in range(4):
        for i in range(n_qubits):
            circuito.ry(parametros[layer * n_qubits + i], i)
        if layer < 3:
            for i in range(n_qubits - 1):
                circuito.cx(i, i + 1)
    return circuito


def energia_qiskit(parametros_numericos, hamiltoniano, n_qubits):
    parametros = ParameterVector("theta", length=4 * n_qubits)
    circuito = construir_ansatz_qiskit(n_qubits, parametros)
    mapa = {parametros[i]: parametros_numericos[i] for i in range(4 * n_qubits)}
    circuito = circuito.assign_parameters(mapa)
    estado = Statevector.from_instruction(circuito)
    energia = np.real(estado.expectation_value(hamiltoniano))
    return float(energia)


def _otimizar_vqe(funcao_objetivo, n_parametros, maxiter=2000, restarts=3, optimizer="random"):
    melhor_resultado = None
    if optimizer == "random":
        n_amostras = max(1, maxiter)
        for _ in range(max(1, restarts)):
            parametros = np.random.uniform(low=0.0, high=2.0 * np.pi, size=n_parametros)
            energia = funcao_objetivo(parametros)
            for _ in range(n_amostras - 1):
                candidato = np.random.uniform(low=0.0, high=2.0 * np.pi, size=n_parametros)
                energia_candidata = funcao_objetivo(candidato)
                if energia_candidata < energia:
                    parametros = candidato
                    energia = energia_candidata
            resultado = SimpleNamespace(
                fun=energia,
                x=parametros,
                success=True,
                message=f"busca aleatoria com {n_amostras} amostras",
            )
            if melhor_resultado is None or resultado.fun < melhor_resultado.fun:
                melhor_resultado = resultado
        return melhor_resultado

    for _ in range(restarts):
        parametros_iniciais = np.random.uniform(low=0.0, high=2.0 * np.pi, size=n_parametros)
        resultado = minimize(
            fun=funcao_objetivo,
            x0=parametros_iniciais,
            method="Powell",
            options={"maxiter": maxiter, "xtol": 1e-6, "ftol": 1e-6},
        )
        if melhor_resultado is None or resultado.fun < melhor_resultado.fun:
            melhor_resultado = resultado
    return melhor_resultado


def executar_vqe_qiskit(xi, g, maxiter=2000, restarts=3, optimizer="random"):
    n_qubits = len(xi)
    hamiltoniano = construir_hamiltoniano_bcs_qiskit(xi, g)

    def objetivo(parametros):
        return energia_qiskit(parametros, hamiltoniano, n_qubits)

    resultado = _otimizar_vqe(
        objetivo, 4 * n_qubits, maxiter=maxiter, restarts=restarts, optimizer=optimizer
    )
    return {
        "energia": float(resultado.fun),
        "parametros": resultado.x,
        "sucesso": resultado.success,
        "mensagem": resultado.message,
    }


def construir_hamiltoniano_bcs_pennylane(xi, g):
    n_qubits = len(xi)
    coeficientes = []
    observaveis = []

    for k, xi_k in enumerate(xi):
        coeficientes.append(float(xi_k))
        observaveis.append(qml.PauliZ(k))

    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            coeficientes.append(-g / 2.0)
            observaveis.append(qml.PauliX(i) @ qml.PauliX(j))
            coeficientes.append(-g / 2.0)
            observaveis.append(qml.PauliY(i) @ qml.PauliY(j))

    return qml.Hamiltonian(coeficientes, observaveis)


def criar_qnode_pennylane(xi, g):
    n_qubits = len(xi)
    dev = qml.device("default.qubit", wires=n_qubits)
    hamiltoniano = construir_hamiltoniano_bcs_pennylane(xi, g)

    @qml.qnode(dev)
    def circuito(parametros):
        for layer in range(4):
            for i in range(n_qubits):
                qml.RY(parametros[layer * n_qubits + i], wires=i)
            if layer < 3:
                for i in range(n_qubits - 1):
                    qml.CNOT(wires=[i, i + 1])
        return qml.expval(hamiltoniano)

    return circuito


def executar_vqe_pennylane(xi, g, maxiter=2000, restarts=3, optimizer="random"):
    n_qubits = len(xi)
    circuito = criar_qnode_pennylane(xi, g)

    def funcao_objetivo(parametros):
        return float(circuito(parametros))

    resultado = _otimizar_vqe(
        funcao_objetivo, 4 * n_qubits, maxiter=maxiter, restarts=restarts, optimizer=optimizer
    )
    return {
        "energia": float(resultado.fun),
        "parametros": resultado.x,
        "sucesso": resultado.success,
        "mensagem": resultado.message,
    }


def construir_circuito_cirq(n_qubits, parametros):
    qubits = cirq.LineQubit.range(n_qubits)
    circuito = cirq.Circuit()
    for layer in range(4):
        for i in range(n_qubits):
            circuito.append(cirq.ry(parametros[layer * n_qubits + i]).on(qubits[i]))
        if layer < 3:
            for i in range(n_qubits - 1):
                circuito.append(cirq.CNOT(qubits[i], qubits[i + 1]))
    return qubits, circuito


def estado_final_cirq(n_qubits, parametros):
    _, circuito = construir_circuito_cirq(n_qubits, parametros)
    simulador = cirq.Simulator()
    resultado = simulador.simulate(circuito)
    return np.array(resultado.final_state_vector, dtype=complex)


def energia_cirq(parametros, xi, g):
    n_qubits = len(xi)
    H = construir_hamiltoniano_bcs_matriz(xi, g)
    estado = estado_final_cirq(n_qubits, parametros)
    energia = np.vdot(estado, H @ estado)
    return float(np.real(energia))


def executar_vqe_cirq(xi, g, maxiter=2000, restarts=3, optimizer="random"):
    n_qubits = len(xi)

    def objetivo(parametros):
        return energia_cirq(parametros, xi, g)

    resultado = _otimizar_vqe(
        objetivo, 4 * n_qubits, maxiter=maxiter, restarts=restarts, optimizer=optimizer
    )
    return {
        "energia": float(resultado.fun),
        "parametros": resultado.x,
        "sucesso": resultado.success,
        "mensagem": resultado.message,
    }


def imprimir_relatorio(xi, g, energia_exata, resultado_qiskit, resultado_pennylane, resultado_cirq):
    print("\n" + "=" * 70)
    print("RELATÓRIO COMPARATIVO — MODELO BCS EM QUBITS")
    print("=" * 70)
    print("\nPARÂMETROS FÍSICOS")
    print("-" * 70)
    print(f"xi_k: {xi}")
    print(f"g: {g}")
    print(f"Número de qubits: {len(xi)}")
    print("\nENERGIA EXATA CLÁSSICA")
    print("-" * 70)
    print(f"E0 exato: {energia_exata:.12f}")
    print("\nRESULTADO QISKIT")
    print("-" * 70)
    print(f"E0 Qiskit: {resultado_qiskit['energia']:.12f}")
    print(f"Erro absoluto: {abs(resultado_qiskit['energia'] - energia_exata):.12e}")
    print(f"Sucesso: {resultado_qiskit['sucesso']}")
    print(f"Mensagem: {resultado_qiskit['mensagem']}")
    print("\nRESULTADO PENNYLANE")
    print("-" * 70)
    print(f"E0 PennyLane: {resultado_pennylane['energia']:.12f}")
    print(f"Erro absoluto: {abs(resultado_pennylane['energia'] - energia_exata):.12e}")
    print(f"Sucesso: {resultado_pennylane['sucesso']}")
    print(f"Mensagem: {resultado_pennylane['mensagem']}")
    print("\nRESULTADO CIRQ")
    print("-" * 70)
    print(f"E0 Cirq: {resultado_cirq['energia']:.12f}")
    print(f"Erro absoluto: {abs(resultado_cirq['energia'] - energia_exata):.12e}")
    print(f"Sucesso: {resultado_cirq['sucesso']}")
    print(f"Mensagem: {resultado_cirq['mensagem']}")
    print("\n" + "=" * 70)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compara o modelo BCS reduzido em Qiskit, PennyLane e Cirq."
    )
    parser.add_argument(
        "--maxiter",
        type=int,
        default=48,
        help="Numero de amostras ou iteracoes por otimizacao VQE.",
    )
    parser.add_argument(
        "--restarts",
        type=int,
        default=1,
        help="Numero de reinicializacoes aleatorias por framework.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semente pseudoaleatoria para inicializacao dos parametros.",
    )
    parser.add_argument(
        "--optimizer",
        choices=["random", "powell"],
        default="random",
        help="Otimizador VQE. Use 'powell' para rodadas mais longas e precisas.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    xi = [-1.0, -0.5, 0.5, 1.0]
    g = 0.8
    np.random.seed(args.seed)
    energia_exata = energia_exata_classica(xi, g)
    resultado_qiskit = executar_vqe_qiskit(
        xi=xi, g=g, maxiter=args.maxiter, restarts=args.restarts, optimizer=args.optimizer
    )
    resultado_pennylane = executar_vqe_pennylane(
        xi=xi, g=g, maxiter=args.maxiter, restarts=args.restarts, optimizer=args.optimizer
    )
    resultado_cirq = executar_vqe_cirq(
        xi=xi, g=g, maxiter=args.maxiter, restarts=args.restarts, optimizer=args.optimizer
    )
    imprimir_relatorio(
        xi=xi,
        g=g,
        energia_exata=energia_exata,
        resultado_qiskit=resultado_qiskit,
        resultado_pennylane=resultado_pennylane,
        resultado_cirq=resultado_cirq,
    )


if __name__ == "__main__":
    main()
