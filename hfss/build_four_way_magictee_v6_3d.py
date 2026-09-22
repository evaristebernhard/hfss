#!/usr/bin/env python3
"""Build and solve the full 3-D, eight-port v6 four-way Magic-T tree.

The model clones the screened stepped-post cell three times.  The first-stage
H ports connect to the second-stage collinear ports through equal straight
WR90 sections.  External port order is IN1, IN2, IN3, IN4, OUT, DUMP_A,
DUMP_B, DUMP_C.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import build_single_magictee_v4_full as base


INTERSTAGE_LENGTH = 4.66
LOWER_POST_RADIUS = 2.0
LOWER_POST_HEIGHT = base.B
UPPER_POST_RADIUS = 1.0
TOTAL_POST_HEIGHT = 16.25


def _launch(project_path: str, version: str, non_graphical: bool):
    Hfss, api = base._import_hfss_class()
    if api == "ansys.aedt.core":
        return Hfss(
            project=project_path,
            design="FourWayMagicT_v6_3D",
            version=version,
            solution_type="Modal",
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=True,
        )
    return Hfss(
        projectname=project_path,
        designname="FourWayMagicT_v6_3D",
        specified_version=version,
        solution_type="DrivenModal",
        non_graphical=non_graphical,
        new_desktop_session=True,
    )


def _configure_base_cell():
    base.RIDGE_W = 4.572
    base.G1 = 7.672
    base.L1 = 9.872
    base.G2 = 5.8
    base.L2 = 8.857
    base.POST_RADIUS = 1.5
    base.POST_HEIGHT = 0.7
    base.POST_Y = 2.0
    base.CENTER_POST_RADIUS = LOWER_POST_RADIUS
    base.CENTER_POST_HEIGHT = 0.0
    base.JUNCTION_PAIR_HEIGHT = 0.0
    base.H_THROAT_A = 20.4
    base.H_THROAT_LEN = 5.5
    base.H_THROAT2_LEN = 0.0
    base.H_IRIS_OPEN = 0.0
    base.E_STEP_LEN = 0.0
    base.SCREW_P1 = base.SCREW_P2 = base.SCREW_P3 = 0.0
    base.TAPER_TOTAL = base.L1 + base.L2
    base.H_ARM_ACTIVE_LEN = (
        base.H_THROAT_LEN
        + base.TERMINAL_RIDGE_LEN
        + base.TAPER_TOTAL
        + base.TUNER_SECTION_LEN
        + base.PORT_STRAIGHT_LEN
    )
    base._validate_geometry()


def _subtract_stepped_post(hfss):
    lower = base._cylinder(
        hfss,
        [0.0, 0.0, -base.B / 2.0],
        LOWER_POST_RADIUS,
        LOWER_POST_HEIGHT,
        "JunctionPost_Lower",
    )
    upper = base._cylinder(
        hfss,
        [0.0, 0.0, -base.B / 2.0 + LOWER_POST_HEIGHT],
        UPPER_POST_RADIUS,
        TOTAL_POST_HEIGHT - LOWER_POST_HEIGHT,
        "JunctionPost_Upper",
    )
    hfss.modeler.subtract("AirWG", [lower.name, upper.name], keep_originals=False)


def _make_seed_cell(hfss):
    base._make_air_volume(hfss)
    base._subtract_e_step(hfss)
    throat = base._subtract_h_width_throat(hfss)
    _subtract_stepped_post(hfss)
    base._subtract_local_post_pair(hfss)
    geom = base._subtract_terminal_and_taper(hfss, throat)
    base._subtract_three_screws(hfss, geom)
    cell = hfss.modeler["AirWG"]
    cell.name = "CellC_Air"
    return cell, geom


def _assemble_tree(hfss):
    cell_c, geom = _make_seed_cell(hfss)
    h_port = geom["h_port_y"]
    left_join = -base.COLLINEAR_HALF_LEN - INTERSTAGE_LENGTH
    right_join = base.COLLINEAR_HALF_LEN + INTERSTAGE_LENGTH

    cell_a = cell_c.clone()
    cell_b = cell_c.clone()
    if not cell_a or not cell_b:
        raise RuntimeError("failed to clone the seed cell")
    cell_a.name = "CellA_Air"
    cell_b.name = "CellB_Air"

    # Local +Y H arm becomes global +X for A and global -X for B.
    if not cell_a.rotate("Z", -90.0):
        raise RuntimeError("failed to rotate Cell A")
    if not cell_b.rotate("Z", 90.0):
        raise RuntimeError("failed to rotate Cell B")
    center_a_x = left_join - h_port
    center_b_x = right_join + h_port
    if not cell_a.move([center_a_x, 0.0, 0.0]):
        raise RuntimeError("failed to move Cell A")
    if not cell_b.move([center_b_x, 0.0, 0.0]):
        raise RuntimeError("failed to move Cell B")

    link_a = base._box(
        hfss,
        [left_join, -base.A / 2.0, -base.B / 2.0],
        [INTERSTAGE_LENGTH, base.A, base.B],
        "Interstage_A",
    )
    link_b = base._box(
        hfss,
        [base.COLLINEAR_HALF_LEN, -base.A / 2.0, -base.B / 2.0],
        [INTERSTAGE_LENGTH, base.A, base.B],
        "Interstage_B",
    )
    hfss.modeler.unite([cell_c.name, cell_a.name, cell_b.name, link_a.name, link_b.name])
    air = hfss.modeler[cell_c.name]
    air.name = "AirWG"
    return {
        "h_port": h_port,
        "e_port": base.B / 2.0 + base.E_ARM_LEN,
        "center_a_x": center_a_x,
        "center_b_x": center_b_x,
    }


def _face(hfss, position):
    face = hfss.modeler.get_faceid_from_position(position, assignment="AirWG")
    if face is None or face < 0:
        raise RuntimeError(f"could not find external port face at {position}")
    return face


def _wave_port(hfss, face, line, name):
    return hfss.wave_port(
        face,
        integration_line=line,
        modes=1,
        name=name,
        renormalize=False,
        characteristic_impedance="Zwave",
    )


def _assign_ports_and_walls(hfss, geom):
    xa = geom["center_a_x"]
    xb = geom["center_b_x"]
    hp = geom["h_port"]
    ep = geom["e_port"]
    positions = [
        [xa, base.COLLINEAR_HALF_LEN, 0.0],
        [xa, -base.COLLINEAR_HALF_LEN, 0.0],
        [xb, -base.COLLINEAR_HALF_LEN, 0.0],
        [xb, base.COLLINEAR_HALF_LEN, 0.0],
        [0.0, hp, 0.0],
        [xa, 0.0, ep],
        [xb, 0.0, ep],
        [0.0, 0.0, ep],
    ]
    faces = [_face(hfss, position) for position in positions]

    zline = lambda x, y: [[x, y, -base.B / 2.0], [x, y, base.B / 2.0]]
    _wave_port(hfss, faces[0], zline(xa, base.COLLINEAR_HALF_LEN), "P1_IN1")
    _wave_port(hfss, faces[1], zline(xa, -base.COLLINEAR_HALF_LEN), "P2_IN2")
    _wave_port(hfss, faces[2], zline(xb, -base.COLLINEAR_HALF_LEN), "P3_IN3")
    _wave_port(hfss, faces[3], zline(xb, base.COLLINEAR_HALF_LEN), "P4_IN4")
    _wave_port(hfss, faces[4], zline(0.0, hp), "P5_OUT")
    _wave_port(
        hfss,
        faces[5],
        [[xa, -base.B / 2.0, ep], [xa, base.B / 2.0, ep]],
        "P6_DUMP_A",
    )
    _wave_port(
        hfss,
        faces[6],
        [[xb, -base.B / 2.0, ep], [xb, base.B / 2.0, ep]],
        "P7_DUMP_B",
    )
    _wave_port(
        hfss,
        faces[7],
        [[-base.B / 2.0, 0.0, ep], [base.B / 2.0, 0.0, ep]],
        "P8_DUMP_C",
    )

    port_faces = set(faces)
    walls = [face.id for face in hfss.modeler["AirWG"].faces if face.id not in port_faces]
    hfss.assign_perfect_e(walls, name="PEC_WaveguideWalls")


def _create_setup(hfss, points: int):
    setup = hfss.create_setup("Setup1")
    setup.props["Frequency"] = "10.2GHz"
    setup.props["MaximumPasses"] = 7
    setup.props["MinimumPasses"] = 2
    setup.props["MinimumConvergedPasses"] = 1
    setup.props["MaxDeltaS"] = 0.03
    setup.update()
    sweep = hfss.create_linear_count_sweep(
        setup=setup.name,
        unit="GHz",
        start_frequency=9.0,
        stop_frequency=11.5,
        num_of_freq_points=points,
        name="Sweep_9_11p5GHz",
        sweep_type="Interpolating",
        interpolation_tol=0.75,
        save_fields=False,
    )
    return setup, sweep


def _write_s8p(hfss, setup_name: str, sweep_name: str, path: Path):
    expressions = [f"S({row},{column})" for row in range(1, 9) for column in range(1, 9)]
    data = hfss.post.get_solution_data(
        expressions=expressions,
        setup_sweep_name=f"{setup_name} : {sweep_name}",
    )
    if not data:
        raise RuntimeError("HFSS returned no eight-port solution data")
    frequencies, _ = data.get_expression_data(expressions[0], formula="real")
    real = {}
    imag = {}
    for expression in expressions:
        _, real[expression] = data.get_expression_data(expression, formula="real")
        _, imag[expression] = data.get_expression_data(expression, formula="imag")
    lines = [
        "! Full 3-D v6 four-way tree: IN1 IN2 IN3 IN4 OUT DUMP_A DUMP_B DUMP_C",
        "# GHz S MA R 50",
    ]
    for index, frequency in enumerate(frequencies):
        fields = [f"{float(frequency):.12g}"]
        for expression in expressions:
            value = complex(float(real[expression][index]), float(imag[expression][index]))
            fields.extend([f"{abs(value):.12g}", f"{math.degrees(math.atan2(value.imag, value.real)):.12g}"])
        lines.append(" ".join(fields))
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def build(args):
    global INTERSTAGE_LENGTH, LOWER_POST_RADIUS, LOWER_POST_HEIGHT
    global UPPER_POST_RADIUS, TOTAL_POST_HEIGHT
    INTERSTAGE_LENGTH = args.interstage_length
    LOWER_POST_RADIUS = args.post_lower_radius
    LOWER_POST_HEIGHT = args.post_lower_height
    UPPER_POST_RADIUS = args.post_upper_radius
    TOTAL_POST_HEIGHT = args.post_total_height
    if INTERSTAGE_LENGTH < 0.0:
        raise ValueError("interstage length must be non-negative")
    if not (0.0 < LOWER_POST_HEIGHT <= TOTAL_POST_HEIGHT < base.B + base.E_ARM_LEN):
        raise ValueError("invalid stepped-post heights")
    if LOWER_POST_RADIUS <= 0.0 or UPPER_POST_RADIUS <= 0.0:
        raise ValueError("stepped-post radii must be positive")
    _configure_base_cell()

    outdir = Path(args.output).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    project = outdir / "four_way_magictee_v6_3d.aedt"
    hfss = _launch(str(project), args.version, args.non_graphical)
    hfss.modeler.model_units = "mm"
    geom = _assemble_tree(hfss)
    _assign_ports_and_walls(hfss, geom)
    setup, sweep = _create_setup(hfss, args.points)
    hfss.modeler.fit_all()
    hfss.save_project(str(project))
    print("Built:", project)
    print("Interstage length: %.3f mm" % INTERSTAGE_LENGTH)
    print("Stepped post lower r/h, upper r, total h: %.3f / %.3f / %.3f / %.3f mm" % (
        LOWER_POST_RADIUS, LOWER_POST_HEIGHT, UPPER_POST_RADIUS, TOTAL_POST_HEIGHT
    ))
    print("External ports: IN1 IN2 IN3 IN4 OUT DUMP_A DUMP_B DUMP_C")
    if args.solve:
        hfss.analyze_setup(setup.name)
        hfss.analyze_setup(setup.name)
        output = outdir / "four_way_magictee_v6_3d.s8p"
        _write_s8p(hfss, setup.name, sweep.name, output)
        print("Touchstone:", output)
        hfss.save_project(str(project))
    else:
        print("Build-only mode; inspect geometry before solving.")
    try:
        hfss.release_desktop()
    except Exception as exc:
        print("AEDT release warning:", exc)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="2025.2")
    parser.add_argument("--output", default=str(Path(__file__).resolve().parent / "output_v6_four_way_3d"))
    parser.add_argument("--interstage-length", type=float, default=INTERSTAGE_LENGTH)
    parser.add_argument("--post-lower-radius", type=float, default=LOWER_POST_RADIUS)
    parser.add_argument("--post-lower-height", type=float, default=LOWER_POST_HEIGHT)
    parser.add_argument("--post-upper-radius", type=float, default=UPPER_POST_RADIUS)
    parser.add_argument("--post-total-height", type=float, default=TOTAL_POST_HEIGHT)
    parser.add_argument("--points", type=int, default=51)
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--non-graphical", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
