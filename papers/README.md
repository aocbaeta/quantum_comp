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

Gerar HTML/PDF:

```bash
pandoc papers/bcs_quantum_simulation.md -s -o papers/bcs_quantum_simulation.html
google-chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf="$PWD/papers/bcs_quantum_simulation.pdf" \
  "file://$PWD/papers/bcs_quantum_simulation.html"
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
