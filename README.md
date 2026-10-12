# Magic-T X-band combiner — current research line

This is the **focused working branch** of the 9–11.5 GHz stepped-post Magic-T study. It deliberately does **not** carry over obsolete HFSS v1–v6 experiments, full dated delivery copies, and old drafts. The earlier material remains recoverable from the original `main` branch and Git history.

## One model

- **Nominal cell:** stepped post lower radius 1.40 mm, split height 6.20 mm, upper radius 0.90 mm, total height 16.25 mm.
- **Matching geometry:** WR90/ridge transition, H throat 20.4 mm wide and 5.5 mm long, local H post pair radius 1.5 mm, height 0.7 mm.
- **Four-way tree:** three Magic-T cells, equal interstage sections of 1.38 mm.
- **Solver/data:** HFSS 2025.2 Student, PEC, 9–11.5 GHz; Jacobian 101 frequency points, four-way simulation 51 points.
- **Recorded physical seed:** [design/seed_v7_optimized_tree.json](design/seed_v7_optimized_tree.json).

## Actual code/data dependency map

```text
hfss/build_single_magictee_v6_stepped_post.py  <-- wrapper: current single cell
   └─ hfss/build_single_magictee_v4_full.py   <-- reusable geometry engine

hfss/build_four_way_magictee_v6_3d.py          <-- current four-way builder
   └─ hfss/build_single_magictee_v4_full.py

retained .s4p data (nominal + 8 central differences + historical comparison)
   ├─ hfss/analyze_v8_modal_controllability.py
   ├─ hfss/analyze_modal_spectral_decomposition.py
   └─ hfss/build_modal_controllability_paper_figures.py
       └─ paper/figures/*.tex
           └─ paper/modal_controllability_magictee.tex
```

These filenames reflect **code provenance** and do not mean multiple physical models remain active. Some v7 Touchstone files are needed because v8 deliberately reuses those perturbation solutions. They are input data, not active alternative model versions.

## Fast reproduction (no HFSS license needed)

From the root, with Python 3 and NumPy:

```bash
python3 hfss/analyze_v8_modal_controllability.py
python3 hfss/analyze_modal_spectral_decomposition.py
python3 hfss/build_modal_controllability_paper_figures.py
cd paper && make pdf
```

To build the LaTeX paper without re-running numerical analysis: `cd paper && make`. To regenerate all numerical figures and manuscript: `cd paper && make reproduce`. To produce a portable source-and-data ZIP: `cd paper && make bundle`. Requires `latexmk` and LaTeX/TikZ for compilation.

For new HFSS runs, see [hfss/README.md](hfss/README.md). **No full-wave solves were performed while preparing this cleanup branch.**

## What has actually been shown?

| Quantity | Reported PEC result |
|---|---:|
| Step-normalized full-band Jacobian condition | 50.3 |
| Full-band lower-vs-upper post control angle | 78.9° |
| Single-cell mean H/sum efficiency | 86.99% |
| Single-cell mean E/difference efficiency | 77.46% |
| Four-way full-3D mean output efficiency | 78.34% |
| Four-way full-3D minimum output efficiency | 50.17% |
| Four-way worst active return loss | 2.95 dB |

The result is a **modal-controllability paper**, not a finished >90%-efficient broadband combiner. Peak >30 kW, CW >1 kW, finite-conductivity loss, thermal, breakdown, and multipactor limits are **not verified**. The next design task is independent broadband matching/spectral-shaping control, with a new full-wave and four-way validation.

**Do not turn this branch into another historical version warehouse.** New numerical work should update the one baseline and its source-data provenance.
