#!/usr/bin/env python3
"""Screen a classic Magic-T matching post extending toward/into the E arm."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Case:
    name: str
    radius: float
    height: float


CASES = [
    Case("through_r2p4_h8p0", 2.4, 8.0),
    Case("through_r2p4_h10p2", 2.4, 10.2),
    Case("through_r2p4_h12p5", 2.4, 12.5),
    Case("through_r2p4_h15p0", 2.4, 15.0),
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
    manifest = {"program": "v5 through-junction matching-post screen", "cases": []}

    for case in CASES:
        outdir = args.output_root / case.name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable,
            str(args.builder),
            "--version",
            args.version,
            "--output",
            str(outdir),
            "--h-throat-a",
            "20.4",
            "--h-throat-len",
            "5.5",
            "--h-throat2-len",
            "0",
            "--h-iris-open",
            "0",
            "--junction-pair-height",
            "0",
            "--center-post-radius",
            str(case.radius),
            "--center-post-height",
            str(case.height),
            "--solve",
            "--non-graphical",
        ]
        manifest["cases"].append(
            {
                "name": case.name,
                "radius_mm": case.radius,
                "height_from_bottom_mm": case.height,
                "tip_z_mm": -5.08 + case.height,
                "output": str(target),
            }
        )
        if args.skip_existing and target.exists():
            print("[skip]", case.name, flush=True)
            continue
        print("[run]", case.name, flush=True)
        subprocess.run(cmd, check=True)
        if not target.exists():
            raise RuntimeError(f"missing S4P: {target}")
    (args.output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
