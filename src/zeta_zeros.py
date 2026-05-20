from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import mpmath as mp
import numpy as np


@dataclass(frozen=True)
class ZetaZero:
    index: int
    real: float
    imag: float


def zeta_zero(index: int) -> ZetaZero:
    if index < 1:
        raise ValueError("Riemann zero index starts at 1")
    zero = mp.zetazero(index)
    return ZetaZero(index=index, real=float(mp.re(zero)), imag=float(mp.im(zero)))


def compute_zeta_zeros(count: int, start: int = 1, precision: int = 50) -> list[ZetaZero]:
    if count <= 0:
        raise ValueError("count must be positive")
    if start < 1:
        raise ValueError("start must be >= 1")
    with mp.workdps(precision):
        return [zeta_zero(index) for index in range(start, start + count)]


def save_zeros_csv(zeros: list[ZetaZero], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["index", "real", "imag"])
        writer.writeheader()
        for zero in zeros:
            writer.writerow({"index": zero.index, "real": zero.real, "imag": zero.imag})


def load_zeros_csv(path: Path) -> list[ZetaZero]:
    with path.open() as handle:
        reader = csv.DictReader(handle)
        return [
            ZetaZero(index=int(row["index"]), real=float(row["real"]), imag=float(row["imag"]))
            for row in reader
        ]


def get_or_compute_zeros(
    count: int,
    start: int,
    path: Path,
    precision: int = 50,
    refresh: bool = False,
) -> list[ZetaZero]:
    if path.exists() and not refresh:
        zeros = load_zeros_csv(path)
        if len(zeros) >= count and zeros[0].index == start:
            return zeros[:count]
    zeros = compute_zeta_zeros(count=count, start=start, precision=precision)
    save_zeros_csv(zeros, path)
    return zeros


def imaginary_parts(zeros: list[ZetaZero]) -> np.ndarray:
    return np.array([zero.imag for zero in zeros], dtype=float)


def riemann_von_mangoldt_count(t: np.ndarray | float) -> np.ndarray | float:
    arr = np.asarray(t, dtype=float)
    if np.any(arr <= 0):
        raise ValueError("t must be positive")
    values = (arr / (2 * math.pi)) * (np.log(arr / (2 * math.pi)) - 1) + 7 / 8
    if np.isscalar(t):
        return float(values)
    return values


def unfolded_positions(zeros: list[ZetaZero]) -> np.ndarray:
    return np.asarray(riemann_von_mangoldt_count(imaginary_parts(zeros)), dtype=float)


def normalized_spacings(zeros: list[ZetaZero]) -> np.ndarray:
    unfolded = unfolded_positions(zeros)
    spacings = np.diff(unfolded)
    return spacings / np.mean(spacings)


def zeta_on_critical_line(t_values: np.ndarray, precision: int = 50) -> np.ndarray:
    with mp.workdps(precision):
        values = [complex(mp.zeta(mp.mpc(0.5, float(t)))) for t in t_values]
    return np.array(values, dtype=complex)


def zeta_in_strip(
    sigma_values: np.ndarray,
    t_values: np.ndarray,
    precision: int = 50,
) -> np.ndarray:
    if len(sigma_values) != len(t_values):
        raise ValueError("sigma_values and t_values must have the same length")
    with mp.workdps(precision):
        values = [complex(mp.zeta(mp.mpc(float(sigma), float(t)))) for sigma, t in zip(sigma_values, t_values)]
    return np.array(values, dtype=complex)
