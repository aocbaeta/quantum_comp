from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from zeta_experiments import perform_critical_line_scan


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan zeta on the critical line")
    parser.add_argument("--t-min", type=float, default=10.0)
    parser.add_argument("--t-max", type=float, default=40.0)
    parser.add_argument("--points", type=int, default=900)
    parser.add_argument("--zero-count", type=int, default=8)
    args = parser.parse_args()

    result = perform_critical_line_scan(
        t_min=args.t_min,
        t_max=args.t_max,
        points=args.points,
        zero_count=args.zero_count,
        save=True,
    )

    print(f"table:  {result['table_path']}")
    print(f"figure: {result['figure_path']}")
    print(f"zeros in window: {result['zeros']}")


if __name__ == "__main__":
    main()
