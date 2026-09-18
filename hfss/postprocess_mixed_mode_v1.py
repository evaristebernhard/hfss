#!/usr/bin/env python3
"""
Post-process the four-port HFSS Touchstone file in the
(Sigma, Delta1, Delta2, Delta3) basis.

Requires:
    pip install scikit-rf numpy
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np

try:
    import skrf as rf
except ImportError as exc:
    raise SystemExit(
        "scikit-rf is required. Install with: pip install scikit-rf"
    ) from exc


U = 0.5 * np.array(
    [
        [1.0, 1.0, 1.0, 1.0],
        [math.sqrt(2.0), -math.sqrt(2.0), 0.0, 0.0],
        [0.0, 0.0, math.sqrt(2.0), -math.sqrt(2.0)],
        [1.0, 1.0, -1.0, -1.0],
    ],
    dtype=complex,
)

MODE_NAMES = ["Sigma", "Delta1", "Delta2", "Delta3"]


def db20(x):
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-15))


def mixed_mode_s(s_port):
    # a_m = U a_p and b_m = U b_p -> S_m = U S_p U^H
    return U @ s_port @ U.conj().T


def analyze(path: Path, csv_path: Path):
    ntwk = rf.Network(str(path))

    if ntwk.nports != 4:
        raise ValueError("Expected a 4-port Touchstone file")

    rows = []

    modal_rl_min = {name: float("inf") for name in MODE_NAMES}
    modal_conversion_worst_db = -300.0

    for f_hz, s_port in zip(ntwk.f, ntwk.s):
        sm = mixed_mode_s(s_port)

        diag = np.diag(sm)
        rl = -db20(diag)

        offdiag = sm.copy()
        np.fill_diagonal(offdiag, 0.0)
        conv_db = float(np.max(db20(offdiag)))
        modal_conversion_worst_db = max(modal_conversion_worst_db, conv_db)

        for i, name in enumerate(MODE_NAMES):
            modal_rl_min[name] = min(modal_rl_min[name], float(rl[i]))

        rows.append(
            [
                f_hz / 1e9,
                *[float(x) for x in rl],
                conv_db,
                float(-db20(s_port[0, 0])),
                float(-db20(s_port[1, 1])),
                float(-db20(s_port[2, 2])),
                float(-db20(s_port[3, 3])),
            ]
        )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(
            [
                "freq_GHz",
                "RL_Sigma_dB",
                "RL_Delta1_dB",
                "RL_Delta2_dB",
                "RL_Delta3_dB",
                "worst_modal_conversion_dB",
                "RL_P1_dB",
                "RL_P2_dB",
                "RL_P3_dB",
                "RL_P4_dB",
            ]
        )
        wr.writerows(rows)

    print("Mixed-mode summary")
    print("------------------")
    for name in MODE_NAMES:
        print("minimum RL %-6s : %8.3f dB" % (name, modal_rl_min[name]))
    print(
        "worst modal conversion amplitude: %8.3f dB"
        % modal_conversion_worst_db
    )
    print("CSV:", csv_path)

    print("\nFirst-v1 interpretation:")
    if modal_rl_min["Sigma"] < 20.0:
        print("- Sigma channel still needs major junction/taper matching.")
    else:
        print("- Sigma channel is already in a useful first-pass range.")

    delta_min = min(
        modal_rl_min["Delta1"],
        modal_rl_min["Delta2"],
        modal_rl_min["Delta3"],
    )
    if delta_min < 20.0:
        print("- At least one Delta channel is poorly matched; isolation tuning is required.")
    else:
        print("- Delta-channel matching is encouraging for a rough v1 model.")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("touchstone", type=Path)
    p.add_argument(
        "--csv",
        type=Path,
        default=Path("mixed_mode_v1.csv"),
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    analyze(args.touchstone, args.csv)
