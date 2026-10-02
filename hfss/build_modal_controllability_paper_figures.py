#!/usr/bin/env python3
"""Regenerate the three reader-facing figures used by the modal-controllability paper.

The figures are written as LaTeX/TikZ/PGFPlots source so the paper remains
vector-native and reproducible without committing binary plot files.

Generated figures:
  paper/figures/fig_gamma_trajectories.tex
  paper/figures/fig_modal_angle_matrix.tex
  paper/figures/fig_singular_spectrum.tex
  paper/figures/fig_broadband_performance.tex
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from analyze_v8_modal_controllability import (
    central_column,
    load_case,
    stack_complex_columns,
    stack_full_columns,
)


PARAMETERS = ["lower_radius", "split_height", "upper_radius", "total_height"]
LABELS = {
    "lower_radius": r"$r_L$",
    "split_height": r"$h_s$",
    "upper_radius": r"$r_U$",
    "total_height": r"$H$",
}
HALF_STEPS_MM = {
    "lower_radius": 0.2,
    "split_height": 1.0,
    "upper_radius": 0.2,
    "total_height": 0.75,
}


def acute_angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return float("nan")
    c = float(np.dot(a, b) / denom)
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(abs(c)))


def final_paths(here: Path):
    v7 = here / "results" / "v7_stepped_post_local"
    v8 = here / "results" / "v8_modal_controllability"
    ts = "single_magictee_v4_full.s4p"
    center = v7 / "joint_l1p4_s6p2" / ts
    pairs = {
        "lower_radius": (
            v8 / "lower_minus" / ts,
            v7 / "joint_l1p6_s6p2" / ts,
        ),
        "split_height": (
            v8 / "split_minus" / ts,
            v7 / "joint_l1p4_s7p2" / ts,
        ),
        "upper_radius": (
            v8 / "upper_minus" / ts,
            v8 / "upper_plus" / ts,
        ),
        "total_height": (
            v8 / "total_minus" / ts,
            v8 / "total_plus" / ts,
        ),
    }
    return center, pairs


def identify(here: Path):
    center_path, pairs = final_paths(here)
    columns = {}
    for name in PARAMETERS:
        minus = load_case(pairs[name][0])
        plus = load_case(pairs[name][1])
        columns[name] = central_column(
            minus, plus, HALF_STEPS_MM[name]
        )

    j_plus = stack_complex_columns(columns, PARAMETERS, "plus")
    j_minus = stack_complex_columns(columns, PARAMETERS, "minus")
    j_full = stack_full_columns(columns, PARAMETERS)
    scale = np.diag([HALF_STEPS_MM[p] for p in PARAMETERS])

    freqs, center_sm = load_case(center_path)
    return {
        "freqs": freqs,
        "center_sm": center_sm,
        "j_plus": j_plus,
        "j_minus": j_minus,
        "j_full": j_full,
        "j_plus_step": j_plus @ scale,
        "j_minus_step": j_minus @ scale,
        "j_full_step": j_full @ scale,
    }


def write_gamma_figure(data, path: Path) -> None:
    freqs = data["freqs"]
    sm = data["center_sm"]
    gp = sm[:, 0, 0]
    gm = sm[:, 1, 1]

    rows = "\n".join(
        f"{f:.3f} {a.real:.8f} {a.imag:.8f} {b.real:.8f} {b.imag:.8f}"
        for f, a, b in zip(freqs, gp, gm)
    )

    text = rf"""\begin{{figure}}[t]
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
width=\columnwidth,
height=0.88\columnwidth,
axis equal image,
xmin=-0.8,xmax=0.8,
ymin=-0.8,ymax=0.8,
xlabel={{$\Re\{{\Gamma\}}$}},
ylabel={{$\Im\{{\Gamma\}}$}},
grid=both,
tick label style={{font=\scriptsize}},
label style={{font=\scriptsize}},
legend style={{font=\scriptsize,at={{(0.5,1.02)}},anchor=south,legend columns=2}},
]
\addplot[densely dashed,domain=0:360,samples=181,forget plot] ({{cos(x)}},{{sin(x)}});
\addplot+[thick,mark=none] table[x=gpr,y=gpi] {{
f gpr gpi gmr gmi
{rows}
}};
\addplot+[thick,mark=none] table[x=gmr,y=gmi] {{
f gpr gpi gmr gmi
{rows}
}};
\legend{{$\Gamma_+$,$\Gamma_-$}}
\end{{axis}}
\end{{tikzpicture}}
\caption{{Complex-plane trajectories of the even- and odd-mode reflection coefficients across 9--11.5~GHz. The trajectories remain inside their symmetry-protected parity blocks; residual performance variation is therefore associated with the frequency dependence of the allowed modal reflections rather than cross-parity conversion.}}
\label{{fig:gamma-trajectories}}
\end{{figure}}
"""
    path.write_text(text, encoding="utf-8")


def write_angle_figure(data, path: Path) -> None:
    j = data["j_full"]
    values = []
    for y in range(4):
        for x in range(4):
            angle = 0.0 if x == y else acute_angle_deg(j[:, x], j[:, y])
            values.append(f"{x}/{y}/{angle:.1f}")
    vals = ",\n".join(values)

    labels = ",".join(
        f"{i}/{LABELS[name]}" for i, name in enumerate(PARAMETERS)
    )

    text = rf"""\begin{{figure}}[t]
\centering
\begin{{tikzpicture}}[x=0.92cm,y=0.92cm]
\def\vals{{
{vals}}}
\foreach \x/\y/\v in \vals {{
  \pgfmathsetmacro{{\pct}}{{5+0.55*\v}}
  \fill[blue!\pct!white] (\x,-\y) rectangle ++(1,-1);
  \node[text=black,font=\scriptsize] at (\x+0.5,-\y-0.5) {{\v$^\circ$}};
}}
\draw (0,0) grid (4,-4);
\foreach \x/\lab in {{{labels}}}
  \node[font=\scriptsize,rotate=35,anchor=west] at (\x+0.5,0.08) {{\lab}};
\foreach \y/\lab in {{{labels}}}
  \node[font=\scriptsize,anchor=east] at (-0.08,-\y-0.5) {{\lab}};
\node[font=\scriptsize] at (2,-4.45) {{Full-band acute angle between response columns}};
\end{{tikzpicture}}
\caption{{Pairwise acute angles between the four full-band geometry-response columns. Large angles indicate controls that act in substantially different directions. The separation between $r_L$ and $r_U$ is the key evidence that splitting the post creates a non-redundant control direction.}}
\label{{fig:angle-matrix}}
\end{{figure}}
"""
    path.write_text(text, encoding="utf-8")


def singular_values(j: np.ndarray) -> np.ndarray:
    return np.linalg.svd(j, compute_uv=False)


def coords(values: np.ndarray) -> str:
    return " ".join(f"({i+1},{v:.8g})" for i, v in enumerate(values))


def write_singular_figure(data, path: Path) -> None:
    full = singular_values(data["j_full_step"])
    even = singular_values(data["j_plus_step"])
    odd = singular_values(data["j_minus_step"])

    text = rf"""\begin{{figure}}[t]
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
width=\columnwidth,
height=0.68\columnwidth,
ymode=log,
ymin=0.004,
ymax=1.4,
xlabel={{Singular-direction index}},
ylabel={{Step-normalized singular value}},
xtick={{1,2,3,4}},
grid=both,
minor y tick num=1,
legend style={{font=\scriptsize,at={{(0.5,1.03)}},anchor=south,legend columns=3}},
tick label style={{font=\scriptsize}},
label style={{font=\scriptsize}},
]
\addplot+[mark=o,thick] coordinates {{{coords(full)}}};
\addplot+[mark=square,thick] coordinates {{{coords(even)}}};
\addplot+[mark=triangle,thick] coordinates {{{coords(odd)}}};
\legend{{Full,Even/H,Odd/E}}
\end{{axis}}
\end{{tikzpicture}}
\caption{{Step-normalized singular spectra of the complete full-band Jacobian and its two parity blocks. The response space contains several strong directions together with one weak combination; the latter is a cancellation-dominated parameter combination rather than a collapse of the entire modal-control space.}}
\label{{fig:singular-spectrum}}
\end{{figure}}
"""
    path.write_text(text, encoding="utf-8")



def write_performance_figure(data, path: Path) -> None:
    freqs = data["freqs"]
    sm = data["center_sm"]

    eta_h = np.abs(sm[:, 2, 0]) ** 2
    eta_e = np.abs(sm[:, 3, 1]) ** 2
    rl_p = -20.0 * np.log10(np.maximum(np.abs(sm[:, 0, 0]), 1e-15))
    rl_m = -20.0 * np.log10(np.maximum(np.abs(sm[:, 1, 1]), 1e-15))

    forbidden = np.column_stack(
        [
            sm[:, 0, 1],
            sm[:, 0, 3],
            sm[:, 1, 2],
            sm[:, 2, 3],
        ]
    )
    iso = -np.max(
        20.0 * np.log10(np.maximum(np.abs(forbidden), 1e-15)),
        axis=1,
    )

    rows = "\n".join(
        f"{f:.3f} {h:.8f} {e:.8f} {rp:.6f} {rm:.6f} {ii:.6f}"
        for f, h, e, rp, rm, ii in zip(freqs, eta_h, eta_e, rl_p, rl_m, iso)
    )

    table = rf"""f etaH etaE rlP rlM iso
{rows}"""

    text = rf"""\begin{{figure*}}[t]
\centering
\begin{{minipage}}{{0.485\textwidth}}
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
width=\linewidth,height=0.62\linewidth,
xmin=9,xmax=11.5,ymin=0.60,ymax=1.02,
xlabel={{Frequency (GHz)}},ylabel={{Power-transfer efficiency}},
grid=both,
legend style={{font=\scriptsize,at={{(0.5,1.02)}},anchor=south,legend columns=2}},
tick label style={{font=\scriptsize}},label style={{font=\scriptsize}},
]
\addplot+[thick,mark=none] table[x=f,y=etaH] {{
{table}
}};
\addplot+[thick,mark=none] table[x=f,y=etaE] {{
{table}
}};
\legend{{H/sum,E/difference}}
\end{{axis}}
\end{{tikzpicture}}
\end{{minipage}}\hfill
\begin{{minipage}}{{0.485\textwidth}}
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
width=\linewidth,height=0.62\linewidth,
xmin=9,xmax=11.5,ymin=0,ymax=60,
xlabel={{Frequency (GHz)}},ylabel={{Return loss / parity isolation (dB)}},
grid=both,
legend style={{font=\scriptsize,at={{(0.5,1.02)}},anchor=south,legend columns=3}},
tick label style={{font=\scriptsize}},label style={{font=\scriptsize}},
]
\addplot+[thick,mark=none] table[x=f,y=rlP] {{
{table}
}};
\addplot+[thick,mark=none] table[x=f,y=rlM] {{
{table}
}};
\addplot+[thick,mark=none,densely dashed] table[x=f,y=iso] {{
{table}
}};
\legend{{$RL_+$,$RL_-$,forbidden parity isolation}}
\end{{axis}}
\end{{tikzpicture}}
\end{{minipage}}
\caption{{Broadband modal performance of the evaluated single-cell PEC geometry. Left: desired H/sum and E/difference power-transfer efficiencies. Right: even- and odd-mode return losses together with the minimum isolation from forbidden parity conversion. The transfer curves show useful average performance across the band, whereas the weaker band-edge points remain an in-block matching problem rather than a parity-leakage problem.}}
\label{{fig:broadband-performance}}
\end{{figure*}}
"""
    path.write_text(text, encoding="utf-8")

def main() -> None:
    here = Path(__file__).resolve().parent
    out = here.parent / "paper" / "figures"
    out.mkdir(parents=True, exist_ok=True)

    data = identify(here)
    write_gamma_figure(data, out / "fig_gamma_trajectories.tex")
    write_angle_figure(data, out / "fig_modal_angle_matrix.tex")
    write_singular_figure(data, out / "fig_singular_spectrum.tex")
    write_performance_figure(data, out / "fig_broadband_performance.tex")

    print("wrote:", out / "fig_gamma_trajectories.tex")
    print("wrote:", out / "fig_modal_angle_matrix.tex")
    print("wrote:", out / "fig_singular_spectrum.tex")
    print("wrote:", out / "fig_broadband_performance.tex")


if __name__ == "__main__":
    main()
