#!/usr/bin/env python3
"""Cascade three identical Magic-T S4P cells into a four-way binary tree.

Topology:

    IN1/IN2 -> MT-A H port -- line A --> MT-C collinear port 1
    IN3/IN4 -> MT-B H port -- line B --> MT-C collinear port 2
    MT-C H port -> OUT

All three E/difference ports remain external and are evaluated with matched
terminations (zero incident waves).  The script scans the common interstage
WR90 length, then reports differential-length sensitivity around the optimum.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


C0 = 299792458.0
WR90_A_M = 22.86e-3


def read_s4p(path: Path):
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
    if len(tokens) % 33:
        raise ValueError("invalid four-port Touchstone record count")

    frequencies = []
    matrices = []
    for start in range(0, len(tokens), 33):
        frequencies.append(float(tokens[start]))
        values = [float(value) for value in tokens[start + 1 : start + 33]]
        matrix = np.zeros((4, 4), dtype=complex)
        cursor = 0
        for row in range(4):
            for column in range(4):
                magnitude = values[cursor]
                angle = math.radians(values[cursor + 1])
                matrix[row, column] = magnitude * np.exp(1j * angle)
                cursor += 2
        matrices.append(matrix)
    return np.asarray(frequencies), np.asarray(matrices)


def propagation_phase(frequency_ghz: float, length_mm: float) -> complex:
    frequency_hz = frequency_ghz * 1e9
    cutoff_hz = C0 / (2.0 * WR90_A_M)
    beta = (2.0 * math.pi / C0) * math.sqrt(max(frequency_hz**2 - cutoff_hz**2, 0.0))
    return np.exp(-1j * beta * length_mm * 1e-3)


def cascade_mixed_at_frequency(
    cell_a: np.ndarray,
    cell_b: np.ndarray,
    cell_c: np.ndarray,
    frequency_ghz: float,
    length_a_mm: float,
    length_b_mm: float,
):
    system = np.zeros((12, 12), dtype=complex)
    system[0:4, 0:4] = cell_a
    system[4:8, 4:8] = cell_b
    system[8:12, 8:12] = cell_c

    # User-facing external order: four inputs, output, then the three dumps.
    external = [0, 1, 4, 5, 10, 3, 7, 11]
    # A.H, C.P1, B.H, C.P2.
    internal = [2, 8, 6, 9]
    see = system[np.ix_(external, external)]
    sei = system[np.ix_(external, internal)]
    sie = system[np.ix_(internal, external)]
    sii = system[np.ix_(internal, internal)]

    connection = np.zeros((4, 4), dtype=complex)
    phase_a = propagation_phase(frequency_ghz, length_a_mm)
    phase_b = propagation_phase(frequency_ghz, length_b_mm)
    connection[0, 1] = connection[1, 0] = phase_a
    connection[2, 3] = connection[3, 2] = phase_b
    internal_drive = np.linalg.solve(
        np.eye(4, dtype=complex) - connection @ sii,
        connection @ sie,
    )
    return see + sei @ internal_drive


def cascade_at_frequency(cell: np.ndarray, frequency_ghz: float, length_a_mm: float, length_b_mm: float):
    return cascade_mixed_at_frequency(
        cell, cell, cell, frequency_ghz, length_a_mm, length_b_mm
    )


def coherent_metrics(network: np.ndarray):
    incident = np.zeros(8, dtype=complex)
    incident[0:4] = 1.0
    outgoing = network @ incident
    total_incident = 4.0
    input_power = float(np.sum(np.abs(outgoing[0:4]) ** 2) / total_incident)
    output_power = float(abs(outgoing[4]) ** 2 / total_incident)
    dump_power = float(np.sum(np.abs(outgoing[5:8]) ** 2) / total_incident)
    accounted = float(np.sum(np.abs(outgoing) ** 2) / total_incident)
    active_rl = min(-20.0 * math.log10(max(abs(value), 1e-15)) for value in outgoing[0:4])

    transfers = network[4, 0:4]
    magnitudes = np.abs(transfers)
    phases = np.unwrap(np.angle(transfers))
    amplitude_spread_db = 20.0 * math.log10(max(magnitudes) / max(min(magnitudes), 1e-15))
    phase_spread_deg = math.degrees(float(max(phases) - min(phases)))
    isolation_terms = [abs(network[row, column]) for row in range(4) for column in range(4) if row != column]
    matched_isolation_db = -20.0 * math.log10(max(max(isolation_terms), 1e-15))
    return {
        "eta_output": output_power,
        "eta_input_reflection": input_power,
        "eta_dump": dump_power,
        "eta_all_external": accounted,
        "active_return_loss_min_dB": active_rl,
        "matched_input_isolation_min_dB": matched_isolation_db,
        "output_path_amplitude_spread_dB": amplitude_spread_db,
        "output_path_phase_spread_deg": phase_spread_deg,
    }


def evaluate(frequencies, cells, common_length_mm: float, delta_length_mm: float = 0.0):
    length_a = common_length_mm + 0.5 * delta_length_mm
    length_b = common_length_mm - 0.5 * delta_length_mm
    networks = []
    rows = []
    for frequency, cell in zip(frequencies, cells):
        network = cascade_at_frequency(cell, float(frequency), length_a, length_b)
        networks.append(network)
        rows.append({"freq_GHz": float(frequency), **coherent_metrics(network)})
    return np.asarray(networks), rows


def summarize(rows):
    def extrema(key):
        low = min(rows, key=lambda row: row[key])
        high = max(rows, key=lambda row: row[key])
        return {
            "min": low[key],
            "min_freq_GHz": low["freq_GHz"],
            "max": high[key],
            "max_freq_GHz": high["freq_GHz"],
            "mean": sum(row[key] for row in rows) / len(rows),
        }

    return {key: extrema(key) for key in rows[0] if key != "freq_GHz"}


def write_s8p(path: Path, frequencies, networks):
    lines = [
        "! Four-way cascade: IN1 IN2 IN3 IN4 OUT DUMP_A DUMP_B DUMP_C",
        "# GHz S MA R 50",
    ]
    for frequency, network in zip(frequencies, networks):
        fields = [f"{float(frequency):.12g}"]
        for row in range(8):
            for column in range(8):
                value = network[row, column]
                fields.extend([f"{abs(value):.12g}", f"{math.degrees(np.angle(value)):.12g}"])
        lines.append(" ".join(fields))
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("s4p", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--length-min-mm", type=float, default=0.0)
    parser.add_argument("--length-max-mm", type=float, default=30.0)
    parser.add_argument("--length-step-mm", type=float, default=0.25)
    parser.add_argument("--delta-max-mm", type=float, default=2.0)
    parser.add_argument("--delta-step-mm", type=float, default=0.25)
    args = parser.parse_args()

    frequencies, cells = read_s4p(args.s4p)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    common_scan = []
    length = args.length_min_mm
    while length <= args.length_max_mm + 1e-9:
        _, rows = evaluate(frequencies, cells, length, 0.0)
        eta = [row["eta_output"] for row in rows]
        common_scan.append({
            "common_length_mm": length,
            "eta_output_min": min(eta),
            "eta_output_mean": sum(eta) / len(eta),
            "eta_output_max": max(eta),
        })
        length += args.length_step_mm
    best = max(common_scan, key=lambda row: (row["eta_output_min"], row["eta_output_mean"]))
    best_length = best["common_length_mm"]

    differential_scan = []
    delta = -args.delta_max_mm
    while delta <= args.delta_max_mm + 1e-9:
        _, rows = evaluate(frequencies, cells, best_length, delta)
        eta = [row["eta_output"] for row in rows]
        differential_scan.append({
            "delta_length_mm": delta,
            "eta_output_min": min(eta),
            "eta_output_mean": sum(eta) / len(eta),
            "eta_output_max": max(eta),
        })
        delta += args.delta_step_mm

    networks, rows = evaluate(frequencies, cells, best_length, 0.0)
    metrics = summarize(rows)
    summary = {
        "source_cell": str(args.s4p),
        "topology": "three identical 4-port Magic-T cells; A.H->C.P1 and B.H->C.P2; all E ports matched",
        "external_port_order": ["IN1", "IN2", "IN3", "IN4", "OUT", "DUMP_A", "DUMP_B", "DUMP_C"],
        "band_GHz": [float(frequencies[0]), float(frequencies[-1])],
        "best_equal_interstage_length_mm": best_length,
        "metrics": metrics,
        "power_scaling": {
            "total_input_30000W": {
                "output_min_W": 30000.0 * metrics["eta_output"]["min"],
                "output_max_W": 30000.0 * metrics["eta_output"]["max"],
                "reflected_max_W": 30000.0 * metrics["eta_input_reflection"]["max"],
                "dump_max_W": 30000.0 * metrics["eta_dump"]["max"],
            },
            "total_input_1000W": {
                "output_min_W": 1000.0 * metrics["eta_output"]["min"],
                "output_max_W": 1000.0 * metrics["eta_output"]["max"],
            },
        },
        "warning": "Lossless PEC S-parameter cascade only; conductor loss, peak field, breakdown, thermal behavior and 3-D interstage discontinuities are not included.",
    }

    (args.output_dir / "cascade_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for filename, records in (("frequency_response.csv", rows), ("common_length_scan.csv", common_scan), ("differential_length_scan.csv", differential_scan)):
        with (args.output_dir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    write_s8p(args.output_dir / "four_way_cascade.s8p", frequencies, networks)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
