#!/usr/bin/env python3
"""
Analyze the five-case v4 post-pair identification program.

The primary question is not scalar return loss.  It is whether the new
post-height and post-position sensitivity columns project strongly onto the
weak output directions of the measured R11 Jacobian.

A heuristic augmented SVD is also reported by appending the two new post
columns to the R11 step-normalized Jacobian.  Because the v4 topology is not
identical to v3.4, this augmented SVD is a direction-screening diagnostic,
not a final Newton model.
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
    p.add_argument("--r11", type=Path, default=repo/"hfss"/"results"/"v3_4_jacobian_r11"/"jacobian_analysis.json")
    p.add_argument("--output", type=Path)
    args = p.parse_args()

    root = args.root.resolve()
    r11 = json.loads(args.r11.resolve().read_text(encoding="utf-8"))
    oldJ = np.array(r11["step_normalized_jacobian"], dtype=float)
    U,s,Vh = np.linalg.svd(oldJ, full_matrices=True)
    weak = U[:,-1]
    weak2 = U[:,-2:]

    rec = {}
    for name in ["center","post_height_minus","post_height_plus","post_y_minus","post_y_plus"]:
        path = root/name/"single_magictee_v4_full.s4p"
        if not path.exists():
            raise FileNotFoundError(path)
        rec[name] = parse_touchstone(path)

    feat = {k:feature(v) for k,v in rec.items()}
    cols = {}
    for param in ["post_height","post_y"]:
        d = HALF_STEPS[param]
        deriv = (feat[param+"_plus"] - feat[param+"_minus"])/(2*d)
        step_col = deriv*d
        cols[param] = {
            "per_mm": deriv,
            "step_normalized": step_col,
            "weak_u4_projection": float(abs(weak @ step_col)),
            "weak_2d_projection_norm": float(np.linalg.norm(weak2.T @ step_col)),
            "column_norm": float(np.linalg.norm(step_col)),
        }

    C = np.column_stack([
        cols["post_height"]["step_normalized"],
        cols["post_y"]["step_normalized"],
    ])
    aug = np.column_stack([oldJ, C])
    saug = np.linalg.svd(aug, compute_uv=False)

    centerF = feat["center"]
    report = {
        "v4_center_feature": centerF.tolist(),
        "r11_singular_values": s.tolist(),
        "r11_weak_output_direction_u4": weak.tolist(),
        "new_post_columns": {
            k:{kk:(vv.tolist() if hasattr(vv,"tolist") else vv) for kk,vv in val.items()}
            for k,val in cols.items()
        },
        "heuristic_augmented_singular_values": saug.tolist(),
        "heuristic_sigma_min_gain_over_r11": float(saug[-1]/s[-1]),
        "heuristic_sigma_min_over_sigma_max": float(saug[-1]/saug[0]),
        "center_metrics": metrics(rec["center"]),
        "decision": (
            "PASS_DIRECTION_GATE"
            if saug[-1] >= 5*s[-1] or saug[-1]/saug[0] >= 0.01
            else "FAIL_DIRECTION_GATE"
        ),
        "warning": "Augmented SVD mixes R11 v3.4 derivatives with v4 post derivatives; use only to screen the new physical direction. Re-identify the full v4 Jacobian after a pass."
    }

    out = args.output.resolve() if args.output else root/"local_control_analysis.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("decision:", report["decision"])
    print("post_height weak projection:", cols["post_height"]["weak_u4_projection"])
    print("post_y weak projection:", cols["post_y"]["weak_u4_projection"])
    print("augmented singular values:", saug)
    print("sigma_min gain:", report["heuristic_sigma_min_gain_over_r11"])
    print("report:", out)


if __name__ == "__main__":
    main()
