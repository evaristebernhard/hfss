#!/usr/bin/env python3
"""Export reader-facing HFSS model and parity-field images for the paper.

Run this through the repository WSL -> Windows PyAEDT launcher because the
model-picture export and AEDT field overlay require a graphical AEDT session.

The script uses the solved nominal single-cell project and produces:

  paper/assets/hfss_single_cell_model.png
  paper/assets/hfss_even_H_field.png
  paper/assets/hfss_odd_E_field.png

The even and odd pictures use equal-magnitude collinear-port excitations with
0/0 deg and 0/180 deg phase, respectively, at the adaptive frequency 10.2 GHz.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def import_hfss():
    try:
        from ansys.aedt.core import Hfss
        return Hfss, "ansys.aedt.core"
    except ImportError:
        from pyaedt import Hfss
        return Hfss, "pyaedt"


def launch(project: Path, version: str):
    Hfss, api = import_hfss()
    if api == "ansys.aedt.core":
        return Hfss(
            project=str(project),
            design="SingleMagicT_v4_Full",
            version=version,
            solution_type="Modal",
            non_graphical=False,
            new_desktop=True,
            close_on_exit=True,
            student_version=True,
        )
    return Hfss(
        projectname=str(project),
        designname="SingleMagicT_v4_Full",
        specified_version=version,
        solution_type="DrivenModal",
        non_graphical=False,
        new_desktop_session=True,
        student_version=True,
    )


def set_parity_sources(hfss, odd: bool) -> None:
    phase2 = "180deg" if odd else "0deg"
    sources = {
        "P1_CollinearMinusX:1": ("1W", "0deg"),
        "P2_CollinearPlusX:1": ("1W", phase2),
        "P3_HArm_v4:1": ("0W", "0deg"),
        "P4_EArm:1": ("0W", "0deg"),
    }
    ok = hfss.edit_sources(sources, include_port_post_processing=True)
    if not ok:
        raise RuntimeError("HFSS edit_sources failed for parity excitation")


def export_field(hfss, output: Path, odd: bool) -> str:
    set_parity_sources(hfss, odd=odd)
    setup = hfss.nominal_adaptive
    intrinsics = {"Freq": "10.2GHz", "Phase": "0deg"}

    plot = hfss.post.create_fieldplot_volume(
        assignment=["AirWG"],
        quantity="ComplexMag_E",
        setup=setup,
        intrinsics=intrinsics,
    )
    if not plot:
        raise RuntimeError("Could not create ComplexMag_E volume field plot")

    result = plot.export_image(
        full_path=str(output),
        width=1800,
        height=1200,
        orientation="isometric",
        display_wireframe=True,
        selections=["AirWG"],
        show_region=False,
        show_axis=True,
        show_grid=False,
        show_ruler=False,
    )
    try:
        plot.delete()
    except Exception:
        pass
    if not result:
        raise RuntimeError(f"Field image export failed: {output}")
    return str(result)


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project",
        type=Path,
        default=here
        / "results"
        / "v7_stepped_post_local"
        / "joint_l1p4_s6p2"
        / "single_magictee_v4_full.aedt",
    )
    parser.add_argument("--version", default="2025.2")
    parser.add_argument(
        "--output",
        type=Path,
        default=here.parent / "paper" / "assets",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    hfss = launch(project, args.version)
    try:
        model_path = out / "hfss_single_cell_model.png"
        exported_model = hfss.post.export_model_picture(
            full_name=str(model_path),
            show_axis=True,
            show_grid=False,
            show_ruler=False,
            show_region=False,
        )
        if not exported_model:
            raise RuntimeError("HFSS model picture export failed")
        print("model:", exported_model)

        even_path = out / "hfss_even_H_field.png"
        print("even/H:", export_field(hfss, even_path, odd=False))

        odd_path = out / "hfss_odd_E_field.png"
        print("odd/E:", export_field(hfss, odd_path, odd=True))

        hfss.save_project()
    finally:
        try:
            hfss.release_desktop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
