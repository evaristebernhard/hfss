#!/usr/bin/env python3
"""Joint screen of the classic through-post and the legacy local post pair."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CASES = [
    ("r2p4_h15_pair_off", 2.4, 15.0, 0.0),
    ("r2p4_h16p25_pair_off", 2.4, 16.25, 0.0),
    ("r2p4_h16p25_pair_on", 2.4, 16.25, 0.7),
    ("r3p0_h16p25_pair_off", 3.0, 16.25, 0.0),
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
    manifest = {"program": "v5 joint through/local-post screen", "cases": []}
    for name, radius, height, local_height in CASES:
        outdir = args.output_root / name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable,
            str(args.builder),
            "--version", args.version,
            "--output", str(outdir),
            "--center-post-radius", str(radius),
            "--center-post-height", str(height),
            "--post-height", str(local_height),
            "--junction-pair-height", "0",
            "--h-throat-a", "20.4",
            "--h-throat-len", "5.5",
            "--h-throat2-len", "0",
            "--h-iris-open", "0",
            "--solve", "--non-graphical",
        ]
        manifest["cases"].append({
            "name": name,
            "through_post_radius_mm": radius,
            "through_post_height_mm": height,
            "local_pair_height_mm": local_height,
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
