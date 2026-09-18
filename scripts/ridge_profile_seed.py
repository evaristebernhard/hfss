#!/usr/bin/env python3
"""
Rough v1 longitudinal ridge-profile generator.

The old script interpolated an obsolete (5.8, 6.0) -> (9.2, 4.0) mm seed
directly in geometry space.  The current first-pass design instead keeps a
common ridge width w = 4.572 mm and treats the desired impedance trajectory as
the primary object.

For v1 we use a piecewise log-impedance smoothstep and only a provisional
smooth gap map between the analytically calibrated control stations.  HFSS
modal-impedance extraction should later replace the provisional g(Z) mapping.

No SciPy dependency is required.
"""

from __future__ import annotations

import math
import numpy as np

B = 10.16
W = 4.572

# z [mm], Z/Zref, gap [mm]
STATIONS = [
    (0.000, 1.000, 10.160),
    (9.872, 0.842, 7.672),
    (18.729, 0.609, 4.984),
]


def smoothstep(t: float) -> float:
    return 3.0 * t * t - 2.0 * t * t * t


def interp_log_impedance(t: float, z0_ratio: float, z1_ratio: float) -> float:
    """Smooth in ln(Z), not in Z itself."""
    s = smoothstep(t)
    return math.exp((1.0 - s) * math.log(z0_ratio) + s * math.log(z1_ratio))


def provisional_gap_map(t: float, g0: float, g1: float) -> float:
    """
    First-HFSS geometry only.

    This is deliberately simple.  It preserves zero slope at each control
    station, but it is NOT claimed to be the exact inverse Cohn map.
    """
    s = smoothstep(t)
    return (1.0 - s) * g0 + s * g1


def profile(z_mm: float):
    if z_mm <= STATIONS[0][0]:
        return STATIONS[0][1], STATIONS[0][2]
    if z_mm >= STATIONS[-1][0]:
        return STATIONS[-1][1], STATIONS[-1][2]

    for p0, p1 in zip(STATIONS[:-1], STATIONS[1:]):
        z0, zr0, g0 = p0
        z1, zr1, g1 = p1
        if z0 <= z_mm <= z1:
            t = (z_mm - z0) / (z1 - z0)
            return (
                interp_log_impedance(t, zr0, zr1),
                provisional_gap_map(t, g0, g1),
            )
    raise RuntimeError("unreachable")


if __name__ == "__main__":
    zs = np.linspace(STATIONS[0][0], STATIONS[-1][0], 81)
    print("z_mm,w_mm,target_Z_over_Zref,g_mm,ridge_depth_each_wall_mm")
    for z in zs:
        zratio, gap = profile(float(z))
        ridge_depth = 0.5 * (B - gap)
        print(
            f"{z:.6f},{W:.6f},{zratio:.8f},"
            f"{gap:.6f},{ridge_depth:.6f}"
        )
