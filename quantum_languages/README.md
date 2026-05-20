# Quantum Language Versions

Versoes em linguagens de computacao quantica dos experimentos do projeto.

## QCL

QCL e a linguagem historica instalada em `~/quantum_ic/bin/qcl`.

```bash
cd ~/quantum_ic
quantum_languages/scripts/run_qcl_examples.sh
```

Arquivos:

```text
qcl/01_bell_pauli.qcl
qcl/02_deutsch_balanced.qcl
qcl/03_grover_search.qcl
qcl/04_qft_phase_kick.qcl
qcl/05_diagonal_hamiltonian_phase.qcl
```

Esses exemplos cobrem:

```text
Bell state
Deutsch
Grover
QFT/DFT
evolucao por fase de Hamiltoniano diagonal
```

## OpenQASM

OpenQASM e mais facil de portar para ferramentas modernas.

Arquivos:

```text
openqasm/bell.qasm
openqasm/grover_2q_mark_3.qasm
```

## Nota Sobre Zeta

Zeros da zeta entram no projeto como dados espectrais/classicos, estatistica
GUE e hipotese de Hilbert-Polya. A parte quantica mais natural nessa fase e
representar espectros por fases/unitarios e estudar algoritmos como QFT,
estimacao de fase e simulacao Hamiltoniana.

## Frameworks Modernos

```bash
cd ~/quantum_ic
source .venv/bin/activate
quantum_languages/scripts/run_framework_examples.sh
```

Implementacoes:

```text
qiskit/algorithms_qiskit.py
cirq/algorithms_cirq.py
pennylane/algorithms_pennylane.py
qml/variational_classifier_pennylane.py
```

Tutoriais:

```text
tutorials/qcl.md
tutorials/qiskit.md
tutorials/cirq.md
tutorials/pennylane.md
tutorials/openqasm.md
tutorials/zeta.md
tutorials/commutator.md
tutorials/bcs.md
```

Documentação teórica:

```text
docs/BCS_QC.pdf
```

Scripts:

```text
scripts/commutator_symbolic.py
scripts/commutator_converter.py
scripts/bcs_project.py
```
