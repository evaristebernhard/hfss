#!/usr/bin/env python3
"""Modal-area and spectral-basis analysis for the stepped-post Magic-T.

This script complements the full-band Jacobian/SVD analysis with two reader-facing
quantities:

1. A two-control Gram area for the lower/upper post radii,

       A_LU = sqrt(det(J_LU^T J_LU))
            = ||j_L|| ||j_U|| sin(theta_LU),

   which is zero for a uniform post because the constraint dr_L = dr_U reduces
   the reachable set to one dimension.

2. A discrete Legendre decomposition of each complex modal sensitivity
   dGamma_+/dp and dGamma_-/dp over the full 9--11.5 GHz band.  The energy
   fractions in orders k=0,1,2,... distinguish offset, slope, curvature, and
   higher-order spectral control.

Outputs are written under hfss/results/v8_modal_controllability/.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from analyze_v8_modal_controllability import central_column, load_case


PARAMETER_ORDER = [
    "lower_radius",
    "split_height",
    "upper_radius",
    "total_height",
]

HALF_STEPS_MM = {
    "lower_radius": 0.2,
    "split_height": 1.0,
    "upper_radius": 0.2,
    "total_height": 0.75,
}


def final_pairs(here: Path):
    v7 = here / "results" / "v7_stepped_post_local"
    v8 = here / "results" / "v8_modal_controllability"
    ts = "single_magictee_v4_full.s4p"
    return {
        "lower_radius": (
            v8 / "lower_minus" / ts,
            v7 / "joint_l1p6_s6p2" / ts,
        ),
        "split_height": (
            v8 / "split_minus" / ts,
            v7 / "joint_l1p4_s7p2" / ts,
        ),
        "upper_radius": (
            v8 / "upper_minus" / ts,
            v8 / "upper_plus" / ts,
        ),
        "total_height": (
            v8 / "total_minus" / ts,
            v8 / "total_plus" / ts,
        ),
    }


def identify_columns(here: Path):
    pairs = final_pairs(here)
    columns = {}
    for name in PARAMETER_ORDER:
        minus = load_case(pairs[name][0])
        plus = load_case(pairs[name][1])
        columns[name] = central_column(
            minus,
            plus,
            HALF_STEPS_MM[name],
        )
    return columns


def real_full_column(column: dict[str, np.ndarray]) -> np.ndarray:
    gp = column["plus"]
    gm = column["minus"]
    return np.concatenate([gp.real, gp.imag, gm.real, gm.imag])


def acute_angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    c = abs(float(np.dot(a, b) / denom))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def gram_area(a: np.ndarray, b: np.ndarray) -> float:
    gram = np.array(
        [
            [float(np.dot(a, a)), float(np.dot(a, b))],
            [float(np.dot(b, a)), float(np.dot(b, b))],
        ]
    )
    return math.sqrt(max(0.0, float(np.linalg.det(gram))))


def orthonormal_legendre_basis(n_points: int, max_order: int) -> np.ndarray:
    x = np.linspace(-1.0, 1.0, n_points)
    raw = np.column_stack(
        [
            np.polynomial.legendre.legval(
                x,
                [0.0] * order + [1.0],
            )
            for order in range(max_order + 1)
        ]
    )
    q, _ = np.linalg.qr(raw)
    return q


def spectral_energy_fractions(
    z: np.ndarray,
    basis: np.ndarray,
) -> tuple[list[float], float]:
    total = float(np.vdot(z, z).real)
    coeff = basis.T @ z
    fractions = (np.abs(coeff) ** 2 / total).real
    residual = max(0.0, 1.0 - float(np.sum(fractions)))
    return fractions.tolist(), residual


def analyze(max_order: int = 6) -> dict[str, object]:
    here = Path(__file__).resolve().parent
    columns = identify_columns(here)

    lower = real_full_column(columns["lower_radius"])
    upper = real_full_column(columns["upper_radius"])
    theta = acute_angle_deg(lower, upper)
    area = gram_area(lower, upper)

    lower_step = lower * HALF_STEPS_MM["lower_radius"]
    upper_step = upper * HALF_STEPS_MM["upper_radius"]
    area_step = gram_area(lower_step, upper_step)

    n_freq = len(columns["lower_radius"]["freqs"])
    basis = orthonormal_legendre_basis(n_freq, max_order)

    spectral = {}
    for name in PARAMETER_ORDER:
        spectral[name] = {}
        for key, label in [("plus", "even_plus"), ("minus", "odd_minus")]:
            fractions, residual = spectral_energy_fractions(
                columns[name][key],
                basis,
            )
            spectral[name][label] = {
                "legendre_energy_fraction": fractions,
                "residual_above_max_order": residual,
                "dominant_order": int(np.argmax(fractions)),
            }

    return {
        "definition": {
            "frequency_basis": "Discrete QR-orthonormalized Legendre basis on 101 uniformly sampled frequencies from 9 to 11.5 GHz.",
            "order_interpretation": {
                "0": "frequency-independent offset component",
                "1": "first-order slope-like component",
                "2": "curvature-like component",
                "3+": "higher-order spectral shaping",
            },
        },
        "lower_upper_controllability_area": {
            "acute_angle_deg": theta,
            "lower_full_norm_per_mm": float(np.linalg.norm(lower)),
            "upper_full_norm_per_mm": float(np.linalg.norm(upper)),
            "gram_area_per_mm2": area,
            "gram_determinant_per_mm4": area * area,
            "step_normalized_area": area_step,
            "step_normalized_gram_determinant": area_step * area_step,
            "uniform_post_two_dimensional_area": 0.0,
            "interpretation": (
                "A uniform post constrains dr_L=dr_U and therefore has zero "
                "two-dimensional reachable area in the (j_L,j_U) plane. "
                "The stepped post releases this constraint."
            ),
        },
        "spectral_decomposition": spectral,
    }


def write_outputs(report: dict[str, object], out_root: Path) -> None:
    out_json = out_root / "modal_spectral_decomposition.json"
    out_csv = out_root / "modal_spectral_decomposition.csv"
    out_md = out_root / "modal_spectral_decomposition.md"

    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    rows = []
    spectral = report["spectral_decomposition"]
    for parameter in PARAMETER_ORDER:
        for mode in ("even_plus", "odd_minus"):
            item = spectral[parameter][mode]
            row = {
                "parameter": parameter,
                "mode": mode,
                "dominant_order": item["dominant_order"],
                "residual_above_max_order": item["residual_above_max_order"],
            }
            for order, value in enumerate(item["legendre_energy_fraction"]):
                row[f"order_{order}_energy_fraction"] = value
            rows.append(row)

    with out_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    area = report["lower_upper_controllability_area"]
    lines = [
        "# Modal area and spectral decomposition",
        "",
        "## Stepped-post two-control area",
        "",
        f"- lower/upper response angle: {area['acute_angle_deg']:.3f} deg",
        f"- per-mm Gram area: {area['gram_area_per_mm2']:.6g}",
        f"- per-mm Gram determinant: {area['gram_determinant_per_mm4']:.6g}",
        f"- step-normalized area: {area['step_normalized_area']:.6g}",
        "- uniform-post two-dimensional area: 0",
        "",
        "The nonzero stepped-post area is the quantitative form of the rank expansion "
        "from one constrained uniform-post direction to two independent local controls.",
        "",
        "## Discrete Legendre spectral energy",
        "",
        "| parameter | mode | k0 | k1 | k2 | k3 | dominant |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for parameter in PARAMETER_ORDER:
        for mode in ("even_plus", "odd_minus"):
            item = spectral[parameter][mode]
            f = item["legendre_energy_fraction"]
            lines.append(
                f"| {parameter} | {mode} | {f[0]:.3f} | {f[1]:.3f} | "
                f"{f[2]:.3f} | {f[3]:.3f} | {item['dominant_order']} |"
            )
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    here = Path(__file__).resolve().parent
    out_root = here / "results" / "v8_modal_controllability"
    out_root.mkdir(parents=True, exist_ok=True)
    report = analyze(max_order=6)
    write_outputs(report, out_root)

    area = report["lower_upper_controllability_area"]
    print("lower-upper angle [deg]:", area["acute_angle_deg"])
    print("Gram area per mm^2:", area["gram_area_per_mm2"])
    print("step-normalized Gram area:", area["step_normalized_area"])
    print("outputs:", out_root)


if __name__ == "__main__":
    main()
