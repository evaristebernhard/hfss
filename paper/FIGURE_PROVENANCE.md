# Figure Provenance

This file is the source-of-truth map for every figure used by the paper.

| Figure source | Paper role | Type | Primary source | Regeneration / edit method |
|---|---|---|---|---|
| `figures/fig_geometry_schematic.tex` | Conceptual parity + control architecture | hand-authored TikZ | paper theory | edit directly |
| `figures/fig_dimensioned_design_layout.tex` | Dimensioned single-cell layout | builder-derived TikZ | `hfss/build_single_magictee_v4_full.py`, `hfss/build_single_magictee_v6_stepped_post.py`, final nominal parameters | edit only if builder geometry changes |
| `figures/fig_gamma_trajectories.tex` | complex-plane `Gamma_+` / `Gamma_-` trajectories | generated PGFPlots | nominal center `.s4p` | `python ../hfss/build_modal_controllability_paper_figures.py` |
| `figures/fig_modal_angle_matrix.tex` | pairwise Jacobian-column angles | generated TikZ | central-difference perturbation `.s4p` files | same figure generator |
| `figures/fig_singular_spectrum.tex` | full/even/odd singular spectra | generated PGFPlots | central-difference perturbation `.s4p` files | same figure generator |
| `figures/fig_broadband_performance.tex` | H/E transfer, modal RL, forbidden parity isolation | generated PGFPlots | nominal center `.s4p` | same figure generator |
| `assets/hfss_single_cell_model.png` | real AEDT model view | AEDT export | nominal `.aedt` | `scripts/wsl_pyaedt_launcher.sh hfss/export_paper_hfss_figures.py` |
| `assets/hfss_even_H_field.png` | even excitation field view | AEDT field export | nominal `.aedt`, equal-phase P1/P2 | same AEDT export script |
| `assets/hfss_odd_E_field.png` | odd excitation field view | AEDT field export | nominal `.aedt`, 180-deg P1/P2 | same AEDT export script |

## Exact Touchstone inputs

Nominal center:

```text
hfss/results/v7_stepped_post_local/joint_l1p4_s6p2/single_magictee_v4_full.s4p
```

Central-difference pairs:

```text
lower radius:
  minus  hfss/results/v8_modal_controllability/lower_minus/single_magictee_v4_full.s4p
  plus   hfss/results/v7_stepped_post_local/joint_l1p6_s6p2/single_magictee_v4_full.s4p

split height:
  minus  hfss/results/v8_modal_controllability/split_minus/single_magictee_v4_full.s4p
  plus   hfss/results/v7_stepped_post_local/joint_l1p4_s7p2/single_magictee_v4_full.s4p

upper radius:
  minus  hfss/results/v8_modal_controllability/upper_minus/single_magictee_v4_full.s4p
  plus   hfss/results/v8_modal_controllability/upper_plus/single_magictee_v4_full.s4p

total height:
  minus  hfss/results/v8_modal_controllability/total_minus/single_magictee_v4_full.s4p
  plus   hfss/results/v8_modal_controllability/total_plus/single_magictee_v4_full.s4p
```

## Nominal geometry represented in the paper

The stepped-post nominal point used by the strict central-difference study is:

```text
r_L = 1.40 mm
h_s = 6.20 mm
r_U = 0.90 mm
H   = 16.25 mm
```

The dimensioned layout also reads the architectural dimensions from the current
single-cell builder, including WR90 dimensions, H-throat length, terminal ridge,
smooth taper, tuner straight, and port straight.

## Analysis scripts

```text
hfss/analyze_v8_modal_controllability.py
hfss/analyze_modal_spectral_decomposition.py
hfss/build_modal_controllability_paper_figures.py
hfss/export_paper_hfss_figures.py
```

Numerical result summaries:

```text
hfss/results/v8_modal_controllability/modal_controllability_report.json
hfss/results/v8_modal_controllability/modal_controllability_report.md
hfss/results/v8_modal_controllability/modal_spectral_decomposition.json
hfss/results/v8_modal_controllability/modal_spectral_decomposition.md
```

## Practical rule

If a number appears in a generated figure, regenerate it from the source data rather
than editing the plotted value manually. If a dimension changes in the builder, update
the dimensioned design figure in the same commit.
