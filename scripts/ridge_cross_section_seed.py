#!/usr/bin/env python3
"""
Self-consistent reduced-model seed for the WR90 double-ridge matching sections.

This script uses:
  - Hoefer/Burton-style closed-form dominant-mode cutoff approximation,
  - Cohn voltage-current characteristic impedance approximation,
  - a transverse-resonance check for the first odd/even quasi-TE roots,
  - exact lossless transmission-line recursion for the two reduced sections.

IMPORTANT:
The assumed load ZL/Zref = 0.5 is conditional. A real magic-tee junction is a
3-D multimode discontinuity. The final seed must be retuned after HFSS
de-embedding of the actual junction.

Requires:
    numpy
    scipy
"""

from __future__ import annotations

import math
import numpy as np
from scipy.optimize import brentq, differential_evolution

C0 = 299_792_458.0

A = 22.86e-3  # WR90 broad dimension, m
B = 10.16e-3  # WR90 narrow dimension, m

F_LO = 9.0e9
F_HI = 11.5e9
F_GRID = np.linspace(F_LO, F_HI, 2001)


def csc(x):
    return 1.0 / np.sin(x)


def ridge_cutoff_lambda(a: float, b: float, w: float, g: float) -> float:
    """Closed-form dominant-mode cutoff wavelength."""
    x = (
        1.0
        + (4.0 / np.pi)
        * (1.0 + 0.2 * np.sqrt(b / (a - w)))
        * (b / (a - w))
        * np.log(csc(np.pi * g / (2.0 * b)))
        + (2.45 + 0.2 * w / a) * (w * b) / (g * (a - w))
    )
    return 2.0 * (a - w) * np.sqrt(x)


def ridge_modal_parameters(
    a: float,
    b: float,
    width_ratio: float,
    gap_ratio: float,
    f_hz,
):
    """
    Return fc, Z_inf, Z(f), beta(f) for the Cohn voltage-current definition.
    """
    w = width_ratio * a
    g = gap_ratio * b
    lam_cr = ridge_cutoff_lambda(a, b, w, g)
    fc = C0 / lam_cr

    k1 = b / lam_cr
    arg = np.pi * (w / b) * k1

    k2 = (
        (b / g) * np.sin(arg)
        + (
            (2.0 * b / lam_cr) * np.log(csc(np.pi * g / (2.0 * b)))
            + np.tan(
                (np.pi / 2.0)
                * (b / lam_cr)
                * ((a - w) / b)
            )
        )
        * np.cos(arg)
    )

    z_inf = 120.0 * np.pi**2 * k1 / k2

    f_hz = np.asarray(f_hz, dtype=float)
    root = np.sqrt(1.0 - (fc / f_hz) ** 2)
    z = z_inf / root
    beta = 2.0 * np.pi * f_hz / C0 * root
    return fc, z_inf, z, beta


def rectangular_reference(f_hz):
    """
    Same-normalization WR90 reference, evaluated as the no-ridge limit.
    """
    return ridge_modal_parameters(
        A,
        B,
        width_ratio=1e-8,
        gap_ratio=0.999999,
        f_hz=f_hz,
    )


def zin_line(zc, zl, theta):
    t = np.tan(theta)
    return zc * (zl + 1j * zc * t) / (zc + 1j * zl * t)


def two_section_response(
    width_ratio: float,
    gap_ratio_1: float,
    gap_ratio_2: float,
    length_1_mm: float,
    length_2_mm: float,
    load_ratio: float = 0.5,
    freqs=F_GRID,
):
    _, _, z_ref, _ = rectangular_reference(freqs)

    fc1, _, z1, beta1 = ridge_modal_parameters(
        A, B, width_ratio, gap_ratio_1, freqs
    )
    fc2, _, z2, beta2 = ridge_modal_parameters(
        A, B, width_ratio, gap_ratio_2, freqs
    )

    z_load = load_ratio * z_ref

    z_in = zin_line(
        z2,
        z_load,
        beta2 * length_2_mm * 1e-3,
    )
    z_in = zin_line(
        z1,
        z_in,
        beta1 * length_1_mm * 1e-3,
    )

    gamma = (z_in - z_ref) / (z_in + z_ref)
    rl_db = -20.0 * np.log10(np.maximum(np.abs(gamma), 1e-15))

    return {
        "fc1": fc1,
        "fc2": fc2,
        "z1": z1,
        "z2": z2,
        "beta1": beta1,
        "beta2": beta2,
        "zref": z_ref,
        "zin": z_in,
        "gamma": gamma,
        "rl_db": rl_db,
    }


def optimize_fixed_width(
    width_ratio: float,
    load_ratio: float = 0.5,
):
    """Optimize g1/b, g2/b, L1, L2 for a fixed common ridge width."""

    def objective(x):
        g1, g2, l1, l2 = x

        try:
            r = two_section_response(
                width_ratio,
                g1,
                g2,
                l1,
                l2,
                load_ratio=load_ratio,
            )
        except Exception:
            return 1.0

        if r["fc1"] >= 8.5e9 or r["fc2"] >= 8.5e9:
            return 1.0

        return float(np.max(np.abs(r["gamma"])))

    result = differential_evolution(
        objective,
        bounds=[
            (0.20, 0.95),
            (0.15, 0.85),
            (6.0, 12.0),
            (6.0, 12.0),
        ],
        seed=max(1, int(round(width_ratio * 1000))),
        popsize=14,
        maxiter=300,
        tol=1e-9,
        polish=True,
    )

    return result


def trm_function(
    f_hz: float,
    a: float,
    b: float,
    w: float,
    g: float,
    mode: str,
) -> float:
    """
    Approximate transverse-resonance equation.

    mode='odd'  -> first root is TE10-like
    mode='even' -> first root is TE20-like
    """
    lam = C0 / f_hz

    theta1 = np.pi * (a - w) / lam
    theta2 = np.pi * w / lam

    b_norm = (
        2.0 * b / lam
        * np.log(csc(np.pi * g / (2.0 * b)))
    )

    if mode == "odd":
        return (
            1.0 / np.tan(theta1)
            - (b / g) * np.tan(theta2)
            - b_norm
        )

    if mode == "even":
        return (
            1.0 / np.tan(theta1)
            + (b / g) / np.tan(theta2)
            - b_norm
        )

    raise ValueError("mode must be 'odd' or 'even'")


def first_trm_root(
    a: float,
    b: float,
    width_ratio: float,
    gap_ratio: float,
    mode: str,
    f_min: float = 0.5e9,
    f_max: float = 20.0e9,
):
    w = width_ratio * a
    g = gap_ratio * b

    grid = np.linspace(f_min, f_max, 100_000)

    prev_f = None
    prev_v = None

    for f in grid:
        try:
            v = trm_function(f, a, b, w, g, mode)
        except Exception:
            prev_f = None
            prev_v = None
            continue

        if not np.isfinite(v) or abs(v) > 1e5:
            prev_f = None
            prev_v = None
            continue

        if prev_v is not None and prev_v * v < 0.0:
            try:
                root = brentq(
                    lambda ff: trm_function(
                        ff, a, b, w, g, mode
                    ),
                    prev_f,
                    f,
                    maxiter=100,
                )
            except ValueError:
                root = None

            if root is not None:
                # Reject crossings that are actually asymptotes.
                eps = 1e-7
                left = trm_function(
                    root * (1.0 - eps), a, b, w, g, mode
                )
                right = trm_function(
                    root * (1.0 + eps), a, b, w, g, mode
                )
                if abs(left) < 1e4 and abs(right) < 1e4:
                    return root

        prev_f = f
        prev_v = v

    return None


def print_seed(width_ratio=0.20, load_ratio=0.5):
    result = optimize_fixed_width(width_ratio, load_ratio)

    g1, g2, l1, l2 = result.x

    response = two_section_response(
        width_ratio,
        g1,
        g2,
        l1,
        l2,
        load_ratio=load_ratio,
    )

    worst_rl = -20.0 * np.log10(result.fun)
    idx = int(np.argmin(response["rl_db"]))

    print("WR90 double-ridge reduced-model seed")
    print(f"common w/a = {width_ratio:.6f}")
    print(f"ridge width = {width_ratio*A*1e3:.6f} mm")
    print(f"conditional ZL/Zref = {load_ratio:.6f}")
    print()

    for n, (gr, ll, fc) in enumerate(
        [
            (g1, l1, response["fc1"]),
            (g2, l2, response["fc2"]),
        ],
        start=1,
    ):
        odd = first_trm_root(
            A, B, width_ratio, gr, "odd"
        )
        even = first_trm_root(
            A, B, width_ratio, gr, "even"
        )

        gap_mm = gr * B * 1e3
        ridge_h_mm = (B - gr * B) * 0.5 * 1e3

        print(f"section {n}:")
        print(f"  g/b = {gr:.9f}")
        print(f"  gap = {gap_mm:.6f} mm")
        print(f"  ridge height each = {ridge_h_mm:.6f} mm")
        print(f"  length = {ll:.6f} mm")
        print(f"  closed-form fc = {fc/1e9:.6f} GHz")
        if odd is not None:
            print(f"  TRM TE10-like = {odd/1e9:.6f} GHz")
        if even is not None:
            print(f"  TRM TE20-like = {even/1e9:.6f} GHz")
        print()

    print(f"worst reduced-model RL = {worst_rl:.6f} dB")
    print(
        "worst-point frequency = "
        f"{F_GRID[idx]/1e9:.6f} GHz"
    )


def width_trade_study():
    print(
        "w/a, RLmin_dB, g1_mm, g2_mm, "
        "L1_mm, L2_mm, TE20_1_GHz, TE20_2_GHz"
    )

    for wr in [
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
    ]:
        result = optimize_fixed_width(wr, 0.5)
        g1, g2, l1, l2 = result.x

        even1 = first_trm_root(A, B, wr, g1, "even")
        even2 = first_trm_root(A, B, wr, g2, "even")

        print(
            f"{wr:.2f},"
            f"{-20*np.log10(result.fun):.4f},"
            f"{g1*B*1e3:.4f},"
            f"{g2*B*1e3:.4f},"
            f"{l1:.4f},"
            f"{l2:.4f},"
            f"{even1/1e9:.4f},"
            f"{even2/1e9:.4f}"
        )


if __name__ == "__main__":
    print_seed(0.20, 0.5)
