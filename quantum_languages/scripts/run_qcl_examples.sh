#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QCL="$ROOT/bin/qcl"
EXAMPLES="$ROOT/quantum_languages/qcl"

for file in \
  01_bell_pauli.qcl \
  02_deutsch_balanced.qcl \
  03_grover_search.qcl \
  04_qft_phase_kick.qcl \
  05_diagonal_hamiltonian_phase.qcl
do
  printf '\n== %s ==\n' "$file"
  output="$("$QCL" -q "$EXAMPLES/$file")"
  printf '%s\n' "$output"
  if printf '%s\n' "$output" | grep -q '^!'; then
    exit 1
  fi
done
