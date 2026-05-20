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
7. Construir o propagador exato `U(t)=exp(-iHt)`;
8. Aproximar a dinâmica por Trotterização de 1ª e 2ª ordem;
9. Comparar fidelidade, erro de estado, conservação de energia e número de pares;
10. Reproduzir a Trotterização como circuito Qiskit.
11. Medir correlações de pares, autovalor condensado e proxy de gap efetivo.
12. Calcular função de Green retardada de pares e densidade espectral aproximada.
13. Calcular função de Green anômala de Gor'kov em um estado produto BCS.
14. Montar a matriz de Gor'kov em base Nambu e seu traço espectral.

## Execução

```bash
cd ~/quantum_ic
source .venv/bin/activate
python quantum_languages/scripts/bcs_project.py
```

Dinâmica temporal e Trotterização:

```bash
python experiments/08_bcs_dynamics_trotter.py
python experiments/09_bcs_qiskit_trotter_circuit.py
python experiments/10_bcs_paper_observables.py
python experiments/11_bcs_pair_green_function.py
python experiments/12_bcs_gorkov_anomalous_green.py
python experiments/13_bcs_gorkov_nambu_matrix.py
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

Dinâmica:

- `src/bcs.py`: termos de Pauli, Hamiltoniano, número de pares, evolução exata,
  Trotterização, fidelidade e normas de comutadores;
- `src/bcs_qiskit.py`: circuito Qiskit com portas `RZ`, `RXX` e `RYY` para
  implementar `exp(-iHdt)` por Trotterização;
- `experiments/08_bcs_dynamics_trotter.py`: salva `bcs_dynamics_trotter.csv`,
  `bcs_commutator_norms.csv` e `bcs_trotter_error.png`;
- `experiments/09_bcs_qiskit_trotter_circuit.py`: salva o circuito Qiskit e
  compara a saída com a evolução matricial.
- `experiments/10_bcs_paper_observables.py`: salva séries temporais de
  ocupação, proxy de gap, autovalor condensado e mapas de correlação de pares.
- `experiments/11_bcs_pair_green_function.py`: salva `G^R_00(t)` e uma densidade
  espectral aproximada por FFT.
- `experiments/12_bcs_gorkov_anomalous_green.py`: salva `F^R_00(t)` e espectro
  anômalo aproximado para um estado produto BCS com fase de ordem.
- `experiments/13_bcs_gorkov_nambu_matrix.py`: salva a matriz Nambu de Gor'kov
  com canais `G`, `F`, `Fdag`, `Gdag`, traço, determinante e traço espectral.

## Observáveis de paper

Além de energia e fidelidade, a implementação mede:

- `n_i = <(I-Z_i)/2>`: ocupação de par no modo `i`;
- `C_ij = <b_i^\dagger b_j>`: matriz de correlação de pares;
- `lambda_max(C)`: proxy de ordem condensada do setor de pares;
- `Delta_eff = g sqrt(lambda_max(C))`: proxy operacional de gap efetivo para
  comparar dinâmica exata e circuito Trotterizado.
- `G^R_ij(t)=-i theta(t)<[b_i(t),b_j^\dagger(0)]>`: resposta retardada de pares.
- `-Im G^R(omega)/pi`: densidade espectral aproximada da resposta de pares.
- `F^R_ij(t)=-i theta(t)<[b_i(t),b_j(0)]>`: resposta anômala de Gor'kov.
- `-Im F^R(omega)/pi`: densidade espectral anômala aproximada.
- `G_Nambu=[[G,F],[Fdag,Gdag]]`: matriz de resposta em base Nambu.
- `-Im Tr G_Nambu(omega)/pi`: traço espectral da resposta normal/anômala.

## Resultados esperados

O script imprime um relatório comparativo com:

- energia fundamental exata;
- energia estimada por Qiskit;
- energia estimada por PennyLane;
- energia estimada por Cirq.
- curva de erro Trotter vs número de passos;
- tabela de normas de comutadores dos termos do Hamiltoniano;
- fidelidade entre circuito Qiskit Trotterizado e evolução matricial.
- curvas temporais de ocupação, gap efetivo e autovalor condensado;
- mapas finais de `|<b_i^\dagger b_j>|`.
- função de Green retardada no tempo;
- espectro aproximado da resposta de pares.
- função de Green anômala de Gor'kov;
- espectro anômalo aproximado.
- matriz Nambu de Gor'kov;
- traço espectral Nambu aproximado.

## Observações técnicas

- A implementação atual utiliza um ansatz variacional de múltiplas camadas de
  rotações `RY` e emaranhamento em cadeia por `CNOT`.
- O exemplo de `n_qubits = 4` serve como validação de conceito para o mapeamento
  BCS->qubits e a implementação de VQE em diferentes frameworks.
- A segunda camada de rotação fornece maior expressividade e melhor aproximação
  da energia fundamental.
- A evolução Trotterizada preserva o número total de pares neste Hamiltoniano,
  porque o operador de número comuta com o Hamiltoniano reduzido.
- A Trotterização de segunda ordem reduz o erro de estado mais rapidamente que a
  primeira ordem para os parâmetros usados no experimento.
