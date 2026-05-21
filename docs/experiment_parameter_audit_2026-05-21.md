# Auditoria de parâmetros dos experimentos

Data: 2026-05-21

Esta auditoria revisa pontos em que a precisão numérica poderia ser aumentada
antes de tornar o repositório público. As alterações aplicadas preservam o
modelo físico principal e evitam mudar interpretações que dependem de nova
análise.

## Melhorias aplicadas

### Trotterização BCS

O experimento `08_bcs_dynamics_trotter.py` passou a avaliar também `128` e
`256` passos. Em `t=2.5`, ordem 2:

| Passos | Fidelidade | Erro de estado |
|---:|---:|---:|
| 64 | 0.9999988959 | 0.0016610647 |
| 128 | 0.9999999311 | 0.0004150952 |
| 256 | 0.9999999957 | 0.0001037631 |

O experimento principal `10_bcs_paper_observables.py` passou de `64` para
`256` passos. No tempo final `t=6.0`, o erro de estado caiu para
`0.0014102508`, com erro no número total de pares da ordem de `10^-14`.

### Shots em Qiskit

Os experimentos `14_bcs_qiskit_shots_noise.py` e
`15_bcs_qiskit_energy_shots.py` passaram a usar:

```text
1024, 4096, 8192, 16384, 32768
```

Na estimativa de energia por decomposição Pauli, o erro ideal contra o
statevector Trotterizado caiu de `0.0065575699` em `8192` shots para
`0.0003472427` em `32768` shots. O caso ruidoso permanece dominado pelo canal
de ruído depolarizante, como esperado.

### Mitigação zero-noise

O experimento `16_bcs_qiskit_error_mitigation.py` passou a usar `16384` shots
e escalas de ruído mais próximas do limite linear:

```text
0.25, 0.50, 0.75, 1.00
```

Antes, com `4096` shots e escalas `1, 2, 3`, o erro mitigado contra o
statevector era `0.7535709162`. Agora, com a janela de ruído menor, o erro
mitigado caiu para `0.1362053970`, com RMSE do ajuste linear `0.0193284493`.

## Mudanças não aplicadas

### Funções de Green e espectros

Foi testada uma malha temporal mais longa para as respostas retardadas. A
janela `tmax=36` melhora a resolução em frequência de aproximadamente `0.3491`
para `0.1745`, mas também muda quais picos aparecem como dominantes. Como isso
altera a leitura física do espectro, os scripts espectrais foram mantidos em
`tmax=18`, `361` pontos e `eta=0.04`.

Próxima melhoria recomendada: criar um experimento separado de convergência
espectral, variando `tmax`, `eta` e número de pontos, em vez de trocar o
parâmetro padrão silenciosamente.

## Conclusão

As melhorias aplicadas aumentam a precisão dos resultados centrais do paper sem
mudar o Hamiltoniano, o estado inicial ou a interpretação principal. Para uma
versão pública, os pontos ainda mais profissionais seriam: adicionar barras de
erro estatísticas por repetição de seeds, separar releases por escopo e
transformar referências em BibTeX/CSL.
