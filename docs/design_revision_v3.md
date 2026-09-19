# HFSS design revision v3 — geometry changes implied by parity-block theory

## Status

Theory-only design revision.

This document defines how the next geometry should be changed. It does **not** claim that the dimensions below have already passed HFSS.

The existing v2 geometry remains the validated parity baseline.

---

## 1. What must not change

Keep the v2 port orientation and mirror symmetry:

- P1/P2: collinear arms;
- P3: H/sum arm;
- P4: parity-corrected E/difference arm;
- E arm: narrow dimension along X, broad dimension along Y;
- all nominal matching features symmetric under X -> -X.

Do not revert to the v1 E-arm orientation.

Do not introduce a single off-center bolt/post as a nominal matching element.

---

## 2. Split the design into two independent matching problems

Use

[
c_+=(P_1+P_2)/sqrt2,
qquad
c_-=(P_1-P_2)/sqrt2.
]

Nominal design objective:

[
(c_+,H)
quad	ext{and}quad
(c_-,E)
]

are optimized independently while the forbidden cross-parity terms remain a tolerance check.

The primary full-wave objective later should be

[
J=
max_fmax(|r_+|,|r_-|).
]

---

## 3. E-arm modification: add a two-section double-ridge matcher

### Current v2

The E arm is a plain parity-corrected WR90 branch.

### v3 change

Insert a centered symmetric double-ridge transformer in the E arm.

For +Z propagation:

- ridge intrusion direction: from x = +/-B/2 toward x = 0;
- ridge width direction: Y;
- ridge gap direction: X;
- longitudinal direction: Z.

### Primary theoretical seed

[
w_E=6.858 {m mm}
]

for both sections.

Near the junction, use the lower-impedance section first:

[
g_{E2}=4.30 {m mm},
qquad
L_{E2}=9.23 {m mm}.
]

Then transition toward WR90 through

[
g_{E1}=6.54 {m mm},
qquad
L_{E1}=10.39 {m mm}.
]

Then use a short ordinary WR90 port extension.

Recommended physical ordering from the junction outward:

[
oxed{
	ext{junction}
	o
(g=4.30,L=9.23)
	o
(g=6.54,L=10.39)
	o
WR90.
}
]

The two steps may initially be modeled discretely for diagnosis and later changed to a smooth impedance-space taper.

### Why these values

They are obtained by fitting the de-embedded odd-mode load and then re-optimizing with the repository Cohn ridge impedance and ridge dispersion model.

Predicted reduced-model worst RL is about 24.6 dB.

This is not an HFSS prediction.

---

## 4. H-arm modification: add a symmetric junction matching cell

### Current v2

The H arm uses the existing double-ridge taper ending in

[
g_2=4.984 {m mm},
qquad
L_t=6.0 {m mm},
qquad
w=4.572 {m mm}.
]

The extracted even-mode conductance is far too low and decreases strongly with frequency.

Changing only g2 or Lt is therefore not enough.

### v3 change

Add a **mirror-symmetric H-plane matching step/iris cell** near the tee.

Parameterize it by

- `h_iris_open`: centered H-plane aperture/opening;
- `h_iris_thickness`: longitudinal thickness;
- `h_iris_offset`: distance from the tee reference plane;
- `h_terminal_ridge_w`: terminal ridge width independent of upstream ridge width.

The exact CAD primitive can be a centered sidewall step/iris or an equivalent broad H-plane shoulder, provided that it preserves x-mirror symmetry.

### Initial dimensional scale

Use these only as first design ranges:

[
h_{m iris,thickness}=2.0	ext{--}4.0 {m mm},
]

[
h_{m iris,offset}=6.5	ext{--}10.5 {m mm}.
]

Keep the aperture broad enough that it does not become a narrow high-field slot.

Use rounded metal edges with a first radius scale around

[
0.8	ext{--}1.5 {m mm}.
]

### Terminal ridge

Initially keep

[
g_tapprox4.98 {m mm}
]

and expose

[
4.57 {m mm}
le
w_t
le
8.0 {m mm}.
]

The wider local ridge is a secondary coupling/impedance control that does not require shrinking the high-field ridge gap.

---

## 5. Parameters to freeze in the first revised geometry

Do not reopen every old parameter.

Initially keep the upstream H taper fixed:

[
w=4.572 {m mm},
]

[
g_1=7.672 {m mm},
qquad
L_1=9.872 {m mm},
]

[
g_2=4.984 {m mm},
qquad
L_2=8.857 {m mm}.
]

Keep

[
L_t=6.0 {m mm}
]

for the first structural version.

The new design degrees of freedom are first concentrated in the H junction cell and the new E-arm transformer.

---

## 6. Future H optimization coordinates

When simulation resumes, do not directly optimize raw left/right dimensions.

Use only symmetric/common-mode coordinates.

First H parameter group:

[
p_H=
(a_i,t_i,d_i,w_t).
]

After sensitivity is known, reduce this using the Jacobian/SVD.

The extracted theoretical targets are approximately

[
ln m_H(x)
=
1.08295+0.26026x+0.03948x^2,
]

and

[
b_{m corr}(x)
=
0.08006+0.05614x-0.02664x^2.
]

The geometry Jacobian should be evaluated against these low-order coefficients rather than against hundreds of raw S-parameter samples.

---

## 7. Tolerance coordinates

For every nominal mirrored feature define

[
p_+=(p_L+p_R)/2,
qquad
p_-=(p_L-p_R)/2.
]

Use (p_+) for design.

Use (p_-) only for tolerance/isolation studies.

Examples:

- left/right iris depth mismatch;
- left/right ridge width mismatch;
- left/right corner-radius mismatch;
- assembly offset.

This preserves the parity protection during optimization.

---

## 8. Bolts are moved later in the sequence

The old two-bolt concept is retained only as residual tuning.

Do not add bolts until:

- H and E parity blocks are both already broadband matched by passive geometry;
- the nominal forbidden coupling remains below the isolation target;
- the 30 kW field scaling is available.

If bolts are eventually used, use mirrored pairs with equal nominal penetration.

A differential bolt penetration is a tolerance variable, not a nominal tuning coordinate.

---

## 9. High-power design rule

For the 30 kW peak-power target:

- avoid making the H matching problem disappear by shrinking the ridge gap aggressively;
- prefer broad H-plane boundary steps/irises to sharp center probes;
- keep nominal geometry smooth and rounded;
- retain (K_E=E_{max,m local}/E_{max,m straight}) as a later acceptance metric;
- evaluate finite-conductivity loss only after the PEC matching topology is credible.

---

## 10. Proposed geometry version naming

Use:

- v2 = parity-corrected baseline already solved;
- v3-theory = this unsolved design revision;
- v3-HFSS = first future model implementing the new E matcher and H junction cell.

Do not overwrite the v2 baseline files.
