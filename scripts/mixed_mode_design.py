#!/usr/bin/env python3
"""
Reference calculations for the mixed-mode design layer.

No HFSS result is implied here.  This script prints analytic scales used to
initialize and audit the full-wave model.
"""

from __future__ import annotations

import numpy as np

from ridge_cross_section_seed import A, B, C0, ridge_modal_parameters

ETA0 = 376.730313668
F0 = 10.19465e9
F_LO = 9.0e9
F_HI = 11.5e9
W = 4.572e-3
G1 = 7.672e-3
G2 = 4.984e-3


def four_way_basis():
    s2 = np.sqrt(2.0)
    return 0.5 * np.array(
        [
            [1.0, 1.0, 1.0, 1.0],
            [s2, -s2, 0.0, 0.0],
            [0.0, 0.0, s2, -s2],
            [1.0, 1.0, -1.0, -1.0],
        ]
    )


def wr90_zte(f_hz):
    fc10 = C0 / (2.0 * A)
    return ETA0 / np.sqrt(1.0 - (fc10 / f_hz) ** 2)


def wr90_emax(f_hz, power_w):
    return np.sqrt(4.0 * power_w * wr90_zte(f_hz) / (A * B))


def te20_evanescent_alpha(f_hz):
    fc20 = C0 / A
    k0 = 2.0 * np.pi * f_hz / C0
    return k0 * np.sqrt((fc20 / f_hz) ** 2 - 1.0)


def ridge_lambda_g(gap_m):
    _, _, _, beta = ridge_modal_parameters(
        A, B, W / A, gap_m / B, F0
    )
    return 2.0 * np.pi / float(np.asarray(beta))


def main():
    u = four_way_basis()
    unitary_error = np.max(np.abs(u @ u.T - np.eye(4)))

    amp_22 = 10.0 ** (-22.0 / 20.0)
    total_il_db = -10.0 * np.log10(0.95)
    stage_eta = np.sqrt(0.95)
    stage_il_db = -10.0 * np.log10(stage_eta)

    lg1 = ridge_lambda_g(G1)
    lg2 = ridge_lambda_g(G2)

    alpha20 = te20_evanescent_alpha(F_HI)
    l20db = np.log(10.0) / alpha20

    print("four-way mixed-mode basis")
    print(u)
    print(f"orthogonality_error={unitary_error:.3e}")
    print()
    print(f"22_dB_amplitude_limit={amp_22:.8f}")
    print(f"95pct_total_insertion_loss_budget_dB={total_il_db:.6f}")
    print(f"equal_stage_efficiency_min={stage_eta:.8f}")
    print(f"equal_stage_insertion_loss_budget_dB={stage_il_db:.6f}")
    print()
    print(f"ridge1_lambda_g_mm={lg1*1e3:.6f}")
    print(f"ridge1_lambda_g_over_4_mm={lg1*1e3/4.0:.6f}")
    print(f"ridge2_lambda_g_mm={lg2*1e3:.6f}")
    print(f"ridge2_lambda_g_over_4_mm={lg2*1e3/4.0:.6f}")
    print()
    for f in [F_LO, F0, F_HI]:
        e = wr90_emax(f, 30_000.0)
        print(
            f"WR90_Emax_30kW_at_{f/1e9:.6f}GHz="
            f"{e/1e6:.6f}_MV_per_m"
        )
    print()
    print(f"TE20_alpha_at_11p5GHz_per_m={alpha20:.6f}")
    print(f"TE20_1_over_alpha_mm={1e3/alpha20:.6f}")
    print(f"TE20_20dB_amplitude_decay_length_mm={l20db*1e3:.6f}")


if __name__ == "__main__":
    main()
