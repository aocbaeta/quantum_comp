from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from zeta_experiments import perform_zeta_spacing_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Zeta zero spacing statistics")
    parser.add_argument("--count", type=int, default=250, help="number of zeta zeros")
    parser.add_argument("--start", type=int, default=1, help="first zeta zero index")
    parser.add_argument("--refresh", action="store_true", help="ignore cached zeros")
    parser.add_argument("--gue-size", type=int, default=320, help="random GUE matrix size")
    args = parser.parse_args()

    zeros_path = ROOT / "results" / "tables" / f"zeta_zeros_{args.start}_{args.count}.csv"
    result = perform_zeta_spacing_experiment(
        count=args.count,
        start=args.start,
        refresh=args.refresh,
        gue_size=args.gue_size,
        save=True,
    )

    print(f"zeros:   {result['zeros_path']}")
    print(f"summary: {result['summary_path']}")
    print(f"figure:  {result['figure_path']}")
    print("\nZeta spacing summary")
    print(result['zeta_summary'])
    print("\nRandom GUE spacing summary")
    print(result['gue_summary'])


if __name__ == "__main__":
    main()
