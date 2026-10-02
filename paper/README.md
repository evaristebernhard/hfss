# Modal Controllability Paper — Reproducible Package

This directory is the self-contained entry point for the short paper

`Symmetry-Protected Modal Controllability for Broadband X-Band Magic-T Power Combining`.

The paper is intentionally organized so that a reader can tell:

1. which figures are conceptual drawings;
2. which figures are regenerated from HFSS Touchstone data;
3. which numerical values come from Jacobian analysis;
4. which images require AEDT/PyAEDT to export;
5. how to rebuild the PDF and create a portable ZIP bundle.

## Fast path

From the repository root:

```bash
cd paper
make all
```

This performs the reproducible non-HFSS-GUI pipeline:

```text
Touchstone data
  -> full-band modal Jacobian
  -> modal-area / spectral analysis
  -> paper TikZ/PGFPlots figures
  -> IEEE PDF
```

To create a portable package:

```bash
make bundle
```

The output is written to:

```text
paper/dist/Modal_Controllability_MagicT_Reproducible_Bundle.zip
```

## HFSS screenshots and field plots

The paper's vector plots do not require launching HFSS. Real model screenshots and
parity-field plots do require graphical AEDT.

From WSL:

```bash
cd ..
scripts/wsl_pyaedt_launcher.sh hfss/export_paper_hfss_figures.py
```

Expected outputs:

```text
paper/assets/hfss_single_cell_model.png
paper/assets/hfss_even_H_field.png
paper/assets/hfss_odd_E_field.png
```

See `FIGURE_PROVENANCE.md` for the exact source of every figure.

## Main files

- `modal_controllability_magictee.tex` — paper source.
- `figures/` — TikZ/PGFPlots figure sources used directly by LaTeX.
- `assets/` — AEDT-exported raster assets; may be absent until the export script is run.
- `FIGURE_PROVENANCE.md` — source-of-truth map for every figure.
- `Makefile` — rebuild commands.
- `package_reproducible_bundle.py` — builds a portable ZIP with the paper, scripts, and the exact Touchstone inputs used by the analyses.

## Editing rules

### If you want to change the explanatory drawings

Edit these directly:

- `figures/fig_geometry_schematic.tex`
- `figures/fig_dimensioned_design_layout.tex`

The first is conceptual. The second is dimensioned from the geometry builder and
must be kept consistent with the builder constants and nominal stepped-post values.

### If you want to change data-driven figures

Do **not** hand-edit the numerical table embedded in the figure source. Change the
underlying data or analysis, then run:

```bash
make figures
```

This regenerates:

- `fig_gamma_trajectories.tex`
- `fig_modal_angle_matrix.tex`
- `fig_singular_spectrum.tex`
- `fig_broadband_performance.tex`

### If you change the final geometry

At minimum update/re-run:

1. the nominal HFSS case;
2. the positive/negative perturbation cases;
3. `hfss/analyze_v8_modal_controllability.py`;
4. `hfss/analyze_modal_spectral_decomposition.py`;
5. `hfss/build_modal_controllability_paper_figures.py`;
6. the dimensioned layout if builder dimensions changed.

Then run:

```bash
make all
```

## Reproducibility boundary

The paper can reproduce all Jacobian, modal-angle, singular-spectrum, reflection
trajectory, and broadband-performance plots from committed Touchstone files.

The only figures that cannot be recreated without Ansys AEDT are the GUI model
screenshot and field-distribution images. Their export script is committed so the
procedure itself remains reproducible.
