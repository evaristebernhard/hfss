#!/usr/bin/env python3
"""Audit an eight-port four-way combiner under four coherent input drives."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


def read_s8p(path: Path):
    tokens = []
    option = ""
    for raw in path.read_text(encoding="ascii", errors="ignore").splitlines():
        line = raw.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            option = line.upper()
            continue
        tokens.extend(line.split())
    if "MA" not in option:
        raise ValueError("only MA Touchstone input is supported")
    fields = 1 + 2 * 8 * 8
    if len(tokens) % fields:
        raise ValueError("invalid eight-port Touchstone record count")
    frequencies = []
    matrices = []
    for start in range(0, len(tokens), fields):
        frequencies.append(float(tokens[start]))
        values = [float(value) for value in tokens[start + 1 : start + fields]]
        matrix = np.zeros((8, 8), dtype=complex)
        cursor = 0
        for row in range(8):
            for column in range(8):
                magnitude = values[cursor]
                angle = math.radians(values[cursor + 1])
                matrix[row, column] = magnitude * np.exp(1j * angle)
                cursor += 2
        matrices.append(matrix)
    return np.asarray(frequencies), np.asarray(matrices)


def row_metrics(frequency: float, matrix: np.ndarray):
    incident = np.zeros(8, dtype=complex)
    incident[0:4] = 1.0
    outgoing = matrix @ incident
    scale = 4.0
    transfers = matrix[4, 0:4]
    transfer_magnitude = np.abs(transfers)
    transfer_phase = np.unwrap(np.angle(transfers))
    isolation = max(abs(matrix[row, column]) for row in range(4) for column in range(4) if row != column)
    singular_max = float(np.linalg.svd(matrix, compute_uv=False)[0])
    return {
        "freq_GHz": float(frequency),
        "eta_output": float(abs(outgoing[4]) ** 2 / scale),
        "eta_input_reflection": float(np.sum(np.abs(outgoing[0:4]) ** 2) / scale),
        "eta_dump": float(np.sum(np.abs(outgoing[5:8]) ** 2) / scale),
        "eta_all_external": float(np.sum(np.abs(outgoing) ** 2) / scale),
        "active_return_loss_min_dB": min(-20.0 * math.log10(max(abs(value), 1e-15)) for value in outgoing[0:4]),
        "matched_input_isolation_min_dB": -20.0 * math.log10(max(isolation, 1e-15)),
        "output_path_amplitude_spread_dB": 20.0 * math.log10(max(transfer_magnitude) / max(min(transfer_magnitude), 1e-15)),
        "output_path_phase_spread_deg": math.degrees(float(max(transfer_phase) - min(transfer_phase))),
        "reciprocity_error_max": float(np.max(np.abs(matrix - matrix.T))),
        "singular_value_max": singular_max,
    }


def extrema(rows, key):
    low = min(rows, key=lambda row: row[key])
    high = max(rows, key=lambda row: row[key])
    return {
        "min": low[key],
        "min_freq_GHz": low["freq_GHz"],
        "max": high[key],
        "max_freq_GHz": high["freq_GHz"],
        "mean": sum(row[key] for row in rows) / len(rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("s8p", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reference-s8p", type=Path)
    args = parser.parse_args()
    frequencies, matrices = read_s8p(args.s8p)
    rows = [row_metrics(frequency, matrix) for frequency, matrix in zip(frequencies, matrices)]
    metric_names = [name for name in rows[0] if name != "freq_GHz"]
    summary = {
        "source": str(args.s8p),
        "port_order": ["IN1", "IN2", "IN3", "IN4", "OUT", "DUMP_A", "DUMP_B", "DUMP_C"],
        "excitation": "a1=a2=a3=a4=1; a5..a8=0; total incident power normalized to 4 W",
        "band_GHz": [float(frequencies[0]), float(frequencies[-1])],
        "points": len(rows),
        "metrics": {name: extrema(rows, name) for name in metric_names},
    }
    summary["power_scaling"] = {
        "total_input_30000W": {
            "output_min_W": 30000.0 * summary["metrics"]["eta_output"]["min"],
            "output_max_W": 30000.0 * summary["metrics"]["eta_output"]["max"],
            "reflection_max_W": 30000.0 * summary["metrics"]["eta_input_reflection"]["max"],
            "dump_max_W": 30000.0 * summary["metrics"]["eta_dump"]["max"],
        },
        "total_input_1000W": {
            "output_min_W": 1000.0 * summary["metrics"]["eta_output"]["min"],
            "output_max_W": 1000.0 * summary["metrics"]["eta_output"]["max"],
        },
    }

    if args.reference_s8p:
        ref_frequencies, ref_matrices = read_s8p(args.reference_s8p)
        reference_rows = []
        for frequency in frequencies:
            index = int(np.argmin(np.abs(ref_frequencies - frequency)))
            if abs(float(ref_frequencies[index]) - float(frequency)) > 1e-6:
                raise ValueError(f"reference lacks frequency {frequency} GHz")
            reference_rows.append(row_metrics(float(frequency), ref_matrices[index]))
        eta_error = [row["eta_output"] - reference["eta_output"] for row, reference in zip(rows, reference_rows)]
        summary["reference_comparison"] = {
            "source": str(args.reference_s8p),
            "eta_output_error_min": min(eta_error),
            "eta_output_error_max": max(eta_error),
            "eta_output_error_rms": math.sqrt(sum(value * value for value in eta_error) / len(eta_error)),
        }
        for row, reference, error in zip(rows, reference_rows, eta_error):
            row["reference_eta_output"] = reference["eta_output"]
            row["eta_output_error"] = error

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (args.output_dir / "audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
