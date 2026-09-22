#!/usr/bin/env python3
"""
Run the minimal v4 local-control identification program.

Cases (screws fully retracted):
  center
  post_height_minus / plus
  post_y_minus / plus

This is intentionally only five solves.  The purpose is to determine whether
the new junction-local rounded post pair adds sensitivity in the weak R11
output directions before any larger optimization is attempted.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


CENTER = {
    "post_height": 0.70,
    "post_y": 1.50,
}
DELTA = {
    "post_height": 0.20,
    "post_y": 0.50,
}


@dataclass(frozen=True)
class Case:
    name: str
    overrides: dict[str, float]


CASES = [
    Case("center", {}),
    Case("post_height_minus", {"post_height": CENTER["post_height"] - DELTA["post_height"]}),
    Case("post_height_plus", {"post_height": CENTER["post_height"] + DELTA["post_height"]}),
    Case("post_y_minus", {"post_y": CENTER["post_y"] - DELTA["post_y"]}),
    Case("post_y_plus", {"post_y": CENTER["post_y"] + DELTA["post_y"]}),
]


def params(case: Case):
    p = dict(CENTER)
    p.update(case.overrides)
    return p


def command(args, case, outdir):
    p = params(case)
    cmd = [
        sys.executable,
        str(args.builder),
        "--version", args.version,
        "--output", str(outdir),
        "--post-height", str(p["post_height"]),
        "--post-y", str(p["post_y"]),
        "--screw-p1", "0",
        "--screw-p2", "0",
        "--screw-p3", "0",
    ]
    if args.solve:
        cmd.append("--solve")
    if args.non_graphical:
        cmd.append("--non-graphical")
    return cmd


def main():
    here = Path(__file__).resolve().parent
    p = argparse.ArgumentParser()
    p.add_argument("--builder", type=Path, default=here / "build_single_magictee_v4_full.py")
    p.add_argument("--output-root", type=Path, default=here / "output_v4_local_id")
    p.add_argument("--version", default="2022.2")
    p.add_argument("--solve", action="store_true")
    p.add_argument("--non-graphical", action="store_true")
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--case", action="append")
    args = p.parse_args()

    args.builder = args.builder.resolve()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    selected = set(args.case or [c.name for c in CASES])
    manifest = {
        "program": "v4 junction-local post direction identification",
        "version": args.version,
        "center": CENTER,
        "half_steps": DELTA,
        "screws_retracted": True,
        "cases": [],
    }

    for case in CASES:
        if case.name not in selected:
            continue
        outdir = root / case.name
        outdir.mkdir(parents=True, exist_ok=True)
        target = outdir / ("single_magictee_v4_full.s4p" if args.solve else "single_magictee_v4_full.aedt")
        cmd = command(args, case, outdir)
        manifest["cases"].append({
            "name": case.name,
            "parameters_mm": params(case),
            "command": cmd,
            "expected_output": str(target),
        })
        if args.skip_existing and target.exists():
            print("[skip]", case.name)
            continue
        print("\n===", case.name, "===")
        print(" ".join(cmd))
        subprocess.run(cmd, check=True)
        if args.solve and not target.exists():
            raise RuntimeError("Expected S4P missing: %s" % target)

    path = root / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("\nManifest:", path)


if __name__ == "__main__":
    main()
