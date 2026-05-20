from __future__ import annotations

import csv
from pathlib import Path

import mpmath as mp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from quantum_colors import QUANTUM_COLORS, apply_quantum_style
from spectral_stats import (
    gue_wigner_surmise_pdf,
    poisson_spacing_pdf,
    random_gue_eigenvalues,
    locally_unfolded_spacings,
    spacing_summary,
)
from zeta_zeros import (
    compute_zeta_zeros,
    get_or_compute_zeros,
    normalized_spacings,
    zeta_in_strip,
    zeta_on_critical_line,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_summary(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dataset",
                "count",
                "mean",
                "variance",
                "min_value",
                "max_value",
                "ks_poisson",
                "ks_gue_wigner",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _parse_expression_value(value: str | float | int, precision: int) -> float:
    if isinstance(value, float) or isinstance(value, int):
        return float(value)
    safe_context = {
        "pi": mp.pi,
        "e": mp.e,
        "tau": 2 * mp.pi,
        "phi": (1 + mp.sqrt(5)) / 2,
        "sqrt": mp.sqrt,
        "log": mp.log,
        "ln": mp.log,
        "exp": mp.exp,
        "sin": mp.sin,
        "cos": mp.cos,
        "tan": mp.tan,
        "atan": mp.atan,
        "asin": mp.asin,
        "acos": mp.acos,
        "sinh": mp.sinh,
        "cosh": mp.cosh,
        "tanh": mp.tanh,
        "mp": mp,
    }
    with mp.workdps(precision):
        try:
            return float(eval(value, {"__builtins__": None}, safe_context))
        except Exception as exc:
            raise ValueError(f"Invalid expression for fixed value: {value} ({exc})")


def _plot_spacing_figure(zeta_spacings: np.ndarray, gue_spacings: np.ndarray) -> Figure:
    apply_quantum_style()
    xs = np.linspace(0, max(4.0, float(np.percentile(zeta_spacings, 99))), 400)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.hist(
        zeta_spacings,
        bins=36,
        density=True,
        alpha=0.55,
        label="Zeta zeros unfolded",
        color=QUANTUM_COLORS["qubit_cyan"],
    )
    ax.hist(
        gue_spacings,
        bins=36,
        density=True,
        alpha=0.28,
        label="Random GUE bulk",
        color=QUANTUM_COLORS["fermion_green"],
    )
    ax.plot(xs, poisson_spacing_pdf(xs), "--", label="Poisson", color=QUANTUM_COLORS["phase_red"])
    ax.plot(xs, gue_wigner_surmise_pdf(xs), label="GUE Wigner surmise", color=QUANTUM_COLORS["cooper_gold"])
    ax.set_xlabel("normalized spacing")
    ax.set_ylabel("density")
    ax.set_title("Nearest-neighbor spacings: zeta zeros vs random matrices")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def _plot_critical_line_figure(t_values: np.ndarray, abs_values: np.ndarray, zeros: list[float]) -> Figure:
    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.plot(t_values, abs_values, color=QUANTUM_COLORS["qubit_cyan"], label=r"$|\zeta(1/2+it)|$")
    for zero in zeros:
        ax.axvline(zero, color=QUANTUM_COLORS["phase_red"], alpha=0.55, linewidth=1.1)
    ax.set_xlabel("t")
    ax.set_ylabel("magnitude")
    ax.set_title("Zeta function on the critical line")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def perform_zeta_spacing_experiment(
    count: int = 250,
    start: int = 1,
    refresh: bool = False,
    gue_size: int = 320,
    save: bool = True,
    progress_callback: callable | None = None,
) -> dict[str, object]:
    if progress_callback:
        progress_callback("Computing zeta zeros...")
    zeros_path = ROOT / "results" / "tables" / f"zeta_zeros_{start}_{count}.csv"
    zeros = get_or_compute_zeros(count=count, start=start, path=zeros_path, refresh=refresh)
    zeta_spacings = normalized_spacings(zeros)

    if progress_callback:
        progress_callback("Generating random GUE sample...")
    gue_values = random_gue_eigenvalues(gue_size)
    gue_spacings = locally_unfolded_spacings(gue_values)

    if progress_callback:
        progress_callback("Summarizing results...")
    zeta_summary = spacing_summary(zeta_spacings)
    gue_summary = spacing_summary(gue_spacings)
    summary_path = ROOT / "results" / "tables" / "zeta_spacing_summary.csv"
    summary_rows = [
        {"dataset": "zeta_zeros", **zeta_summary.__dict__},
        {"dataset": "random_gue", **gue_summary.__dict__},
    ]
    if save:
        _write_summary(summary_path, summary_rows)

    if progress_callback:
        progress_callback("Plotting spacing histogram...")
    figure = _plot_spacing_figure(zeta_spacings, gue_spacings)
    figure_path = ROOT / "results" / "figures" / "zeta_spacing_histogram.png"
    if save:
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(figure_path, dpi=180)
        plt.close(figure)
    return {
        "zeros_path": zeros_path,
        "summary_path": summary_path,
        "figure_path": figure_path,
        "zeta_summary": zeta_summary,
        "gue_summary": gue_summary,
        "figure": figure,
    }


def perform_critical_line_scan(
    t_min: float = 10.0,
    t_max: float = 40.0,
    points: int = 900,
    zero_count: int = 8,
    save: bool = True,
    progress_callback: callable | None = None,
) -> dict[str, object]:
    if progress_callback:
        progress_callback("Sampling t values on critical line...")
    t_values = np.linspace(t_min, t_max, points)
    z_values = zeta_on_critical_line(t_values)
    abs_values = np.abs(z_values)

    if progress_callback:
        progress_callback("Saving table data...")
    table_path = ROOT / "results" / "tables" / "zeta_critical_line_scan.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    if save:
        with table_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["t", "real", "imag", "abs"])
            writer.writeheader()
            for t, z, magnitude in zip(t_values, z_values, abs_values):
                writer.writerow(
                    {
                        "t": float(t),
                        "real": float(z.real),
                        "imag": float(z.imag),
                        "abs": float(magnitude),
                    }
                )

    if progress_callback:
        progress_callback("Computing zeros for the interval...")
    zeros = [
        zero.imag
        for zero in compute_zeta_zeros(zero_count)
        if t_min <= zero.imag <= t_max
    ]

    if progress_callback:
        progress_callback("Plotting critical line scan...")
    figure = _plot_critical_line_figure(t_values, abs_values, zeros)
    figure_path = ROOT / "results" / "figures" / "zeta_critical_line_scan.png"
    if save:
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(figure_path, dpi=180)
        plt.close(figure)
    return {
        "table_path": table_path,
        "figure_path": figure_path,
        "zeros": zeros,
        "figure": figure,
        "t_values": t_values,
        "abs_values": abs_values,
    }


def _plot_strip_search_figure(
    sigma_values: np.ndarray,
    t_values: np.ndarray,
    abs_values: np.ndarray,
    best_indices: np.ndarray,
) -> Figure:
    apply_quantum_style()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    scatter = ax.scatter(
        sigma_values,
        t_values,
        c=np.log10(abs_values + 1e-16),
        cmap="viridis",
        s=12,
        alpha=0.75,
    )
    ax.scatter(
        sigma_values[best_indices],
        t_values[best_indices],
        color="red",
        s=40,
        edgecolor="white",
        linewidth=0.8,
        label="Best candidates",
    )
    fig.colorbar(scatter, ax=ax, label=r"$\,\log_{10}|\zeta(\sigma+it)|$")
    ax.set_xlabel("sigma")
    ax.set_ylabel("t")
    ax.set_title("Random strip search for small |ζ(σ+it)|")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def perform_random_strip_search(
    sigma_min: float = 0.01,
    sigma_max: float = 0.99,
    t_min: float = 10.0,
    t_max: float = 40.0,
    samples: int = 2000,
    top_k: int = 10,
    seed: int = 7,
    precision: int = 50,
    fixed_sigma: float | str | None = None,
    fixed_t: float | str | None = None,
    save: bool = True,
    progress_callback: callable | None = None,
) -> dict[str, object]:
    def _parse_fixed_value(value: float | str | None) -> float | None:
        if value is None:
            return None
        return _parse_expression_value(value, precision)

    fixed_sigma_value = _parse_fixed_value(fixed_sigma)
    fixed_t_value = _parse_fixed_value(fixed_t)

    if progress_callback:
        progress_callback("Sampling random points in the critical strip...")
    rng = np.random.default_rng(seed)
    # Support fixing sigma and/or t
    if fixed_sigma_value is not None and fixed_t_value is not None:
        sigma_values = np.array([fixed_sigma_value], dtype=float)
        t_values = np.array([fixed_t_value], dtype=float)
        samples = 1
    elif fixed_sigma_value is not None:
        sigma_values = np.full(samples, fixed_sigma_value, dtype=float)
        t_values = rng.uniform(t_min, t_max, samples)
    elif fixed_t_value is not None:
        sigma_values = rng.uniform(sigma_min, sigma_max, samples)
        t_values = np.full(samples, fixed_t_value, dtype=float)
    else:
        sigma_values = rng.uniform(sigma_min, sigma_max, samples)
        t_values = rng.uniform(t_min, t_max, samples)

    abs_values = np.empty(samples, dtype=float)
    zeta_values = np.empty(samples, dtype=complex)
    with mp.workdps(precision):
        for idx, (sigma, t) in enumerate(zip(sigma_values, t_values), start=1):
            zeta_values[idx - 1] = complex(mp.zeta(mp.mpc(float(sigma), float(t))))
            abs_values[idx - 1] = abs(zeta_values[idx - 1])
            if progress_callback and idx % max(1, samples // 20) == 0:
                progress_callback(f"Evaluated {idx}/{samples} points...")

    top_k = min(top_k, samples)
    best_indices = np.argsort(abs_values)[:top_k]
    candidates = [
        {
            "sigma": float(sigma_values[idx]),
            "t": float(t_values[idx]),
            "abs": float(abs_values[idx]),
            "real": float(zeta_values[idx].real),
            "imag": float(zeta_values[idx].imag),
        }
        for idx in best_indices
    ]

    if save:
        table_path = ROOT / "results" / "tables" / "zeta_strip_random_search.csv"
        table_path.parent.mkdir(parents=True, exist_ok=True)
        with table_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sigma", "t", "real", "imag", "abs"])
            writer.writeheader()
            for sigma, t, z, magnitude in zip(sigma_values, t_values, zeta_values, abs_values):
                writer.writerow(
                    {
                        "sigma": float(sigma),
                        "t": float(t),
                        "real": float(z.real),
                        "imag": float(z.imag),
                        "abs": float(magnitude),
                    }
                )
    else:
        table_path = None

    if progress_callback:
        progress_callback("Plotting random search results...")
    figure = _plot_strip_search_figure(sigma_values, t_values, abs_values, best_indices)
    figure_path = ROOT / "results" / "figures" / "zeta_strip_random_search.png"
    if save:
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(figure_path, dpi=180)
        plt.close(figure)

    return {
        "table_path": table_path,
        "figure_path": figure_path,
        "candidates": candidates,
        "figure": figure,
        "sigma_values": sigma_values,
        "t_values": t_values,
        "abs_values": abs_values,
    }
