#!/usr/bin/env python3
"""Screen a short symmetric E-arm height step on the best H candidate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CASES = [
    ("e_b8p0_l3p0", 8.0, 3.0),
    ("e_b8p0_l5p0", 8.0, 5.0),
    ("e_b6p5_l5p0", 6.5, 5.0),
    ("e_b8p0_l7p5", 8.0, 7.5),
]


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, default=here / "build_single_magictee_v4_full.py")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest = {"program": "v5 E-arm short height-step screen", "cases": []}
    for name, width, length in CASES:
        outdir = args.output_root / name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable, str(args.builder), "--version", args.version,
            "--output", str(outdir),
            "--center-post-radius", "2.4", "--center-post-height", "16.25",
            "--post-height", "0.7",
            "--junction-pair-height", "0",
            "--h-throat-a", "20.4", "--h-throat-len", "5.5",
            "--h-throat2-len", "0", "--h-iris-open", "0",
            "--e-step-b", str(width), "--e-step-len", str(length),
            "--solve", "--non-graphical",
        ]
        manifest["cases"].append({
            "name": name, "e_step_b_mm": width, "e_step_len_mm": length,
            "through_post_radius_mm": 2.4, "through_post_height_mm": 16.25,
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
