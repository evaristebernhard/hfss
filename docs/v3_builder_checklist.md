# v3 builder checklist

This checklist is intentionally short. It is the coding contract for `hfss/build_single_magictee_v3.py`.

## Copy from v2 unchanged

- coordinate convention;
- P1/P2/P3/P4 wave-port definitions;
- parity-correct E-arm orientation;
- frequency sweep 9--11.5 GHz, 101 points;
- modal post-processing basis;
- upstream H taper function and section-1 dimensions.

## Change H baseline

Use:

- `g2 = 5.8 mm`;
- `terminal_ridge_len = 7.5 mm`.

Create a separate terminal ridge width variable.

## Add H iris

For H-arm propagation +Y:

- full cross section before iris: X width A, Z height B;
- leave centered clear X opening `h_iris_open`;
- create equal left/right PEC sidewall blocks;
- thickness along Y = `h_iris_thickness`;
- start position = `A/2 + h_iris_offset`;
- span full Z height B.

Default:

- open = 20.0 mm;
- thickness = 3.0 mm;
- offset = 8.5 mm.

## Add E two-section double ridge

For E-arm propagation +Z:

- ridges intrude from x = +/-B/2;
- gap is along X;
- ridge width is along Y.

Near-junction section:

- width = 6.858 mm;
- gap = 4.299 mm;
- length = 9.228 mm.

Outer section:

- width = 6.858 mm;
- gap = 6.544 mm;
- length = 10.392 mm.

Then add 10 mm straight WR90 before P4.

Set E-arm total length from the section lengths plus the straight extension.

## Required CLI arguments

- `--g2`
- `--terminal-ridge-len`
- `--h-iris-open`
- `--h-iris-thickness`
- `--h-iris-offset`
- `--h-terminal-ridge-w`
- `--e-ridge-w`
- `--e-gap-near`
- `--e-len-near`
- `--e-gap-outer`
- `--e-len-outer`

## First run

Run exactly one structural baseline before any sweep.

Acceptance:

- solve/export succeeds;
- parity forbidden terms remain < -30 dB;
- H (G_H) moves materially relative to Stage-A best;
- E (r_-) moves materially relative to v2;
- no higher-mode or geometry failure.

Only after that baseline should sensitivity runs start.
