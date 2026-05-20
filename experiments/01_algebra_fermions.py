from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from algebra import X, Y, Z, anticommutator, commutator, pretty_matrix
from fermions import verify_canonical_anticommutation


def main() -> None:
    print("[X, Y]")
    print(pretty_matrix(commutator(X, Y)))
    print("\n2iZ")
    print(pretty_matrix(2j * Z))
    print("\n{X, Y}")
    print(pretty_matrix(anticommutator(X, Y)))

    errors = verify_canonical_anticommutation(3)
    print("\nCanonical fermion anticommutation errors")
    for key, value in errors.items():
        print(f"{key}: {value:.3e}")

    assert np.allclose(commutator(X, Y), 2j * Z)
    assert np.allclose(anticommutator(X, Y), np.zeros((2, 2)))
    assert errors["passed"] == 1.0


if __name__ == "__main__":
    main()
