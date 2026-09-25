#!/usr/bin/env python3
"""
Analyze the v3.4 9-case central-difference program.

The H/even block uses the parity basis:
    c+ = (P1 + P2)/sqrt(2)
    c- = (P1 - P2)/sqrt(2)
    H  = P3
    E  = P4

Feature vector:
    F = [Re(Gamma0), Im(Gamma0), Re(Gamma1), Im(Gamma1)]^T

where Gamma0 is c+ reflection at f0=10.25 GHz and Gamma1 is the centered
frequency derivative. The script forms the 4x4 parameter Jacobian, reports
raw and step-normalized SVDs, and computes a local Newton suggestion without
automatically changing geometry.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


CENTER = {
    "h_throat_a": 20.4,
    "h_throat_len": 5.5,
    "h_cap_height": 9.0,
    "h_terminal_ridge_w": 4.572,
}

DELTAS = {
    "h_throat_a": 0.4,
    "h_throat_len": 1.0,
    "h_cap_height": 0.4,
    "h_terminal_ridge_w": 0.5,
}

PARAMS = list(CENTER)

W = np.array(
    [
        [1 / math.sqrt(2), 1 / math.sqrt(2), 0, 0],
        [1 / math.sqrt(2), -1 / math.sqrt(2), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
    dtype=complex,
)


def parse_touchstone_ma(path: Path):
    numbers = []
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

    records = []
    for start in range(0, len(numbers), record_size):
        row = numbers[start : start + record_size]
        freq = row[0]
        s = np.zeros((4, 4), dtype=complex)
        k = 1
        for r in range(4):
            for c in range(4):
                mag = row[k]
                ang = math.radians(row[k + 1])
                s[r, c] = mag * np.exp(1j * ang)
                k += 2
        records.append((freq, W @ s @ W.T))
    return records


def nearest(records, target):
    return min(records, key=lambda item: abs(item[0] - target))


def db20(z):
    return 20 * np.log10(np.maximum(np.abs(z), 1e-15))


def feature(records, f0, df):
    fm, sm = nearest(records, f0 - df)
    fz, sz = nearest(records, f0)
    fp, sp = nearest(records, f0 + df)

    if abs(fz - f0) > 1e-6:
        raise ValueError(f"Center frequency {f0} GHz not found; nearest is {fz}")
    if abs((fp - fm) - 2 * df) > 1e-6:
        raise ValueError(
            f"Expected derivative points at {f0-df}/{f0+df} GHz, got {fm}/{fp}"
        )

    gamma0 = sz[0, 0]
    gamma1 = (sp[0, 0] - sm[0, 0]) / (fp - fm)
    return np.array(
        [gamma0.real, gamma0.imag, gamma1.real, gamma1.imag],
        dtype=float,
    )


def case_metrics(records):
    cp_rl = []
    cm_rl = []
    th = []
    te = []
    leaks = []

    for freq, sm in records:
        cp_rl.append((freq, -float(db20(sm[0, 0]))))
        cm_rl.append((freq, -float(db20(sm[1, 1]))))
        th.append((freq, float(db20(sm[2, 0]))))
        te.append((freq, float(db20(sm[3, 1]))))
        forbidden = np.array(
            [sm[0, 1], sm[0, 3], sm[1, 2], sm[2, 3]],
            dtype=complex,
        )
        leaks.append((freq, float(np.max(db20(forbidden)))))

    worst_cp = min(cp_rl, key=lambda x: x[1])
    worst_cm = min(cm_rl, key=lambda x: x[1])
    min_th = min(th, key=lambda x: x[1])
    min_te = min(te, key=lambda x: x[1])
    worst_leak = max(leaks, key=lambda x: x[1])

    return {
        "c_plus_worst_return_loss_dB": worst_cp[1],
        "c_plus_worst_return_loss_freq_GHz": worst_cp[0],
        "c_minus_worst_return_loss_dB": worst_cm[1],
        "c_minus_worst_return_loss_freq_GHz": worst_cm[0],
        "c_plus_to_H_min_coupling_dB": min_th[1],
        "c_plus_to_H_min_coupling_freq_GHz": min_th[0],
        "c_minus_to_E_min_coupling_dB": min_te[1],
        "c_minus_to_E_min_coupling_freq_GHz": min_te[0],
        "worst_forbidden_coupling_dB": worst_leak[1],
        "worst_forbidden_coupling_freq_GHz": worst_leak[0],
        "tH_min_linear": 10 ** (min_th[1] / 20.0),
    }


def svd_summary(matrix):
    s = np.linalg.svd(matrix, compute_uv=False)
    ratio = float(s[-1] / s[0]) if s[0] > 0 else 0.0
    return {
        "singular_values": [float(x) for x in s],
        "sigma_min_over_sigma_max": ratio,
        "condition_number": float(s[0] / s[-1]) if s[-1] > 0 else math.inf,
        "numerical_rank": int(np.linalg.matrix_rank(matrix)),
        "effective_rank_5pct": int(np.sum(s >= 0.05 * s[0])) if s[0] else 0,
        "effective_rank_1pct": int(np.sum(s >= 0.01 * s[0])) if s[0] else 0,
    }


def find_case_s4p(root: Path, name: str) -> Path:
    return root / name / "single_magictee_v3_4_hreactive.s4p"


def parse_args():
    here = Path(__file__).resolve().parent
    repo_root = here.parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=here / "output_v3_4_jacobian",
        help="Directory containing case subdirectories.",
    )
    parser.add_argument(
        "--center-s4p",
        type=Path,
        default=(
            repo_root
            / "hfss"
            / "results"
            / "v3_4_H_reactive_cell_latest"
            / "single_magictee_v3_4_hreactive.s4p"
        ),
        help="Fallback committed center result if root/center is absent.",
    )
    parser.add_argument("--f0", type=float, default=10.25)
    parser.add_argument("--df", type=float, default=0.025)
    parser.add_argument(
        "--trust-fraction",
        type=float,
        default=0.75,
        help="Clip each normalized Newton coordinate to +/- this value.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON output path; default is ROOT/jacobian_analysis.json.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = args.root.resolve()
    center_fallback = args.center_s4p.resolve()
    output = (
        args.output.resolve()
        if args.output is not None
        else root / "jacobian_analysis.json"
    )

    records = {}
    paths = {}

    center_path = find_case_s4p(root, "center")
    if not center_path.exists():
        center_path = center_fallback
    if not center_path.exists():
        raise FileNotFoundError(
            "No center S4P found in the run root and fallback center is missing"
        )

    paths["center"] = center_path
    records["center"] = parse_touchstone_ma(center_path)

    for param in PARAMS:
        for sign in ("minus", "plus"):
            name = f"{param}_{sign}"
            path = find_case_s4p(root, name)
            if not path.exists():
                raise FileNotFoundError(f"Missing Jacobian case: {path}")
            paths[name] = path
            records[name] = parse_touchstone_ma(path)

    features = {
        name: feature(rec, args.f0, args.df)
        for name, rec in records.items()
    }

    jac = np.zeros((4, 4), dtype=float)
    for col, param in enumerate(PARAMS):
        fp = features[f"{param}_plus"]
        fm = features[f"{param}_minus"]
        jac[:, col] = (fp - fm) / (2.0 * DELTAS[param])

    delta_vec = np.array([DELTAS[p] for p in PARAMS], dtype=float)
    jac_step = jac @ np.diag(delta_vec)

    f_center = features["center"]
    q_newton = -np.linalg.pinv(jac_step) @ f_center
    q_trust = np.clip(q_newton, -args.trust_fraction, args.trust_fraction)
    dp_trust = q_trust * delta_vec
    p_trust = np.array([CENTER[p] for p in PARAMS]) + dp_trust

    metrics = {
        name: case_metrics(rec)
        for name, rec in records.items()
    }

    report = {
        "feature_definition": [
            "Re(Gamma_H_even(f0))",
            "Im(Gamma_H_even(f0))",
            "Re(dGamma_H_even/df at f0)",
            "Im(dGamma_H_even/df at f0)",
        ],
        "f0_GHz": args.f0,
        "df_GHz": args.df,
        "parameters": PARAMS,
        "center_parameters_mm": CENTER,
        "central_difference_half_steps_mm": DELTAS,
        "center_feature": [float(x) for x in f_center],
        "jacobian_per_mm": jac.tolist(),
        "step_normalized_jacobian": jac_step.tolist(),
        "raw_svd": svd_summary(jac),
        "step_normalized_svd": svd_summary(jac_step),
        "newton_step_in_halfstep_units": [float(x) for x in q_newton],
        "trust_limited_step_in_halfstep_units": [float(x) for x in q_trust],
        "trust_limited_parameter_delta_mm": {
            p: float(dp_trust[i]) for i, p in enumerate(PARAMS)
        },
        "trust_limited_candidate_mm": {
            p: float(p_trust[i]) for i, p in enumerate(PARAMS)
        },
        "case_metrics": metrics,
        "case_paths": {name: str(path) for name, path in paths.items()},
        "structural_gates": {
            "tH_min_required": 0.85,
            "tH_min_preferred": 0.90,
            "forbidden_coupling_max_dB": -30.0,
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    svd = report["step_normalized_svd"]
    print("Step-normalized singular values:", svd["singular_values"])
    print("sigma_min/sigma_max:", svd["sigma_min_over_sigma_max"])
    print("condition number:", svd["condition_number"])
    print("numerical rank:", svd["numerical_rank"])
    print("effective rank @5%:", svd["effective_rank_5pct"])
    print("effective rank @1%:", svd["effective_rank_1pct"])
    print("center feature:", report["center_feature"])
    print("trust-limited candidate [mm]:")
    for param in PARAMS:
        print(f"  {param}: {report['trust_limited_candidate_mm'][param]:.6g}")
    print("Report:", output)


if __name__ == "__main__":
    main()
