# Roteiro reprodutível para o experimento BCS

Este roteiro fixa o experimento principal usado para gerar resultados de paper
no projeto.

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
```

Ou, para a suíte completa:

```bash
scripts/run_research_suite.sh
```

## Saídas principais

- `results/tables/bcs_dynamics_trotter.csv`;
- `results/tables/bcs_commutator_norms.csv`;
- `results/tables/bcs_qiskit_trotter_circuit.csv`;
- `results/tables/bcs_paper_observables.csv`;
- `results/tables/bcs_pair_green_retarded.csv`;
- `results/tables/bcs_pair_green_spectral_density.csv`;
- `results/figures/bcs_trotter_error.png`;
- `results/figures/bcs_gap_condensate_time.png`;
- `results/figures/bcs_pair_occupations_time.png`;
- `results/figures/bcs_pair_correlation_exact_final.png`;
- `results/figures/bcs_pair_correlation_trotter_final.png`.
- `results/figures/bcs_pair_green_time.png`;
- `results/figures/bcs_pair_green_spectrum.png`.

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
