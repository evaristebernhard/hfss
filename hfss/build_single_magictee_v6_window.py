#!/usr/bin/env python3
"""v6 wrapper adding one or two localized E-arm inductive windows to v4.

The base v4 builder remains untouched.  Each window is a thin PEC diaphragm
normal to the E-arm propagation direction (+Z), with a centered aperture in
the broad (Y) dimension.  This is a localized discontinuity rather than the
long reduced-height E-arm section that failed in v5.
"""

from __future__ import annotations

import argparse
import sys

import build_single_magictee_v4_full as base


E_WINDOW1_OPEN = 0.0
E_WINDOW1_THICKNESS = 1.5
E_WINDOW1_OFFSET = 7.0
E_WINDOW2_OPEN = 0.0
E_WINDOW2_THICKNESS = 1.5
E_WINDOW2_OFFSET = 13.0


def _validate_window(opening: float, thickness: float, offset: float, label: str) -> None:
    if opening <= 0.0:
        return
    if not (0.0 < opening < base.A):
        raise ValueError(f"{label} opening must satisfy 0 < opening < {base.A} mm")
    if thickness <= 0.0:
        raise ValueError(f"{label} thickness must be positive")
    if offset < 0.0 or offset + thickness > base.E_ARM_LEN:
        raise ValueError(f"{label} must remain inside the E arm")


def _subtract_e_windows(hfss):
    windows = [
        (E_WINDOW1_OPEN, E_WINDOW1_THICKNESS, E_WINDOW1_OFFSET, "EWindow1"),
        (E_WINDOW2_OPEN, E_WINDOW2_THICKNESS, E_WINDOW2_OFFSET, "EWindow2"),
    ]
    enabled = []
    for opening, thickness, offset, name in windows:
        if opening <= 0.0:
            continue
        z0 = base.B / 2.0 + offset
        shoulder = 0.5 * (base.A - opening)
        minus_y = base._box(
            hfss,
            [-base.B / 2.0, -base.A / 2.0, z0],
            [base.B, shoulder, thickness],
            name + "_MinusY",
            material="pec",
        )
        plus_y = base._box(
            hfss,
            [-base.B / 2.0, opening / 2.0, z0],
            [base.B, shoulder, thickness],
            name + "_PlusY",
            material="pec",
        )
        hfss.modeler.subtract(
            "AirWG", [minus_y.name, plus_y.name], keep_originals=False
        )
        enabled.append(
            {"name": name, "opening_mm": opening, "thickness_mm": thickness, "offset_mm": offset}
        )
    return {"e_step_enabled": False, "e_windows": enabled}


def parse_args():
    global E_WINDOW1_OPEN, E_WINDOW1_THICKNESS, E_WINDOW1_OFFSET
    global E_WINDOW2_OPEN, E_WINDOW2_THICKNESS, E_WINDOW2_OFFSET

    own = argparse.ArgumentParser(add_help=False)
    own.add_argument("--e-window1-open", type=float, default=E_WINDOW1_OPEN)
    own.add_argument("--e-window1-thickness", type=float, default=E_WINDOW1_THICKNESS)
    own.add_argument("--e-window1-offset", type=float, default=E_WINDOW1_OFFSET)
    own.add_argument("--e-window2-open", type=float, default=E_WINDOW2_OPEN)
    own.add_argument("--e-window2-thickness", type=float, default=E_WINDOW2_THICKNESS)
    own.add_argument("--e-window2-offset", type=float, default=E_WINDOW2_OFFSET)
    custom, remaining = own.parse_known_args()

    E_WINDOW1_OPEN = custom.e_window1_open
    E_WINDOW1_THICKNESS = custom.e_window1_thickness
    E_WINDOW1_OFFSET = custom.e_window1_offset
    E_WINDOW2_OPEN = custom.e_window2_open
    E_WINDOW2_THICKNESS = custom.e_window2_thickness
    E_WINDOW2_OFFSET = custom.e_window2_offset
    _validate_window(E_WINDOW1_OPEN, E_WINDOW1_THICKNESS, E_WINDOW1_OFFSET, "window 1")
    _validate_window(E_WINDOW2_OPEN, E_WINDOW2_THICKNESS, E_WINDOW2_OFFSET, "window 2")

    original = sys.argv
    try:
        sys.argv = [original[0], *remaining]
        return base.parse_args()
    finally:
        sys.argv = original


if __name__ == "__main__":
    base._subtract_e_step = _subtract_e_windows
    base.build(parse_args())
