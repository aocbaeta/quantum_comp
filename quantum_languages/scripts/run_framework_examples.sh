#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/.venv/bin/python"

for file in \
  "$ROOT/quantum_languages/qiskit/algorithms_qiskit.py" \
  "$ROOT/quantum_languages/cirq/algorithms_cirq.py" \
  "$ROOT/quantum_languages/pennylane/algorithms_pennylane.py" \
  "$ROOT/quantum_languages/qml/variational_classifier_pennylane.py"
do
  printf '\n######## %s ########\n' "${file#$ROOT/}"
  "$PY" "$file"
done
