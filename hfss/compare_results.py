#!/usr/bin/env python3
"""Compare rebuilt HFSS S4P/S8P against the *actual historical* PEC solve.

No rerun or publication data are altered. Complex S matrices are compared over
matching frequency grids, with an optional acceptance threshold on max |ΔS|.
This is an electromagnetic **regression check**, not a high-power validation.
"""
from __future__ import annotations
import argparse
import cmath
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = {
    "cell": ROOT / "hfss/results/v7_stepped_post_local/joint_l1p4_s6p2/single_magictee_v4_full.s4p",
    "tree": ROOT / "hfss/results/v7_four_way_3d_optimized/four_way_magictee_v6_3d.s8p",
}
CANDIDATE = {
    "cell": ROOT / "hfss/output_current/cell/magictee_cell.s4p",
    "tree": ROOT / "hfss/output_current/tree/magictee_tree.s8p",
}
PORTS = {"cell":4,"tree":8}


def read_touchstone(path: Path, ports: int):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"missing simulation file: {path}")
    frequencies, matrices, fields = [], [], []
    units = "ghz"
    fmt = "ma"
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("!",1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            words = line[1:].lower().split()
            if words:
                units = words[0]
            if "s" not in words:
                raise ValueError(f"{path}: only S parameters supported")
            if "ma" in words:
                fmt="ma"
            elif "ri" in words:
                fmt="ri"
            else:
                raise ValueError(f"{path}: only S MA/RI supported")
            continue
        fields.extend(float(x) for x in line.split())
    if units not in ("ghz","mhz","hz","khz"):
        raise ValueError(f"{path}: unrecognized frequency unit {units}")
    scale = {"hz":1e-9,"khz":1e-6,"mhz":1e-3,"ghz":1.0}[units]
    length=1+2*ports*ports
    if not fields or len(fields)%length:
        raise ValueError(f"{path}: wrong number of {ports}-port Touchstone fields")
    for start in range(0,len(fields),length):
        part=fields[start:start+length]
        frequencies.append(part[0]*scale)
        values=[]
        for k in range(1,len(part),2):
            a,b=part[k],part[k+1]
            values.append(cmath.rect(a,math.radians(b)) if fmt=="ma" else complex(a,b))
        matrices.append(values)
    return frequencies, matrices


def compare(reference: Path, candidate: Path, ports: int) -> dict:
    base_freq, base=read_touchstone(reference,ports)
    new_freq, new=read_touchstone(candidate,ports)
    if len(base_freq)!=len(new_freq):
        raise ValueError(f"frequency point count differs: {len(base_freq)} vs {len(new_freq)}")
    for i,(a,b) in enumerate(zip(base_freq,new_freq)):
        if not math.isclose(a,b,abs_tol=1e-8,rel_tol=0):
            raise ValueError(f"frequency mismatch at index {i}: {a} vs {b} GHz")
    diffs=[abs(a-b) for m,n in zip(base,new) for a,b in zip(m,n)]
    return {
        "frequency_points":len(base_freq),
        "band_GHz":[base_freq[0],base_freq[-1]],
        "ports":ports,
        "max_abs_complex_S_error":max(diffs),
        "rms_complex_S_error":math.sqrt(sum(v*v for v in diffs)/len(diffs)),
        "max_abs_complex_S_error_dB_relative_to_unity":20*math.log10(max(max(diffs),1e-15)),
    }


def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode",choices=("cell","tree"),required=True)
    ap.add_argument("--reference",type=Path)
    ap.add_argument("--candidate",type=Path)
    ap.add_argument("--max-abs",type=float,help="optional max complex |ΔS| acceptance bound")
    args=ap.parse_args(argv)
    result=compare(args.reference or REFERENCE[args.mode],
                   args.candidate or CANDIDATE[args.mode],PORTS[args.mode])
    print(json.dumps(result,indent=2))
    if args.max_abs is not None:
        if args.max_abs<0:
            raise ValueError("--max-abs must be >=0")
        if result["max_abs_complex_S_error"]>args.max_abs:
            print("FAIL: rebuilt model differs from original beyond requested bound")
            return 1
        print("PASS: rebuilt model is within requested complex-S bound")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
