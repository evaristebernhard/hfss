#!/usr/bin/env python3
"""Analyze strict full-band modal controllability of the stepped-post Magic-T.

The analysis is performed in the parity basis

    c+ = (P1 + P2)/sqrt(2)
    c- = (P1 - P2)/sqrt(2)

so that the two relevant modal reflections are

    Gamma_+(f) = S_modal[c+, c+]
    Gamma_-(f) = S_modal[c-, c-].

For every geometry parameter p, a central-difference column is built across
the complete frequency sweep. The real and imaginary parts are stacked, so
the full-band Jacobian is

    J = d[Re Gamma_+, Im Gamma_+, Re Gamma_-, Im Gamma_-] / dp.

Both the per-mm Jacobian and a half-step-normalized Jacobian are reported.
The latter is the fairer conditioning diagnostic when the natural parameter
steps have different scales.

The script also re-analyzes the original v7 local-screen center
(2.0, 10.16, 0.9, 16.25 mm) with its three strict central differences. This
legacy result must not be confused with the final optimized v7 seed
(1.4, 6.2, 0.9, 16.25 mm).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


W = np.array(
    [
        [1 / math.sqrt(2), 1 / math.sqrt(2), 0, 0],
        [1 / math.sqrt(2), -1 / math.sqrt(2), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
    dtype=complex,
)


def parse_touchstone_ma(path: Path) -> tuple[np.ndarray, np.ndarray]:
    numbers: list[float] = []
    option = ""

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            option = line.upper()
            continue
        numbers.extend(float(token) for token in line.split())

    if "MA" not in option:
        raise ValueError(f"Only magnitude-angle Touchstone is supported: {option}")

    record_size = 1 + 2 * 16
    if len(numbers) % record_size:
        raise ValueError(f"Unexpected numeric count in {path}")

    freqs: list[float] = []
    matrices: list[np.ndarray] = []

    for start in range(0, len(numbers), record_size):
        row = numbers[start : start + record_size]
        freq = row[0]
        s = np.zeros((4, 4), dtype=complex)
        k = 1
        for r in range(4):
            for c in range(4):
                mag = row[k]
                angle = math.radians(row[k + 1])
                s[r, c] = mag * np.exp(1j * angle)
                k += 2
        freqs.append(freq)
        matrices.append(W @ s @ W.T)

    return np.asarray(freqs), np.asarray(matrices)


def load_case(path: Path) -> tuple[np.ndarray, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(path)
    return parse_touchstone_ma(path)


def check_frequency_grid(reference: np.ndarray, other: np.ndarray, label: str) -> None:
    if reference.shape != other.shape or not np.allclose(reference, other, rtol=0, atol=1e-12):
        raise ValueError(f"Frequency grid mismatch for {label}")


def central_column(
    minus: tuple[np.ndarray, np.ndarray],
    plus: tuple[np.ndarray, np.ndarray],
    half_step_mm: float,
) -> dict[str, np.ndarray]:
    f_minus, s_minus = minus
    f_plus, s_plus = plus
    check_frequency_grid(f_minus, f_plus, "central-difference pair")

    derivative = (s_plus - s_minus) / (2.0 * half_step_mm)
    return {
        "freqs": f_minus,
        "plus": derivative[:, 0, 0],
        "minus": derivative[:, 1, 1],
    }


def stack_complex_columns(
    columns: dict[str, dict[str, np.ndarray]],
    parameter_order: list[str],
    mode: str,
) -> np.ndarray:
    stacked = []
    for name in parameter_order:
        z = columns[name][mode]
        stacked.append(np.concatenate([z.real, z.imag]))
    return np.column_stack(stacked)


def stack_full_columns(
    columns: dict[str, dict[str, np.ndarray]],
    parameter_order: list[str],
) -> np.ndarray:
    stacked = []
    for name in parameter_order:
        gp = columns[name]["plus"]
        gm = columns[name]["minus"]
        stacked.append(np.concatenate([gp.real, gp.imag, gm.real, gm.imag]))
    return np.column_stack(stacked)


def svd_report(jacobian: np.ndarray) -> dict[str, object]:
    singular = np.linalg.svd(jacobian, compute_uv=False)
    if singular[-1] <= 1e-14 * max(singular[0], 1.0):
        condition = math.inf
    else:
        condition = float(singular[0] / singular[-1])

    return {
        "shape": list(jacobian.shape),
        "singular_values": singular.tolist(),
        "condition_number": condition,
        "controllability_index_1_over_kappa": (
            0.0 if not math.isfinite(condition) else 1.0 / condition
        ),
    }


def acute_angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return float("nan")
    cos_theta = float(np.dot(a, b) / denom)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    return math.degrees(math.acos(abs(cos_theta)))


def column_report(
    j_plus: np.ndarray,
    j_minus: np.ndarray,
    j_full: np.ndarray,
    parameter_order: list[str],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for i, name in enumerate(parameter_order):
        n_plus = float(np.linalg.norm(j_plus[:, i]))
        n_minus = float(np.linalg.norm(j_minus[:, i]))
        result[name] = {
            "even_plus_norm_per_mm": n_plus,
            "odd_minus_norm_per_mm": n_minus,
            "even_over_odd": math.inf if n_minus == 0 else n_plus / n_minus,
            "odd_over_even": math.inf if n_plus == 0 else n_minus / n_plus,
            "full_norm_per_mm": float(np.linalg.norm(j_full[:, i])),
        }
    return result


def angle_report(
    jacobian: np.ndarray,
    parameter_order: list[str],
) -> dict[str, float]:
    out: dict[str, float] = {}
    for i in range(len(parameter_order)):
        for j in range(i + 1, len(parameter_order)):
            key = f"{parameter_order[i]}__{parameter_order[j]}"
            out[key] = acute_angle_deg(jacobian[:, i], jacobian[:, j])
    return out


def center_modal_metrics(
    freqs: np.ndarray,
    sm: np.ndarray,
) -> dict[str, object]:
    gp = sm[:, 0, 0]
    gm = sm[:, 1, 1]
    th = sm[:, 2, 0]
    te = sm[:, 3, 1]

    forbidden = np.column_stack(
        [
            sm[:, 0, 1],
            sm[:, 0, 3],
            sm[:, 1, 2],
            sm[:, 2, 3],
        ]
    )

    def worst_rl(z: np.ndarray) -> tuple[float, float]:
        rl = -20.0 * np.log10(np.maximum(np.abs(z), 1e-15))
        k = int(np.argmin(rl))
        return float(rl[k]), float(freqs[k])

    plus_rl, plus_f = worst_rl(gp)
    minus_rl, minus_f = worst_rl(gm)

    h_db = 20.0 * np.log10(np.maximum(np.abs(th), 1e-15))
    e_db = 20.0 * np.log10(np.maximum(np.abs(te), 1e-15))
    h_k = int(np.argmin(h_db))
    e_k = int(np.argmin(e_db))

    leak_db = 20.0 * np.log10(np.maximum(np.abs(forbidden), 1e-15))
    leak_per_f = np.max(leak_db, axis=1)
    leak_k = int(np.argmax(leak_per_f))

    return {
        "plus_worst_return_loss_dB": plus_rl,
        "plus_worst_return_loss_freq_GHz": plus_f,
        "minus_worst_return_loss_dB": minus_rl,
        "minus_worst_return_loss_freq_GHz": minus_f,
        "plus_to_H_min_coupling_dB": float(h_db[h_k]),
        "plus_to_H_min_coupling_freq_GHz": float(freqs[h_k]),
        "minus_to_E_min_coupling_dB": float(e_db[e_k]),
        "minus_to_E_min_coupling_freq_GHz": float(freqs[e_k]),
        "worst_forbidden_coupling_dB": float(leak_per_f[leak_k]),
        "worst_forbidden_coupling_freq_GHz": float(freqs[leak_k]),
    }


def analyze_identification(
    pairs: dict[str, tuple[Path, Path, float]],
    center_path: Path,
) -> dict[str, object]:
    parameter_order = list(pairs)
    columns: dict[str, dict[str, np.ndarray]] = {}
    half_steps = {}

    reference_freqs = None
    for name, (minus_path, plus_path, half_step) in pairs.items():
        minus = load_case(minus_path)
        plus = load_case(plus_path)

        if reference_freqs is None:
            reference_freqs = minus[0]
        else:
            check_frequency_grid(reference_freqs, minus[0], name)
            check_frequency_grid(reference_freqs, plus[0], name)

        columns[name] = central_column(minus, plus, half_step)
        half_steps[name] = half_step

    assert reference_freqs is not None

    j_plus = stack_complex_columns(columns, parameter_order, "plus")
    j_minus = stack_complex_columns(columns, parameter_order, "minus")
    j_full = stack_full_columns(columns, parameter_order)

    scale = np.diag([half_steps[name] for name in parameter_order])
    j_plus_step = j_plus @ scale
    j_minus_step = j_minus @ scale
    j_full_step = j_full @ scale

    center_freqs, center_sm = load_case(center_path)
    check_frequency_grid(reference_freqs, center_freqs, "center")

    return {
        "parameter_order": parameter_order,
        "half_steps_mm": half_steps,
        "frequency_points": int(reference_freqs.size),
        "band_GHz": [float(reference_freqs[0]), float(reference_freqs[-1])],
        "center_metrics": center_modal_metrics(center_freqs, center_sm),
        "per_mm": {
            "full": svd_report(j_full),
            "even_plus": svd_report(j_plus),
            "odd_minus": svd_report(j_minus),
            "columns": column_report(j_plus, j_minus, j_full, parameter_order),
            "pairwise_acute_angles_deg": angle_report(j_full, parameter_order),
        },
        "step_normalized": {
            "full": svd_report(j_full_step),
            "even_plus": svd_report(j_plus_step),
            "odd_minus": svd_report(j_minus_step),
            "columns": column_report(
                j_plus_step, j_minus_step, j_full_step, parameter_order
            ),
            "pairwise_acute_angles_deg": angle_report(j_full_step, parameter_order),
        },
    }


def write_csv(report: dict[str, object], path: Path) -> None:
    new = report["final_seed_v8"]
    rows = []
    per_mm = new["per_mm"]["columns"]
    step = new["step_normalized"]["columns"]

    for name in new["parameter_order"]:
        rows.append(
            {
                "parameter": name,
                "half_step_mm": new["half_steps_mm"][name],
                "even_norm_per_mm": per_mm[name]["even_plus_norm_per_mm"],
                "odd_norm_per_mm": per_mm[name]["odd_minus_norm_per_mm"],
                "even_over_odd_per_mm": per_mm[name]["even_over_odd"],
                "odd_over_even_per_mm": per_mm[name]["odd_over_even"],
                "full_step_norm": step[name]["full_norm_per_mm"],
                "even_step_norm": step[name]["even_plus_norm_per_mm"],
                "odd_step_norm": step[name]["odd_minus_norm_per_mm"],
            }
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt_condition(x: float) -> str:
    return "inf" if not math.isfinite(x) else f"{x:.4g}"


def write_markdown(report: dict[str, object], path: Path) -> None:
    old = report["legacy_v7_center"]
    new = report["final_seed_v8"]

    lines = [
        "# Modal controllability identification",
        "",
        "## Important scope note",
        "",
        "The legacy three-parameter central-difference result is centered at "
        "(rL, hs, rU, H) = (2.0, 10.16, 0.9, 16.25) mm. "
        "It is not the final optimized v7 seed.",
        "",
        "The strict v8 result is centered at "
        "(1.4, 6.2, 0.9, 16.25) mm and includes the upper-post radius.",
        "",
        "## Conditioning",
        "",
        "| identification | full kappa | even/H kappa | odd/E kappa |",
        "|---|---:|---:|---:|",
        (
            "| legacy v7 center, per mm | "
            f"{fmt_condition(old['per_mm']['full']['condition_number'])} | "
            f"{fmt_condition(old['per_mm']['even_plus']['condition_number'])} | "
            f"{fmt_condition(old['per_mm']['odd_minus']['condition_number'])} |"
        ),
        (
            "| final v8 seed, per mm | "
            f"{fmt_condition(new['per_mm']['full']['condition_number'])} | "
            f"{fmt_condition(new['per_mm']['even_plus']['condition_number'])} | "
            f"{fmt_condition(new['per_mm']['odd_minus']['condition_number'])} |"
        ),
        (
            "| final v8 seed, step-normalized | "
            f"{fmt_condition(new['step_normalized']['full']['condition_number'])} | "
            f"{fmt_condition(new['step_normalized']['even_plus']['condition_number'])} | "
            f"{fmt_condition(new['step_normalized']['odd_minus']['condition_number'])} |"
        ),
        "",
        "## Final-seed parameter selectivity",
        "",
        "| parameter | ||dGamma+|| | ||dGamma-|| | even/odd | odd/even |",
        "|---|---:|---:|---:|---:|",
    ]

    cols = new["per_mm"]["columns"]
    for name in new["parameter_order"]:
        c = cols[name]
        lines.append(
            f"| {name} | {c['even_plus_norm_per_mm']:.5g} | "
            f"{c['odd_minus_norm_per_mm']:.5g} | "
            f"{c['even_over_odd']:.4g} | {c['odd_over_even']:.4g} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation rule",
            "",
            "The stepped-post hypothesis is supported only if opening the upper radius "
            "adds a non-redundant odd/E control direction at the final seed. "
            "A smaller odd-block condition number and a non-small smallest singular "
            "value are stronger evidence than a single-frequency return-loss improvement.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    here = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--v7-root",
        type=Path,
        default=here / "results" / "v7_stepped_post_local",
    )
    parser.add_argument(
        "--v8-root",
        type=Path,
        default=here / "results" / "v8_modal_controllability",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=here / "results" / "v8_modal_controllability" / "modal_controllability_report.json",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=here / "results" / "v8_modal_controllability" / "modal_controllability_columns.csv",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=here / "results" / "v8_modal_controllability" / "modal_controllability_report.md",
    )
    args = parser.parse_args()

    v7 = args.v7_root.resolve()
    v8 = args.v8_root.resolve()
    ts = "single_magictee_v4_full.s4p"

    legacy_pairs = {
        "lower_radius": (
            v7 / "lower1p8" / ts,
            v7 / "lower2p2" / ts,
            0.2,
        ),
        "split_height": (
            v7 / "split9p2" / ts,
            v7 / "split11p2" / ts,
            1.0,
        ),
        "total_height": (
            v7 / "total15p5" / ts,
            v7 / "total17p0" / ts,
            0.75,
        ),
    }

    final_pairs = {
        "lower_radius": (
            v8 / "lower_minus" / ts,
            v7 / "joint_l1p6_s6p2" / ts,
            0.2,
        ),
        "split_height": (
            v8 / "split_minus" / ts,
            v7 / "joint_l1p4_s7p2" / ts,
            1.0,
        ),
        "upper_radius": (
            v8 / "upper_minus" / ts,
            v8 / "upper_plus" / ts,
            0.2,
        ),
        "total_height": (
            v8 / "total_minus" / ts,
            v8 / "total_plus" / ts,
            0.75,
        ),
    }

    report = {
        "definition": {
            "modal_basis": "c+=(P1+P2)/sqrt(2), c-=(P1-P2)/sqrt(2)",
            "full_band_feature": "[Re Gamma+, Im Gamma+, Re Gamma-, Im Gamma-] over all frequencies",
            "conditioning_note": "Use step-normalized conditioning for cross-parameter comparison.",
        },
        "legacy_v7_center": analyze_identification(
            legacy_pairs,
            v7 / "center_l2p0_u0p9_s10p16_t16p25" / ts,
        ),
        "final_seed_v8": analyze_identification(
            final_pairs,
            v7 / "joint_l1p4_s6p2" / ts,
        ),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_csv(report, args.output_csv)
    write_markdown(report, args.output_md)

    print(
        "legacy full kappa:",
        report["legacy_v7_center"]["per_mm"]["full"]["condition_number"],
    )
    print(
        "legacy odd  kappa:",
        report["legacy_v7_center"]["per_mm"]["odd_minus"]["condition_number"],
    )
    print(
        "final full kappa:",
        report["final_seed_v8"]["step_normalized"]["full"]["condition_number"],
    )
    print(
        "final odd  kappa:",
        report["final_seed_v8"]["step_normalized"]["odd_minus"]["condition_number"],
    )
    print("json:", args.output_json)
    print("csv :", args.output_csv)
    print("md  :", args.output_md)


if __name__ == "__main__":
    main()
