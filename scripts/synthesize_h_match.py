#!/usr/bin/env python3
"""Synthesize an idealized two-reactance H/even matching network from S4P."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution


W = np.array([
    [1 / math.sqrt(2), 1 / math.sqrt(2), 0, 0],
    [1 / math.sqrt(2), -1 / math.sqrt(2), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
], dtype=complex)


def parse_s4p(path: Path):
    tokens = []
    for raw in path.read_text(encoding="ascii", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("!") and not line.startswith("#"):
            tokens.extend(line.split())
    if len(tokens) % 33:
        raise ValueError("invalid four-port Touchstone record count")
    freqs, blocks = [], []
    for k in range(0, len(tokens), 33):
        freq = float(tokens[k])
        vals = [float(x) for x in tokens[k + 1:k + 33]]
        s = np.zeros((4, 4), dtype=complex)
        n = 0
        for row in range(4):
            for col in range(4):
                mag, deg = vals[2 * n], vals[2 * n + 1]
                s[row, col] = mag * np.exp(1j * math.radians(deg))
                n += 1
        sm = W @ s @ W.T
        blocks.append(sm[np.ix_([0, 2], [0, 2])])
        freqs.append(freq)
    return np.asarray(freqs), np.asarray(blocks)


def beta_ratio(freqs, f0=10.25, a_mm=22.86):
    c = 299792458.0
    a = a_mm * 1e-3
    fc = c / (2 * a) / 1e9
    beta = np.sqrt(np.maximum(freqs**2 - fc**2, 1e-12))
    beta0 = math.sqrt(f0**2 - fc**2)
    return beta / beta0


def line(theta):
    c, s = np.cos(theta), np.sin(theta)
    result = np.zeros((len(theta), 2, 2), dtype=complex)
    result[:, 0, 0] = c
    result[:, 0, 1] = 1j * s
    result[:, 1, 0] = 1j * s
    result[:, 1, 1] = c
    return result


def shunt(b, count):
    result = np.zeros((count, 2, 2), dtype=complex)
    result[:, 0, 0] = 1
    result[:, 1, 1] = 1
    result[:, 1, 0] = 1j * b
    return result


def response(params, freqs, sblock):
    theta1, theta2, b1, b2 = params
    ratio = beta_ratio(freqs)
    mats = line(theta1 * ratio)
    mats = mats @ shunt(b1, len(freqs))
    mats = mats @ line(theta2 * ratio)
    mats = mats @ shunt(b2, len(freqs))
    zin = (mats[:, 0, 0] + mats[:, 0, 1]) / (mats[:, 1, 0] + mats[:, 1, 1])
    gamma_load = (zin - 1) / (zin + 1)
    s11, s12 = sblock[:, 0, 0], sblock[:, 0, 1]
    s21, s22 = sblock[:, 1, 0], sblock[:, 1, 1]
    gamma_in = s11 + s12 * s21 * gamma_load / (1 - s22 * gamma_load)
    return gamma_in, gamma_load


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("s4p", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    freqs, sblock = parse_s4p(args.s4p)

    def objective(x):
        gamma, _ = response(x, freqs, sblock)
        mag = np.abs(gamma)
        # Smooth max plus a small mean term improves equal-ripple behavior.
        return float(np.max(mag) + 0.08 * np.mean(mag))

    result = differential_evolution(
        objective,
        bounds=[(0.0, math.pi), (0.0, math.pi), (-5.0, 5.0), (-5.0, 5.0)],
        seed=20260922,
        popsize=18,
        maxiter=350,
        polish=True,
        workers=1,
    )
    gamma, gamma_load = response(result.x, freqs, sblock)
    rl = -20 * np.log10(np.maximum(np.abs(gamma), 1e-15))
    eta = 1 - np.abs(gamma) ** 2
    theta1, theta2, b1, b2 = result.x
    ratio = beta_ratio(np.array([10.25]))[0]
    c = 299792458.0
    fc = c / (2 * 22.86e-3)
    f0 = 10.25e9
    beta0 = 2 * math.pi / c * math.sqrt(f0**2 - fc**2)
    data = {
        "source": str(args.s4p),
        "model": "normalized lossless TL(theta1)-shunt(b1)-TL(theta2)-shunt(b2), matched termination",
        "solution": {
            "theta1_deg_at_10p25GHz": math.degrees(theta1),
            "theta2_deg_at_10p25GHz": math.degrees(theta2),
            "equivalent_length1_mm_WR90": 1000 * theta1 / beta0,
            "equivalent_length2_mm_WR90": 1000 * theta2 / beta0,
            "b1_normalized": b1,
            "b2_normalized": b2,
        },
        "predicted": {
            "return_loss_min_dB": float(np.min(rl)),
            "return_loss_mean_dB": float(np.mean(rl)),
            "efficiency_min": float(np.min(eta)),
            "efficiency_mean": float(np.mean(eta)),
            "gamma_load_max": float(np.max(np.abs(gamma_load))),
        },
        "optimizer": {"success": bool(result.success), "message": str(result.message), "objective": float(result.fun)},
        "warning": "This is a reduced normalized single-mode network target, not an HFSS-qualified geometry.",
    }
    text = json.dumps(data, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
