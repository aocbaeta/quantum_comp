#!/usr/bin/env python3
"""Validate generated artifacts used by the BCS paper workflow."""

from __future__ import annotations

import argparse
import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Artifact:
    path: str
    kind: str
    min_bytes: int = 1


REQUIRED_ARTIFACTS = [
    Artifact("CITATION.cff", "text", 100),
    Artifact("LICENSE", "text", 1_000),
    Artifact("LICENSE-DOCS", "text", 1_000),
    Artifact("docs/bcs_publication_checklist.md", "text", 1_000),
    Artifact("docs/bcs_release_abstract.md", "text", 1_000),
    Artifact("docs/bcs_release_notes.md", "text", 1_000),
    Artifact("RELEASE_NOTES_v1.5.md", "text", 1_000),
    Artifact("papers/bcs_quantum_simulation.md", "text", 1_000),
    Artifact("papers/bcs_quantum_simulation.html", "html", 1_000),
    Artifact("papers/bcs_quantum_simulation.pdf", "pdf", 10_000),
    Artifact("notebooks/bcs_paper_reproduction.ipynb", "notebook", 1_000),
    Artifact("results/notebooks/bcs_paper_reproduction_executed.ipynb", "notebook", 10_000),
    Artifact("results/notebooks/bcs_paper_reproduction.html", "html", 10_000),
    Artifact("results/notebooks/bcs_paper_reproduction.pdf", "pdf", 10_000),
    Artifact("results/releases/bcs_quantum_simulation_v1.5.zip", "zip", 10_000),
    Artifact("results/tables/bcs_dynamics_trotter.csv", "csv", 100),
    Artifact("results/tables/bcs_commutator_norms.csv", "csv", 100),
    Artifact("results/tables/bcs_qiskit_trotter_circuit.csv", "csv", 100),
    Artifact("results/tables/bcs_paper_observables.csv", "csv", 100),
    Artifact("results/tables/bcs_pair_green_retarded.csv", "csv", 100),
    Artifact("results/tables/bcs_pair_green_spectral_density.csv", "csv", 100),
    Artifact("results/tables/bcs_gorkov_anomalous_time.csv", "csv", 100),
    Artifact("results/tables/bcs_gorkov_anomalous_spectrum.csv", "csv", 100),
    Artifact("results/tables/bcs_gorkov_nambu_time.csv", "csv", 100),
    Artifact("results/tables/bcs_gorkov_nambu_spectral_trace.csv", "csv", 100),
    Artifact("results/tables/bcs_qiskit_shots_noise.csv", "csv", 100),
    Artifact("results/tables/bcs_qiskit_energy_shots.csv", "csv", 100),
    Artifact("results/tables/bcs_qiskit_error_mitigation.csv", "csv", 100),
    Artifact("results/figures/bcs_trotter_error.png", "png", 10_000),
    Artifact("results/figures/bcs_gap_condensate_time.png", "png", 10_000),
    Artifact("results/figures/bcs_pair_occupations_time.png", "png", 10_000),
    Artifact("results/figures/bcs_pair_correlation_exact_final.png", "png", 10_000),
    Artifact("results/figures/bcs_pair_correlation_trotter_final.png", "png", 10_000),
    Artifact("results/figures/bcs_pair_green_time.png", "png", 10_000),
    Artifact("results/figures/bcs_pair_green_spectrum.png", "png", 10_000),
    Artifact("results/figures/bcs_gorkov_anomalous_time.png", "png", 10_000),
    Artifact("results/figures/bcs_gorkov_anomalous_spectrum.png", "png", 10_000),
    Artifact("results/figures/bcs_gorkov_nambu_channels.png", "png", 10_000),
    Artifact("results/figures/bcs_gorkov_nambu_spectral_trace.png", "png", 10_000),
    Artifact("results/figures/bcs_qiskit_shots_noise_total_pairs.png", "png", 10_000),
    Artifact("results/figures/bcs_qiskit_shots_noise_occupations.png", "png", 10_000),
    Artifact("results/figures/bcs_qiskit_energy_shots_values.png", "png", 10_000),
    Artifact("results/figures/bcs_qiskit_energy_shots_error.png", "png", 10_000),
    Artifact("results/figures/bcs_qiskit_error_mitigation_zne.png", "png", 10_000),
    Artifact("results/figures/bcs_qiskit_error_mitigation_errors.png", "png", 10_000),
]


def validate_csv(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        row = next(reader, None)
    if not header:
        raise ValueError("CSV has no header")
    if row is None:
        raise ValueError("CSV has no data rows")


def validate_notebook(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("nbformat") != 4:
        raise ValueError("notebook is not nbformat v4")
    if not data.get("cells"):
        raise ValueError("notebook has no cells")


def validate_magic(path: Path, expected: bytes) -> None:
    actual = path.read_bytes()[: len(expected)]
    if actual != expected:
        raise ValueError(f"unexpected file signature {actual!r}")


def validate_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    if "<html" not in text:
        raise ValueError("HTML root tag not found")


def validate_text(path: Path) -> None:
    if not path.read_text(encoding="utf-8").strip():
        raise ValueError("text file is empty")


def validate_zip(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required = {
            "CITATION.cff",
            "LICENSE",
            "LICENSE-DOCS",
            "RELEASE_NOTES_v1.5.md",
            "docs/bcs_release_abstract.md",
            "papers/bcs_quantum_simulation.pdf",
            "notebooks/bcs_paper_reproduction.ipynb",
            "results/notebooks/bcs_paper_reproduction.pdf",
        }
        missing = sorted(required - names)
        if missing:
            raise ValueError(f"missing files in zip: {', '.join(missing)}")


def validate_artifact(root: Path, artifact: Artifact) -> str | None:
    path = root / artifact.path
    try:
        if not path.exists():
            raise FileNotFoundError("missing")
        size = path.stat().st_size
        if size < artifact.min_bytes:
            raise ValueError(f"too small: {size} bytes < {artifact.min_bytes}")
        if artifact.kind == "csv":
            validate_csv(path)
        elif artifact.kind == "notebook":
            validate_notebook(path)
        elif artifact.kind == "png":
            validate_magic(path, b"\x89PNG\r\n\x1a\n")
        elif artifact.kind == "pdf":
            validate_magic(path, b"%PDF")
        elif artifact.kind == "html":
            validate_html(path)
        elif artifact.kind == "text":
            validate_text(path)
        elif artifact.kind == "zip":
            validate_zip(path)
        else:
            raise ValueError(f"unknown artifact kind: {artifact.kind}")
    except Exception as exc:  # noqa: BLE001 - report all validation failures.
        return f"{artifact.path}: {exc}"
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    failures = [
        failure
        for artifact in REQUIRED_ARTIFACTS
        if (failure := validate_artifact(root, artifact)) is not None
    ]
    if failures:
        print("BCS paper artifact validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Validated {len(REQUIRED_ARTIFACTS)} BCS paper artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
