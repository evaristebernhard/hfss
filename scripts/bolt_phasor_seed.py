#!/usr/bin/env python3
"""
Rough two-bolt tuning initializer.

The model treats each shallow bolt as a weak local reflection:
    Gamma ~= Gamma0 + sum gamma_i exp(-2j beta z_i)

It is only an initializer for HFSS placement/penetration sweeps.
"""

from __future__ import annotations

import math
import numpy as np

C0 = 299_792_458.0
F0 = 10.19465e9

# Closed-form dominant cutoffs from the current analytic ridge seed.
FC1 = 5.97e9
FC2 = 5.12e9


def beta_from_fc(f_hz: float, fc_hz: float) -> float:
    return (
        2.0
        * math.pi
        * f_hz
        / C0
        * math.sqrt(1.0 - (fc_hz / f_hz) ** 2)
    )


def guided_wavelength(f_hz: float, fc_hz: float) -> float:
    return 2.0 * math.pi / beta_from_fc(f_hz, fc_hz)


def two_equal_bolts_residual(spacing_m: float, beta: float) -> float:
    """
    Magnitude of the normalized sum of two equal weak reflected phasors.
    Zero is ideal cancellation.
    """
    return abs(1.0 + np.exp(-2j * beta * spacing_m))


def main():
    lg1 = guided_wavelength(F0, FC1)
    lg2 = guided_wavelength(F0, FC2)

    print(f"electrical center = {F0/1e9:.6f} GHz")
    print(f"section 1 lambda_g = {lg1*1e3:.4f} mm")
    print(f"section 1 lambda_g/4 = {lg1*1e3/4:.4f} mm")
    print(f"section 2 lambda_g = {lg2*1e3:.4f} mm")
    print(f"section 2 lambda_g/4 = {lg2*1e3/4:.4f} mm")

    beta_mid = 0.5 * (beta_from_fc(F0, FC1) + beta_from_fc(F0, FC2))

    spacings_mm = np.linspace(7.5, 10.0, 101)
    residual = np.array(
        [two_equal_bolts_residual(s * 1e-3, beta_mid) for s in spacings_mm]
    )
    best = int(np.argmin(residual))

    print("\ncoarse equal-bolt phase-cancellation sweep")
    print(f"best spacing ~= {spacings_mm[best]:.3f} mm")
    print(f"normalized residual phasor magnitude ~= {residual[best]:.6f}")
    print("recommended HFSS first value = 8.8 mm")
    print("recommended spacing sweep = 7.5...10.0 mm")
    print("recommended shallow penetration sweep = 0...2.0 mm")


if __name__ == "__main__":
    main()
