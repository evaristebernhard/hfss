# Standalone paper

**Symmetry-Protected Modal Controllability for Broadband X-Band Magic-T Power Combining**

The manuscript's LaTeX source and all six TikZ/PGFPlots figure source files are in **this directory**. Editing or compiling the paper does not require HFSS or the rest of this repository:

```bash
cd paper
make                  # stand-alone LaTeX compilation, same as make pdf
```

Compilation needs `latexmk`, IEEEtran, TikZ and PGFPlots. You can copy `modal_controllability_magictee.tex` together with `figures/` into another TeX project and compile it independently.

**Data regeneration is a different workflow.** It consumes committed Touchstone data and the corresponding Python scripts in `../hfss`:

```bash
make reproduce        # recompute Jacobian + spectral analysis + figures + PDF
make bundle           # create source/data ZIP with everything needed
```

The portable ZIP contains repository-relative scripts, input .s4p/.s8p files and the paper source so `make reproduce` can be run after extraction without access to the original repository. `make hfss-assets` needs AEDT GUI. Refer to [FIGURE_PROVENANCE.md](FIGURE_PROVENANCE.md) for the source of each figure.

The paper is a **PEC-based local modal-controllability study**, not a hardware validation. The four-way example has mean 78.34% efficiency and fails the desired >=90% across-band engineering target. There is no verified peak/CW high-power rating.
