#!/usr/bin/env python3
"""Run the Stage-A g2/terminal-ridge sweep from the v2 design note."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "scripts" / "wsl_pyaedt_launcher.sh"
WIN_ROOT = r"C:\Users\chaoy\Documents\single_magictee_v2_stageA"
WSL_ROOT = Path("/mnt/c/Users/chaoy/Documents/single_magictee_v2_stageA")
RESULT_ROOT = REPO / "hfss" / "results" / "v2_stage_a"

G2_VALUES = [4.6, 5.0, 5.4, 5.8]
TERMINAL_VALUES = [4.5, 6.0, 7.5]

sys.path.insert(0, str(REPO / "hfss"))
from analyze_magictee_modal_v2 import W, db20, parse_touchstone_ma  # noqa: E402


def tag(g2: float, terminal: float) -> str:
    return f"g2_{g2:.2f}mm_lt_{terminal:.2f}mm".replace(".", "p")


def summarize(path: Path) -> dict[str, float]:
    records = parse_touchstone_ma(path)
    freqs = np.array([freq for freq, _ in records])
    refl = []
    desired_h = []
    desired_e = []
    forbidden = []
    for _, s in records:
        sm = W @ s @ W.T
        refl.append(np.diag(sm))
        desired_h.append(sm[2, 0])
        desired_e.append(sm[3, 1])
        forbidden.append([sm[0, 1], sm[0, 3], sm[1, 2], sm[2, 3]])

    refl = np.asarray(refl)
    desired_h = np.asarray(desired_h)
    desired_e = np.asarray(desired_e)
    forbidden = np.asarray(forbidden)
    rl = -db20(refl)
    h_db = db20(desired_h)
    e_db = db20(desired_e)
    leak_db = np.max(db20(forbidden), axis=1)

    return {
        "c_plus_rl_min_dB": float(np.min(rl[:, 0])),
        "c_minus_rl_min_dB": float(np.min(rl[:, 1])),
        "H_rl_min_dB": float(np.min(rl[:, 2])),
        "E_rl_min_dB": float(np.min(rl[:, 3])),
        "c_plus_to_H_min_dB": float(np.min(h_db)),
        "c_minus_to_E_min_dB": float(np.min(e_db)),
        "worst_forbidden_dB": float(np.max(leak_db)),
        "band_start_GHz": float(freqs[0]),
        "band_stop_GHz": float(freqs[-1]),
        "points": int(len(freqs)),
    }


def main() -> None:
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    summary = []

    for g2 in G2_VALUES:
        for terminal in TERMINAL_VALUES:
            case = tag(g2, terminal)
            windows_output = WIN_ROOT + "\\" + case
            case_dir = RESULT_ROOT / case
            case_dir.mkdir(parents=True, exist_ok=True)
            log_path = case_dir / "run.log"

            command = [
                str(LAUNCHER),
                "hfss/build_single_magictee_v2.py",
                "--version",
                "2025.2",
                "--output",
                windows_output,
                "--non-graphical",
                "--solve",
                "--g2",
                str(g2),
                "--terminal-ridge-len",
                str(terminal),
            ]
            print(f"\n=== {case} ===", flush=True)
            completed = subprocess.run(
                command,
                cwd=REPO,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            log_path.write_text(completed.stdout, encoding="utf-8")

            s4p = WSL_ROOT / case / "single_magictee_v2.s4p"
            result = {"case": case, "g2_mm": g2, "terminal_ridge_len_mm": terminal}
            result["returncode"] = completed.returncode
            if completed.returncode == 0 and s4p.is_file():
                copied = case_dir / "single_magictee_v2.s4p"
                shutil.copy2(s4p, copied)
                result.update(summarize(copied))
                print(json.dumps(result, indent=2), flush=True)
            else:
                result["error"] = "HFSS solve or Touchstone export failed"
                print(result, flush=True)
            summary.append(result)

    (RESULT_ROOT / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"\nSummary: {RESULT_ROOT / 'summary.json'}")


if __name__ == "__main__":
    main()
