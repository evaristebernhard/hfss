#!/usr/bin/env python3
"""
HFSS 2022 / PyAEDT v4 single-Magic-T full architecture builder.

Frozen H/sum-arm architecture:

    tee junction
      -> symmetric rounded partial-height post pair
      -> mild reduced-width H-plane throat
      -> terminal double ridge
      -> smooth double-ridge transformer
      -> three-screw residual tuner
      -> WR90 reference port

The three tuning screws are part of the geometry from the beginning but default
to zero penetration.  The E arm keeps the v2 parity-correct orientation.

This is the v4 architecture model, not a final optimized geometry.  Default
mode is build-only.  Add --solve to run the 9.0--11.5 GHz sweep and export S4P.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

A = 22.86
B = 10.16

RIDGE_W = 4.572
G1 = 7.672
L1 = 9.872
G2 = 5.800
L2 = 8.857

POST_RADIUS = 1.50
POST_HEIGHT = 0.70
POST_Y = 2.00  # post axis from H-arm junction mouth [mm]
CENTER_POST_RADIUS = 1.50
CENTER_POST_HEIGHT = 0.0  # disabled; may pass through the junction into the E arm
JUNCTION_PAIR_RADIUS = 1.50
JUNCTION_PAIR_HEIGHT = 0.0  # disabled by default; symmetric top/bottom pair at center

H_THROAT_A = 20.40
H_THROAT_LEN = 5.50
H_THROAT2_A = 20.40
H_THROAT2_LEN = 0.0  # optional second H-plane matching section
H_IRIS_OPEN = 0.0  # disabled by default; >0 enables a dedicated symmetric iris
H_IRIS_THICKNESS = 3.00
H_IRIS_OFFSET = 8.50  # from the H-arm junction mouth [mm]
H_TERMINAL_RIDGE_W = 4.572
TERMINAL_RIDGE_LEN = 7.50

SCREW_RADIUS = 1.00
SCREW_TUNER_OFFSET = 3.00
SCREW_Z1 = 0.00
SCREW_Z2 = 8.40
SCREW_Z3 = 17.60
SCREW_P1 = 0.00
SCREW_P2 = 0.00
SCREW_P3 = 0.00

TUNER_SECTION_LEN = 24.0
PORT_STRAIGHT_LEN = 6.0
COLLINEAR_HALF_LEN = 35.0
E_ARM_LEN = 30.0
E_STEP_B = 0.0  # disabled; reduced E-arm narrow dimension near the junction
E_STEP_LEN = 0.0
N_TAPER_SEGMENTS = 24

F_ADAPT_GHZ = 10.20
F_START_GHZ = 9.0
F_STOP_GHZ = 11.5
N_SWEEP = 101

TAPER_TOTAL = L1 + L2
H_ARM_ACTIVE_LEN = (
    H_THROAT_LEN
    + H_THROAT2_LEN
    + TERMINAL_RIDGE_LEN
    + TAPER_TOTAL
    + TUNER_SECTION_LEN
    + PORT_STRAIGHT_LEN
)


def smoothstep(t: float) -> float:
    return 3.0 * t * t - 2.0 * t * t * t


def log_interp(a: float, b: float, t: float) -> float:
    s = smoothstep(t)
    return math.exp((1.0 - s) * math.log(a) + s * math.log(b))


def taper_gap_from_port_distance(s_mm: float) -> float:
    if s_mm <= 0.0:
        return B
    if s_mm >= TAPER_TOTAL:
        return G2
    if s_mm <= L1:
        return log_interp(B, G1, s_mm / L1)
    return log_interp(G1, G2, (s_mm - L1) / L2)


def _import_hfss_class():
    try:
        from ansys.aedt.core import Hfss
        return Hfss, "ansys.aedt.core"
    except ImportError:
        from pyaedt import Hfss
        return Hfss, "pyaedt"


def _launch_hfss(project_path: str, version: str, non_graphical: bool):
    Hfss, api = _import_hfss_class()
    if api == "ansys.aedt.core":
        return Hfss(
            project=project_path,
            design="SingleMagicT_v4_Full",
            version=version,
            solution_type="Modal",
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=True,
        )
    return Hfss(
        projectname=project_path,
        designname="SingleMagicT_v4_Full",
        specified_version=version,
        solution_type="DrivenModal",
        non_graphical=non_graphical,
        new_desktop_session=True,
    )


def _box(hfss, origin, sizes, name, material="vacuum"):
    return hfss.modeler.create_box(
        origin=origin,
        sizes=sizes,
        name=name,
        material=material,
    )


def _cylinder(hfss, origin, radius, height, name, material="pec"):
    # Modern PyAEDT uses orientation/origin; older versions accept the same
    # positional ordering.  Keep the call simple for HFSS 2022 compatibility.
    try:
        return hfss.modeler.create_cylinder(
            orientation="Z",
            origin=origin,
            radius=radius,
            height=height,
            name=name,
            material=material,
        )
    except TypeError:
        return hfss.modeler.create_cylinder(
            "Z", origin, radius, height, 0, name, material
        )


def _validate_geometry():
    if not (0.0 < H_THROAT_A <= A):
        raise ValueError("h_throat_a must satisfy 0 < a <= WR90 broad dimension")
    if H_THROAT_LEN <= 0.0:
        raise ValueError("h_throat_len must be positive")
    if H_THROAT2_LEN < 0.0:
        raise ValueError("h_throat2_len must be non-negative")
    if H_THROAT2_LEN > 0.0 and not (0.0 < H_THROAT2_A <= A):
        raise ValueError("h_throat2_a must satisfy 0 < a <= WR90 broad dimension")
    if H_IRIS_OPEN > 0.0:
        if not (0.0 < H_IRIS_OPEN < H_THROAT_A):
            raise ValueError("h_iris_open must be smaller than h_throat_a")
        if H_IRIS_THICKNESS <= 0.0:
            raise ValueError("h_iris_thickness must be positive")
        if H_IRIS_OFFSET < 0.0 or H_IRIS_OFFSET + H_IRIS_THICKNESS > H_THROAT_LEN:
            raise ValueError("dedicated H iris must remain inside the H throat")
    if not (0.0 <= POST_HEIGHT < B / 2.0):
        raise ValueError("post_height must satisfy 0 <= h < B/2")
    if POST_HEIGHT > 0.0 and POST_RADIUS <= 0.0:
        raise ValueError("post_radius must be positive when local posts are enabled")
    if CENTER_POST_HEIGHT < 0.0 or CENTER_POST_HEIGHT >= B + E_ARM_LEN:
        raise ValueError("center_post_height must remain inside the junction/E arm")
    if CENTER_POST_HEIGHT > 0.0 and CENTER_POST_RADIUS <= 0.0:
        raise ValueError("center_post_radius must be positive when enabled")
    if JUNCTION_PAIR_HEIGHT < 0.0 or JUNCTION_PAIR_HEIGHT >= B / 2.0:
        raise ValueError("junction_pair_height must satisfy 0 <= h < waveguide half-height")
    if JUNCTION_PAIR_HEIGHT > 0.0 and JUNCTION_PAIR_RADIUS <= 0.0:
        raise ValueError("junction_pair_radius must be positive when enabled")
    if E_STEP_LEN < 0.0 or E_STEP_LEN > E_ARM_LEN:
        raise ValueError("e_step_len must remain inside the E arm")
    if E_STEP_LEN > 0.0 and not (0.0 < E_STEP_B <= B):
        raise ValueError("e_step_b must satisfy 0 < b <= waveguide height")

    y_center = A / 2.0 + POST_Y
    if y_center - POST_RADIUS < A / 2.0 - 1e-9:
        raise ValueError("local post overlaps back into the collinear junction volume")
    if y_center + POST_RADIUS > A / 2.0 + H_THROAT_LEN + 1e-9:
        raise ValueError("local post must remain inside the H-throat region")

    if not (0.0 < G2 <= B and 0.0 < G1 <= B):
        raise ValueError("ridge gaps must lie inside WR90 narrow dimension")
    if not (0.0 < H_TERMINAL_RIDGE_W <= A):
        raise ValueError("terminal ridge width must lie inside H-arm broad dimension")

    positions = [
        SCREW_TUNER_OFFSET + SCREW_Z1,
        SCREW_TUNER_OFFSET + SCREW_Z2,
        SCREW_TUNER_OFFSET + SCREW_Z3,
    ]
    for p in positions:
        if p - SCREW_RADIUS < 0.0 or p + SCREW_RADIUS > TUNER_SECTION_LEN:
            raise ValueError("screw center/radius lies outside tuner straight section")

    for p in (SCREW_P1, SCREW_P2, SCREW_P3):
        if p < 0.0 or p > 2.0:
            raise ValueError("screw penetration must satisfy 0 <= p <= 2 mm")


def _make_air_volume(hfss):
    _box(
        hfss,
        [-COLLINEAR_HALF_LEN, -A / 2.0, -B / 2.0],
        [2.0 * COLLINEAR_HALF_LEN, A, B],
        "AirWG",
    )
    _box(
        hfss,
        [-A / 2.0, A / 2.0, -B / 2.0],
        [A, H_ARM_ACTIVE_LEN, B],
        "HArmAir",
    )
    _box(
        hfss,
        [-B / 2.0, -A / 2.0, B / 2.0],
        [B, A, E_ARM_LEN],
        "EArmAir",
    )
    hfss.modeler.unite(["AirWG", "HArmAir", "EArmAir"])
    return hfss.modeler["AirWG"]


def _subtract_e_step(hfss):
    """Short symmetric E-arm height step, followed by the full WR90 port."""
    if E_STEP_LEN <= 0.0 or E_STEP_B >= B - 1e-9:
        return {"e_step_enabled": False}
    z0 = B / 2.0
    side_depth = 0.5 * (B - E_STEP_B)
    left = _box(
        hfss,
        [-B / 2.0, -A / 2.0, z0],
        [side_depth, A, E_STEP_LEN],
        "EStepWall_Left",
        material="pec",
    )
    right = _box(
        hfss,
        [E_STEP_B / 2.0, -A / 2.0, z0],
        [side_depth, A, E_STEP_LEN],
        "EStepWall_Right",
        material="pec",
    )
    hfss.modeler.subtract("AirWG", [left.name, right.name], keep_originals=False)
    return {"e_step_enabled": True, "e_step_b": E_STEP_B, "e_step_len": E_STEP_LEN}


def _subtract_h_width_throat(hfss):
    y0 = A / 2.0
    sections = [(H_THROAT_A, H_THROAT_LEN, "HThroat1")]
    if H_THROAT2_LEN > 0.0:
        sections.append((H_THROAT2_A, H_THROAT2_LEN, "HThroat2"))
    y = y0
    for width, length, prefix in sections:
        side_depth = 0.5 * (A - width)
        if side_depth > 1e-9:
            left = _box(
                hfss,
                [-A / 2.0, y, -B / 2.0],
                [side_depth, length, B],
                prefix + "Wall_Left",
                material="pec",
            )
            right = _box(
                hfss,
                [width / 2.0, y, -B / 2.0],
                [side_depth, length, B],
                prefix + "Wall_Right",
                material="pec",
            )
            hfss.modeler.subtract("AirWG", [left.name, right.name], keep_originals=False)
        y += length
    return {
        "h_throat_start_y": y0,
        "h_throat_end_y": y,
        "h_throat_side_depth": 0.5 * (A - H_THROAT_A),
    }


def _subtract_local_post_pair(hfss):
    """Symmetric rounded top/bottom partial-height posts near the H junction."""
    y = A / 2.0 + POST_Y
    if POST_HEIGHT <= 0.0:
        return {"post_axis_y": y, "local_post_pair_enabled": False}

    top = _cylinder(
        hfss,
        [0.0, y, B / 2.0 - POST_HEIGHT],
        POST_RADIUS,
        POST_HEIGHT,
        "JunctionPost_Top",
    )
    bot = _cylinder(
        hfss,
        [0.0, y, -B / 2.0],
        POST_RADIUS,
        POST_HEIGHT,
        "JunctionPost_Bottom",
    )
    hfss.modeler.subtract("AirWG", [top.name, bot.name], keep_originals=False)
    return {"post_axis_y": y, "local_post_pair_enabled": True}


def _subtract_center_post(hfss):
    """Create a junction post that may extend from the bottom into the E arm."""
    if CENTER_POST_HEIGHT <= 0.0:
        return {"center_post_enabled": False}
    post = _cylinder(
        hfss,
        [0.0, 0.0, -B / 2.0],
        CENTER_POST_RADIUS,
        CENTER_POST_HEIGHT,
        "JunctionCenterPost",
    )
    hfss.modeler.subtract("AirWG", [post.name], keep_originals=False)
    return {"center_post_enabled": True}


def _subtract_junction_pair(hfss):
    """Create a strong z-symmetric rounded post pair at the junction center."""
    if JUNCTION_PAIR_HEIGHT <= 0.0:
        return {"junction_pair_enabled": False}
    top = _cylinder(
        hfss,
        [0.0, 0.0, B / 2.0 - JUNCTION_PAIR_HEIGHT],
        JUNCTION_PAIR_RADIUS,
        JUNCTION_PAIR_HEIGHT,
        "JunctionPair_Top",
    )
    bot = _cylinder(
        hfss,
        [0.0, 0.0, -B / 2.0],
        JUNCTION_PAIR_RADIUS,
        JUNCTION_PAIR_HEIGHT,
        "JunctionPair_Bottom",
    )
    hfss.modeler.subtract("AirWG", [top.name, bot.name], keep_originals=False)
    return {"junction_pair_enabled": True}


def _subtract_h_iris(hfss):
    """Create a centered symmetric sidewall iris in the dedicated H throat."""
    if H_IRIS_OPEN <= 0.0:
        return {"h_iris_enabled": False}

    y0 = A / 2.0 + H_IRIS_OFFSET
    side_depth = 0.5 * (H_THROAT_A - H_IRIS_OPEN)
    left = _box(
        hfss,
        [-H_THROAT_A / 2.0, y0, -B / 2.0],
        [side_depth, H_IRIS_THICKNESS, B],
        "H_Iris_Left",
        material="pec",
    )
    right = _box(
        hfss,
        [H_IRIS_OPEN / 2.0, y0, -B / 2.0],
        [side_depth, H_IRIS_THICKNESS, B],
        "H_Iris_Right",
        material="pec",
    )
    hfss.modeler.subtract("AirWG", [left.name, right.name], keep_originals=False)
    return {
        "h_iris_enabled": True,
        "h_iris_start_y": y0,
        "h_iris_end_y": y0 + H_IRIS_THICKNESS,
    }


def _subtract_terminal_and_taper(hfss, throat_geom):
    tools = []

    terminal_start_y = throat_geom["h_throat_end_y"]
    depth = 0.5 * (B - G2)
    top = _box(
        hfss,
        [-H_TERMINAL_RIDGE_W / 2.0, terminal_start_y, G2 / 2.0],
        [H_TERMINAL_RIDGE_W, TERMINAL_RIDGE_LEN, depth],
        "RidgeTop_terminal",
        material="pec",
    )
    bot = _box(
        hfss,
        [-H_TERMINAL_RIDGE_W / 2.0, terminal_start_y, -B / 2.0],
        [H_TERMINAL_RIDGE_W, TERMINAL_RIDGE_LEN, depth],
        "RidgeBot_terminal",
        material="pec",
    )
    tools.extend([top.name, bot.name])

    taper_start_y = terminal_start_y + TERMINAL_RIDGE_LEN
    ds = TAPER_TOTAL / float(N_TAPER_SEGMENTS)
    for i in range(N_TAPER_SEGMENTS):
        s0 = i * ds
        s1 = (i + 1) * ds
        smid = 0.5 * (s0 + s1)
        # s=0 is near the tee; reverse the old port-distance definition.
        gap = taper_gap_from_port_distance(TAPER_TOTAL - smid)
        ridge_depth = max(0.0, 0.5 * (B - gap))
        if ridge_depth <= 1e-6:
            continue

        y0 = taper_start_y + s0
        dy = s1 - s0
        top = _box(
            hfss,
            [-RIDGE_W / 2.0, y0, gap / 2.0],
            [RIDGE_W, dy, ridge_depth],
            "RidgeTop_%02d" % i,
            material="pec",
        )
        bot = _box(
            hfss,
            [-RIDGE_W / 2.0, y0, -B / 2.0],
            [RIDGE_W, dy, ridge_depth],
            "RidgeBot_%02d" % i,
            material="pec",
        )
        tools.extend([top.name, bot.name])

    hfss.modeler.subtract("AirWG", tools, keep_originals=False)

    taper_end_y = taper_start_y + TAPER_TOTAL
    tuner_start_y = taper_end_y
    h_port_y = (
        tuner_start_y
        + TUNER_SECTION_LEN
        + PORT_STRAIGHT_LEN
    )

    expected_port_y = A / 2.0 + H_ARM_ACTIVE_LEN
    if abs(h_port_y - expected_port_y) > 1e-6:
        raise RuntimeError("H-arm longitudinal layout bookkeeping error")

    return {
        "terminal_start_y": terminal_start_y,
        "taper_start_y": taper_start_y,
        "taper_end_y": taper_end_y,
        "tuner_start_y": tuner_start_y,
        "h_port_y": h_port_y,
    }


def _subtract_three_screws(hfss, geom):
    tuner_start_y = geom["tuner_start_y"]
    rel = [SCREW_Z1, SCREW_Z2, SCREW_Z3]
    pen = [SCREW_P1, SCREW_P2, SCREW_P3]
    names = []

    for i, (zrel, p) in enumerate(zip(rel, pen), start=1):
        if p <= 1e-9:
            continue
        y = tuner_start_y + SCREW_TUNER_OFFSET + zrel
        obj = _cylinder(
            hfss,
            [0.0, y, B / 2.0 - p],
            SCREW_RADIUS,
            p,
            "TuneScrew_%d" % i,
        )
        names.append(obj.name)

    if names:
        hfss.modeler.subtract("AirWG", names, keep_originals=False)


def _port_face(hfss, position):
    face_id = hfss.modeler.get_faceid_from_position(position, assignment="AirWG")
    if face_id is None or face_id < 0:
        raise RuntimeError("Could not find port face at %r" % (position,))
    return face_id


def _assign_ports_and_walls(hfss, geom):
    h_port_y = geom["h_port_y"]
    e_port_z = B / 2.0 + E_ARM_LEN

    f1 = _port_face(hfss, [-COLLINEAR_HALF_LEN, 0.0, 0.0])
    f2 = _port_face(hfss, [COLLINEAR_HALF_LEN, 0.0, 0.0])
    f3 = _port_face(hfss, [0.0, h_port_y, 0.0])
    f4 = _port_face(hfss, [0.0, 0.0, e_port_z])
    port_faces = {f1, f2, f3, f4}

    zline_1 = [
        [-COLLINEAR_HALF_LEN, 0.0, -B / 2.0],
        [-COLLINEAR_HALF_LEN, 0.0, B / 2.0],
    ]
    zline_2 = [
        [COLLINEAR_HALF_LEN, 0.0, -B / 2.0],
        [COLLINEAR_HALF_LEN, 0.0, B / 2.0],
    ]
    zline_3 = [
        [0.0, h_port_y, -B / 2.0],
        [0.0, h_port_y, B / 2.0],
    ]
    xline_4 = [
        [-B / 2.0, 0.0, e_port_z],
        [B / 2.0, 0.0, e_port_z],
    ]

    hfss.wave_port(
        f1,
        integration_line=zline_1,
        modes=1,
        name="P1_CollinearMinusX",
        renormalize=False,
        characteristic_impedance="Zwave",
    )
    hfss.wave_port(
        f2,
        integration_line=zline_2,
        modes=1,
        name="P2_CollinearPlusX",
        renormalize=False,
        characteristic_impedance="Zwave",
    )
    hfss.wave_port(
        f3,
        integration_line=zline_3,
        modes=1,
        name="P3_HArm_v4",
        renormalize=False,
        characteristic_impedance="Zwave",
    )
    hfss.wave_port(
        f4,
        integration_line=xline_4,
        modes=1,
        name="P4_EArm",
        renormalize=False,
        characteristic_impedance="Zwave",
    )

    air = hfss.modeler["AirWG"]
    wall_faces = [face.id for face in air.faces if face.id not in port_faces]
    hfss.assign_perfect_e(wall_faces, name="PEC_WaveguideWalls")


def _create_setup(hfss):
    setup = hfss.create_setup("Setup1")
    setup.props["Frequency"] = "%gGHz" % F_ADAPT_GHZ
    setup.props["MaximumPasses"] = 8
    setup.props["MinimumPasses"] = 2
    setup.props["MinimumConvergedPasses"] = 1
    setup.props["MaxDeltaS"] = 0.02
    setup.update()

    try:
        sweep = hfss.create_linear_count_sweep(
            setup=setup.name,
            unit="GHz",
            start_frequency=F_START_GHZ,
            stop_frequency=F_STOP_GHZ,
            num_of_freq_points=N_SWEEP,
            name="Sweep_9_11p5GHz",
            sweep_type="Interpolating",
            interpolation_tol=0.5,
            save_fields=False,
        )
    except Exception:
        sweep = setup.add_sweep("Sweep_9_11p5GHz", "Interpolating")
        sweep.props["RangeType"] = "LinearCount"
        sweep.props["RangeStart"] = "%gGHz" % F_START_GHZ
        sweep.props["RangeEnd"] = "%gGHz" % F_STOP_GHZ
        sweep.props["RangeCount"] = N_SWEEP
        sweep.props["SaveFields"] = False
        sweep.update()

    return setup, sweep


def _write_touchstone_from_solution_data(hfss, setup_name, sweep_name, output_file):
    """Write MA Touchstone directly from PyAEDT SolutionData.

    AEDT 2025.2SV can solve and expose sweep data through the report API while
    its ExportNetworkData macro still reports the sweep as unavailable.  The
    report API provides the same complex S-parameter samples, so serialize
    those samples locally and keep the matrix ordering explicit.
    """
    expressions = [f"S({row},{col})" for row in range(1, 5) for col in range(1, 5)]
    data = hfss.post.get_solution_data(
        expressions=expressions,
        setup_sweep_name=f"{setup_name} : {sweep_name}",
    )
    if not data:
        raise RuntimeError("HFSS returned no SolutionData for the solved sweep")

    frequencies, _ = data.get_expression_data(expressions[0], formula="real")
    real_parts = {}
    imag_parts = {}
    for expression in expressions:
        freq_real, real = data.get_expression_data(expression, formula="real")
        freq_imag, imag = data.get_expression_data(expression, formula="imag")
        if len(freq_real) != len(frequencies) or len(freq_imag) != len(frequencies):
            raise RuntimeError(f"Unexpected frequency count for {expression}")
        real_parts[expression] = real
        imag_parts[expression] = imag

    lines = [
        "! Generated from PyAEDT SolutionData; AEDT ExportNetworkData workaround",
        "# GHz S MA R 50",
    ]
    for index, frequency in enumerate(frequencies):
        values = [f"{float(frequency):.12g}"]
        for expression in expressions:
            z_real = float(real_parts[expression][index])
            z_imag = float(imag_parts[expression][index])
            values.extend([
                f"{math.hypot(z_real, z_imag):.12g}",
                f"{math.degrees(math.atan2(z_imag, z_real)):.12g}",
            ])
        lines.append(" ".join(values))

    Path(output_file).write_text("\n".join(lines) + "\n", encoding="ascii")
    return output_file


def _define_design_variables(hfss):
    vals = {
        "wg_a": "%gmm" % A,
        "wg_b": "%gmm" % B,
        "post_radius": "%gmm" % POST_RADIUS,
        "post_height": "%gmm" % POST_HEIGHT,
        "post_y": "%gmm" % POST_Y,
        "center_post_radius": "%gmm" % CENTER_POST_RADIUS,
        "center_post_height": "%gmm" % CENTER_POST_HEIGHT,
        "junction_pair_radius": "%gmm" % JUNCTION_PAIR_RADIUS,
        "junction_pair_height": "%gmm" % JUNCTION_PAIR_HEIGHT,
        "h_throat_a": "%gmm" % H_THROAT_A,
        "h_throat_len": "%gmm" % H_THROAT_LEN,
        "h_throat2_a": "%gmm" % H_THROAT2_A,
        "h_throat2_len": "%gmm" % H_THROAT2_LEN,
        "h_iris_open": "%gmm" % H_IRIS_OPEN,
        "h_iris_thickness": "%gmm" % H_IRIS_THICKNESS,
        "h_iris_offset": "%gmm" % H_IRIS_OFFSET,
        "e_step_b": "%gmm" % E_STEP_B,
        "e_step_len": "%gmm" % E_STEP_LEN,
        "ridge_w": "%gmm" % RIDGE_W,
        "ridge_g1": "%gmm" % G1,
        "ridge_l1": "%gmm" % L1,
        "ridge_g2": "%gmm" % G2,
        "ridge_l2": "%gmm" % L2,
        "terminal_ridge_w": "%gmm" % H_TERMINAL_RIDGE_W,
        "terminal_ridge_len": "%gmm" % TERMINAL_RIDGE_LEN,
        "screw_radius": "%gmm" % SCREW_RADIUS,
        "screw_p1": "%gmm" % SCREW_P1,
        "screw_p2": "%gmm" % SCREW_P2,
        "screw_p3": "%gmm" % SCREW_P3,
        "screw_z1": "%gmm" % SCREW_Z1,
        "screw_z2": "%gmm" % SCREW_Z2,
        "screw_z3": "%gmm" % SCREW_Z3,
        "f_adapt": "%gGHz" % F_ADAPT_GHZ,
    }
    for key, value in vals.items():
        try:
            hfss[key] = value
        except Exception:
            pass


def _apply_args(args):
    global RIDGE_W, G1, L1, G2, L2
    global POST_RADIUS, POST_HEIGHT, POST_Y, CENTER_POST_RADIUS, CENTER_POST_HEIGHT
    global JUNCTION_PAIR_RADIUS, JUNCTION_PAIR_HEIGHT
    global H_THROAT_A, H_THROAT_LEN, H_THROAT2_A, H_THROAT2_LEN
    global H_IRIS_OPEN, H_IRIS_THICKNESS, H_IRIS_OFFSET
    global E_STEP_B, E_STEP_LEN
    global H_TERMINAL_RIDGE_W, TERMINAL_RIDGE_LEN
    global SCREW_RADIUS, SCREW_Z1, SCREW_Z2, SCREW_Z3
    global SCREW_P1, SCREW_P2, SCREW_P3
    global TAPER_TOTAL, H_ARM_ACTIVE_LEN

    RIDGE_W = args.ridge_w
    G1 = args.g1
    L1 = args.l1
    G2 = args.g2
    L2 = args.l2

    POST_RADIUS = args.post_radius
    POST_HEIGHT = args.post_height
    POST_Y = args.post_y
    CENTER_POST_RADIUS = args.center_post_radius
    CENTER_POST_HEIGHT = args.center_post_height
    JUNCTION_PAIR_RADIUS = args.junction_pair_radius
    JUNCTION_PAIR_HEIGHT = args.junction_pair_height

    H_THROAT_A = args.h_throat_a
    H_THROAT_LEN = args.h_throat_len
    H_THROAT2_A = args.h_throat2_a
    H_THROAT2_LEN = args.h_throat2_len
    H_IRIS_OPEN = args.h_iris_open
    H_IRIS_THICKNESS = args.h_iris_thickness
    H_IRIS_OFFSET = args.h_iris_offset
    E_STEP_B = args.e_step_b
    E_STEP_LEN = args.e_step_len
    H_TERMINAL_RIDGE_W = args.h_terminal_ridge_w
    TERMINAL_RIDGE_LEN = args.terminal_ridge_len

    SCREW_RADIUS = args.screw_radius
    SCREW_Z1 = args.screw_z1
    SCREW_Z2 = args.screw_z2
    SCREW_Z3 = args.screw_z3
    SCREW_P1 = args.screw_p1
    SCREW_P2 = args.screw_p2
    SCREW_P3 = args.screw_p3

    TAPER_TOTAL = L1 + L2
    H_ARM_ACTIVE_LEN = (
        H_THROAT_LEN
        + H_THROAT2_LEN
        + TERMINAL_RIDGE_LEN
        + TAPER_TOTAL
        + TUNER_SECTION_LEN
        + PORT_STRAIGHT_LEN
    )
    _validate_geometry()


def build(args):
    _apply_args(args)

    outdir = Path(args.output).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    project_path = outdir / "single_magictee_v4_full.aedt"

    hfss = _launch_hfss(str(project_path), args.version, args.non_graphical)
    hfss.modeler.model_units = "mm"

    _define_design_variables(hfss)
    _make_air_volume(hfss)
    e_step = _subtract_e_step(hfss)
    throat = _subtract_h_width_throat(hfss)
    center_post = _subtract_center_post(hfss)
    junction_pair = _subtract_junction_pair(hfss)
    post = _subtract_local_post_pair(hfss)
    iris = _subtract_h_iris(hfss)
    geom = _subtract_terminal_and_taper(hfss, throat)
    geom.update(post)
    geom.update(center_post)
    geom.update(junction_pair)
    geom.update(iris)
    geom.update(e_step)
    _subtract_three_screws(hfss, geom)

    _assign_ports_and_walls(hfss, geom)
    setup, _ = _create_setup(hfss)

    hfss.modeler.fit_all()
    hfss.save_project(str(project_path))

    print("Built:", project_path)
    print("Design: SingleMagicT_v4_Full")
    print("Sweep: %.2f--%.2f GHz, %d points" % (F_START_GHZ, F_STOP_GHZ, N_SWEEP))
    print("J0 post pair: radius/height/y = %.3f / %.3f / %.3f mm" % (
        POST_RADIUS, POST_HEIGHT, POST_Y
    ))
    if CENTER_POST_HEIGHT > 0.0:
        print("J0 center post radius/height = %.3f / %.3f mm" % (
            CENTER_POST_RADIUS, CENTER_POST_HEIGHT
        ))
    if JUNCTION_PAIR_HEIGHT > 0.0:
        print("J0 junction pair radius/height = %.3f / %.3f mm" % (
            JUNCTION_PAIR_RADIUS, JUNCTION_PAIR_HEIGHT
        ))
    print("J1 throat a/L = %.3f / %.3f mm" % (H_THROAT_A, H_THROAT_LEN))
    if H_THROAT2_LEN > 0.0:
        print("J1b throat2 a/L = %.3f / %.3f mm" % (H_THROAT2_A, H_THROAT2_LEN))
    if H_IRIS_OPEN > 0.0:
        print("J1 iris open/thickness/offset = %.3f / %.3f / %.3f mm" % (
            H_IRIS_OPEN, H_IRIS_THICKNESS, H_IRIS_OFFSET
        ))
    print("J2 terminal ridge w/g/L = %.3f / %.3f / %.3f mm" % (
        H_TERMINAL_RIDGE_W, G2, TERMINAL_RIDGE_LEN
    ))
    print("J3 taper g1/L1 -> g2/L2 = %.3f/%.3f -> %.3f/%.3f mm" % (
        G1, L1, G2, L2
    ))
    print("J4 screws z = %.3f, %.3f, %.3f mm; p = %.3f, %.3f, %.3f mm" % (
        SCREW_Z1, SCREW_Z2, SCREW_Z3, SCREW_P1, SCREW_P2, SCREW_P3
    ))
    print("E arm: v2 parity-correct orientation retained")

    if args.solve:
        hfss.analyze_setup(setup.name)
        # A second Analyze call is required by AEDT 2025.2SV in this
        # WSL/Windows configuration to materialize the interpolating sweep
        # in SolutionData after the adaptive solution has converged.
        hfss.analyze_setup(setup.name)
        touchstone = outdir / "single_magictee_v4_full.s4p"
        try:
            result = _write_touchstone_from_solution_data(
                hfss,
                setup_name=setup.name,
                sweep_name="Sweep_9_11p5GHz",
                output_file=str(touchstone),
            )
            print("Touchstone:", result)
        except Exception as exc:
            print("SolutionData Touchstone export failed:", exc)
            try:
                result = hfss.export_touchstone(
                    setup=setup.name,
                    sweep="Sweep_9_11p5GHz",
                    output_file=str(touchstone),
                )
                print("Touchstone:", result)
            except Exception as fallback_exc:
                print("Touchstone export failed:", fallback_exc)
        hfss.save_project(str(project_path))
    else:
        print("Build-only mode. Inspect v4 geometry before using --solve.")

    try:
        hfss.release_desktop()
    except Exception as exc:
        print("AEDT release warning:", exc)

    return hfss


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--version", default="2022.2")
    p.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parent / "output_v4_full"),
    )
    p.add_argument("--solve", action="store_true")
    p.add_argument("--non-graphical", action="store_true")

    p.add_argument("--post-radius", type=float, default=POST_RADIUS)
    p.add_argument("--post-height", type=float, default=POST_HEIGHT)
    p.add_argument("--post-y", type=float, default=POST_Y)
    p.add_argument("--center-post-radius", type=float, default=CENTER_POST_RADIUS)
    p.add_argument("--center-post-height", type=float, default=CENTER_POST_HEIGHT)
    p.add_argument("--junction-pair-radius", type=float, default=JUNCTION_PAIR_RADIUS)
    p.add_argument("--junction-pair-height", type=float, default=JUNCTION_PAIR_HEIGHT)

    p.add_argument("--h-throat-a", type=float, default=H_THROAT_A)
    p.add_argument("--h-throat-len", type=float, default=H_THROAT_LEN)
    p.add_argument("--h-throat2-a", type=float, default=H_THROAT2_A)
    p.add_argument("--h-throat2-len", type=float, default=H_THROAT2_LEN)
    p.add_argument("--h-iris-open", type=float, default=H_IRIS_OPEN)
    p.add_argument("--h-iris-thickness", type=float, default=H_IRIS_THICKNESS)
    p.add_argument("--h-iris-offset", type=float, default=H_IRIS_OFFSET)
    p.add_argument("--e-step-b", type=float, default=E_STEP_B)
    p.add_argument("--e-step-len", type=float, default=E_STEP_LEN)
    p.add_argument("--h-terminal-ridge-w", type=float, default=H_TERMINAL_RIDGE_W)
    p.add_argument("--terminal-ridge-len", type=float, default=TERMINAL_RIDGE_LEN)

    p.add_argument("--ridge-w", type=float, default=RIDGE_W)
    p.add_argument("--g1", type=float, default=G1)
    p.add_argument("--l1", type=float, default=L1)
    p.add_argument("--g2", type=float, default=G2)
    p.add_argument("--l2", type=float, default=L2)

    p.add_argument("--screw-radius", type=float, default=SCREW_RADIUS)
    p.add_argument("--screw-z1", type=float, default=SCREW_Z1)
    p.add_argument("--screw-z2", type=float, default=SCREW_Z2)
    p.add_argument("--screw-z3", type=float, default=SCREW_Z3)
    p.add_argument("--screw-p1", type=float, default=SCREW_P1)
    p.add_argument("--screw-p2", type=float, default=SCREW_P2)
    p.add_argument("--screw-p3", type=float, default=SCREW_P3)
    return p.parse_args()


if __name__ == "__main__":
    build(parse_args())
