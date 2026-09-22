#!/usr/bin/env python3
"""Run a minimal screen of a dedicated symmetric H-arm iris."""

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
    throat_len: float
    iris_open: float
    iris_thickness: float = 3.0
    iris_offset: float = 8.5
    throat_a: float = 20.4


CASES = [
    Case("long_no_iris", 12.0, 0.0),
    Case("throat7p5", 7.5, 0.0),
    Case("throat9p0", 9.0, 0.0),
    Case("throat10p5", 10.5, 0.0),
    Case("width22p0_l7p5", 7.5, 0.0, throat_a=22.0),
    Case("width22p0_l9p0", 9.0, 0.0, throat_a=22.0),
    Case("width22p86_l9p0", 9.0, 0.0, throat_a=22.86),
    Case("iris20p0", 12.0, 20.0),
    Case("iris18p8", 12.0, 18.8),
]


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, default=here / "build_single_magictee_v4_full.py")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--case", action="append")
    args = parser.parse_args()

    selected = set(args.case or [case.name for case in CASES])
    manifest = {"program": "v5 dedicated H-iris screen", "cases": []}
    args.output_root.mkdir(parents=True, exist_ok=True)

    for case in CASES:
        if case.name not in selected:
            continue
        outdir = args.output_root / case.name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable,
            str(args.builder),
            "--version", args.version,
            "--output", str(outdir),
            "--h-throat-len", str(case.throat_len),
            "--h-throat-a", str(case.throat_a),
            "--h-iris-open", str(case.iris_open),
            "--h-iris-thickness", str(case.iris_thickness),
            "--h-iris-offset", str(case.iris_offset),
            "--solve",
            "--non-graphical",
        ]
        manifest["cases"].append({"name": case.name, "command": cmd, "output": str(target)})
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
