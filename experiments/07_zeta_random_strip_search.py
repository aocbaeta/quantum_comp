from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mpmath as mp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zeta_experiments import perform_random_strip_search, _parse_expression_value


def main() -> None:
    parser = argparse.ArgumentParser(description="Random search for small zeta values in the critical strip")
    parser.add_argument("--sigma-min", type=float, default=0.01, help="minimum real part sigma")
    parser.add_argument("--sigma-max", type=float, default=0.99, help="maximum real part sigma")
    parser.add_argument("--t-min", type=float, default=10.0, help="minimum imaginary part t")
    parser.add_argument("--t-max", type=float, default=40.0, help="maximum imaginary part t")
    parser.add_argument("--samples", type=int, default=2000, help="number of random points to sample")
    parser.add_argument("--top-k", type=int, default=10, help="number of best candidates to report")
    parser.add_argument("--seed", type=int, default=7, help="random seed")
    parser.add_argument("--precision", type=int, default=50, help="mpmath precision in decimal places")
    parser.add_argument("--no-save", action="store_true", help="do not save table and figure")
    parser.add_argument("--fix-sigma", type=str, default=None, help="fix real part sigma (e.g. 0.5 or pi/4 or atan(1))")
    parser.add_argument("--fix-t", type=str, default=None, help="fix imaginary part t (e.g. 14.13 or pi/4)")
    args = parser.parse_args()

    def parse_optional_mpmath(expr: str | None) -> float | None:
        if expr is None:
            return None
        try:
            return _parse_expression_value(expr, args.precision)
        except Exception as exc:
            raise SystemExit(f"Invalid expression for fixed value: {expr} ({exc})")

    result = perform_random_strip_search(
        sigma_min=args.sigma_min,
        sigma_max=args.sigma_max,
        t_min=args.t_min,
        t_max=args.t_max,
        samples=args.samples,
        top_k=args.top_k,
        seed=args.seed,
        precision=args.precision,
        fixed_sigma=parse_optional_mpmath(args.fix_sigma),
        fixed_t=parse_optional_mpmath(args.fix_t),
        save=not args.no_save,
    )

    if result["table_path"] is not None:
        print(f"table:  {result['table_path']}")
    print(f"figure: {result['figure_path']}")
    print("\nBest candidate points:")
    for idx, candidate in enumerate(result["candidates"], start=1):
        print(
            f"{idx}. sigma={candidate['sigma']:.6f}, t={candidate['t']:.6f}, |zeta|={candidate['abs']:.4e}, real={candidate['real']:.4e}, imag={candidate['imag']:.4e}"
        )


if __name__ == "__main__":
    main()
