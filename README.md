# HFSS — X-band four-way high-power magic-tee combiner

Target problem: a compact four-way waveguide power combiner for **9–11.5 GHz**, implemented around cascaded magic tees, impedance-transforming/ridged transitions, and optional tuning bolts.

## External requirements

- Frequency band: 9–11.5 GHz
- Return loss: > 22 dB over band
- Input-port isolation: > 22 dB over band
- Coherent combining efficiency: > 95%
- Peak output power: > 30 kW
- CW average power: > 1 kW
- Compact mechanical envelope
- HFSS 2022 target environment

## Repository status

This repository currently contains an **analytic design baseline**, not a validated HFSS geometry.

Primary standalone design note:

- [main.tex](main.tex) — current parameter-design rationale and recommended Cohn/TRM ridge seed

The main technical notes are:

- [docs/analytic_baseline.md](docs/analytic_baseline.md)
- [docs/ridge_cross_section.md](docs/ridge_cross_section.md)

Reproducibility scripts:

- [scripts/transformer_seed.py](scripts/transformer_seed.py)
- [scripts/ridge_cross_section_seed.py](scripts/ridge_cross_section_seed.py)

The current **conditional** first HFSS ridge seed uses a common ridge width of 4.572 mm, with section-1 gap/length 7.672/9.872 mm and section-2 gap/length 4.984/8.857 mm. These dimensions come from a self-consistent Cohn/TRM reduced model and must still be calibrated against HFSS eigenmode/wave-port extraction and the actual magic-tee junction.

## Important modeling rule

A cascaded magic-tee junction is a multiport 3-D waveguide discontinuity. Do **not** assume that two combining arms imply an exact scalar load of (Z_0/2). The 2:1 transformer calculations in the note are a conditional reduced-model initializer only.

The production workflow is:

1. establish the ideal multiport/mode target;
2. simulate/de-embed the actual magic-tee junction;
3. extract modal/effective impedance for candidate uniform ridged sections;
4. map the required impedance trajectory into ridge geometry;
5. optimize the full 3-D structure over 9–11.5 GHz;
6. add tuning bolts only for residual susceptance/ripple;
7. verify finite-conductivity loss, field hot-spots, and thermal behavior at the power targets.

No result in this repository should be treated as hardware-qualified until the full-wave and high-power checks are complete.
