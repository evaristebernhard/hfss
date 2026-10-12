# HFSS modeling — one geometry engine

**Do not use old versioned builders.** The single entry is `build_model.py`, which loads `../design/current_model.json`.

- `magictee/config.py`: validated frozen `CellConfig`, `TreeConfig`, geometry lengths and frequency sweep.
- `magictee/geometry.py`: all current air volume, H throat, stepped lower/upper post, local H post pair, terminal ridge, smoothly segmented transformer, optional retracted tuner screws, and the single-cell port convention.
- `magictee/tree.py`: clone the same cell three times and add two WR90 interstage links; independent eight-port boundary assignment.
- `magictee/solver.py`: AEDT session, adaptive/interpolating sweep and S-parameter export; no Ansys import occurs for dry run.
- `build_model.py`: CLI for cell/tree, output, config, override parameters, dry-run and solve.

### No HFSS required

```bash
python3 hfss/build_model.py --mode cell --dry-run
python3 hfss/build_model.py --mode tree --dry-run
python3 -m unittest discover -s tests -v
```

### New simulation

```bash
scripts/wsl_pyaedt_launcher.sh hfss/build_model.py --mode cell
scripts/wsl_pyaedt_launcher.sh hfss/build_model.py --mode tree
```

By default, these **only construct and save** AEDT projects; add `--solve --non-graphical` after geometry/port inspection. Output goes under ignored `hfss/output_current`.

### Separate experimental reproducibility

`analyze_v8_modal_controllability.py` and `analyze_modal_spectral_decomposition.py` intentionally consume the **retained original 2026 S4P files**, because those were the actual simulation inputs used for the paper. `run_modal_perturbations.py` prepares rebuilt perturbations under `output_current/modal_perturbations`, not in the historical result folder.

### HFSS 2025.2 solver regression

```bash
python3 hfss/compare_results.py --mode cell --max-abs 0.02
python3 hfss/compare_results.py --mode tree --max-abs 0.02
```

The nominal rebuilt cell and tree have been solved in HFSS 2025.2 Student and compared against **the original retained simulations**. Both outputs match every complex S entry on their frequency grids (maximum absolute error 0.0; the 0.02 bound passes). Rebuilt `.s4p`/`.s8p` files and comparison details are stored in `results/refactor_validation_20261012/`. Missing rebuilt files fail explicitly.

The AEDT design names and single-cell port names remain compatible with historical project inspection. The current CLI uses non-versioned file output names, so rebuilt analyses must be compared to the old Touchstone data before publication.

PEC only. This regression confirms the refactor reproduces the nominal historical solves; it does not validate conductor loss, thermal behavior, breakdown limits, or high-power operation.
