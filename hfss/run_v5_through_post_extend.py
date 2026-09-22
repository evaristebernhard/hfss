#!/usr/bin/env python3
"""Extend the through-post height sweep after the first monotonic screen."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CASES = [
    ("through_r2p4_h17p5", 17.5),
    ("through_r2p4_h20p0", 20.0),
    ("through_r2p4_h22p5", 22.5),
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
    manifest = {"program": "v5 through-post extended-height screen", "cases": []}
    for name, height in CASES:
        outdir = args.output_root / name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable,
            str(args.builder),
            "--version", args.version,
            "--output", str(outdir),
            "--center-post-radius", "2.4",
            "--center-post-height", str(height),
            "--junction-pair-height", "0",
            "--h-throat-a", "20.4",
            "--h-throat-len", "5.5",
            "--h-throat2-len", "0",
            "--h-iris-open", "0",
            "--solve", "--non-graphical",
        ]
        manifest["cases"].append({
            "name": name,
            "radius_mm": 2.4,
            "height_from_bottom_mm": height,
            "tip_z_mm": -5.08 + height,
            "output": str(target),
        })
        if args.skip_existing and target.exists():
            print("[skip]", name, flush=True)
            continue
        print("[run]", name, flush=True)
        subprocess.run(cmd, check=True)
        if not target.exists():
            raise RuntimeError(f"missing S4P: {target}")
    (args.output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
