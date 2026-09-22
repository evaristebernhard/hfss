#!/usr/bin/env python3
"""Minimal E/difference-mode screen using a localized E-arm window."""

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
    opening: float
    thickness: float
    offset: float


CASES = [
    Case("no_window", 0.0, 1.5, 7.0),
    Case("win20p0_o7p0", 20.0, 1.5, 7.0),
    Case("win18p0_o7p0", 18.0, 1.5, 7.0),
    Case("win20p0_o10p0", 20.0, 1.5, 10.0),
]


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, default=here / "build_single_magictee_v6_window.py")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--case", action="append")
    args = parser.parse_args()

    selected = set(args.case or (case.name for case in CASES))
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "program": "v6 localized E-window screen",
        "fixed": {
            "through_post_radius_mm": 2.4,
            "through_post_height_mm": 16.25,
            "local_post_pair_height_mm": 0.7,
            "H_throat_a_mm": 20.4,
            "H_throat_length_mm": 5.5,
        },
        "cases": [],
    }
    for case in CASES:
        if case.name not in selected:
            continue
        outdir = args.output_root / case.name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable, str(args.builder),
            "--version", args.version,
            "--output", str(outdir),
            "--center-post-radius", "2.4",
            "--center-post-height", "16.25",
            "--post-height", "0.7",
            "--junction-pair-height", "0",
            "--h-throat-a", "20.4",
            "--h-throat-len", "5.5",
            "--h-throat2-len", "0",
            "--h-iris-open", "0",
            "--e-step-len", "0",
            "--e-window1-open", str(case.opening),
            "--e-window1-thickness", str(case.thickness),
            "--e-window1-offset", str(case.offset),
            "--e-window2-open", "0",
            "--solve", "--non-graphical",
        ]
        manifest["cases"].append({**asdict(case), "output": str(target)})
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
