# HFSS v3 design revision — implementation specification

## 0. Status and role

This is the canonical design-input document for the next HFSS geometry.

It supersedes the old plan of continuing the v2 `g2/Lt` sweep.

The dimensions below are either:

- **measured from HFSS Stage-A** and marked empirical; or
- **theory seeds** and explicitly marked not yet HFSS-qualified.

The v2 solved geometry and its Stage-A results must remain untouched for comparison.

---

## 1. Coordinate system

Keep the v2 coordinate convention exactly:

- X: collinear propagation axis;
- Y: H-arm propagation axis;
- Z: E-arm propagation axis.

Cross sections:

- collinear arms: A along Y, B along Z;
- H arm: A along X, B along Z;
- E arm: B along X, A along Y.

Constants:

[
A=22.86 {m mm},qquad B=10.16 {m mm}.
]

Do not change the v2 E-arm rotation.

---

## 2. Existing H taper to retain

Keep the upstream H taper architecture.

Fixed first-pass values:

[
w=4.572 {m mm},
]

[
g_1=7.672 {m mm},
qquad
L_1=9.872 {m mm},
]

[
L_2=8.857 {m mm}.
]

For the v3 starting point use the best empirical Stage-A terminal values:

[
oxed{
g_2=5.8 {m mm},
qquad
L_t=7.5 {m mm}.
}
]

These are only a starting point because the new H matching cell will shift the optimum.

Do not run a larger standalone (g_2/L_t) grid before the new cell is present.

---

## 3. New H-plane matching cell

### 3.1 Geometry

Insert a centered, mirror-symmetric H-plane sidewall step/iris inside the H arm.

The H arm starts at

[
y=A/2.
]

Define the iris center region by

[
y_{m iris,start}=A/2+d_i,
]

[
y_{m iris,end}=A/2+d_i+t_i.
]

Create two PEC sidewall intrusions spanning the full H-arm narrow dimension (B) along Z:

Left intrusion:

[
xin[-A/2,-a_i/2].
]

Right intrusion:

[
xin[a_i/2,A/2].
]

Both occupy

[
zin[-B/2,B/2].
]

Subtract the two PEC volumes from the H-arm air volume.

This leaves a centered clear aperture (a_i) along X and preserves (xmapsto-x) symmetry.

### 3.2 New builder parameters

Expose:

- `--h-iris-open` = (a_i);
- `--h-iris-thickness` = (t_i);
- `--h-iris-offset` = (d_i);
- `--h-terminal-ridge-w` = (w_t).

### 3.3 First seed

Use:

[
oxed{a_i=20.0 {m mm}},
]

[
oxed{t_i=3.0 {m mm}},
]

[
oxed{d_i=8.5 {m mm}},
]

[
oxed{w_t=4.572 {m mm}}.
]

### 3.4 Initial allowed ranges

[
18.8le a_ile21.5 {m mm},
]

[
2.0le t_ile4.0 {m mm},
]

[
6.5le d_ile10.5 {m mm},
]

[
4.57le w_tle8.0 {m mm}.
]

Keep

[
g_t=5.8 {m mm},
qquad
L_t=7.5 {m mm}
]

fixed during the first structural sensitivity check.

The reason for the lower aperture bound is conservative cutoff margin: a local clear broad dimension below about 16.65 mm would put the corresponding TE10 cutoff above 9 GHz. The recommended 18.8 mm floor retains additional margin and avoids a narrow high-field slot.

---

## 4. Terminal H ridge change

In v2 the terminal ridge uses the same width as the upstream taper.

In v3, replace the terminal ridge width `RIDGE_W` by a separate variable `H_TERMINAL_RIDGE_W`.

The terminal top/bottom ridge boxes remain centered on X and symmetric about Z.

Use:

[
g_t=5.8 {m mm},
qquad
L_t=7.5 {m mm}
]

for the first v3 baseline.

Only `H_TERMINAL_RIDGE_W` is released initially.

---

## 5. New E-arm two-section double-ridge matcher

### 5.1 Purpose

The E/odd block is nearly independent of the H-side parameters and behaves as a broadband transformer problem.

Insert a centered two-section double-ridge matcher in the E arm.

### 5.2 Orientation

The E arm propagates along +Z.

Its narrow dimension is along X, so the two E ridges intrude from:

[
x=-B/2
]

and

[
x=+B/2
]

toward the center.

The ridge clear gap is measured along X.

The ridge width is measured along Y.

All E ridges are centered about (y=0).

### 5.3 Primary theory seed

Common ridge width:

[
oxed{w_E=6.858 {m mm}}.
]

Section nearest the junction:

[
oxed{
g_{E2}=4.299 {m mm},
qquad
L_{E2}=9.228 {m mm}.
}
]

Outer section:

[
oxed{
g_{E1}=6.544 {m mm},
qquad
L_{E1}=10.392 {m mm}.
}
]

### 5.4 Placement

Let

[
z_0=B/2
]

be the current E-arm start.

Place the near-junction section first:

[
zin[z_0,z_0+L_{E2}].
]

Then place the outer section:

[
zin[z_0+L_{E2},z_0+L_{E2}+L_{E1}].
]

After these two sections, retain a straight WR90 segment before the P4 wave port.

The present `E_ARM_LEN=30 mm` is sufficient for the 19.62 mm total matcher plus roughly 10 mm straight port extension, but the builder should compute this explicitly rather than rely on a hidden coincidence.

Recommended:

[
E_PORT_STRAIGHT=10.0 {m mm},
]

[
E_ARM_LEN=L_{E2}+L_{E1}+E_PORT_STRAIGHT.
]

### 5.5 E-ridge construction

For a section with gap (g), define ridge depth

[
d_E=rac{B-g}{2}.
]

Negative-X ridge:

[
xin[-B/2,-g/2].
]

Positive-X ridge:

[
xin[g/2,B/2].
]

Both have Y extent

[
[-w_E/2,w_E/2]
]

and the section's Z length.

Subtract these PEC volumes from the E-arm air region.

---

## 6. Required v3 builder outputs

Create a new builder:

`hfss/build_single_magictee_v3.py`

Do not overwrite v2.

The v3 project/design names should be:

- project prefix: `single_magictee_v3`;
- design: `SingleMagicT_v3`.

The builder must print all new dimensions and export them as AEDT design variables.

At minimum expose:

- existing `g2`, `terminal_ridge_len`;
- `h_iris_open`;
- `h_iris_thickness`;
- `h_iris_offset`;
- `h_terminal_ridge_w`;
- `e_ridge_w`;
- `e_gap_near`;
- `e_len_near`;
- `e_gap_outer`;
- `e_len_outer`.

---

## 7. First v3 baseline parameter set

Use exactly this structural first case:

### H side

[
w=4.572,
quad
g_1=7.672,
quad
L_1=9.872,
]

[
g_2=5.8,
quad
L_2=8.857,
quad
L_t=7.5 {m mm}.
]

New H cell:

[
a_i=20.0,
quad
t_i=3.0,
quad
d_i=8.5,
quad
w_t=4.572 {m mm}.
]

### E side

[
w_E=6.858 {m mm},
]

near junction:

[
g_{E2}=4.299,
quad
L_{E2}=9.228 {m mm},
]

outer:

[
g_{E1}=6.544,
quad
L_{E1}=10.392 {m mm}.
]

Straight E-port extension:

[
10.0 {m mm}.
]

---

## 8. Post-processing contract

Continue using

`hfss/analyze_magictee_modal_v2.py`

or a compatible v3 copy.

Always report:

- (RL_{c_+});
- (RL_{c_-});
- (RL_H);
- (RL_E);
- (c_+	o H) transmission;
- (c_-	o E) transmission;
- worst forbidden parity coupling.

Also de-embed the 35 mm collinear arms before interpreting H/E effective admittance or impedance.

Do not accept physical-port (S_{11}) alone as evidence of good matching.

---

## 9. Structural acceptance gates

Before any optimizer:

1. forbidden modal terms remain below -30 dB;
2. H iris produces a clearly measurable change in de-embedded (G_H(f));
3. E matcher produces a clearly measurable improvement in (r_-(f));
4. no new propagating higher mode appears below 11.5 GHz;
5. no geometry overlap or malformed air volume occurs.

A first structural success does not require 22 dB yet.

The purpose of the first v3 solve is to verify that the new parameters span the missing physical directions.

---

## 10. First sensitivity plan after structural validation

Do not run a large Cartesian sweep.

For H, perturb one parameter at a time around the v3 baseline:

- (a_i): ±0.6 mm;
- (t_i): ±0.5 mm;
- (d_i): ±1.0 mm;
- (w_t): ±0.8 mm.

Extract low-order changes in (G_H(f)) and (B_H(f)), then build a Jacobian.

For E, initially perturb:

- (g_{E2}): ±0.4 mm;
- (g_{E1}): ±0.5 mm;
- (L_{E2}): ±0.7 mm;
- (L_{E1}): ±0.7 mm.

Use the Jacobian/SVD to reduce the variable set before optimization.

---

## 11. High-power constraints

Do not cure mismatch by creating narrow gaps or sharp tips.

Retain:

[
K_E=
rac{E_{max,m local}}
{E_{max,m straight,WR90}}
]

as the field-enhancement metric.

The first geometry should use broad symmetric steps and large radii where practical.

Bolts remain disabled in the nominal v3 geometry.

They may be introduced later only as mirrored residual-tuning elements after passive broadband matching is already credible.

---

## 12. What is now considered obsolete

The following are no longer the active design strategy:

- continuing the v2 Stage-A (g_2/L_t) sweep;
- using the old scalar (0.5Z_0) load as the full tee model;
- trying to solve both parity blocks with one H-side taper;
- adding a single asymmetric tuning bolt as the main matching mechanism.

The active design is:

[
oxed{
H: 	ext{junction matching cell + terminal ridge + existing taper}
}
]

and

[
oxed{
E: 	ext{independent two-section double-ridge transformer}.
}
]
