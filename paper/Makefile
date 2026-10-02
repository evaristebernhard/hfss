PYTHON ?= python3
LATEXMK ?= latexmk
PAPER := modal_controllability_magictee.tex
PDF := modal_controllability_magictee.pdf

.PHONY: all analysis figures pdf hfss-assets bundle clean distclean help

all: analysis figures pdf

analysis:
	cd .. && $(PYTHON) hfss/analyze_v8_modal_controllability.py
	cd .. && $(PYTHON) hfss/analyze_modal_spectral_decomposition.py

figures:
	cd .. && $(PYTHON) hfss/build_modal_controllability_paper_figures.py

pdf:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error $(PAPER)

hfss-assets:
	cd .. && scripts/wsl_pyaedt_launcher.sh hfss/export_paper_hfss_figures.py

bundle: all
	$(PYTHON) package_reproducible_bundle.py

clean:
	$(LATEXMK) -c $(PAPER)

distclean: clean
	rm -rf dist

help:
	@echo "make all         - recompute analyses, regenerate figures, compile PDF"
	@echo "make analysis    - regenerate JSON/MD numerical analyses"
	@echo "make figures     - regenerate data-driven TikZ/PGFPlots figures"
	@echo "make pdf         - compile IEEE paper PDF"
	@echo "make hfss-assets - export AEDT model/field PNGs (requires graphical AEDT)"
	@echo "make bundle      - create portable reproducible ZIP under paper/dist/"
