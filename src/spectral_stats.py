from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SpacingSummary:
    count: int
    mean: float
    variance: float
    min_value: float
    max_value: float
    ks_poisson: float
    ks_gue_wigner: float


def poisson_spacing_pdf(s: np.ndarray) -> np.ndarray:
    return np.exp(-s)


def poisson_spacing_cdf(s: np.ndarray) -> np.ndarray:
    return 1 - np.exp(-s)


def gue_wigner_surmise_pdf(s: np.ndarray) -> np.ndarray:
    return (32 / math.pi**2) * s**2 * np.exp(-4 * s**2 / math.pi)


def gue_wigner_surmise_cdf(s: np.ndarray) -> np.ndarray:
    return 1 - np.exp(-4 * s**2 / math.pi) * (1 + 4 * s**2 / math.pi)


def empirical_cdf(samples: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    xs = np.sort(np.asarray(samples, dtype=float))
    ys = np.arange(1, len(xs) + 1, dtype=float) / len(xs)
    return xs, ys


def kolmogorov_smirnov_distance(samples: np.ndarray, cdf) -> float:
    xs, empirical = empirical_cdf(samples)
    expected = cdf(xs)
    return float(np.max(np.abs(empirical - expected)))


def spacing_summary(spacings: np.ndarray) -> SpacingSummary:
    samples = np.asarray(spacings, dtype=float)
    if samples.ndim != 1 or len(samples) == 0:
        raise ValueError("spacings must be a non-empty 1D array")
    return SpacingSummary(
        count=len(samples),
        mean=float(np.mean(samples)),
        variance=float(np.var(samples)),
        min_value=float(np.min(samples)),
        max_value=float(np.max(samples)),
        ks_poisson=kolmogorov_smirnov_distance(samples, poisson_spacing_cdf),
        ks_gue_wigner=kolmogorov_smirnov_distance(samples, gue_wigner_surmise_cdf),
    )


def random_gue_eigenvalues(size: int, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    real = rng.normal(size=(size, size))
    imag = rng.normal(size=(size, size))
    matrix = (real + 1j * imag) / math.sqrt(2 * size)
    hermitian = (matrix + matrix.conj().T) / 2
    return np.linalg.eigvalsh(hermitian)


def locally_unfolded_spacings(values: np.ndarray, trim_fraction: float = 0.2) -> np.ndarray:
    xs = np.sort(np.asarray(values, dtype=float))
    if len(xs) < 4:
        raise ValueError("need at least 4 eigenvalues")
    lo = int(len(xs) * trim_fraction)
    hi = int(len(xs) * (1 - trim_fraction))
    bulk = xs[lo:hi]
    spacings = np.diff(bulk)
    return spacings / np.mean(spacings)
