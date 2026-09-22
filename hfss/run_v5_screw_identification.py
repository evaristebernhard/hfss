#!/usr/bin/env python3
"""Identify three H-arm screw controls around the 9 mm throat candidate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CASES = {
    "screw1_1mm": (1.0, 0.0, 0.0),
    "screw2_1mm": (0.0, 1.0, 0.0),
    "screw3_1mm": (0.0, 0.0, 1.0),
}


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, default=here / "build_single_magictee_v4_full.py")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest = {"program": "v5 three-screw identification", "baseline": "throat9p0", "cases": []}

    for name, penetrations in CASES.items():
        outdir = args.output_root / name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable, str(args.builder),
            "--version", args.version,
            "--output", str(outdir),
            "--h-throat-a", "20.4",
            "--h-throat-len", "9.0",
            "--h-throat2-len", "0",
            "--h-iris-open", "0",
            "--screw-z1", "0",
            "--screw-z2", "5.0",
            "--screw-z3", "19.5",
            "--screw-p1", str(penetrations[0]),
            "--screw-p2", str(penetrations[1]),
            "--screw-p3", str(penetrations[2]),
            "--solve", "--non-graphical",
        ]
        manifest["cases"].append({"name": name, "penetrations_mm": penetrations, "output": str(target)})
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
