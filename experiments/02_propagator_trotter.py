from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from algebra import X, Z
from propagator import trotter_error_curve


def main() -> None:
    rows = trotter_error_curve([X, Z], time=1.0, steps_values=[1, 2, 4, 8, 16, 32, 64])
    out = ROOT / "results" / "tables" / "trotter_error.csv"
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["steps", "error", "unitary"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved: {out}")
    for row in rows:
        print(f"N={int(row['steps']):>2} error={row['error']:.6e} unitary={bool(row['unitary'])}")


if __name__ == "__main__":
    main()
