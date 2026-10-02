# AEDT-exported paper assets

This directory is intentionally allowed to be empty in Git.

Run from the repository root:

```bash
scripts/wsl_pyaedt_launcher.sh hfss/export_paper_hfss_figures.py
```

Expected files:

- `hfss_single_cell_model.png`
- `hfss_even_H_field.png`
- `hfss_odd_E_field.png`

These images are not substitutes for the vector TikZ/PGFPlots figures. They are
the real AEDT visual evidence for the simulated geometry and parity-field patterns.

If the files exist when `paper/package_reproducible_bundle.py` runs, they are
automatically included in the ZIP bundle.
