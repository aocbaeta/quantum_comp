# Zeros da Zeta

Esta parte e classica/espectral, nao um circuito quantico direto.

## Estatistica de espacamentos

```bash
cd ~/quantum_ic
source .venv/bin/activate
python experiments/05_zeta_zeros_statistics.py --count 500 --gue-size 500
```

Gera:

```text
results/tables/zeta_zeros_1_500.csv
results/tables/zeta_spacing_summary.csv
results/figures/zeta_spacing_histogram.png
```

## Linha critica

```bash
python experiments/06_zeta_critical_line_scan.py --t-min 10 --t-max 40
```

Gera:

```text
results/tables/zeta_critical_line_scan.csv
results/figures/zeta_critical_line_scan.png
```

## Ponte com computacao quantica

O caminho de pesquisa natural e:

```text
zeros da zeta -> espectro -> estatistica GUE -> hipotese Hilbert-Polya
Hamiltoniano H -> propagador exp(-iHt) -> fases -> QFT/estimacao de fase
```

Nesta fase, o codigo calcula os dados espectrais e compara com GUE. O proximo
passo e construir Hamiltonianos toy cujos espectros imitem estatisticas GUE.
