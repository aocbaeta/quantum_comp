# Checklist de publicação BCS

Esta checklist organiza o pacote mínimo para revisar, compartilhar ou submeter
o trabalho de simulação quântica do Hamiltoniano BCS reduzido.

## Código

- [x] Núcleo matemático em `src/bcs.py`.
- [x] Circuitos, shots, ruído e energia Pauli em `src/bcs_qiskit.py`.
- [x] Experimentos reprodutíveis em `experiments/08` a `experiments/16`.
- [x] Testes automatizados em `tests/test_core.py`.
- [x] CI no GitHub Actions em `.github/workflows/ci.yml`.

## Resultados

- [x] Tabelas CSV em `results/tables/`.
- [x] Figuras PNG em `results/figures/`.
- [x] Notebook executado em `results/notebooks/bcs_paper_reproduction_executed.ipynb`.
- [x] HTML estático em `results/notebooks/bcs_paper_reproduction.html`.
- [x] PDF estático em `results/notebooks/bcs_paper_reproduction.pdf`.

## Manuscrito e documentação

- [x] Manuscrito fonte em `papers/bcs_quantum_simulation.md`.
- [x] PDF do manuscrito em `papers/bcs_quantum_simulation.pdf`.
- [x] Roteiro de reprodutibilidade em `docs/bcs_paper_reproducibility.md`.
- [x] Marcos versionados em `docs/bcs_release_notes.md`.
- [x] Metadados de citação em `CITATION.cff`.

## Auditoria antes de compartilhar

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests
.venv/bin/python scripts/validate_bcs_paper_artifacts.py
gh run list --repo aocbaeta/quantum_comp --limit 3
```

## Pendências editoriais

- [ ] Revisar linguagem e formatação final do manuscrito.
- [ ] Decidir licença formal do repositório.
- [ ] Adicionar DOI quando houver depósito em Zenodo, OSF ou plataforma equivalente.
- [ ] Adaptar o manuscrito ao template do periódico ou conferência escolhida.
