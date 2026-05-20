# BCS quântico em Qiskit, PennyLane e Cirq

Este tutorial descreve a implementação do Hamiltoniano BCS reduzido no contexto de
simulação quântica de muitos corpos. O modelo é expresso em termos de pseudospins de
Anderson e mapeado para operadores de Pauli em qubits.

## Formulação do modelo

O Hamiltoniano de interesse é o Hamiltoniano BCS reduzido, escrito como:

```text
H = \sum_k \xi_k Z_k - \frac{g}{2} \sum_{i<j} (X_i X_j + Y_i Y_j)
```

Neste mapeamento, cada qubit representa um nível de pseudospin de Anderson:

```text
|0⟩ = nível vazio
|1⟩ = nível ocupado por um par de Cooper
```

## Objetivo do tutorial

Demonstrar a correspondência entre:

- a formulação teórica do modelo BCS em pseudospins;
- o mapeamento para qubits e operadores de Pauli;
- a implementação em Qiskit, PennyLane e Cirq;
- a comparação entre energia fundamental exata e estimativas de VQE.

## Procedimento

1. Construir o Hamiltoniano clássico em matriz densa;
2. Calcular a energia fundamental exata por diagonalização;
3. Montar o Hamiltoniano em Qiskit como `SparsePauliOp`;
4. Montar o Hamiltoniano em PennyLane como `qml.Hamiltonian`;
5. Definir circuitos variacionais em Qiskit, PennyLane e Cirq;
6. Executar VQE e comparar os resultados com a solução exata.

## Execução

```bash
cd ~/quantum_ic
source .venv/bin/activate
python quantum_languages/scripts/bcs_project.py
```

## Estrutura de código

- `construir_hamiltoniano_bcs_matriz(xi, g)`: Hamiltoniano clássico matricial;
- `energia_exata_classica(xi, g)`: energia fundamental obtida por diagonalização;
- `construir_hamiltoniano_bcs_qiskit(xi, g)`: Hamiltoniano em Qiskit;
- `executar_vqe_qiskit(xi, g)`: rotina VQE em Qiskit;
- `construir_hamiltoniano_bcs_pennylane(xi, g)`: Hamiltoniano em PennyLane;
- `executar_vqe_pennylane(xi, g)`: rotina VQE em PennyLane;
- `construir_circuito_cirq(n_qubits, parametros)`: circuito variacional em Cirq;
- `executar_vqe_cirq(xi, g)`: rotina VQE em Cirq.

## Resultados esperados

O script imprime um relatório comparativo com:

- energia fundamental exata;
- energia estimada por Qiskit;
- energia estimada por PennyLane;
- energia estimada por Cirq.

## Observações técnicas

- A implementação atual utiliza um ansatz variacional de múltiplas camadas de
  rotações `RY` e emaranhamento em cadeia por `CNOT`.
- O exemplo de `n_qubits = 4` serve como validação de conceito para o mapeamento
  BCS->qubits e a implementação de VQE em diferentes frameworks.
- A segunda camada de rotação fornece maior expressividade e melhor aproximação
  da energia fundamental.
