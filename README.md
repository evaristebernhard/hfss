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

## Current design status

The repository now uses a **rough v1 HFSS baseline** rather than the obsolete early ridge seed.

Current common-width Cohn/TRM seed:

- ridge width: **4.572 mm**
- section 1: **g = 7.672 mm, L = 9.872 mm**
- section 2: **g = 4.984 mm, L = 8.857 mm**
- first two-bolt spacing seed: **8.8 mm**
- electrical center: **10.19465 GHz**

Primary machine-readable seed:

- [design/seed_v1.json](design/seed_v1.json)

design/seed_v0.json is retained as a compatibility path but has also been updated to the current v1 values so old automation no longer builds the obsolete 5.8/9.2 mm ridge geometry.

## Design notes

- [main.tex](main.tex) — Cohn/TRM parameter-design rationale
- [docs/analytic_baseline.md](docs/analytic_baseline.md) — original reduced-model baseline
- [docs/ridge_cross_section.md](docs/ridge_cross_section.md) — double-ridge cross-section theory
- [docs/mixed_mode_design_v1.md](docs/mixed_mode_design_v1.md) — current rough mixed-mode / impedance-taper / bolt-tuning design

## Scripts

- [scripts/transformer_seed.py](scripts/transformer_seed.py)
- [scripts/ridge_cross_section_seed.py](scripts/ridge_cross_section_seed.py)
- [scripts/ridge_profile_seed.py](scripts/ridge_profile_seed.py)
- [scripts/mixed_mode_seed.py](scripts/mixed_mode_seed.py)
- [scripts/bolt_phasor_seed.py](scripts/bolt_phasor_seed.py)

## Current physical model

The design is now organized as

[
\text{mixed-mode magic tee}
\rightarrow
\text{impedance-space ridge taper}
\rightarrow
\text{small residual bolt tuning}.
]

The old literal scalar interpretation ZL = 0.5 Z0 is retained only as a reduced-model initializer. The actual single magic-tee junction should be simulated in symmetric/antisymmetric excitation to extract

[
\Gamma_\Sigma(f),\qquad \Gamma_\Delta(f).
]

The first HFSS version does **not** need a rigorous multimode network extraction. A practical sequence is:

1. validate the two uniform ridge sections;
2. validate the passive ridge transformer;
3. simulate one magic tee under Sigma and Delta excitation;
4. combine tee + nearest taper as one full-wave block;
5. build the four-way tree;
6. add two shallow tuning bolts only after the passive match is reasonably good;
7. scale peak electric field to 30 kW and check finite-conductivity loss.

## Important modeling rule

A cascaded magic-tee junction is a multiport 3-D waveguide discontinuity. Do **not** assume that two combining arms imply an exact scalar load of Z0/2. The analytic transformer remains an initializer; HFSS full-wave results take precedence.

No result in this repository should be treated as hardware-qualified until the full-wave and high-power checks are complete.
