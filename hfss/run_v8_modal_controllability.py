#!/usr/bin/env python3
"""Run the six missing HFSS cases needed for a strict v8 modal Jacobian.

The v7 final seed is
    lower radius  = 1.4 mm
    split height  = 6.2 mm
    upper radius  = 0.9 mm
    total height  = 16.25 mm

Existing v7 results already provide:
    center        : (1.4, 6.2, 0.9, 16.25)
    lower_plus    : (1.6, 6.2, 0.9, 16.25)
    split_plus    : (1.4, 7.2, 0.9, 16.25)

This script only adds the six missing cases:
    lower_minus, split_minus,
    upper_minus, upper_plus,
    total_minus, total_plus.

Together they define a four-parameter central-difference Jacobian around the
v7 seed without rerunning cases that are already in the repository.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Case:
    name: str
    lower_radius: float
    lower_height: float
    upper_radius: float
    total_height: float


CASES = [
    Case("lower_minus", 1.2, 6.2, 0.9, 16.25),
    Case("split_minus", 1.4, 5.2, 0.9, 16.25),
    Case("upper_minus", 1.4, 6.2, 0.7, 16.25),
    Case("upper_plus", 1.4, 6.2, 1.1, 16.25),
    Case("total_minus", 1.4, 6.2, 0.9, 15.50),
    Case("total_plus", 1.4, 6.2, 0.9, 17.00),
]


def build_command(
    launcher: Path,
    builder: Path,
    version: str,
    windows_output: str,
    case: Case,
) -> list[str]:
    return [
        str(launcher),
        str(builder),
        "--version",
        version,
        "--output",
        windows_output,
        "--post-lower-radius",
        str(case.lower_radius),
        "--post-lower-height",
        str(case.lower_height),
        "--post-upper-radius",
        str(case.upper_radius),
        "--post-total-height",
        str(case.total_height),
        "--post-height",
        "0.7",
        "--junction-pair-height",
        "0",
        "--h-throat-a",
        "20.4",
        "--h-throat-len",
        "5.5",
        "--h-throat2-len",
        "0",
        "--h-iris-open",
        "0",
        "--e-step-len",
        "0",
        "--solve",
        "--non-graphical",
    ]


def wsl_to_windows_path(path: Path) -> str:
    """Convert a WSL path to a path accepted by Windows Python/AEDT."""
    try:
        converted = subprocess.check_output(
            ["wslpath", "-w", str(path)],
            text=True,
        ).strip()
    except FileNotFoundError as exc:
        raise RuntimeError(
            "wslpath is unavailable; run this workflow from WSL2"
        ) from exc
    if not converted:
        raise RuntimeError(f"wslpath returned an empty path for {path}")
    return converted


def main() -> None:
    here = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--builder",
        type=Path,
        default=here / "build_single_magictee_v6_stepped_post.py",
    )
    parser.add_argument(
        "--launcher",
        type=Path,
        default=here.parent / "scripts" / "wsl_pyaedt_launcher.sh",
        help="WSL launcher for the Windows PyAEDT environment",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=here / "results" / "v8_modal_controllability",
    )
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    builder = args.builder.resolve()
    launcher = args.launcher.resolve()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    windows_root = wsl_to_windows_path(root)

    manifest = {
        "program": "v8 strict modal controllability identification",
        "center": {
            "lower_radius_mm": 1.4,
            "split_height_mm": 6.2,
            "upper_radius_mm": 0.9,
            "total_height_mm": 16.25,
        },
        "central_difference_half_steps_mm": {
            "lower_radius": 0.2,
            "split_height": 1.0,
            "upper_radius": 0.2,
            "total_height": 0.75,
        },
        "reused_v7_cases": {
            "center": "hfss/results/v7_stepped_post_local/joint_l1p4_s6p2",
            "lower_plus": "hfss/results/v7_stepped_post_local/joint_l1p6_s6p2",
            "split_plus": "hfss/results/v7_stepped_post_local/joint_l1p4_s7p2",
        },
        "new_cases": [],
    }

    for case in CASES:
        outdir = root / case.name
        target = outdir / "single_magictee_v4_full.s4p"
        manifest["new_cases"].append(
            {
                **asdict(case),
                "output": str(target),
            }
        )

        if args.skip_existing and target.exists():
            print("[skip]", case.name, flush=True)
            continue

        outdir.mkdir(parents=True, exist_ok=True)
        windows_output = windows_root.rstrip("\\/") + "\\" + case.name
        cmd = build_command(launcher, builder, args.version, windows_output, case)
        print("[run]", case.name, flush=True)
        subprocess.run(cmd, check=True)

        if not target.exists():
            raise RuntimeError(f"missing Touchstone result: {target}")

    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("manifest:", manifest_path)


if __name__ == "__main__":
    main()
