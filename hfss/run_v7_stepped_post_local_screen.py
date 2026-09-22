#!/usr/bin/env python3
"""Local v7 screen around the promising two-radius through-post geometry."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Case:
    name: str
    lower_radius: float
    lower_height: float
    upper_radius: float
    total_height: float


CASES = [
    Case("center_l2p0_u0p9_s10p16_t16p25", 2.0, 10.16, 0.9, 16.25),
    Case("lower1p8", 1.8, 10.16, 0.9, 16.25),
    Case("lower2p2", 2.2, 10.16, 0.9, 16.25),
    Case("split9p2", 2.0, 9.2, 0.9, 16.25),
    Case("split11p2", 2.0, 11.2, 0.9, 16.25),
    Case("total15p5", 2.0, 10.16, 0.9, 15.5),
    Case("total17p0", 2.0, 10.16, 0.9, 17.0),
    Case("joint_l1p8_s9p2", 1.8, 9.2, 0.9, 16.25),
    Case("joint_l1p6_s9p2", 1.6, 9.2, 0.9, 16.25),
    Case("joint_l1p8_s8p2", 1.8, 8.2, 0.9, 16.25),
    Case("joint_l1p6_s8p2", 1.6, 8.2, 0.9, 16.25),
    Case("joint_l1p4_s8p2", 1.4, 8.2, 0.9, 16.25),
    Case("joint_l1p6_s7p2", 1.6, 7.2, 0.9, 16.25),
    Case("joint_l1p4_s7p2", 1.4, 7.2, 0.9, 16.25),
    Case("joint_l1p6_s6p2", 1.6, 6.2, 0.9, 16.25),
    Case("joint_l1p4_s6p2", 1.4, 6.2, 0.9, 16.25),
]


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, default=here / "build_single_magictee_v6_stepped_post.py")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest = {"program": "v7 local stepped-post screen", "cases": []}
    for case in CASES:
        outdir = args.output_root / case.name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable, str(args.builder),
            "--version", args.version, "--output", str(outdir),
            "--post-lower-radius", str(case.lower_radius),
            "--post-lower-height", str(case.lower_height),
            "--post-upper-radius", str(case.upper_radius),
            "--post-total-height", str(case.total_height),
            "--post-height", "0.7", "--junction-pair-height", "0",
            "--h-throat-a", "20.4", "--h-throat-len", "5.5",
            "--h-throat2-len", "0", "--h-iris-open", "0",
            "--e-step-len", "0", "--solve", "--non-graphical",
        ]
        manifest["cases"].append({**asdict(case), "output": str(target)})
        if args.skip_existing and target.exists():
            print("[skip]", case.name, flush=True)
            continue
        print("[run]", case.name, flush=True)
        subprocess.run(cmd, check=True)
        if not target.exists():
            raise RuntimeError(f"missing S4P: {target}")
    (args.output_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
