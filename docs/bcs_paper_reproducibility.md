# Roteiro reprodutível para o experimento BCS

Este roteiro fixa o experimento principal usado para gerar resultados de paper
no projeto.

Para a linha do tempo de versões, consulte `docs/bcs_release_notes.md`.

## Modelo

```text
H = sum_k xi_k Z_k - g/2 sum_{i<j} (X_i X_j + Y_i Y_j)
```

Parâmetros padrão:

- `xi = [-1.0, -0.35, 0.35, 1.0]`;
- `g = 0.8`;
- estado inicial com dois pares: `|1100>`;
- tempo final: `t = 6.0`;
- Trotter de segunda ordem com `64` passos.

## Comandos

```bash
cd ~/quantum_ic
source .venv/bin/activate
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

Ou, para a suíte completa:

```bash
scripts/run_research_suite.sh
```

Para revisar os resultados em modo interativo:

```bash
jupyter notebook notebooks/bcs_paper_reproduction.ipynb
```

Para gerar uma cópia executada e artefatos estáticos:

```bash
python -m nbconvert --to notebook --execute notebooks/bcs_paper_reproduction.ipynb \
  --output bcs_paper_reproduction_executed.ipynb --output-dir results/notebooks
python -m nbconvert --to html results/notebooks/bcs_paper_reproduction_executed.ipynb \
  --output bcs_paper_reproduction.html --output-dir results/notebooks
google-chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf="$PWD/results/notebooks/bcs_paper_reproduction.pdf" \
  "file://$PWD/results/notebooks/bcs_paper_reproduction.html"
```

Para validar o pacote reprodutível do paper:

```bash
python scripts/validate_bcs_paper_artifacts.py
```

## Saídas principais

- `results/tables/bcs_dynamics_trotter.csv`;
- `results/tables/bcs_commutator_norms.csv`;
- `results/tables/bcs_qiskit_trotter_circuit.csv`;
- `results/tables/bcs_paper_observables.csv`;
- `results/tables/bcs_pair_green_retarded.csv`;
- `results/tables/bcs_pair_green_spectral_density.csv`;
- `results/tables/bcs_gorkov_anomalous_time.csv`;
- `results/tables/bcs_gorkov_anomalous_spectrum.csv`;
- `results/tables/bcs_gorkov_nambu_time.csv`;
- `results/tables/bcs_gorkov_nambu_spectral_trace.csv`;
- `results/tables/bcs_qiskit_shots_noise.csv`;
- `results/tables/bcs_qiskit_energy_shots.csv`;
- `results/tables/bcs_qiskit_error_mitigation.csv`;
- `results/figures/bcs_trotter_error.png`;
- `results/figures/bcs_gap_condensate_time.png`;
- `results/figures/bcs_pair_occupations_time.png`;
- `results/figures/bcs_pair_correlation_exact_final.png`;
- `results/figures/bcs_pair_correlation_trotter_final.png`.
- `results/figures/bcs_pair_green_time.png`;
- `results/figures/bcs_pair_green_spectrum.png`.
- `results/figures/bcs_gorkov_anomalous_time.png`;
- `results/figures/bcs_gorkov_anomalous_spectrum.png`.
- `results/figures/bcs_gorkov_nambu_channels.png`;
- `results/figures/bcs_gorkov_nambu_spectral_trace.png`.
- `results/figures/bcs_qiskit_shots_noise_total_pairs.png`;
- `results/figures/bcs_qiskit_shots_noise_occupations.png`.
- `results/figures/bcs_qiskit_energy_shots_values.png`;
- `results/figures/bcs_qiskit_energy_shots_error.png`.
- `results/figures/bcs_qiskit_error_mitigation_zne.png`;
- `results/figures/bcs_qiskit_error_mitigation_errors.png`.
- `notebooks/bcs_paper_reproduction.ipynb`.
- `results/notebooks/bcs_paper_reproduction_executed.ipynb`.
- `results/notebooks/bcs_paper_reproduction.html`.
- `results/notebooks/bcs_paper_reproduction.pdf`.

## Observáveis

- Fidelidade entre evolução exata e Trotterizada.
- Erro vetorial de estado.
- Energia e número total de pares.
- Ocupações `n_i`.
- Matriz de correlação de pares `C_ij=<b_i^\dagger b_j>`.
- Autovalor condensado `lambda_max(C)`.
- Proxy de gap efetivo `Delta_eff=g sqrt(lambda_max(C))`.
- Função de Green retardada de pares `G^R_ij(t)=-i theta(t)<[b_i(t),b_j^\dagger(0)]>`.
- Densidade espectral aproximada `-Im G^R(omega)/pi`.
- Função de Green anômala `F^R_ij(t)=-i theta(t)<[b_i(t),b_j(0)]>`.
- Espectro anômalo aproximado `-Im F^R(omega)/pi`.
- Matriz de Gor'kov em base Nambu com canais `G`, `F`, `Fdag` e `Gdag`.
- Traço espectral aproximado `-Im Tr G_Nambu(omega)/pi`.
- Ocupações medidas por shots em Qiskit Aer.
- Comparação entre statevector, shots ideais e ruído depolarizante simples.
- Energia por decomposição Pauli `E=sum_k c_k <P_k>`.
- Erro absoluto da energia por shots ideal e ruidosa.
- Extrapolação zero-noise linear com escalas de ruído depolarizante.
- Erro antes/depois de mitigação.
