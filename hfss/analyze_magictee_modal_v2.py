#!/usr/bin/env python3
"""Analyze a 4-port magic-tee Touchstone file in the natural parity basis.

Physical ports:
    P1, P2 : collinear arms
    P3     : H arm
    P4     : E arm

Modal basis:
    c+ = (P1 + P2)/sqrt(2)
    c- = (P1 - P2)/sqrt(2)
    H  = P3
    E  = P4

For an ideal magic tee, the desired channels are c+ <-> H and c- <-> E.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np


W = np.array(
    [
        [1 / math.sqrt(2), 1 / math.sqrt(2), 0, 0],
        [1 / math.sqrt(2), -1 / math.sqrt(2), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ],
    dtype=complex,
)

NAMES = ["c_plus", "c_minus", "H", "E"]


def parse_touchstone_ma(path: Path):
    numbers = []
    option = ""
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            option = line.upper()
            continue
        numbers.extend(float(token) for token in line.split())

    if "MA" not in option:
        raise ValueError(f"Only magnitude-angle Touchstone is supported: {option}")

    record_size = 1 + 2 * 16
    if len(numbers) % record_size:
        raise ValueError("Unexpected numeric count for a 4-port Touchstone file")

    records = []
    for start in range(0, len(numbers), record_size):
        row = numbers[start : start + record_size]
        freq = row[0]
        s = np.zeros((4, 4), dtype=complex)
        k = 1
        for r in range(4):
            for c in range(4):
                mag = row[k]
                ang = math.radians(row[k + 1])
                s[r, c] = mag * np.exp(1j * ang)
                k += 2
        records.append((freq, s))
    return records


def db20(z):
    return 20 * np.log10(np.maximum(np.abs(z), 1e-15))


def summarize(path: Path):
    records = parse_touchstone_ma(path)

    reflections = []
    desired_h = []
    desired_e = []
    forbidden = []

    for freq, s in records:
        sm = W @ s @ W.T

        reflections.append((freq, np.diag(sm)))
        desired_h.append((freq, sm[2, 0]))
        desired_e.append((freq, sm[3, 1]))

        forbidden_terms = np.array(
            [
                sm[0, 1],  # c+ <-> c-
                sm[0, 3],  # c+ <-> E
                sm[1, 2],  # c- <-> H
                sm[2, 3],  # H <-> E
            ],
            dtype=complex,
        )
        forbidden.append((freq, forbidden_terms))

    freqs = np.array([f for f, _ in reflections])
    refl = np.array([v for _, v in reflections])
    th = np.array([v for _, v in desired_h])
    te = np.array([v for _, v in desired_e])
    leak = np.array([v for _, v in forbidden])

    print(f"Touchstone: {path}")
    print(f"Band: {freqs[0]:.3f}--{freqs[-1]:.3f} GHz, points={len(freqs)}")

    print("\nWorst modal return loss")
    for i, name in enumerate(NAMES):
        rl = -db20(refl[:, i])
        j = int(np.argmin(rl))
        print(f"  {name:7s}: {rl[j]:8.3f} dB at {freqs[j]:.3f} GHz")

    for label, arr in [("c+ <-> H", th), ("c- <-> E", te)]:
        gain = db20(arr)
        j = int(np.argmin(gain))
        print(f"Minimum desired coupling {label}: {gain[j]:.3f} dB at {freqs[j]:.3f} GHz")

    worst_leak = np.max(db20(leak), axis=1)
    j = int(np.argmax(worst_leak))
    print(f"Worst forbidden coupling: {worst_leak[j]:.3f} dB at {freqs[j]:.3f} GHz")

    j0 = int(np.argmin(np.abs(freqs - 10.2)))
    sm0 = W @ records[j0][1] @ W.T
    print("\n|S_modal| at %.3f GHz" % freqs[j0])
    for row in sm0:
        print("  " + " ".join(f"{abs(z):.6f}" for z in row))

    print("\nTargets:")
    print("  external 22 dB -> |Gamma| < 0.07943")
    print("  internal 25 dB -> |Gamma| < 0.05623")
    print("  desired topology: c+<->H and c-<->E")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("touchstone", type=Path)
    summarize(p.parse_args().touchstone)


if __name__ == "__main__":
    main()
