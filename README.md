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

This repository contains an **analytic design baseline and current HFSS seed**, not a validated hardware geometry.

Primary standalone design note:

- [main.tex](main.tex) — current parameter-design rationale
- [docs/mixed_mode_design_v1.md](docs/mixed_mode_design_v1.md) — newest theory layer: Sigma/Delta extraction, impedance-space tapering, bolt phasors, evanescent coupling and field normalization

Supporting notes:

- [docs/analytic_baseline.md](docs/analytic_baseline.md)
- [docs/ridge_cross_section.md](docs/ridge_cross_section.md)

Current machine-readable geometry:

- [design/seed_v0.json](design/seed_v0.json) — despite the historical filename, its contents now hold the **current** 4.572 mm common-width seed; the obsolete 5.8/9.2 mm ridge seed has been removed

Reproducibility scripts:

- [scripts/transformer_seed.py](scripts/transformer_seed.py)
- [scripts/ridge_cross_section_seed.py](scripts/ridge_cross_section_seed.py)
- [scripts/ridge_profile_seed.py](scripts/ridge_profile_seed.py) — impedance-space profile inversion; no longer direct geometry smoothstep
- [scripts/mixed_mode_design.py](scripts/mixed_mode_design.py) — modal/efficiency/field/evanescent reference scales

## Current ridge seed

Use a common ridge width

[
w = 4.572 {m mm}.
]

Section 1:

[
g_1=7.672 {m mm},
qquad
L_1=9.872 {m mm}.
]

Section 2:

[
g_2=4.984 {m mm},
qquad
L_2=8.857 {m mm}.
]

These dimensions come from the self-consistent Cohn/TRM reduced model and must still be calibrated against HFSS eigenmode/wave-port extraction and the actual magic-tee junction.

## Important modeling rule

Do **not** identify the magic-tee junction with a literal scalar (Z_0/2) load.

For a symmetric pair, the natural variables are the sum/difference eigenchannels,

[
Gamma_Sigma=r+c,
qquad
Gamma_Delta=r-c.
]

The next HFSS stage should therefore extract/de-embed the real junction in the
Sigma/Delta basis, then optimize the ridge/taper around those complex
frequency-dependent modal data.

Likewise, do not assume a smooth geometry interpolation implies a smooth
impedance transition.  The current profile seed first designs (Z(z)), then
inverts the reduced model for ridge geometry.

## Production workflow

1. verify the two uniform ridge sections;
2. verify the impedance-space taper;
3. simulate/de-embed one magic tee in Sigma/Delta basis;
4. extract modal/effective complex load data;
5. simulate tee + nearest taper jointly because compact spacing can retain evanescent coupling;
6. add tuning bolts only for residual susceptance/ripple;
7. build the full four-way tree and transform its S matrix into the four-mode basis;
8. verify finite-conductivity loss, field hot-spots and thermal behavior.

No result in this repository should be treated as hardware-qualified until the full-wave and high-power checks are complete.
