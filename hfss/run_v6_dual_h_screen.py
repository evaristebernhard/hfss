#!/usr/bin/env python3
"""Minimal v6 screen: combine the best through-post with a separated H iris.

The v5 through-post supplies the first strong junction reactance.  The thin
sidewall iris is placed in an extended ordinary-guide throat so it supplies a
second, spatially independent reactance before the ridge transformer.
"""

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
    throat_a: float
    throat_len: float
    iris_open: float
    iris_thickness: float
    iris_offset: float


CASES = [
    Case("post_only_long", 22.86, 12.0, 0.0, 1.5, 5.0),
    Case("iris21p0_o5p0", 22.86, 12.0, 21.0, 1.5, 5.0),
    Case("iris20p0_o5p0", 22.86, 12.0, 20.0, 1.5, 5.0),
    Case("iris21p0_o8p0", 22.86, 12.0, 21.0, 1.5, 8.0),
    Case("iris20p0_o8p0", 22.86, 12.0, 20.0, 1.5, 8.0),
]


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--builder", type=Path, default=here / "build_single_magictee_v4_full.py")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--case", action="append")
    args = parser.parse_args()

    selected = set(args.case or (case.name for case in CASES))
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "program": "v6 dual-reactance H screen",
        "fixed": {
            "through_post_radius_mm": 2.4,
            "through_post_height_mm": 16.25,
            "local_post_pair_height_mm": 0.7,
            "screws": "retracted",
        },
        "cases": [],
    }

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
            "--center-post-radius", "2.4",
            "--center-post-height", "16.25",
            "--post-height", "0.7",
            "--junction-pair-height", "0",
            "--h-throat-a", str(case.throat_a),
            "--h-throat-len", str(case.throat_len),
            "--h-throat2-len", "0",
            "--h-iris-open", str(case.iris_open),
            "--h-iris-thickness", str(case.iris_thickness),
            "--h-iris-offset", str(case.iris_offset),
            "--e-step-len", "0",
            "--solve",
            "--non-graphical",
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
