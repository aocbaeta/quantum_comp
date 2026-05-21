# Marcos do projeto BCS

Este arquivo resume os marcos versionados do fluxo de paper BCS. As tags
correspondem a incrementos reprodutíveis do código, resultados e documentação.

## Linha do tempo

| Tag | Commit | Entrega principal |
| --- | --- | --- |
| `v0.1-bcs-paper` | `e976b30` | Fluxo inicial do paper BCS, com dinâmica exata/Trotter, observáveis, figuras e rascunho do manuscrito. |
| `v0.2-bcs-green` | `5ff0e78` | Função de Green retardada de pares e densidade espectral aproximada. |
| `v0.3-bcs-gorkov` | `eba069f` | Função de Green anômala de Gor'kov e espectro anômalo. |
| `v0.4-bcs-nambu` | `6761bd1` | Matriz de Gor'kov em base Nambu e traço espectral. |
| `v0.5-bcs-shots-noise` | `c2c060b` | Simulação Qiskit Aer com shots e ruído depolarizante para ocupações. |
| `v0.6-bcs-energy-shots` | `a8e4f83` | Estimativa de energia por decomposição Pauli medida com shots. |
| `v0.7-bcs-error-mitigation` | `413f1c4` | Extrapolação zero-noise linear para energia BCS ruidosa. |
| `v0.8-bcs-reproduction-notebook` | `3cae45a` | Notebook interativo de reprodução do paper. |
| `v0.9-bcs-reproduction-artifacts` | `6b9b177` | Notebook executado, HTML e PDF estático de reprodução. |
| `v1.0-bcs-paper-validation` | `cedef64` | Validador automatizado dos artefatos do pacote reprodutível. |
| `v1.1-bcs-release-notes` | `73e5f6d` | Changelog dos marcos BCS e comandos de auditoria. |
| `v1.2-bcs-ci` | `d62f136` | CI no GitHub Actions para testes e validação dos artefatos BCS. |
| `v1.3-bcs-citation-package` | `cc8ff38` | Metadados de citação, checklist editorial e validação ampliada do pacote. |
| `v1.4-bcs-license-policy` | `27c1b9b` | Licença BSD-3-Clause para código e CC BY 4.0 para documentação/resultados. |

## Estado em `v1.0`

O pacote BCS inclui:

- núcleo matemático em `src/bcs.py`;
- circuitos e medições Qiskit em `src/bcs_qiskit.py`;
- experimentos `experiments/08` a `experiments/16`;
- tabelas em `results/tables/`;
- figuras em `results/figures/`;
- manuscrito em `papers/bcs_quantum_simulation.md`;
- PDF do manuscrito em `papers/bcs_quantum_simulation.pdf`;
- notebook em `notebooks/bcs_paper_reproduction.ipynb`;
- artefatos renderizados em `results/notebooks/`;
- validação em `scripts/validate_bcs_paper_artifacts.py`;
- CI em `.github/workflows/ci.yml`;
- metadados de citação em `CITATION.cff`;
- checklist editorial em `docs/bcs_publication_checklist.md`;
- licenças em `LICENSE` e `LICENSE-DOCS`.

## Comandos de auditoria

```bash
git tag --list 'v*-bcs*' --sort=creatordate
python scripts/validate_bcs_paper_artifacts.py
PYTHONPATH=src .venv/bin/python -m pytest -q tests
```
