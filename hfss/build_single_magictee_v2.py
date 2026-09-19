#!/usr/bin/env python3
"""
HFSS 2022 / PyAEDT rough v2 builder.

Builds a deliberately simple first full-wave model:

    WR90 collinear arm
        +
    H-plane side arm containing the current double-ridge taper seed
        +
    E-plane side arm

The three air-filled waveguide volumes are united into one four-port
magic-tee-like junction.  The ridges are represented as PEC intrusions by
subtracting them from the air region.  All non-port air-region faces receive
Perfect-E boundaries.

This is NOT a production magic-tee geometry.  It is the first parameterized
HFSS model used to validate:
    - port orientation,
    - 9--11.5 GHz sweep,
    - Sigma/Delta mixed-mode post-processing,
    - current ridge dimensions,
    - junction/ridge interaction.

The model defaults to BUILD-ONLY.  Use --solve to run HFSS and export S4P.

PyAEDT supports AEDT 2022 R1 and later.  This script tries both the modern
ansys.aedt.core import and the older pyaedt import path.

Examples
--------
Build only, GUI:
    python build_single_magictee_v2.py

Build + solve:
    python build_single_magictee_v2.py --solve

Target 2022 R1 instead of 2022 R2:
    python build_single_magictee_v2.py --version 2022.1
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Current reduced-model seed
# ---------------------------------------------------------------------------

A = 22.86      # WR90 broad dimension [mm]
B = 10.16      # WR90 narrow dimension [mm]

RIDGE_W = 4.572
G1 = 7.672
L1 = 9.872
G2 = 4.984
L2 = 8.857

TAPER_TOTAL = L1 + L2          # 18.729 mm
TERMINAL_RIDGE_LEN = 6.0       # short g2 section before the junction
PORT_STRAIGHT_LEN = 10.0       # un-ridged WR90 section before the H-port
H_ARM_ACTIVE_LEN = PORT_STRAIGHT_LEN + TAPER_TOTAL + TERMINAL_RIDGE_LEN

# Straight collinear arms measured from the junction center.
COLLINEAR_HALF_LEN = 35.0

# E-arm straight extension from the broad wall.
E_ARM_LEN = 30.0

# Stair-step approximation to the longitudinal ridge taper.
N_TAPER_SEGMENTS = 20

F_ADAPT_GHZ = 10.20
F_START_GHZ = 9.0
F_STOP_GHZ = 11.5
N_SWEEP = 101


def smoothstep(t: float) -> float:
    return 3.0 * t * t - 2.0 * t * t * t


def log_interp(a: float, b: float, t: float) -> float:
    s = smoothstep(t)
    return math.exp((1.0 - s) * math.log(a) + s * math.log(b))


def taper_gap_from_port_distance(s_mm: float) -> float:
    """
    Provisional geometry map used by v1.

    s=0 is the first taper station after the ordinary WR90 port extension.
    s=TAPER_TOTAL is the g2 end nearest the tee.

    Section 1 maps B -> G1; section 2 maps G1 -> G2.
    """
    if s_mm <= 0.0:
        return B
    if s_mm >= TAPER_TOTAL:
        return G2

    if s_mm <= L1:
        t = s_mm / L1
        # v1 proxy: interpolate log(g), not a rigorous inverse Cohn map.
        return log_interp(B, G1, t)

    t = (s_mm - L1) / L2
    return log_interp(G1, G2, t)


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
            design="SingleMagicT_v2",
            version=version,
            solution_type="Modal",
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=True,
        )

    # Compatibility path for older PyAEDT releases.
    return Hfss(
        projectname=project_path,
        designname="SingleMagicT_v2",
        specified_version=version,
        solution_type="DrivenModal",
        non_graphical=non_graphical,
        new_desktop_session=True,
    )


def _box(hfss, origin, sizes, name, material="vacuum"):
    return hfss.modeler.create_box(
        origin,
        sizes,
        name=name,
        material=material,
    )


def _make_air_volume(hfss):
    """
    Coordinate convention
    ---------------------
    X: collinear propagation axis.
    Y: H-arm propagation axis.
    Z: E-arm propagation axis.

    Collinear WR90 cross-section:
        broad dimension A along Y,
        narrow dimension B along Z.

    H arm:
        broad dimension A along X,
        narrow dimension B along Z.

    E arm:
        narrow dimension B along X,
        broad dimension A along Y.

    This 90-degree rotation relative to v1 gives the Z-propagating TE10
    mode an X-directed electric field, which has the odd vector parity needed
    to couple to the antisymmetric collinear mode c-.
    """

    # Main collinear guide.
    _box(
        hfss,
        [-COLLINEAR_HALF_LEN, -A / 2.0, -B / 2.0],
        [2.0 * COLLINEAR_HALF_LEN, A, B],
        "AirWG",
    )

    # H-arm starts at the collinear narrow side wall y=+A/2.
    h_y0 = A / 2.0
    _box(
        hfss,
        [-A / 2.0, h_y0, -B / 2.0],
        [A, H_ARM_ACTIVE_LEN, B],
        "HArmAir",
    )

    # E-arm starts at the collinear broad wall z=+B/2.
    e_z0 = B / 2.0
    _box(
        hfss,
        [-B / 2.0, -A / 2.0, e_z0],
        [B, A, E_ARM_LEN],
        "EArmAir",
    )

    hfss.modeler.unite(["AirWG", "HArmAir", "EArmAir"])
    return hfss.modeler["AirWG"]


def _subtract_double_ridge_taper(hfss):
    """
    Create metal intrusions in the H arm and subtract them from the vacuum
    propagation region.

    The final TERMINAL_RIDGE_LEN section nearest the tee uses g2.  Moving from the H-port
    toward the tee:

        WR90 -> smooth-ish B-to-G1 -> G1-to-G2 -> uniform G2 -> tee.
    """
    h_port_y = A / 2.0 + H_ARM_ACTIVE_LEN
    taper_near_tee_y = h_port_y - PORT_STRAIGHT_LEN - TAPER_TOTAL

    tools = []

    ds = TAPER_TOTAL / float(N_TAPER_SEGMENTS)

    for i in range(N_TAPER_SEGMENTS):
        s0 = i * ds
        s1 = (i + 1) * ds
        smid = 0.5 * (s0 + s1)
        gap = taper_gap_from_port_distance(smid)
        depth = max(0.0, 0.5 * (B - gap))

        if depth <= 1e-6:
            continue

        # y decreases as s increases from the external H port toward the tee.
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

    # Uniform deepest section directly adjacent to the tee.
    gap = G2
    depth = 0.5 * (B - gap)
    y0 = A / 2.0
    dy = TERMINAL_RIDGE_LEN

    top = _box(
        hfss,
        [-RIDGE_W / 2.0, y0, gap / 2.0],
        [RIDGE_W, dy, depth],
        "RidgeTop_terminal",
        material="pec",
    )
    bot = _box(
        hfss,
        [-RIDGE_W / 2.0, y0, -B / 2.0],
        [RIDGE_W, dy, depth],
        "RidgeBot_terminal",
        material="pec",
    )
    tools.extend([top.name, bot.name])

    hfss.modeler.subtract("AirWG", tools, keep_originals=False)

    return {
        "h_port_y": h_port_y,
        "taper_near_tee_y": taper_near_tee_y,
    }


def _port_face(hfss, position):
    face_id = hfss.modeler.get_faceid_from_position(
        position,
        assignment="AirWG",
    )
    if face_id is None or face_id < 0:
        raise RuntimeError("Could not find port face at %r" % (position,))
    return face_id


def _assign_ports_and_walls(hfss, geom):
    h_port_y = geom["h_port_y"]
    e_port_z = B / 2.0 + E_ARM_LEN

    # Face centers.
    p1 = [-COLLINEAR_HALF_LEN, 0.0, 0.0]
    p2 = [COLLINEAR_HALF_LEN, 0.0, 0.0]
    p3 = [0.0, h_port_y, 0.0]
    p4 = [0.0, 0.0, e_port_z]

    f1 = _port_face(hfss, p1)
    f2 = _port_face(hfss, p2)
    f3 = _port_face(hfss, p3)
    f4 = _port_face(hfss, p4)

    port_faces = {f1, f2, f3, f4}

    # Integration lines align the dominant TE10 electric field consistently.
    # X- and Y-propagating arms: E is along Z.
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

    # Z-propagating E arm in v2: broad dimension is Y, so TE10 E is along X.
    # This is the parity-corrected orientation required for c- <-> E coupling.
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

    # PEC on every remaining surface of the air channel.
    air = hfss.modeler["AirWG"]
    wall_faces = [face.id for face in air.faces if face.id not in port_faces]
    hfss.assign_perfect_e(wall_faces, name="PEC_WaveguideWalls")

    return {
        "port_faces": [f1, f2, f3, f4],
        "wall_faces": wall_faces,
    }


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
        # Older PyAEDT fallback.
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
        "f_adapt": "%gGHz" % F_ADAPT_GHZ,
    }
    for key, value in vals.items():
        try:
            hfss[key] = value
        except Exception:
            pass


def build(args):
    global RIDGE_W, G1, L1, G2, L2, TERMINAL_RIDGE_LEN, TAPER_TOTAL, H_ARM_ACTIVE_LEN

    RIDGE_W = args.ridge_w
    G1 = args.g1
    L1 = args.l1
    G2 = args.g2
    L2 = args.l2
    TERMINAL_RIDGE_LEN = args.terminal_ridge_len
    TAPER_TOTAL = L1 + L2
    H_ARM_ACTIVE_LEN = PORT_STRAIGHT_LEN + TAPER_TOTAL + TERMINAL_RIDGE_LEN

    outdir = Path(args.output).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    project_path = outdir / "single_magictee_v2.aedt"

    hfss = _launch_hfss(
        str(project_path),
        args.version,
        args.non_graphical,
    )
    hfss.modeler.model_units = "mm"

    _define_design_variables(hfss)

    _make_air_volume(hfss)
    geom = _subtract_double_ridge_taper(hfss)
    _assign_ports_and_walls(hfss, geom)
    setup, _ = _create_setup(hfss)

    hfss.modeler.fit_all()
    hfss.save_project(str(project_path))

    print("Built:", project_path)
    print("Design: SingleMagicT_v2")
    print("Ports: P1/P2 collinear, P3 H-arm ridged, P4 E-arm")
    print("Sweep: %.2f--%.2f GHz" % (F_START_GHZ, F_STOP_GHZ))
    print("Current ridge seed:")
    print("  w = %.3f mm" % RIDGE_W)
    print("  g1/L1 = %.3f / %.3f mm" % (G1, L1))
    print("  g2/L2 = %.3f / %.3f mm" % (G2, L2))
    print("  terminal ridge = %.3f mm" % TERMINAL_RIDGE_LEN)
    print("E arm: parity-corrected WR90 orientation (B along X, A along Y)")

    if args.solve:
        print("Solving HFSS...")
        hfss.analyze_setup(setup.name)

        touchstone = outdir / "single_magictee_v2.s4p"
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
        print("Build-only mode. Re-run with --solve after checking geometry.")

    # Do not leave ansysedtsv.exe or an .aedt.lock behind when this launcher
    # process exits. The saved project can be reopened from AEDT afterwards.
    try:
        hfss.release_desktop()
    except Exception as exc:
        print("AEDT release warning:", exc)

    return hfss


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--version",
        default="2022.2",
        help="AEDT version, e.g. 2022.1 or 2022.2",
    )
    p.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parent / "output_v2"),
        help="Output directory for .aedt and .s4p files",
    )
    p.add_argument(
        "--solve",
        action="store_true",
        help="Run adaptive solve + 9--11.5 GHz sweep after building",
    )
    p.add_argument(
        "--non-graphical",
        action="store_true",
        help="Run AEDT without GUI",
    )
    p.add_argument("--ridge-w", type=float, default=RIDGE_W)
    p.add_argument("--g1", type=float, default=G1)
    p.add_argument("--l1", type=float, default=L1)
    p.add_argument("--g2", type=float, default=G2)
    p.add_argument("--l2", type=float, default=L2)
    p.add_argument("--terminal-ridge-len", type=float, default=TERMINAL_RIDGE_LEN)
    return p.parse_args()


if __name__ == "__main__":
    build(parse_args())
