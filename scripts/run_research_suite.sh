#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"

cd "$ROOT"

printf '\n== Tests ==\n'
PYTHONPATH="$ROOT/src" "$PY" -m pytest -q tests

printf '\n== Core experiments ==\n'
"$PY" experiments/run_all.py

printf '\n== BCS VQE comparison ==\n'
"$PY" quantum_languages/scripts/bcs_project.py --optimizer random --maxiter 32 --restarts 1

printf '\n== Quantum language examples ==\n'
quantum_languages/scripts/run_qcl_examples.sh
quantum_languages/scripts/run_framework_examples.sh

printf '\n== BCS paper artifacts ==\n'
"$PY" scripts/validate_bcs_paper_artifacts.py

printf '\nResearch suite completed.\n'
