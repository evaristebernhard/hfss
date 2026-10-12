#!/usr/bin/env python3
"""Single entry for current Magic-T cell and four-way HFSS model.

Model values always come from design/current_model.json; CLI flags override a
temporary immutable copy. --dry-run requires no Ansys installation.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from magictee.config import DEFAULT_CONFIG, load_config
from magictee.geometry import CellGeometry
from magictee.tree import assemble_tree, assign_tree_ports
from magictee.solver import create_setup, export_touchstone, launch


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("cell", "tree"), default="cell")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--version", default="2025.2")
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--solve", action="store_true")
    p.add_argument("--non-graphical", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="validate/print geometry without AEDT")
    p.add_argument("--points", type=int, default=None)
    for field in ("post_lower_radius", "post_lower_height", "post_upper_radius",
                  "post_total_height", "post_radius", "post_height", "post_y",
                  "h_throat_a", "h_throat_len", "g1", "g2", "l1", "l2",
                  "screw_p1", "screw_p2", "screw_p3"):
        p.add_argument("--" + field.replace("_", "-"), type=float, default=None)
    p.add_argument("--interstage-length", type=float, default=None)
    return p


def resolve(args):
    cell, tree = load_config(args.config)
    overrides = {k: getattr(args, k) for k in (
        "post_lower_radius", "post_lower_height", "post_upper_radius",
        "post_total_height", "post_radius", "post_height", "post_y",
        "h_throat_a", "h_throat_len", "g1", "g2", "l1", "l2",
        "screw_p1", "screw_p2", "screw_p3"
    ) if getattr(args, k) is not None}
    if overrides:
        cell = cell.updated(**overrides)
    if args.interstage_length is not None:
        from dataclasses import replace
        tree = replace(tree, interstage_length_mm=args.interstage_length)
        tree.validate()
    points = args.points if args.points is not None else (
        tree.sweep_points if args.mode == "tree" else cell.n_sweep
    )
    if points < 2:
        raise ValueError("sweep must contain >= 2 points")
    return cell, tree, points


def main(argv=None):
    args = parser().parse_args(argv)
    cell, tree, points = resolve(args)
    output = args.output or Path(__file__).resolve().parent / "output_current" / args.mode
    summary = {"mode": args.mode, "config": str(args.config), "cell": asdict(cell),
               "tree": asdict(tree), "points": points,
               "h_port_y_mm": cell.h_port_y}
    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return 0

    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    basename = "magictee_cell" if args.mode == "cell" else "magictee_tree"
    suffix = "s4p" if args.mode == "cell" else "s8p"
    project = output / (basename + ".aedt")
    builder = CellGeometry(cell)
    hfss = launch(project, "SingleMagicT_v4_Full" if args.mode == "cell"
                  else "FourWayMagicT_v6_3D", args.version, args.non_graphical)
    try:
        hfss.modeler.model_units = "mm"
        builder.define_design_variables(hfss)
        if args.mode == "cell":
            _, geom = builder.create_cell(hfss)
            builder._assign_ports_and_walls(hfss, geom)
        else:
            geometry = assemble_tree(hfss, builder, tree)
            assign_tree_ports(hfss, geometry, cell)
        setup, sweep = create_setup(hfss, cell, points=points, four_way=(args.mode=="tree"))
        hfss.modeler.fit_all()
        hfss.save_project(str(project))
        print("Built:", project)
        print("Config:", json.dumps(summary, sort_keys=True))
        if args.solve:
            # Two passes required by the original HFSS Student 2025.2 export path.
            hfss.analyze_setup(setup.name)
            hfss.analyze_setup(setup.name)
            sfile = output / (basename + "." + suffix)
            try:
                export_touchstone(hfss, setup.name, sweep.name, sfile,
                                  4 if args.mode=="cell" else 8)
            except Exception:
                if args.mode != "cell":
                    raise
                hfss.export_touchstone(setup=setup.name, sweep=sweep.name,
                                       output_file=str(sfile))
            print("Touchstone:", sfile)
            hfss.save_project(str(project))
        else:
            print("Build only: inspect waveguide unions and port faces before solving.")
    finally:
        hfss.release_desktop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
