# Quantum IC

Quantum IC é um laboratório Python para pesquisa, desenvolvimento e validação de modelos de muitos corpos e simulação quântica.

O repositório integra:

- modelagem de Hamiltonianos hermitianos e estruturas BCS;
- análise de propagadores, comutadores e dinâmica quântica;
- implementações em QCL, Qiskit, PennyLane e Cirq;
- tutoriais, documentação técnica e resultados reproduzíveis.

## Pré-requisitos

```bash
cd ~/quantum_ic
source .venv/bin/activate
```

## Estrutura do repositório

```text
src/                código reutilizável e núcleo matemático
experiments/        scripts de experimentos reproduzíveis
quantum_languages/  implementações e tutoriais de linguagens quânticas
docs/               documentação técnica e arquivos de suporte
results/            figuras, tabelas e logs gerados
notebooks/          análises interativas e notebooks exploratórios
papers/             referências acadêmicas e relatórios
tests/              testes unitários e de integração
bin/                utilitários e wrappers locais
```

## Documentação relevante

- `docs/BCS_QC.pdf` — fundamentação teórica para o modelo BCS e o mapeamento para qubits.
- `docs/BCS_QC_comparacao.md` — análise de compatibilidade entre teoria e implementação.
- `docs/tutoriais_quantum.md` — guia unificado de tutoriais do laboratório.

## Execução de exemplos

### Frameworks quânticos

```bash
cd ~/quantum_ic
source .venv/bin/activate
quantum_languages/scripts/run_framework_examples.sh
```

### Exemplos QCL

```bash
cd ~/quantum_ic
source .venv/bin/activate
quantum_languages/scripts/run_qcl_examples.sh
```

### Experimentos principais

```bash
cd ~/quantum_ic
source .venv/bin/activate
python experiments/run_all.py
```

### Suíte completa de pesquisa

```bash
cd ~/quantum_ic
scripts/run_research_suite.sh
```

### Manuscrito BCS

```bash
pandoc papers/bcs_quantum_simulation.md -s -o papers/bcs_quantum_simulation.html
google-chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf="$PWD/papers/bcs_quantum_simulation.pdf" \
  "file://$PWD/papers/bcs_quantum_simulation.html"
```

### Simulação da hipótese de Riemann

```bash
python experiments/05_zeta_zeros_statistics.py --count 500 --gue-size 500
python experiments/06_zeta_critical_line_scan.py --t-min 10 --t-max 40
```

### Interface gráfica

```bash
python experiments/zeta_explorer.py
```

### Busca aleatória no strip crítico

```bash
python experiments/07_zeta_random_strip_search.py --sigma-min 0.01 --sigma-max 0.99 --t-min 10 --t-max 40 --samples 2000
```

## Projeto BCS

- `quantum_languages/scripts/bcs_project.py` — implementação VQE para o Hamiltoniano BCS reduzido;
- `src/bcs.py` — Hamiltoniano BCS reduzido, observáveis, evolução exata, Trotterização e métricas;
- `src/bcs_qiskit.py` — circuito Qiskit para evolução Trotterizada do BCS;
- `experiments/08_bcs_dynamics_trotter.py` — comparação exata vs Trotter de 1ª e 2ª ordem;
- `experiments/09_bcs_qiskit_trotter_circuit.py` — validação circuito Qiskit vs evolução matricial;
- `experiments/10_bcs_paper_observables.py` — observáveis físicos para figuras do paper;
- `experiments/11_bcs_pair_green_function.py` — função de Green retardada de pares e espectro aproximado;
- `experiments/12_bcs_gorkov_anomalous_green.py` — função de Green anômala de Gor'kov em estado produto BCS;
- `experiments/13_bcs_gorkov_nambu_matrix.py` — matriz de Gor'kov em base Nambu e traço espectral;
- `experiments/14_bcs_qiskit_shots_noise.py` — medição Qiskit por shots e ruído depolarizante simples;
- `experiments/15_bcs_qiskit_energy_shots.py` — energia BCS por decomposição Pauli medida com shots;
- `quantum_languages/tutorials/bcs.md` — tutorial técnico para mapeamento BCS → qubits;
- `docs/BCS_QC.pdf` — referência teórica associada.
- `papers/bcs_quantum_simulation.md` — rascunho de paper com figuras e resultados.

## QCL local

O repositório inclui uma instalação local de QCL 0.6.4.

```bash
bin/qcl -V
bin/qcl quantum_languages/qcl/01_bell_pauli.qcl
```

## Dependências

```bash
cd ~/quantum_ic
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Testes

```bash
cd ~/quantum_ic
PYTHONPATH=src .venv/bin/python -m pytest -q tests
```

## Resultados

- as saídas estruturadas são gravadas em `results/tables/`;
- figuras e painéis são gerados em `results/figures/`.

## Referências adicionais

- `quantum_languages/README.md` — visão geral das linguagens quânticas e frameworks suportados;
- `docs/color_scheme.md` — esquema de cores adotado pelo projeto;
- `src/quantum_colors.py` — definições de paleta para visualização.
