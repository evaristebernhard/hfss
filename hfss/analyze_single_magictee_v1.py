#!/usr/bin/env python3
"""Analyze the HFSS four-port Touchstone result without scikit-rf."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np


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


def parse_touchstone_ma(path: Path):
    """Read a 4-port Touchstone file with GHz / magnitude-angle data."""
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
        raise ValueError(f"Only MA Touchstone format is supported: {option}")

    record_size = 1 + 2 * 16
    if len(numbers) % record_size:
        raise ValueError(
            f"Unexpected numeric count {len(numbers)} for 4-port records"
        )

    records = []
    for start in range(0, len(numbers), record_size):
        row = numbers[start : start + record_size]
        freq_ghz = row[0]
        s = np.zeros((4, 4), dtype=complex)
        for k in range(16):
            magnitude = row[1 + 2 * k]
            phase_rad = math.radians(row[2 + 2 * k])
            s[k // 4, k % 4] = magnitude * np.exp(1j * phase_rad)
        records.append((freq_ghz, s))
    return records


def db20(z):
    return 20.0 * np.log10(np.maximum(np.abs(z), 1e-15))


def analyze(path: Path, csv_path: Path | None = None):
    records = parse_touchstone_ma(path)
    freqs = np.array([freq for freq, _ in records])
    port_rl = []
    modal_rl = []
    modal_conversion = []

    for _, s in records:
        sm = U @ s @ U.conj().T
        port_rl.append(-db20(np.diag(s)))
        modal_rl.append(-db20(np.diag(sm)))
        offdiag = sm.copy()
        np.fill_diagonal(offdiag, np.nan)
        modal_conversion.append(np.nanmax(db20(offdiag)))

    port_rl = np.asarray(port_rl)
    modal_rl = np.asarray(modal_rl)
    modal_conversion = np.asarray(modal_conversion)

    print(f"Touchstone: {path}")
    print(f"Points: {len(freqs)}, band: {freqs[0]:.3f}--{freqs[-1]:.3f} GHz")
    print("\nMinimum physical-port return loss")
    for i in range(4):
        j = int(np.argmin(port_rl[:, i]))
        print(f"  P{i + 1}: {port_rl[j, i]:8.3f} dB at {freqs[j]:.3f} GHz")

    print("\nMinimum mixed-mode diagonal return loss")
    for i, name in enumerate(MODE_NAMES):
        j = int(np.argmin(modal_rl[:, i]))
        print(f"  {name:6s}: {modal_rl[j, i]:8.3f} dB at {freqs[j]:.3f} GHz")

    j = int(np.argmax(modal_conversion))
    print(
        "\nWorst mixed-mode conversion amplitude: "
        f"{modal_conversion[j]:.3f} dB at {freqs[j]:.3f} GHz"
    )
    print("Targets: physical/mixed-mode RL >= 22/25 dB")

    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                [
                    "freq_GHz",
                    *[f"P{i + 1}_RL_dB" for i in range(4)],
                    *[f"{name}_RL_dB" for name in MODE_NAMES],
                    "worst_modal_conversion_dB",
                ]
            )
            for i, freq in enumerate(freqs):
                writer.writerow(
                    [
                        freq,
                        *port_rl[i],
                        *modal_rl[i],
                        modal_conversion[i],
                    ]
                )
        print("CSV:", csv_path)

    return {
        "freqs": freqs,
        "port_rl": port_rl,
        "modal_rl": modal_rl,
        "modal_conversion": modal_conversion,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("touchstone", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    analyze(args.touchstone, args.csv)


if __name__ == "__main__":
    main()
