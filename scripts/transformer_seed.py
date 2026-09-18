#!/usr/bin/env python3
"""
Reduced-model seed calculations for the 9–11.5 GHz WR90 magic-tee combiner.

IMPORTANT:
This script does NOT model the 3-D magic-tee junction or ridged waveguide.
The default ZL/Z0=0.5 case is only a conditional transmission-line initializer.

Requires:
    numpy
    scipy
"""

import numpy as np
from scipy.optimize import differential_evolution, brentq

C0 = 299_792_458.0
ETA0 = 376.730313668
A_WR90 = 22.86e-3
B_WR90 = 10.16e-3

F_LO = 9.0e9
F_HI = 11.5e9
FC10 = C0 / (2.0 * A_WR90)


def beta_te10(f_hz):
    f_hz = np.asarray(f_hz)
    return 2.0 * np.pi * f_hz / C0 * np.sqrt(1.0 - (FC10 / f_hz) ** 2)


def zte_te10(f_hz):
    f_hz = np.asarray(f_hz)
    return ETA0 / np.sqrt(1.0 - (FC10 / f_hz) ** 2)


def zin_line(zc, zl, theta):
    t = np.tan(theta)
    return zc * (zl + 1j * zc * t) / (zc + 1j * zl * t)


def dispersion_symmetric_length():
    return np.pi / (beta_te10(F_LO) + beta_te10(F_HI))


def electrical_center(length_m):
    return brentq(
        lambda f: beta_te10(f) * length_m - np.pi / 2.0,
        F_LO,
        F_HI,
    )


def band_return_loss_db(z1, z2, l1_m, l2_m, load_ratio=0.5, npts=2001):
    f = np.linspace(F_LO, F_HI, npts)
    th1 = beta_te10(f) * l1_m
    th2 = beta_te10(f) * l2_m

    zin = zin_line(z2, load_ratio, th2)
    zin = zin_line(z1, zin, th1)

    gamma = np.abs((zin - 1.0) / (zin + 1.0))
    return f, -20.0 * np.log10(np.maximum(gamma, 1e-15))


def optimize_two_section(load_ratio=0.5):
    l0 = dispersion_symmetric_length()
    f = np.linspace(F_LO, F_HI, 2001)
    beta = beta_te10(f)

    def objective(x):
        z1, z2, l1_mm, l2_mm = x
        zin = zin_line(z2, load_ratio, beta * l2_mm * 1e-3)
        zin = zin_line(z1, zin, beta * l1_mm * 1e-3)
        gamma = np.abs((zin - 1.0) / (zin + 1.0))
        return np.max(gamma)

    # Bounds are intentionally broad around a 2:1 seed and can be changed
    # for another extracted/de-embedded load ratio.
    result = differential_evolution(
        objective,
        bounds=[
            (0.65, 1.05),
            (0.40, 0.85),
            (0.75 * l0 * 1e3, 1.25 * l0 * 1e3),
            (0.75 * l0 * 1e3, 1.25 * l0 * 1e3),
        ],
        tol=1e-10,
        polish=True,
        seed=1,
    )
    return result


def pair_difference_to_sum_db(amplitude_ratio=1.0, phase_deg=0.0):
    phi = np.deg2rad(phase_deg)
    r = amplitude_ratio
    p_delta = 1.0 + r * r - 2.0 * r * np.cos(phi)
    p_sum = 1.0 + r * r + 2.0 * r * np.cos(phi)
    if p_delta <= 0.0:
        return -np.inf
    return 10.0 * np.log10(p_delta / p_sum)


def main():
    l0 = dispersion_symmetric_length()
    fec = electrical_center(l0)

    print("WR90 analytic baseline")
    print(f"fc10 = {FC10 / 1e9:.6f} GHz")
    print(f"dispersion-symmetric L = {l0 * 1e3:.6f} mm")
    print(f"electrical center = {fec / 1e9:.6f} GHz")
    print(
        "band-edge electrical lengths = "
        f"{np.rad2deg(beta_te10(F_LO) * l0):.6f} deg, "
        f"{np.rad2deg(beta_te10(F_HI) * l0):.6f} deg"
    )

    for f in [F_LO, fec, 10.25e9, F_HI]:
        lg = 2.0 * np.pi / beta_te10(f)
        print(
            f"{f / 1e9:8.5f} GHz: "
            f"lambda_g={lg * 1e3:8.4f} mm, "
            f"Z_TE={zte_te10(f):8.3f} ohm"
        )

    result = optimize_two_section(load_ratio=0.5)
    z1, z2, l1_mm, l2_mm = result.x
    worst_rl = -20.0 * np.log10(result.fun)

    print("\nConditional 2:1 reduced-model minimax seed")
    print(f"Z1/Z0 = {z1:.9f}")
    print(f"Z2/Z0 = {z2:.9f}")
    print(f"L1 = {l1_mm:.6f} mm")
    print(f"L2 = {l2_mm:.6f} mm")
    print(f"worst in-band RL = {worst_rl:.6f} dB")

    # Isolation/difference-mode reference
    target = -22.0
    # For equal amplitudes: tan^2(phi/2) = 10^(target/10)
    phi_lim = 2.0 * np.arctan(10.0 ** (target / 20.0))
    print(
        "\nEqual-amplitude pair phase-error limit for -22 dB "
        f"difference/sum power = {np.rad2deg(phi_lim):.6f} deg"
    )


if __name__ == "__main__":
    main()
