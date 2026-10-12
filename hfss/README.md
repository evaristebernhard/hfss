# Active HFSS code

Only **two** build scripts are treated as current:
- `build_single_magictee_v6_stepped_post.py`: current 4-port cell. It imports `build_single_magictee_v4_full.py` purely as its geometry engine.
- `build_four_way_magictee_v6_3d.py`: current 8-port three-cell tree. It also imports the same engine.

Nominal stepped post parameters are (lower radius, split height, upper radius, total height) = **(1.4, 6.2, 0.9, 16.25) mm**. Tree interstage length **1.38 mm**. The code's old revision numbers are not separate research branches. The reference geometry is documented in `../design/seed_v7_optimized_tree.json`.

## Paper/data analysis

Use these from the repository root (Python 3 + NumPy):

```bash
python3 hfss/analyze_v8_modal_controllability.py
python3 hfss/analyze_modal_spectral_decomposition.py
python3 hfss/build_modal_controllability_paper_figures.py
```

`run_v8_modal_controllability.py` is used **only to regenerate the six missing finite-difference HFSS cases**. The remaining three relevant samples (nominal and two positive perturbations) were solved earlier and are retained in `results/v7_stepped_post_local/`; the seven other old samples retained in the tree are needed only for the analysis script's historical comparison. These are data dependencies, not a reason to bring back all old parameter sweeps.

## New HFSS simulation

Requires an installed Windows AEDT/PyAEDT environment, launched through `../scripts/wsl_pyaedt_launcher.sh` from WSL2. Use the geometry scripts' build-only mode first, inspect waveports, PEC air volume, union topology and integration lines, then add `--solve --non-graphical` when ready.

For the cell, use `build_single_magictee_v6_stepped_post.py` with `--post-lower-radius 1.4 --post-lower-height 6.2 --post-upper-radius 0.9 --post-total-height 16.25 --post-height 0.7 --junction-pair-height 0 --h-throat-a 20.4 --h-throat-len 5.5 --h-throat2-len 0 --h-iris-open 0 --e-step-len 0`.

For the tree, use `build_four_way_magictee_v6_3d.py` with `--interstage-length 1.38 --post-lower-radius 1.4 --post-lower-height 6.2 --post-upper-radius 0.9 --post-total-height 16.25 --points 51`.

**Note:** The builder uses some fixed internal constants and does not automatically load the JSON seed. The post/tree defaults were aligned here, but exact rebuilt-model equivalence must still be verified by an AEDT solve. No new HFSS simulation has been run for this cleanup.
