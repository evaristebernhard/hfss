#!/usr/bin/env python3
"""Screen different first- and second-stage Magic-T cells in a four-way tree."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

import cascade_four_way_touchstone as cascade


def parse_candidate(value: str):
    if "=" not in value:
        raise argparse.ArgumentTypeError("candidate must be NAME=PATH")
    name, raw_path = value.split("=", 1)
    path = Path(raw_path)
    if not name or not path.exists():
        raise argparse.ArgumentTypeError(f"invalid candidate: {value}")
    return name, path


def evaluate_mixed(frequencies, cells_ab, cells_c, length_mm):
    rows = []
    for frequency, cell_ab, cell_c in zip(frequencies, cells_ab, cells_c):
        network = cascade.cascade_mixed_at_frequency(
            cell_ab, cell_ab, cell_c, float(frequency), length_mm, length_mm
        )
        rows.append({"freq_GHz": float(frequency), **cascade.coherent_metrics(network)})
    return rows


def load_candidates(specifications):
    loaded = {}
    reference_frequencies = None
    for name, path in specifications:
        frequencies, cells = cascade.read_s4p(path)
        if reference_frequencies is None:
            reference_frequencies = frequencies
        elif len(frequencies) != len(reference_frequencies) or not np.allclose(frequencies, reference_frequencies):
            raise ValueError(f"frequency grid mismatch for {name}")
        loaded[name] = {"path": path, "cells": cells}
    return reference_frequencies, loaded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", action="append", type=parse_candidate, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--length-min-mm", type=float, default=0.0)
    parser.add_argument("--length-max-mm", type=float, default=30.0)
    parser.add_argument("--length-step-mm", type=float, default=0.25)
    parser.add_argument("--refine-half-span-mm", type=float, default=0.5)
    parser.add_argument("--refine-step-mm", type=float, default=0.02)
    args = parser.parse_args()

    frequencies, candidates = load_candidates(args.candidate)
    coarse = []
    names = list(candidates)
    for first_name in names:
        for second_name in names:
            length = args.length_min_mm
            best = None
            while length <= args.length_max_mm + 1e-9:
                rows = evaluate_mixed(
                    frequencies,
                    candidates[first_name]["cells"],
                    candidates[second_name]["cells"],
                    length,
                )
                eta = [row["eta_output"] for row in rows]
                record = {
                    "first_stage": first_name,
                    "second_stage": second_name,
                    "length_mm": length,
                    "eta_min": min(eta),
                    "eta_mean": sum(eta) / len(eta),
                    "eta_max": max(eta),
                    "active_return_loss_min_dB": min(row["active_return_loss_min_dB"] for row in rows),
                    "matched_input_isolation_min_dB": min(row["matched_input_isolation_min_dB"] for row in rows),
                }
                if best is None or (record["eta_min"], record["eta_mean"]) > (best["eta_min"], best["eta_mean"]):
                    best = record
                length += args.length_step_mm
            coarse.append(best)

    coarse_best = max(coarse, key=lambda row: (row["eta_min"], row["eta_mean"]))
    first_name = coarse_best["first_stage"]
    second_name = coarse_best["second_stage"]
    refined = []
    length = max(args.length_min_mm, coarse_best["length_mm"] - args.refine_half_span_mm)
    stop = min(args.length_max_mm, coarse_best["length_mm"] + args.refine_half_span_mm)
    while length <= stop + 1e-9:
        rows = evaluate_mixed(
            frequencies,
            candidates[first_name]["cells"],
            candidates[second_name]["cells"],
            length,
        )
        summary = cascade.summarize(rows)
        refined.append({
            "first_stage": first_name,
            "second_stage": second_name,
            "length_mm": length,
            "eta_min": summary["eta_output"]["min"],
            "eta_mean": summary["eta_output"]["mean"],
            "eta_max": summary["eta_output"]["max"],
            "active_return_loss_min_dB": summary["active_return_loss_min_dB"]["min"],
            "matched_input_isolation_min_dB": summary["matched_input_isolation_min_dB"]["min"],
        })
        length += args.refine_step_mm
    best = max(refined, key=lambda row: (row["eta_min"], row["eta_mean"]))
    final_rows = evaluate_mixed(
        frequencies,
        candidates[first_name]["cells"],
        candidates[second_name]["cells"],
        best["length_mm"],
    )
    metrics = cascade.summarize(final_rows)
    report = {
        "candidate_count": len(candidates),
        "combination_count": len(candidates) ** 2,
        "best": best,
        "first_stage_source": str(candidates[first_name]["path"]),
        "second_stage_source": str(candidates[second_name]["path"]),
        "metrics": metrics,
        "power_scaling_30000W": {
            "output_min_W": 30000.0 * metrics["eta_output"]["min"],
            "output_max_W": 30000.0 * metrics["eta_output"]["max"],
            "reflection_max_W": 30000.0 * metrics["eta_input_reflection"]["max"],
        },
        "warning": "Network optimization using existing PEC single-cell samples; selected geometry requires full 3-D confirmation.",
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "optimization.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for filename, records in (("combination_best.csv", coarse), ("length_refinement.csv", refined), ("frequency_response.csv", final_rows)):
        with (args.output_dir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
