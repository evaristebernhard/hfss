#!/usr/bin/env python3
"""
Analytic system seed for the v4 4-to-1 Magic-T tree.

Reports:
- WR90 TE10 guided wavelengths over 9--11.5 GHz
- the three-screw electrical phases for the frozen 0/8.4/17.6 mm spacing
- 95% system insertion-loss budget
- equal-path phase tolerance scales for the two-stage 4-to-1 tree

This is a reduced-order budgeting tool, not an HFSS replacement.
"""

from __future__ import annotations

import math

C0 = 299_792_458.0
A = 22.86e-3
FC = C0 / (2*A)

FREQS = [9.0e9, 10.25e9, 11.5e9]
SCREW_REL_MM = [0.0, 8.4, 17.6]
ETA_TARGET = 0.95


def beta(f):
    k0 = 2*math.pi*f/C0
    return k0*math.sqrt(1-(FC/f)**2)


def lambda_g(f):
    return 2*math.pi/beta(f)


def main():
    print("v4 four-way architecture analytic seed")
    print("WR90 TE10 cutoff = %.6f GHz" % (FC/1e9))
    print()

    for f in FREQS:
        lg = lambda_g(f)
        print("%.2f GHz: lambda_g = %.3f mm, lambda_g/4 = %.3f mm" % (
            f/1e9, lg*1e3, lg*1e3/4
        ))
        phases = []
        for zmm in SCREW_REL_MM:
            phi = (-2*beta(f)*zmm*1e-3)*180/math.pi
            phases.append(phi)
        print("  screw reflected-phasor phases [deg] =", ["%.1f" % x for x in phases])

    il_total = -10*math.log10(ETA_TARGET)
    il_stage = il_total/2
    print()
    print("95%% efficiency -> total excess insertion loss <= %.4f dB" % il_total)
    print("two comparable stages -> nominal budget <= %.4f dB/stage" % il_stage)

    f0 = 10.25e9
    lg0 = lambda_g(f0)
    print()
    print("At 10.25 GHz:")
    for phase_deg in [1,2,3,5]:
        # one-way phase beta*dL = phase
        dL = math.radians(phase_deg)/beta(f0)
        print("  %.1f deg one-way phase error <-> %.3f mm path error" % (phase_deg,dL*1e3))

    frac_bw = (11.5-9.0)/10.25
    print()
    print("fractional bandwidth = %.2f%%" % (100*frac_bw))
    print("tree rule: keep MT-A and MT-B electrical paths equal before MT-C")
    print("difference ports must terminate in matched loads during imbalance cases")


if __name__ == "__main__":
    main()
