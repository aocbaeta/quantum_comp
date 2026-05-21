# Revisão técnica do projeto em 2026-05-21

Esta revisão cobre o pacote BCS, documentação, scripts de reprodução e artefatos
de distribuição existentes no marco posterior a `v1.6-bcs-release-package`.

## Correções aplicadas

- O manuscrito BCS passou a usar matemática LaTeX para Hamiltoniano, estados,
  funções de Green, matriz Nambu, energia Pauli e escalas de ruído.
- Os comandos de geração do PDF do paper agora usam `pandoc` com
  `--pdf-engine=pdflatex`, melhorando a renderização de símbolos e equações em
  comparação com a impressão HTML por navegador.
- O HTML do paper passou a ser gerado com `--mathjax`, preservando equações no
  navegador.
- O roteiro de reprodutibilidade, a comparação BCS e o tutorial quântico foram
  ajustados para evitar pseudo-matemática em blocos de código quando o conteúdo
  é matemático.
- O PDF de tutoriais foi regenerado após as correções de `markdownlint`.

## Validações realizadas

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q tests
.venv/bin/python scripts/validate_bcs_paper_artifacts.py
pandoc papers/bcs_quantum_simulation.md -s --resource-path=papers:. --pdf-engine=pdflatex \
  -o papers/bcs_quantum_simulation.pdf
pandoc docs/tutoriais_quantum.md -s --pdf-engine=pdflatex \
  -o docs/tutoriais_quantum.pdf
```

## Pontos fortes

- O núcleo BCS está bem separado entre implementação matricial (`src/bcs.py`) e
  circuitos/medições Qiskit (`src/bcs_qiskit.py`).
- Há testes unitários para álgebra, dinâmica BCS, funções de Green, circuito
  Qiskit, contagens, energia por Pauli e extrapolação zero-noise.
- O pacote de paper tem validação automática de tabelas, figuras, notebooks,
  PDFs, licenças, citação e ZIP de distribuição.
- O CI remoto executa testes e validação de artefatos a cada push.

## Pontos de otimização recomendados

- `src/bcs.py` recompõe operadores de criação, aniquilação e número em várias
  chamadas. Para sistemas maiores, vale introduzir cache por `(n_qubits, index)`.
- A Trotterização matricial usa matrizes densas e `matrix_power`; isso é ótimo
  para quatro qubits, mas deve migrar para evolução por estado/circuito quando
  `n_qubits` crescer.
- O pacote ZIP inclui `results/tables/` e `results/figures/` completos,
  incluindo artefatos de linguagens quânticas. Para uma release puramente BCS,
  pode-se criar um ZIP menor contendo apenas arquivos `bcs_*`.
- O validador confirma a presença e assinatura dos arquivos, mas ainda não
  verifica se o ZIP contém exatamente a versão mais recente de cada artefato.
- As referências bibliográficas ainda estão como lista inicial. Para submissão
  acadêmica, o próximo passo é transformar essa seção em BibTeX/CSL com citações
  completas.

## Risco residual

- As simulações Qiskit com ruído são demonstrativas e dependem de modelo simples
  depolarizante; não devem ser apresentadas como calibração de hardware real.
- A análise espectral por FFT usa janela finita e amortecimento fenomenológico;
  os picos devem ser interpretados como diagnóstico numérico, não como espectro
  termodinâmico.
