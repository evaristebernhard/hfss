#!/usr/bin/env python3
"""Create a portable, provenance-preserving paper bundle.

Run from paper/:

    python package_reproducible_bundle.py

or:

    make bundle

The ZIP preserves repository-relative paths so figure/data provenance remains
obvious after extraction. It contains the paper source, figure sources, analysis
scripts, geometry builders, the exact Touchstone inputs used by the paper, key
numerical reports, the nominal AEDT project, four-way validation data, and any
AEDT-exported paper PNGs that already exist.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = HERE / "dist"
BUNDLE_NAME = "Modal_Controllability_MagicT_Reproducible_Bundle.zip"


REQUIRED_FILES = [
    # Paper entry point and documentation.
    "paper/modal_controllability_magictee.tex",
    "paper/README.md",
    "paper/FIGURE_PROVENANCE.md",
    "paper/Makefile",
    "paper/package_reproducible_bundle.py",
    "paper/assets/README.md",

    # Paper vector figure sources.
    "paper/figures/fig_geometry_schematic.tex",
    "paper/figures/fig_dimensioned_design_layout.tex",
    "paper/figures/fig_gamma_trajectories.tex",
    "paper/figures/fig_modal_angle_matrix.tex",
    "paper/figures/fig_singular_spectrum.tex",
    "paper/figures/fig_broadband_performance.tex",

    # Analysis / regeneration code.
    "hfss/analyze_v8_modal_controllability.py",
    "hfss/analyze_modal_spectral_decomposition.py",
    "hfss/build_modal_controllability_paper_figures.py",
    "hfss/export_paper_hfss_figures.py",

    # Geometry builders defining the actual simulated structure.
    "hfss/build_single_magictee_v4_full.py",
    "hfss/build_single_magictee_v6_stepped_post.py",
    "hfss/build_four_way_magictee_v6_3d.py",

    # WSL -> Windows PyAEDT bridge used by this repository.
    "scripts/wsl_pyaedt_launcher.sh",

    # Nominal single-cell Touchstone and AEDT project.
    "hfss/results/v7_stepped_post_local/joint_l1p4_s6p2/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/joint_l1p4_s6p2/single_magictee_v4_full.aedt",

    # Legacy baseline Touchstone inputs re-analyzed by analyze_v8_modal_controllability.py.
    "hfss/results/v7_stepped_post_local/center_l2p0_u0p9_s10p16_t16p25/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/lower1p8/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/lower2p2/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/split9p2/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/split11p2/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/total15p5/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/total17p0/single_magictee_v4_full.s4p",

    # Strict central-difference Touchstone inputs.
    "hfss/results/v8_modal_controllability/lower_minus/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/joint_l1p6_s6p2/single_magictee_v4_full.s4p",
    "hfss/results/v8_modal_controllability/split_minus/single_magictee_v4_full.s4p",
    "hfss/results/v7_stepped_post_local/joint_l1p4_s7p2/single_magictee_v4_full.s4p",
    "hfss/results/v8_modal_controllability/upper_minus/single_magictee_v4_full.s4p",
    "hfss/results/v8_modal_controllability/upper_plus/single_magictee_v4_full.s4p",
    "hfss/results/v8_modal_controllability/total_minus/single_magictee_v4_full.s4p",
    "hfss/results/v8_modal_controllability/total_plus/single_magictee_v4_full.s4p",

    # Numerical reports used by the manuscript.
    "hfss/results/v8_modal_controllability/modal_controllability_report.json",
    "hfss/results/v8_modal_controllability/modal_controllability_report.md",
    "hfss/results/v8_modal_controllability/modal_controllability_columns.csv",
    "hfss/results/v8_modal_controllability/modal_spectral_decomposition.json",
    "hfss/results/v8_modal_controllability/modal_spectral_decomposition.md",

    # Four-way validation data referenced by the manuscript.
    "hfss/results/v7_four_way_3d_optimized/four_way_magictee_v6_3d.s8p",
    "hfss/results/v7_four_way_3d_optimized/audit.csv",
    "hfss/results/v7_four_way_3d_optimized/audit.json",
]


OPTIONAL_FILES = [
    # Compiled artifact if present.
    "paper/modal_controllability_magictee.pdf",

    # Real AEDT screenshots / parity fields if the export step has been run.
    "paper/assets/hfss_single_cell_model.png",
    "paper/assets/hfss_even_H_field.png",
    "paper/assets/hfss_odd_E_field.png",

    # Full four-way AEDT project (useful but not needed to regenerate paper plots).
    "hfss/results/v7_four_way_3d_optimized/four_way_magictee_v6_3d.aedt",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect() -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    missing: list[str] = []

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
        else:
            files.append(path)

    for rel in OPTIONAL_FILES:
        path = ROOT / rel
        if path.is_file():
            files.append(path)

    return files, missing


def manifest_text(files: list[Path], missing: list[str]) -> str:
    lines = [
        "Modal Controllability Magic-T — Reproducible Bundle Manifest",
        "",
        "All paths below are relative to the repository root.",
        "SHA-256 hashes allow the extracted bundle to be audited independently.",
        "",
        "FILES",
        "-----",
    ]
    for path in sorted(files):
        rel = path.relative_to(ROOT).as_posix()
        lines.append(f"{sha256(path)}  {path.stat().st_size:>10d}  {rel}")

    lines += [
        "",
        "MISSING REQUIRED FILES",
        "----------------------",
    ]
    if missing:
        lines.extend(missing)
    else:
        lines.append("(none)")

    lines += [
        "",
        "REBUILD",
        "-------",
        "cd paper",
        "make all",
        "",
        "HFSS GUI ASSETS",
        "---------------",
        "cd <repo-root>",
        "scripts/wsl_pyaedt_launcher.sh hfss/export_paper_hfss_figures.py",
        "",
        "PROVENANCE",
        "----------",
        "See paper/FIGURE_PROVENANCE.md.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    bundle = DIST / BUNDLE_NAME
    files, missing = collect()

    if missing:
        print("warning: missing required files:")
        for item in missing:
            print("  -", item)

    manifest = manifest_text(files, missing)

    with zipfile.ZipFile(
        bundle,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in sorted(files):
            rel = path.relative_to(ROOT).as_posix()
            archive.write(path, arcname=rel)
        archive.writestr("BUNDLE_MANIFEST.txt", manifest)

    print("bundle:", bundle)
    print("files:", len(files))
    print("size:", bundle.stat().st_size, "bytes")
    if missing:
        print("bundle created with missing required files; inspect BUNDLE_MANIFEST.txt")
    else:
        print("bundle is complete")


if __name__ == "__main__":
    main()
