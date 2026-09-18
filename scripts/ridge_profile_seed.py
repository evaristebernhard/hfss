#!/usr/bin/env python3
"""
Current impedance-space ridge profile seed.

This replaces the legacy geometry-smoothstep seed.  The new construction:
  1. chooses a smooth target in log characteristic impedance at f0;
  2. grows the first ridge from plain WR90 to the current section-1 geometry;
  3. keeps the common ridge width fixed for section 1 -> section 2;
  4. numerically inverts the Cohn reduced model for gap g(z).

This is still an analytic initializer.  HFSS eigenmode/wave-port extraction
must calibrate the impedance definition and the final 3-D geometry.
"""

from __future__ import annotations

import math
import numpy as np
from scipy.optimize import brentq

from ridge_cross_section_seed import (
    A,
    B,
    rectangular_reference,
    ridge_modal_parameters,
)

F0 = 10.19465e9

W = 4.572e-3
G1 = 7.672e-3
G2 = 4.984e-3
L1 = 9.872e-3
L2 = 8.857e-3
LTOT = L1 + L2


def smoothstep(t: float) -> float:
    t = min(1.0, max(0.0, float(t)))
    return 3.0 * t * t - 2.0 * t * t * t


def z_cohn(w: float, g: float) -> float:
    wr = max(w / A, 1e-8)
    gr = min(max(g / B, 1e-6), 0.999999)
    _, _, z, _ = ridge_modal_parameters(A, B, wr, gr, F0)
    return float(np.asarray(z))


def z_plain_wr90() -> float:
    _, _, z, _ = rectangular_reference(F0)
    return float(np.asarray(z))


Z0 = z_plain_wr90()
Z1 = z_cohn(W, G1)
Z2 = z_cohn(W, G2)


def log_interp(z_a: float, z_b: float, s: float) -> float:
    return math.exp((1.0 - s) * math.log(z_a) + s * math.log(z_b))


def solve_gap(w: float, z_target: float, g_lo: float, g_hi: float) -> float:
    def residual(g: float) -> float:
        return z_cohn(w, g) - z_target

    f_lo = residual(g_lo)
    f_hi = residual(g_hi)

    if abs(f_lo) < 1e-9:
        return g_lo
    if abs(f_hi) < 1e-9:
        return g_hi
    if f_lo * f_hi > 0.0:
        raise RuntimeError(
            f"target impedance {z_target:.6f} ohm is not bracketed "
            f"for w={w*1e3:.6f} mm, g in "
            f"[{g_lo*1e3:.6f}, {g_hi*1e3:.6f}] mm"
        )
    return brentq(residual, g_lo, g_hi, xtol=1e-13, rtol=1e-13)


def ridge_profile(z_m: float):
    if z_m <= 0.0:
        return {
            "w": 0.0,
            "g": B,
            "z_target": Z0,
            "z_model": Z0,
            "segment": 1,
        }

    if z_m >= LTOT:
        return {
            "w": W,
            "g": G2,
            "z_target": Z2,
            "z_model": Z2,
            "segment": 2,
        }

    if z_m <= L1:
        t = z_m / L1
        s = smoothstep(t)

        # Grow the ridge width from zero while independently enforcing the
        # desired impedance trajectory through the solved gap.
        w = W * s
        z_target = log_interp(Z0, Z1, s)
        g = solve_gap(w, z_target, G1, B * 0.999999)
        return {
            "w": w,
            "g": g,
            "z_target": z_target,
            "z_model": z_cohn(w, g),
            "segment": 1,
        }

    t = (z_m - L1) / L2
    s = smoothstep(t)

    # Section 1 -> section 2: common ridge width, gap found from target Z.
    w = W
    z_target = log_interp(Z1, Z2, s)
    g = solve_gap(w, z_target, G2, G1)
    return {
        "w": w,
        "g": g,
        "z_target": z_target,
        "z_model": z_cohn(w, g),
        "segment": 2,
    }


def main():
    print("current impedance-space ridge profile")
    print(f"f0_GHz={F0/1e9:.6f}")
    print(f"Z0={Z0:.6f} ohm")
    print(f"Z1={Z1:.6f} ohm")
    print(f"Z2={Z2:.6f} ohm")
    print(
        "z_mm,segment,w_mm,g_mm,ridge_depth_each_wall_mm,"
        "Z_target_ohm,Z_model_ohm"
    )

    for z_m in np.linspace(0.0, LTOT, 81):
        p = ridge_profile(float(z_m))
        hr = 0.5 * (B - p["g"])
        print(
            f"{z_m*1e3:.6f},{p['segment']},"
            f"{p['w']*1e3:.6f},{p['g']*1e3:.6f},"
            f"{hr*1e3:.6f},{p['z_target']:.6f},{p['z_model']:.6f}"
        )


if __name__ == "__main__":
    main()
