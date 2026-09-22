#!/usr/bin/env python3
"""Screen symmetric two-step H-plane matching throats."""

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
    a1: float
    l1: float
    a2: float
    l2: float


CASES = [
    Case("wide22_to_narrow18p8", 22.0, 4.5, 18.8, 4.5),
    Case("narrow18p8_to_wide22", 18.8, 4.5, 22.0, 4.5),
    Case("full22p86_to_mid20", 22.86, 4.5, 20.0, 4.5),
    Case("mid20_to_full22p86", 20.0, 4.5, 22.86, 4.5),
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
    manifest = {"program": "v5 two-step H-plane throat screen", "cases": []}

    for case in CASES:
        outdir = args.output_root / case.name
        target = outdir / "single_magictee_v4_full.s4p"
        cmd = [
            sys.executable, str(args.builder),
            "--version", args.version,
            "--output", str(outdir),
            "--h-throat-a", str(case.a1),
            "--h-throat-len", str(case.l1),
            "--h-throat2-a", str(case.a2),
            "--h-throat2-len", str(case.l2),
            "--h-iris-open", "0",
            "--solve", "--non-graphical",
        ]
        manifest["cases"].append({"name": case.name, "parameters": case.__dict__, "output": str(target)})
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
