#!/usr/bin/env python3
"""Audit coherent Magic-T port efficiency and linear power scaling from S4P."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def read_s4p(path: Path):
    tokens = []
    for raw in path.read_text(encoding="ascii", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("!") and not line.startswith("#"):
            tokens.extend(line.split())
    if len(tokens) % 33:
        raise ValueError(f"S4P field count is invalid: {path}")
    freqs, matrices = [], []
    for k in range(0, len(tokens), 33):
        freqs.append(float(tokens[k]))
        values = [float(x) for x in tokens[k + 1:k + 33]]
        matrix = []
        for i in range(0, 32, 2):
            magnitude, degrees = values[i], values[i + 1]
            angle = math.radians(degrees)
            matrix.append(magnitude * complex(math.cos(angle), math.sin(angle)))
        matrices.append(matrix)
    return freqs, matrices


def run(path: Path):
    freqs, matrices = read_s4p(path)
    rows = []
    for freq, matrix in zip(freqs, matrices):
        # Port order from the v4 builder: P1=-X, P2=+X, P3=H-arm, P4=E-arm.
        # Equal in-phase incident waves on P1/P2 form the sum/H mode.
        b_sum = [matrix[i * 4] + matrix[i * 4 + 1] for i in range(4)]
        # Equal anti-phase incident waves form the difference/E mode.
        b_diff = [matrix[i * 4] - matrix[i * 4 + 1] for i in range(4)]
        incident = 2.0
        p_sum = [abs(value) ** 2 for value in b_sum]
        p_diff = [abs(value) ** 2 for value in b_diff]
        rows.append({
            "freq_GHz": freq,
            "sum_eta_H": p_sum[2] / incident,
            "sum_eta_E_leak": p_sum[3] / incident,
            "sum_eta_reflection": (p_sum[0] + p_sum[1]) / incident,
            "sum_eta_all_ports": sum(p_sum) / incident,
            "sum_balance_gap": 1.0 - sum(p_sum) / incident,
            "diff_eta_E": p_diff[3] / incident,
            "diff_eta_H_leak": p_diff[2] / incident,
        })
    return rows


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
    parser.add_argument("s4p", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()

    rows = run(args.s4p)
    summary = {
        "source": str(args.s4p),
        "port_mapping": {"P1": "-X", "P2": "+X", "P3": "H-arm/sum", "P4": "E-arm/difference"},
        "excitation": "a1=a2=1, a3=a4=0 for in-phase sum/H mode; normalization is 2 W incident in the S-parameter reference system",
        "band_GHz": [rows[0]["freq_GHz"], rows[-1]["freq_GHz"]],
        "points": len(rows),
        "metrics": {
            key: extrema(rows, key)
            for key in ("sum_eta_H", "sum_eta_E_leak", "sum_eta_reflection", "sum_eta_all_ports", "sum_balance_gap", "diff_eta_E", "diff_eta_H_leak")
        },
        "power_scaling": {},
        "interpretation": {
            "efficiency_gate": ">90% coherent sum/H output efficiency",
            "network_result": "The raw single-cell S4P can verify port-power accounting only; it cannot verify full four-way tree efficiency.",
            "high_power_result": "30 kW and 1 kW values below are linear port-power scaling. Peak E-field, conductor loss, breakdown and thermal limits remain unverified because the solve used PEC walls and save_fields=False.",
        },
    }
    for input_power in (30000.0, 1000.0):
        summary["power_scaling"][f"{int(input_power)}W"] = {
            "H_output_min_W": summary["metrics"]["sum_eta_H"]["min"] * input_power,
            "H_output_max_W": summary["metrics"]["sum_eta_H"]["max"] * input_power,
            "E_leak_max_W": summary["metrics"]["sum_eta_E_leak"]["max"] * input_power,
            "input_reflection_max_W": summary["metrics"]["sum_eta_reflection"]["max"] * input_power,
            "all_ports_min_W": summary["metrics"]["sum_eta_all_ports"]["min"] * input_power,
            "balance_gap_max_W": summary["metrics"]["sum_balance_gap"]["max"] * input_power,
        }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
