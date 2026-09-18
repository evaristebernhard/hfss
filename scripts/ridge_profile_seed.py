#!/usr/bin/env python3
import numpy as np

B = 10.16
STATIONS = [
    (0.0, 0.0, 10.16),
    (9.60125, 5.8, 6.0),
    (19.20250, 9.2, 4.0),
]

def smoothstep(t):
    return 3.0*t*t - 2.0*t*t*t

def interp_segment(z, p0, p1):
    z0, w0, g0 = p0
    z1, w1, g1 = p1
    t = (z-z0)/(z1-z0)
    s = smoothstep(t)
    return w0 + (w1-w0)*s, g0 + (g1-g0)*s

def ridge_profile(z):
    if z <= STATIONS[0][0]:
        return STATIONS[0][1], STATIONS[0][2]
    if z >= STATIONS[-1][0]:
        return STATIONS[-1][1], STATIONS[-1][2]
    for p0, p1 in zip(STATIONS[:-1], STATIONS[1:]):
        if p0[0] <= z <= p1[0]:
            return interp_segment(z, p0, p1)
    raise RuntimeError("unreachable")

if __name__ == "__main__":
    zs = np.linspace(STATIONS[0][0], STATIONS[-1][0], 41)
    print("z_mm,w_mm,g_mm,ridge_depth_each_wall_mm")
    for z in zs:
        w, g = ridge_profile(z)
        hr = 0.5*(B-g)
        print(f"{z:.6f},{w:.6f},{g:.6f},{hr:.6f}")
