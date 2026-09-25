#!/usr/bin/env python3
"""
Run the v3.4 H-block center point plus central-difference perturbations.

Default behavior is build-only. Add --solve to run HFSS and export S4P.
Use --skip-center to reuse the committed v3.4 center result and run only the
eight perturbation cases.

Primary coordinates:
    a_H  = h_throat_a
    L_H  = h_throat_len
    b_C  = h_cap_height
    w_t  = h_terminal_ridge_w

Central-difference half-steps:
    a_H: +/- 0.4 mm
    L_H: +/- 1.0 mm
    b_C: +/- 0.4 mm
    w_t: +/- 0.5 mm

The w_t half-step is intentionally 0.5 mm rather than the older 0.8 mm draft
so both samples remain inside the documented 4.0--6.5 mm geometry range.
"""

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
    overrides: dict[str, float]


CENTER = {
    "h_throat_a": 20.4,
    "h_throat_len": 5.5,
    "h_cap_height": 9.0,
    "h_terminal_ridge_w": 4.572,
}

DELTAS = {
    "h_throat_a": 0.4,
    "h_throat_len": 1.0,
    "h_cap_height": 0.4,
    "h_terminal_ridge_w": 0.5,
}

CLI_FLAG = {
    "h_throat_a": "--h-throat-a",
    "h_throat_len": "--h-throat-len",
    "h_cap_height": "--h-cap-height",
    "h_terminal_ridge_w": "--h-terminal-ridge-w",
}


def make_cases() -> list[Case]:
    cases = [Case("center", {})]
    for param in CENTER:
        d = DELTAS[param]
        cases.append(Case(f"{param}_minus", {param: CENTER[param] - d}))
        cases.append(Case(f"{param}_plus", {param: CENTER[param] + d}))
    return cases


CASES = make_cases()


def resolved_parameters(case: Case) -> dict[str, float]:
    params = dict(CENTER)
    params.update(case.overrides)
    return params


def build_command(args, case: Case, case_dir: Path) -> list[str]:
    cmd = [
        sys.executable,
        str(args.builder),
        "--version",
        args.version,
        "--output",
        str(case_dir),
    ]
    if args.solve:
        cmd.append("--solve")
    if args.non_graphical:
        cmd.append("--non-graphical")

    for param, value in resolved_parameters(case).items():
        cmd.extend([CLI_FLAG[param], f"{value:.9g}"])
    return cmd


def expected_output(case_dir: Path, solve: bool) -> Path:
    if solve:
        return case_dir / "single_magictee_v3_4_hreactive.s4p"
    return case_dir / "single_magictee_v3_4_hreactive.aedt"


def parse_args():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--builder",
        type=Path,
        default=here / "build_single_magictee_v3_4_hreactive.py",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=here / "output_v3_4_jacobian",
    )
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--non-graphical", action="store_true")
    parser.add_argument("--skip-center", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--case",
        action="append",
        dest="selected_cases",
        help="Run only the named case; may be repeated.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.builder = args.builder.resolve()
    args.output_root = args.output_root.resolve()

    if not args.builder.exists():
        raise FileNotFoundError(f"Builder not found: {args.builder}")

    known = {case.name for case in CASES}
    selected = set(args.selected_cases or known)
    unknown = sorted(selected - known)
    if unknown:
        raise ValueError(f"Unknown case(s): {', '.join(unknown)}")

    if args.skip_center:
        selected.discard("center")

    args.output_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "program": "v3.4 first-order H-block Jacobian",
        "builder": str(args.builder),
        "version": args.version,
        "solve": args.solve,
        "center": CENTER,
        "deltas": DELTAS,
        "cases": [],
    }

    for case in CASES:
        if case.name not in selected:
            continue

        case_dir = args.output_root / case.name
        case_dir.mkdir(parents=True, exist_ok=True)
        target = expected_output(case_dir, args.solve)
        cmd = build_command(args, case, case_dir)

        manifest["cases"].append(
            {
                "name": case.name,
                "parameters_mm": resolved_parameters(case),
                "command": cmd,
                "expected_output": str(target),
            }
        )

        if args.skip_existing and target.exists():
            print(f"[skip] {case.name}: {target} exists")
            continue

        print(f"\n=== {case.name} ===")
        print(" ".join(f'"{x}"' if " " in x else x for x in cmd))
        subprocess.run(cmd, check=True)

        if args.solve and not target.exists():
            raise RuntimeError(
                f"HFSS command completed but expected S4P was not found: {target}"
            )

    manifest_path = args.output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest: {manifest_path}")


if __name__ == "__main__":
    main()
