#!/usr/bin/env python3
"""Analytic seed report for the v3.3 H-junction reduced-width throat.

This is not a full-wave model.  It only reports TE10 cutoff, propagation,
wave-impedance and simple relative field scales used to choose the first
HFSS structural candidate.
"""

from __future__ import annotations

import argparse
import math

C0 = 299_792_458.0
ETA0 = 376.730313668
A_WR90_MM = 22.86


def fc_hz(a_mm: float) -> float:
    return C0 / (2.0 * a_mm * 1e-3)


def root(f_hz: float, a_mm: float) -> float:
    fc = fc_hz(a_mm)
    if f_hz <= fc:
        raise ValueError("frequency is below cutoff")
    return math.sqrt(1.0 - (fc / f_hz) ** 2)


def beta(f_hz: float, a_mm: float) -> float:
    return 2.0 * math.pi * f_hz / C0 * root(f_hz, a_mm)


def zte(f_hz: float, a_mm: float) -> float:
    return ETA0 / root(f_hz, a_mm)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--a", type=float, default=18.8, help="throat broad dimension mm")
    p.add_argument("--length", type=float, default=5.5, help="throat length mm")
    args = p.parse_args()

    shoulder = 0.5 * (A_WR90_MM - args.a)
    print("v3.3 H-junction throat analytic seed")
    print(f"a_H = {args.a:.4f} mm")
    print(f"L_H = {args.length:.4f} mm")
    print(f"fc = {fc_hz(args.a)/1e9:.6f} GHz")
    print(f"symmetric shoulder depth = {shoulder:.4f} mm")
    print()

    q = {}
    for f_ghz in [9.0, 10.2, 11.5]:
        f = f_ghz * 1e9
        q[f_ghz] = root(f, args.a)
        zratio = zte(f, args.a) / zte(f, A_WR90_MM)
        phase = beta(f, args.a) * args.length * 1e-3 * 180.0 / math.pi
        # Equal-power E-field scale for TE10: Emax ~ sqrt(P Z_TE / a).
        field_ratio = math.sqrt(
            zte(f, args.a) / zte(f, A_WR90_MM)
            * A_WR90_MM / args.a
        )
        print(
            f"{f_ghz:4.1f} GHz: "
            f"q={q[f_ghz]:.6f}, "
            f"Zratio={zratio:.6f}, "
            f"phase={phase:.3f} deg, "
            f"Eratio={field_ratio:.3f}"
        )

    print()
    print(
        "q(11.5)/q(9.0) = "
        f"{q[11.5]/q[9.0]:.6f}"
    )
    print("Stage-A missing-coupling slope proxy target ~1.56")


if __name__ == "__main__":
    main()
