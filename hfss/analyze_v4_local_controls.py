#!/usr/bin/env python3
"""
Analyze the five-case v4 post-pair identification program.

The primary question is not scalar return loss and not merely whether the
smallest singular value increases.  It is whether the new post-height and
post-position sensitivity columns can directly control the measured weak R11
output direction strongly enough to remove the remaining weak-direction error.

R11 weak-direction residual magnitude is approximately 0.260.  With at most
two identification half-steps allowed per post coordinate, the direct first
gate is:

    |u4^T c_h| + |u4^T c_y| >= 0.130 per half-step,

because two steps then provide an upper-bound weak-direction correction of at
least 0.260.

A heuristic augmented SVD is still reported, but it is secondary because the
v4 topology is not identical to v3.4.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import numpy as np


W = np.array([
    [1/math.sqrt(2), 1/math.sqrt(2), 0, 0],
    [1/math.sqrt(2),-1/math.sqrt(2), 0, 0],
    [0,0,1,0],
    [0,0,0,1],
], dtype=complex)

HALF_STEPS = {"post_height": 0.20, "post_y": 0.50}
R11_WEAK_DIRECTION_ERROR = 0.260
MAX_IDENTIFICATION_STEPS_PER_COORDINATE = 2.0
REQUIRED_SUM_ABS_U4_PROJECTION = (
    R11_WEAK_DIRECTION_ERROR / MAX_IDENTIFICATION_STEPS_PER_COORDINATE
)


def parse_touchstone(path: Path):
    nums = []
    opt = ""
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("!",1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            opt = line.upper()
            continue
        nums.extend(float(x) for x in line.split())
    if "MA" not in opt:
        raise ValueError("Only MA Touchstone supported")
    if len(nums) % 33:
        raise ValueError("Unexpected 4-port numeric count")
    out = []
    for k in range(0, len(nums), 33):
        f = nums[k]
        S = np.zeros((4,4), dtype=complex)
        j = k + 1
        for r in range(4):
            for c in range(4):
                mag = nums[j]
                ang = math.radians(nums[j+1])
                S[r,c] = mag * np.exp(1j*ang)
                j += 2
        out.append((f, W @ S @ W.T))
    return out


def nearest(records, f):
    return min(records, key=lambda q: abs(q[0]-f))


def feature(records, f0=10.25, df=0.025):
    fm, Sm = nearest(records, f0-df)
    fz, Sz = nearest(records, f0)
    fp, Sp = nearest(records, f0+df)
    g0 = Sz[0,0]
    g1 = (Sp[0,0]-Sm[0,0])/(fp-fm)
    return np.array([g0.real,g0.imag,g1.real,g1.imag], dtype=float)


def metrics(records):
    rl = []
    th = []
    leak = []
    for f,S in records:
        rl.append((f, -20*math.log10(max(abs(S[0,0]),1e-15))))
        th.append((f, 20*math.log10(max(abs(S[2,0]),1e-15))))
        terms = [S[0,1],S[0,3],S[1,2],S[2,3]]
        leak.append((f, max(20*math.log10(max(abs(z),1e-15)) for z in terms)))
    wr = min(rl,key=lambda x:x[1])
    mt = min(th,key=lambda x:x[1])
    wl = max(leak,key=lambda x:x[1])
    return {
        "c_plus_worst_return_loss_dB": wr[1],
        "c_plus_worst_return_loss_freq_GHz": wr[0],
        "c_plus_to_H_min_coupling_dB": mt[1],
        "tH_min_linear": 10**(mt[1]/20),
        "worst_forbidden_coupling_dB": wl[1],
    }


def main():
    here = Path(__file__).resolve().parent
    repo = here.parent
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=here/"output_v4_local_id")
    p.add_argument(
        "--r11",
        type=Path,
        default=repo/"hfss"/"results"/"v3_4_jacobian_r11"/"jacobian_analysis.json",
    )
    p.add_argument("--output", type=Path)
    args = p.parse_args()

    root = args.root.resolve()
    r11 = json.loads(args.r11.resolve().read_text(encoding="utf-8"))
    oldJ = np.array(r11["step_normalized_jacobian"], dtype=float)
    U,s,Vh = np.linalg.svd(oldJ, full_matrices=True)
    weak = U[:,-1]
    weak2 = U[:,-2:]

    rec = {}
    for name in [
        "center",
        "post_height_minus",
        "post_height_plus",
        "post_y_minus",
        "post_y_plus",
    ]:
        path = root/name/"single_magictee_v4_full.s4p"
        if not path.exists():
            raise FileNotFoundError(path)
        rec[name] = parse_touchstone(path)

    feat = {k:feature(v) for k,v in rec.items()}
    cols = {}
    signed_u4 = {}
    for param in ["post_height","post_y"]:
        d = HALF_STEPS[param]
        deriv = (feat[param+"_plus"] - feat[param+"_minus"])/(2*d)
        step_col = deriv*d
        signed = float(weak @ step_col)
        signed_u4[param] = signed
        cols[param] = {
            "per_mm": deriv,
            "step_normalized": step_col,
            "weak_u4_projection_signed": signed,
            "weak_u4_projection_abs": abs(signed),
            "weak_2d_projection_norm": float(np.linalg.norm(weak2.T @ step_col)),
            "column_norm": float(np.linalg.norm(step_col)),
        }

    sum_abs_u4 = sum(abs(v) for v in signed_u4.values())
    weak_capacity_two_steps = (
        MAX_IDENTIFICATION_STEPS_PER_COORDINATE * sum_abs_u4
    )

    C = np.column_stack([
        cols["post_height"]["step_normalized"],
        cols["post_y"]["step_normalized"],
    ])
    aug = np.column_stack([oldJ, C])
    saug = np.linalg.svd(aug, compute_uv=False)

    direct_pass = sum_abs_u4 >= REQUIRED_SUM_ABS_U4_PROJECTION
    heuristic_svd_pass = (
        saug[-1] >= 5*s[-1] or saug[-1]/saug[0] >= 0.01
    )

    centerF = feat["center"]
    report = {
        "v4_center_feature": centerF.tolist(),
        "r11_singular_values": s.tolist(),
        "r11_weak_output_direction_u4": weak.tolist(),
        "r11_weak_direction_error": R11_WEAK_DIRECTION_ERROR,
        "max_identification_steps_per_coordinate": MAX_IDENTIFICATION_STEPS_PER_COORDINATE,
        "required_sum_abs_u4_projection_per_halfstep": REQUIRED_SUM_ABS_U4_PROJECTION,
        "new_post_columns": {
            k:{kk:(vv.tolist() if hasattr(vv,"tolist") else vv) for kk,vv in val.items()}
            for k,val in cols.items()
        },
        "sum_abs_u4_projection_per_halfstep": sum_abs_u4,
        "estimated_two_step_weak_direction_capacity": weak_capacity_two_steps,
        "direct_weak_direction_gate_pass": direct_pass,
        "heuristic_augmented_singular_values": saug.tolist(),
        "heuristic_sigma_min_gain_over_r11": float(saug[-1]/s[-1]),
        "heuristic_sigma_min_over_sigma_max": float(saug[-1]/saug[0]),
        "heuristic_svd_gate_pass": heuristic_svd_pass,
        "center_metrics": metrics(rec["center"]),
        "decision": (
            "PASS_DIRECTION_GATE"
            if direct_pass
            else "FAIL_DIRECTION_GATE"
        ),
        "warning": (
            "The direct u4 controllability gate is primary. The augmented SVD "
            "mixes R11 v3.4 derivatives with v4 post derivatives and is only a "
            "secondary direction-screening diagnostic. Re-identify the full "
            "v4 Jacobian after a pass."
        ),
    }

    out = args.output.resolve() if args.output else root/"local_control_analysis.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("decision:", report["decision"])
    print("post_height signed u4 projection:", signed_u4["post_height"])
    print("post_y signed u4 projection:", signed_u4["post_y"])
    print("sum abs u4 projection / half-step:", sum_abs_u4)
    print("two-step weak-direction capacity:", weak_capacity_two_steps)
    print("required weak-direction correction:", R11_WEAK_DIRECTION_ERROR)
    print("augmented singular values:", saug)
    print("report:", out)


if __name__ == "__main__":
    main()
