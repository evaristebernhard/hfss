#!/usr/bin/env python3
"""
HFSS / PyAEDT single magic-tee v3.4 H-block builder.

Topology (from the H-plane tee mouth outward):

    tee
      -> mild reduced-width H-plane throat
      -> short symmetric reduced-height capacitive cell
      -> terminal double ridge
      -> existing two-section ridge taper
      -> straight WR90 H port

The E arm remains the v2 parity-corrected WR90 orientation. This builder is
intended for the first v3.4 structural/Jacobian study. It is not a final
high-power-qualified geometry.

Default mode is build-only. Add --solve to run the 9.0--11.5 GHz sweep and
export a 4-port Touchstone file.
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

H_THROAT_A = 20.40
H_THROAT_LEN = 5.50
H_CAP_HEIGHT = 9.00
H_CAP_LEN = 2.50
H_TERMINAL_RIDGE_W = 4.572
TERMINAL_RIDGE_LEN = 7.50

PORT_STRAIGHT_LEN = 10.0
COLLINEAR_HALF_LEN = 35.0
E_ARM_LEN = 30.0
N_TAPER_SEGMENTS = 20

F_ADAPT_GHZ = 10.20
F_START_GHZ = 9.0
F_STOP_GHZ = 11.5
N_SWEEP = 101

TAPER_TOTAL = L1 + L2
H_ARM_ACTIVE_LEN = (
    PORT_STRAIGHT_LEN
    + TAPER_TOTAL
    + TERMINAL_RIDGE_LEN
    + H_CAP_LEN
    + H_THROAT_LEN
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
            design="SingleMagicT_v3_4_HReactiveCell",
            version=version,
            solution_type="Modal",
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=True,
        )
    return Hfss(
        projectname=project_path,
        designname="SingleMagicT_v3_4_HReactiveCell",
        specified_version=version,
        solution_type="DrivenModal",
        non_graphical=non_graphical,
        new_desktop_session=True,
    )


def _box(hfss, origin, sizes, name, material="vacuum"):
    return hfss.modeler.create_box(origin, sizes, name=name, material=material)


def _validate_geometry():
    if not (0.0 < H_THROAT_A <= A):
        raise ValueError("h_throat_a must satisfy 0 < h_throat_a <= WR90 broad dimension")
    if not (0.0 < H_CAP_HEIGHT <= B):
        raise ValueError("h_cap_height must satisfy 0 < h_cap_height <= WR90 narrow dimension")
    if H_THROAT_LEN < 0.0 or H_CAP_LEN < 0.0 or TERMINAL_RIDGE_LEN < 0.0:
        raise ValueError("local section lengths must be non-negative")
    if not (0.0 < G2 <= B and 0.0 < G1 <= B):
        raise ValueError("ridge gaps must lie inside the WR90 narrow dimension")
    if H_TERMINAL_RIDGE_W <= 0.0 or H_TERMINAL_RIDGE_W > A:
        raise ValueError("terminal ridge width must satisfy 0 < width <= WR90 broad dimension")


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


def _subtract_h_width_throat(hfss):
    side_depth = 0.5 * (A - H_THROAT_A)
    y0 = A / 2.0
    if side_depth <= 1e-9 or H_THROAT_LEN <= 1e-9:
        return {
            "h_throat_start_y": y0,
            "h_throat_end_y": y0 + H_THROAT_LEN,
            "h_throat_side_depth": max(side_depth, 0.0),
        }

    left = _box(
        hfss,
        [-A / 2.0, y0, -B / 2.0],
        [side_depth, H_THROAT_LEN, B],
        "HThroatWall_Left",
        material="pec",
    )
    right = _box(
        hfss,
        [H_THROAT_A / 2.0, y0, -B / 2.0],
        [side_depth, H_THROAT_LEN, B],
        "HThroatWall_Right",
        material="pec",
    )
    hfss.modeler.subtract("AirWG", [left.name, right.name], keep_originals=False)

    return {
        "h_throat_start_y": y0,
        "h_throat_end_y": y0 + H_THROAT_LEN,
        "h_throat_side_depth": side_depth,
    }


def _subtract_h_capacitive_cell(hfss, throat_geom):
    depth = 0.5 * (B - H_CAP_HEIGHT)
    y0 = throat_geom["h_throat_end_y"]

    if depth <= 1e-9 or H_CAP_LEN <= 1e-9:
        return {
            "h_cap_start_y": y0,
            "h_cap_end_y": y0 + H_CAP_LEN,
            "h_cap_wall_depth": max(depth, 0.0),
        }

    top = _box(
        hfss,
        [-A / 2.0, y0, H_CAP_HEIGHT / 2.0],
        [A, H_CAP_LEN, depth],
        "HCapCell_Top",
        material="pec",
    )
    bot = _box(
        hfss,
        [-A / 2.0, y0, -B / 2.0],
        [A, H_CAP_LEN, depth],
        "HCapCell_Bottom",
        material="pec",
    )
    hfss.modeler.subtract("AirWG", [top.name, bot.name], keep_originals=False)

    return {
        "h_cap_start_y": y0,
        "h_cap_end_y": y0 + H_CAP_LEN,
        "h_cap_wall_depth": depth,
    }


def _subtract_double_ridge_taper(hfss, cap_geom):
    h_port_y = A / 2.0 + H_ARM_ACTIVE_LEN
    tools = []
    ds = TAPER_TOTAL / float(N_TAPER_SEGMENTS)

    for i in range(N_TAPER_SEGMENTS):
        s0 = i * ds
        s1 = (i + 1) * ds
        gap = taper_gap_from_port_distance(0.5 * (s0 + s1))
        depth = max(0.0, 0.5 * (B - gap))
        if depth <= 1e-6:
            continue

        y0 = h_port_y - PORT_STRAIGHT_LEN - s1
        dy = s1 - s0
        top = _box(
            hfss,
            [-RIDGE_W / 2.0, y0, gap / 2.0],
            [RIDGE_W, dy, depth],
            "RidgeTop_%02d" % i,
            material="pec",
        )
        bot = _box(
            hfss,
            [-RIDGE_W / 2.0, y0, -B / 2.0],
            [RIDGE_W, dy, depth],
            "RidgeBot_%02d" % i,
            material="pec",
        )
        tools.extend([top.name, bot.name])

    gap = G2
    depth = 0.5 * (B - gap)
    y0 = cap_geom["h_cap_end_y"]

    top = _box(
        hfss,
        [-H_TERMINAL_RIDGE_W / 2.0, y0, gap / 2.0],
        [H_TERMINAL_RIDGE_W, TERMINAL_RIDGE_LEN, depth],
        "RidgeTop_terminal",
        material="pec",
    )
    bot = _box(
        hfss,
        [-H_TERMINAL_RIDGE_W / 2.0, y0, -B / 2.0],
        [H_TERMINAL_RIDGE_W, TERMINAL_RIDGE_LEN, depth],
        "RidgeBot_terminal",
        material="pec",
    )
    tools.extend([top.name, bot.name])
    hfss.modeler.subtract("AirWG", tools, keep_originals=False)

    taper_near_tee_y = h_port_y - PORT_STRAIGHT_LEN - TAPER_TOTAL
    terminal_end_y = y0 + TERMINAL_RIDGE_LEN

    if abs(terminal_end_y - taper_near_tee_y) > 1e-6:
        raise RuntimeError(
            "H-arm layout discontinuity: terminal ridge ends at %.6f mm, "
            "taper starts at %.6f mm" % (terminal_end_y, taper_near_tee_y)
        )

    return {
        "h_port_y": h_port_y,
        "terminal_start_y": y0,
        "terminal_end_y": terminal_end_y,
        "taper_near_tee_y": taper_near_tee_y,
    }


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
        name="P3_HArm_Ridged",
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


def _define_design_variables(hfss):
    vals = {
        "wg_a": "%gmm" % A,
        "wg_b": "%gmm" % B,
        "ridge_w": "%gmm" % RIDGE_W,
        "ridge_g1": "%gmm" % G1,
        "ridge_l1": "%gmm" % L1,
        "ridge_g2": "%gmm" % G2,
        "ridge_l2": "%gmm" % L2,
        "terminal_ridge_len": "%gmm" % TERMINAL_RIDGE_LEN,
        "h_throat_a": "%gmm" % H_THROAT_A,
        "h_throat_len": "%gmm" % H_THROAT_LEN,
        "h_cap_height": "%gmm" % H_CAP_HEIGHT,
        "h_cap_len": "%gmm" % H_CAP_LEN,
        "h_terminal_ridge_w": "%gmm" % H_TERMINAL_RIDGE_W,
        "f_adapt": "%gGHz" % F_ADAPT_GHZ,
    }
    for key, value in vals.items():
        try:
            hfss[key] = value
        except Exception:
            pass


def _apply_args(args):
    global RIDGE_W, G1, L1, G2, L2
    global TERMINAL_RIDGE_LEN, H_THROAT_A, H_THROAT_LEN
    global H_CAP_HEIGHT, H_CAP_LEN, H_TERMINAL_RIDGE_W
    global TAPER_TOTAL, H_ARM_ACTIVE_LEN

    RIDGE_W = args.ridge_w
    G1 = args.g1
    L1 = args.l1
    G2 = args.g2
    L2 = args.l2
    TERMINAL_RIDGE_LEN = args.terminal_ridge_len
    H_THROAT_A = args.h_throat_a
    H_THROAT_LEN = args.h_throat_len
    H_CAP_HEIGHT = args.h_cap_height
    H_CAP_LEN = args.h_cap_len
    H_TERMINAL_RIDGE_W = args.h_terminal_ridge_w

    TAPER_TOTAL = L1 + L2
    H_ARM_ACTIVE_LEN = (
        PORT_STRAIGHT_LEN
        + TAPER_TOTAL
        + TERMINAL_RIDGE_LEN
        + H_CAP_LEN
        + H_THROAT_LEN
    )
    _validate_geometry()


def build(args):
    _apply_args(args)

    outdir = Path(args.output).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    project_path = outdir / "single_magictee_v3_4_hreactive.aedt"

    hfss = _launch_hfss(str(project_path), args.version, args.non_graphical)
    hfss.modeler.model_units = "mm"

    _define_design_variables(hfss)
    _make_air_volume(hfss)

    throat = _subtract_h_width_throat(hfss)
    cap = _subtract_h_capacitive_cell(hfss, throat)
    geom = _subtract_double_ridge_taper(hfss, cap)
    geom.update(throat)
    geom.update(cap)

    _assign_ports_and_walls(hfss, geom)
    setup, _ = _create_setup(hfss)

    hfss.modeler.fit_all()
    hfss.save_project(str(project_path))

    print("Built:", project_path)
    print("Design: SingleMagicT_v3_4_HReactiveCell")
    print("Sweep: %.2f--%.2f GHz, %d points" % (F_START_GHZ, F_STOP_GHZ, N_SWEEP))
    print("H topology:")
    print("  throat a/L = %.3f / %.3f mm" % (H_THROAT_A, H_THROAT_LEN))
    print("  capacitive cell b/L = %.3f / %.3f mm" % (H_CAP_HEIGHT, H_CAP_LEN))
    print(
        "  terminal ridge w/g/L = %.3f / %.3f / %.3f mm"
        % (H_TERMINAL_RIDGE_W, G2, TERMINAL_RIDGE_LEN)
    )
    print("  upstream taper w = %.3f mm" % RIDGE_W)
    print("  upstream taper g1/L1 = %.3f / %.3f mm" % (G1, L1))
    print("  upstream taper g2/L2 = %.3f / %.3f mm" % (G2, L2))
    print("E arm: v2 parity-corrected orientation retained")

    if args.solve:
        print("Solving HFSS...")
        hfss.analyze_setup(setup.name)
        touchstone = outdir / "single_magictee_v3_4_hreactive.s4p"
        try:
            result = hfss.export_touchstone(
                setup=setup.name,
                sweep="Sweep_9_11p5GHz",
                output_file=str(touchstone),
            )
            print("Touchstone:", result)
        except Exception as exc:
            print("Touchstone export failed:", exc)
        hfss.save_project(str(project_path))
    else:
        print("Build-only mode. Inspect geometry before using --solve.")

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
        default=str(Path(__file__).resolve().parent / "output_v3_4_hreactive"),
    )
    p.add_argument("--solve", action="store_true")
    p.add_argument("--non-graphical", action="store_true")

    p.add_argument("--ridge-w", type=float, default=RIDGE_W)
    p.add_argument("--g1", type=float, default=G1)
    p.add_argument("--l1", type=float, default=L1)
    p.add_argument("--g2", type=float, default=G2)
    p.add_argument("--l2", type=float, default=L2)

    p.add_argument("--terminal-ridge-len", type=float, default=TERMINAL_RIDGE_LEN)
    p.add_argument("--h-throat-a", type=float, default=H_THROAT_A)
    p.add_argument("--h-throat-len", type=float, default=H_THROAT_LEN)
    p.add_argument("--h-cap-height", type=float, default=H_CAP_HEIGHT)
    p.add_argument("--h-cap-len", type=float, default=H_CAP_LEN)
    p.add_argument("--h-terminal-ridge-w", type=float, default=H_TERMINAL_RIDGE_W)
    return p.parse_args()


if __name__ == "__main__":
    build(parse_args())
