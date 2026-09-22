#!/usr/bin/env python3
"""Screen the E-arm extension radius of a stepped junction post."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CASES = [
    ("uniform_r2p4", 2.4, 2.4),
    ("upper_r1p5", 2.4, 1.5),
    ("upper_r3p2", 2.4, 3.2),
    ("lower_r2p4_upper_r0p8", 2.4, 0.8),
    ("lower_r2p0_upper_r1p0", 2.0, 1.0),
    ("lower_r2p0_upper_r0p8", 2.0, 0.8),
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
    manifest = {
        "program": "v6 stepped through-post screen",
        "fixed": {"lower_height_mm": 10.16, "total_height_mm": 16.25},
        "cases": [],
    }
    for name, lower_radius, upper_radius in CASES:
        outdir = args.output_root / name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable, str(args.builder),
            "--version", args.version, "--output", str(outdir),
            "--post-lower-radius", str(lower_radius),
            "--post-lower-height", "10.16",
            "--post-upper-radius", str(upper_radius),
            "--post-total-height", "16.25",
            "--post-height", "0.7",
            "--junction-pair-height", "0",
            "--h-throat-a", "20.4", "--h-throat-len", "5.5",
            "--h-throat2-len", "0", "--h-iris-open", "0",
            "--e-step-len", "0", "--solve", "--non-graphical",
        ]
        manifest["cases"].append({
            "name": name,
            "lower_radius_mm": lower_radius,
            "upper_radius_mm": upper_radius,
            "output": str(target),
        })
        if args.skip_existing and target.exists():
            print("[skip]", name, flush=True)
            continue
        print("[run]", name, flush=True)
        subprocess.run(cmd, check=True)
        if not target.exists():
            raise RuntimeError(f"missing S4P: {target}")
    (args.output_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
