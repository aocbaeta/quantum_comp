# Comparação entre `BCS_QC` e o projeto `quantum_ic`

Este documento documenta a relação entre o material teórico presente em `docs/BCS_QC.pdf` e a implementação prática do modelo BCS no repositório `quantum_ic`.

## Objetivo

Estabelecer a correspondência entre:

- a fundamentação teórica do modelo BCS e do mapeamento para qubits;
- a implementação de Hamiltonianos e algoritmos variacionais em Qiskit, PennyLane e Cirq.

## Escopo do material teórico

O PDF aborda os seguintes pontos relevantes:

- estrutura da álgebra fermiônica graduada e relações canônicas de anticomutação;
- definição de operadores de par de Cooper `b_k` e `b_k^\dagger`;
- formulação do Hamiltoniano BCS reduzido em termos de pseudospins de Anderson;
- conversão do Hamiltoniano para a forma em qubits:

```text
H = \sum_k \xi_k Z_k - \frac{g}{2} \sum_{k<j} (X_k X_j + Y_k Y_j)
```

- implementação em Qiskit, PennyLane e Cirq;
- aplicação do algoritmo VQE para estimar a energia do estado fundamental;
- discussão sobre propagadores, Trotterização e dinâmica quântica.

## Correspondência com a implementação existente

A implementação atual no repositório cobre os seguintes elementos:

- `quantum_languages/scripts/bcs_project.py` representa o Hamiltoniano BCS reduzido em termos de operadores de Pauli;
- `quantum_languages/tutorials/bcs.md` descreve explicitamente o uso de pseudospins de Anderson e a energia fundamental de BCS;
- a comparação de resultados contempla a energia exata clássica e as estimativas de VQE em Qiskit, PennyLane e Cirq;
- a conversão para `SparsePauliOp`, `qml.Hamiltonian` e a simulação via estado final em Cirq está alinhada com a formulação teórica do PDF.

## Lacunas e extensões possíveis

O PDF contém material teórico que ainda não está plenamente representado em código no repositório:

- desenvolvimento detalhado da álgebra fermiônica graduada;
- mapeamento completo de operadores de criação/aniquilação fermiônicos;
- funções de Green e equações de Gor'kov.

As seguintes lacunas foram endereçadas na implementação posterior:

- análise de dinâmica BCS, propagadores unitários e evolução temporal;
- decomposição Trotterizada para termos não comutativos;
- validação de circuito Qiskit para a dinâmica Trotterizada;
- tabela de normas de comutadores entre termos do Hamiltoniano.
- observáveis físicos de pares: ocupações, matriz `C_ij=<b_i^\dagger b_j>`,
  autovalor condensado e proxy de gap efetivo.
- função de Green retardada de pares e densidade espectral aproximada.

## Conclusão

A abordagem teórica de `BCS_QC.pdf` é compatível com o escopo prático do projeto `quantum_ic`.

- A implementação atual materializa o Hamiltoniano reduzido BCS, a comparação
  VQE, a dinâmica Trotterizada e observáveis físicos de pares.
- O mapeamento para qubits está correto e coerente com a teoria apresentada.
- O principal diferencial do PDF é a profundidade teórica adicional em muitos corpos e evolução temporal.

## Recomendações

Para aumentar o alinhamento entre teoria e código, recomenda-se:

- expandir o tutorial `quantum_languages/tutorials/bcs.md` com a derivação do mapeamento de pseudospins e das relações de anticomutação;
- derivar funções de Green mais completas, incluindo versões anômalas e
  equações de Gor'kov;
- derivar observáveis BCS adicionais de resposta linear com ruído e shots;
- referenciar `docs/BCS_QC.pdf` diretamente nas seções teóricas do projeto.
