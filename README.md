# Magic-T — single current research model

This branch contains **one** parametric 9–11.5 GHz Magic-T cell and a three-cell binary four-way tree. The obsolete v1–v7 generator copies and historical sweeps are not in the active checkout. Previous work remains in the original main branch / Git history.

## Files to start with

| Purpose | Current source |
|---|---|
| **All nominal dimensions** | [design/current_model.json](design/current_model.json) |
| Validation and immutable model objects | [hfss/magictee/config.py](hfss/magictee/config.py) |
| **Single cell geometry, used in both assemblies** | [hfss/magictee/geometry.py](hfss/magictee/geometry.py) |
| Three-cell four-way assembly and port orientation | [hfss/magictee/tree.py](hfss/magictee/tree.py) |
| AEDT startup, sweep and .sNp export | [hfss/magictee/solver.py](hfss/magictee/solver.py) |
| **One HFSS command-line entry** | [hfss/build_model.py](hfss/build_model.py) |
| Modal Jacobian and spectral post-processing | [hfss/analyze_v8_modal_controllability.py](hfss/analyze_v8_modal_controllability.py) |
| Standalone manuscript | [paper/modal_controllability_magictee.tex](paper/modal_controllability_magictee.tex) |

The four-way code calls the **same** `CellGeometry.create_cell()` as the four-port builder, then clones/rotates/translates that solid twice and adds two WR90 links. It does **not** patch module globals or implement a second junction.

## Build and test without AEDT

```bash
python3 hfss/build_model.py --mode cell --dry-run
python3 hfss/build_model.py --mode tree --dry-run
python3 -m unittest discover -s tests -v
```

## Build in HFSS 2025.2 Student

From WSL2, with the configured Windows PyAEDT environment:

```bash
scripts/wsl_pyaedt_launcher.sh hfss/build_model.py --mode cell --version 2025.2
scripts/wsl_pyaedt_launcher.sh hfss/build_model.py --mode tree --version 2025.2
```

These are **build-only** by default. Inspect the solids/ports before adding `--solve --non-graphical`. Solved output names are `magictee_cell.s4p` and `magictee_tree.s8p` in `hfss/output_current/` (ignored by Git).

The nominal stepped post is `(rL,hs,rU,H)=(1.4,6.2,0.9,16.25) mm`; the tree interstage length is 1.38 mm. CLI overrides are **per run**, never written back into the configuration or shared global state. Example:

```bash
python3 hfss/build_model.py --mode cell --post-upper-radius 1.1 --dry-run
```

## Paper vs. engineering status

```bash
python3 hfss/analyze_v8_modal_controllability.py
python3 hfss/analyze_modal_spectral_decomposition.py
python3 hfss/build_modal_controllability_paper_figures.py
cd paper && make pdf
```

`cd paper && make` only compiles standalone LaTeX/TikZ; `make reproduce` recomputes from the **archived actual S4P inputs**; `make bundle` creates a portable reproducibility ZIP. The manuscript numbers remain tied to their original simulation inputs. The refactored nominal cell and tree were also solved in HFSS 2025.2 and reproduced the retained complex S matrices exactly; see [the refactor validation report](hfss/results/refactor_validation_20261012/README.md).

The stepped post introduces different modal controls (full-band radius angle 78.9°, Jacobian condition 50.3), but PEC four-way efficiency remains 78.34% mean and 50.17% minimum. Peak >30 kW, CW >1 kW, 90% broadband efficiency, metal loss, thermal and breakdown requirements are **not** established.

The nominal HFSS regression has been run against the retained historical data:

```bash
python3 hfss/compare_results.py --mode cell --max-abs 0.02
python3 hfss/compare_results.py --mode tree --max-abs 0.02
```

Both rebuilt models passed the 0.02 regression bound with a measured maximum complex-S error of 0.0 across the full 9–11.5 GHz band. The comparison checks every S-matrix element on each shared frequency and does not overwrite reference data. The rebuilt Touchstone files and machine-readable comparison details are in [the validation report](hfss/results/refactor_validation_20261012/README.md).

**Validation boundary:** this establishes nominal solver regression against the retained PEC models. It does not establish metal loss, thermal performance, breakdown limits, or high-power operation.
