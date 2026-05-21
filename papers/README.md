# Papers

Manuscritos e rascunhos científicos do projeto.

## BCS quantum simulation

Fonte principal:

```bash
papers/bcs_quantum_simulation.md
```

Notebook de reprodução:

```bash
notebooks/bcs_paper_reproduction.ipynb
```

Marcos versionados:

```bash
docs/bcs_release_notes.md
```

Checklist de publicação:

```bash
docs/bcs_publication_checklist.md
```

Citação e licenças:

```bash
CITATION.cff
LICENSE
LICENSE-DOCS
```

Gerar HTML/PDF:

```bash
pandoc papers/bcs_quantum_simulation.md -s --mathjax -o papers/bcs_quantum_simulation.html
pandoc papers/bcs_quantum_simulation.md -s --resource-path=papers:. --pdf-engine=pdflatex \
  -o papers/bcs_quantum_simulation.pdf
```

Regenerar dados antes do paper:

```bash
python experiments/08_bcs_dynamics_trotter.py
python experiments/09_bcs_qiskit_trotter_circuit.py
python experiments/10_bcs_paper_observables.py
python experiments/11_bcs_pair_green_function.py
python experiments/12_bcs_gorkov_anomalous_green.py
python experiments/13_bcs_gorkov_nambu_matrix.py
python experiments/14_bcs_qiskit_shots_noise.py
python experiments/15_bcs_qiskit_energy_shots.py
python experiments/16_bcs_qiskit_error_mitigation.py
```
