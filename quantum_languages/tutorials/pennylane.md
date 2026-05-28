# PennyLane

PennyLane e a melhor ponte entre circuitos quanticos e otimizacao/diferenciacao.

## Rodar circuitos basicos

```bash
cd ~/quantum_comp
source .venv/bin/activate
python quantum_languages/pennylane/algorithms_pennylane.py
```

## Rodar QML

```bash
python quantum_languages/qml/variational_classifier_pennylane.py
```

## Saidas

```text
results/tables/quantum_languages/pennylane_*.json
results/tables/quantum_languages/qml_variational_classifier.json
```

## Quando usar

Use PennyLane para VQE variacional, QML, circuitos diferenciaveis, classificadores
quanticos e modelos hibridos classico-quanticos.
