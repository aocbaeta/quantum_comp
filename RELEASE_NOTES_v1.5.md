# Release notes: v1.5-bcs-manuscript-ready

Esta release consolida o pacote reprodutível do paper BCS para revisão,
compartilhamento e preparação de depósito com DOI.

## Incluído

- Manuscrito revisado em `papers/bcs_quantum_simulation.md`.
- PDF e HTML regenerados do manuscrito.
- Notebook reprodutível e artefatos renderizados em `results/notebooks/`.
- Validação automática dos artefatos do paper.
- Política formal de licenças:
  - BSD-3-Clause para código;
  - CC BY 4.0 para documentação, figuras, notebooks, tabelas e resultados.
- Metadados formais de citação em `CITATION.cff`.
- Checklist de publicação em `docs/bcs_publication_checklist.md`.
- CI no GitHub Actions para testes e validação dos artefatos.
- Auditoria pré-publicação de parâmetros em
  `docs/experiment_parameter_audit_2026-05-21.md`, com Trotterização mais
  precisa, maior orçamento de shots e mitigação ZNE em escalas de ruído mais
  lineares.

## Arquivo de distribuição

O pacote de distribuição fica em:

```text
results/releases/bcs_quantum_simulation_v1.5.zip
```

## Validação local

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests
.venv/bin/python scripts/validate_bcs_paper_artifacts.py
```

## Citação

```text
Andre Baeta, "Quantum IC: reduced BCS Hamiltonian quantum simulation workflow",
GitHub repository, https://github.com/aocbaeta/quantum_comp.
```

Use `CITATION.cff` para metadados formais.
