# Resumo de release BCS v1.5

## Projeto

`Quantum IC` inclui um fluxo reprodutível para simulação quântica do
Hamiltoniano BCS reduzido em qubits. O pacote combina evolução exata,
Trotterização, circuitos Qiskit, funções de Green, canais anômalos de Gor'kov,
matriz Nambu, medições por shots, ruído depolarizante e mitigação por
extrapolação zero-noise.

Esta é uma pesquisa independente de Andre Baeta. Uso acadêmico, técnico ou
derivado deve citar o projeto conforme `CITATION.cff`.

## Principais resultados

- Trotterização de segunda ordem com 256 passos em `t=2.5`:
  fidelidade `0.9999999957`.
- Série temporal até `t=6.0` preservando número total de pares com erro da
  ordem de `10^-14`.
- Circuito Qiskit Trotterizado validado contra evolução matricial com
  fidelidade `0.9999999999999658`.
- Função de Green retardada de pares, canal anômalo de Gor'kov e matriz Nambu
  com espectros aproximados gerados em figuras reproduzíveis.
- Energia por decomposição Pauli estimada com shots e primeira mitigação
  zero-noise linear.

## Artefatos principais

- `papers/bcs_quantum_simulation.pdf`;
- `papers/bcs_quantum_simulation.md`;
- `notebooks/bcs_paper_reproduction.ipynb`;
- `results/notebooks/bcs_paper_reproduction.pdf`;
- `results/notebooks/bcs_paper_reproduction.html`;
- `results/tables/`;
- `results/figures/`;
- `CITATION.cff`;
- `LICENSE`;
- `LICENSE-DOCS`.

## Como citar

```text
Andre Baeta, "Quantum IC: reduced BCS Hamiltonian quantum simulation workflow",
GitHub repository, https://github.com/aocbaeta/quantum_comp.
```

## Licenças

- Código-fonte: BSD-3-Clause.
- Documentação, manuscrito, figuras, notebooks, tabelas e artefatos
  renderizados: CC BY 4.0.

## Validação

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests
.venv/bin/python scripts/validate_bcs_paper_artifacts.py
```
