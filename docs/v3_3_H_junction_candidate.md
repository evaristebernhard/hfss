# v3.3 H-junction structural candidate

## 1. Purpose

This document converts the v3.2 H/even-mode theory into one concrete geometry that can be built and tested independently before any E-arm redesign.

No new HFSS result is claimed here.

The E arm remains exactly the validated v2 parity-corrected geometry.

The H arm is modified only at the junction side.

---

## 2. Why the H structure must change

For the best completed Stage-A case,

[
g_2=5.8 {m mm},
qquad
L_t=7.5 {m mm},
]

the H/even transmission magnitude is approximately

[
|t_H|=0.785, 0.672, 0.503
]

at 9, 10.2 and 11.5 GHz.

The 22 dB lossless target requires approximately

[
|t_H|>0.9968.
]

The missing coupling angle grows strongly toward the high-frequency edge.

The old `g2` sensitivity has the wrong spectral direction: it helps the low-frequency edge more strongly than the high-frequency edge.

Therefore the new H parameter must introduce a **high-pass-like coupling correction**.

---

## 3. Selected structural family

Use a clean reduced-broad-dimension throat directly after the H-plane junction.

Coordinate convention is unchanged:

- H arm propagates along +Y;
- H-arm broad dimension is X;
- H-arm narrow dimension is Z.

The candidate is

[
oxed{
	ext{tee junction}
ightarrow
	ext{reduced-width H throat}
ightarrow
	ext{terminal double ridge}
ightarrow
	ext{existing ridge taper}
ightarrow
	ext{straight H port}.
}
]

The throat contains no ridge.

This is deliberate: the high-pass throat is kept physically separate from the ridge taper so its function can be diagnosed cleanly.

---

## 4. Throat broad dimension from the required coupling slope

Use a simple near-cutoff TE10 factor

[
q(f)=
sqrt{1-left(rac{f_c}{f}ight)^2}
]

as a first proxy for a frequency-selective coupling factor.

The Stage-A best response requires approximately

[
rac{q(11.5)}{q(9)}
approx
rac{|t_H(9)|}{|t_H(11.5)|}
approx
1.56.
]

This gives

[
f_capprox8.0 {m GHz}.
]

For a rectangular H-arm throat,

[
f_c=rac{c}{2a_H},
]

so

[
oxed{
a_Happrox18.8 {m mm}.
}
]

Compared with WR90,

[
A=22.86 {m mm},
]

this means equal sidewall shoulders of

[
oxed{
d_{m shoulder}
=
rac{A-a_H}{2}
approx2.03 {m mm}.
}
]

---

## 5. Recommended first parameter range

The throat width is the principal **spectral-slope parameter**.

Use

[
oxed{
18.4le a_Hle19.2 {m mm}
}
]

for the first sensitivity study.

Representative analytic values:

| (a_H) mm | cutoff GHz | (q(11.5)/q(9)) |
|---:|---:|---:|
| 18.4 | 8.147 | 1.661 |
| 18.6 | 8.059 | 1.602 |
| **18.8** | **7.973** | **1.554** |
| 19.0 | 7.889 | 1.512 |
| 19.2 | 7.807 | 1.476 |

The target slope proxy is about 1.56, hence 18.8 mm is the first seed.

---

## 6. Throat impedance and high-power scale

For (a_H=18.8) mm, the ideal TE10 wave-impedance ratio relative to ordinary WR90 is approximately

| f | (Z_{m TE,throat}/Z_{m TE,WR90}) |
|---:|---:|
| 9.0 GHz | 1.477 |
| 10.2 GHz | 1.228 |
| 11.5 GHz | 1.140 |

Thus the throat naturally gives a stronger low-frequency impedance transformation while its propagation/coupling factor increases more strongly at high frequency.

The equal-power electric-field scale is approximately 1.35 at 9 GHz and decreases toward about 1.18 at 11.5 GHz.

This is acceptable as a theory seed but still requires HFSS field extraction.

---

## 7. Throat length

The throat length is the principal **phase parameter**.

Use

[
oxed{
4.0le L_Hle7.0 {m mm}
}
]

with first seed

[
oxed{
L_H=5.5 {m mm}.
}
]

For (a_H=18.8) mm and (L_H=5.5) mm, ideal TE10 phase accumulation is approximately

[
27.6^circ, 42.0^circ, 54.7^circ
]

at 9, 10.2 and 11.5 GHz.

This is large enough to influence the junction reflection phase but short enough to avoid a long resonant matching chain.

---

## 8. Coupling-level parameter

Do not use throat width for every design function.

Keep an independent level-control parameter downstream.

For the first H-only candidate use

[
oxed{
w_t=4.572 {m mm}
}
]

for the terminal ridge width, but expose

[
oxed{
4.57le w_tle8.0 {m mm}.
}
]

Keep the Stage-A empirical starting values

[
oxed{
g_t=5.8 {m mm},
qquad
L_t=7.5 {m mm}.
}
]

The intended first-order coordinate roles are therefore

[
oxed{
a_Hightarrow	ext{coupling slope},
}
]

[
oxed{
L_Hightarrow	ext{phase},
}
]

[
oxed{
w_tightarrow	ext{coupling level/local impedance}.
}
]

These roles are hypotheses to be tested by the first HFSS Jacobian, not assumed exact identities.

---

## 9. Exact geometric ordering

Measured outward from the H-plane tee mouth (y=A/2):

### Region H0 — high-pass throat

[
0le s<L_H.
]

Cross section:

[
a_H	imes B
]

centered on (x=0).

No ridge.

### Region H1 — terminal ridge

[
L_Hle s<L_H+L_t.
]

Return to full WR90 broad dimension (A).

Use symmetric top/bottom ridge:

[
g_t=5.8 {m mm},
]

[
w_t=4.572 {m mm}
]

for the first case.

### Region H2 — existing taper

Length:

[
L_1+L_2=18.729 {m mm}.
]

Retain the current upstream taper architecture.

### Region H3 — ordinary port extension

[
10 {m mm}
]

straight WR90 before P3.

The new structure therefore adds only

[
oxed{5.5 {m mm}}
]

to the H-arm length in the first candidate.

---

## 10. Why the throat is placed before the ridge

Placing the throat inside the ridge taper would create a hybrid double-ridge/sidewall discontinuity.

That may eventually be useful, but it destroys the clean interpretation of the new degree of freedom.

The first structural test should therefore isolate the mechanism:

[
	ext{junction high-pass correction}
quad	ext{versus}quad
	ext{ridge impedance transformation}.
]

If the throat produces the required high-frequency H coupling increase, later versions can compact the two structures.

---

## 11. First HFSS sensitivity matrix

Do not start with a large grid.

After one structural baseline, use central differences approximately around

[
(a_H,L_H,w_t)
=
(18.8, 5.5, 4.572).
]

Suggested perturbations:

[
a_H: pm0.4 {m mm},
]

[
L_H: pm1.0 {m mm},
]

[
w_t: pm0.8 {m mm}.
]

At each case extract

[
	heta_H(f)=arcsin |S_{H,c_+}(f)|
]

and fit

[
	heta_H(x)
approx
	heta_0+	heta_1x+	heta_2x^2.
]

Then form

[
J_H
=
rac{partial(	heta_0,	heta_1,	heta_2)}
{partial(a_H,L_H,w_t)}.
]

The candidate is successful only if this Jacobian has useful independent directions, especially a positive high-frequency slope direction.

---

## 12. Structural success and failure criteria

### Continue this topology if

1. (|t_H|) improves at 11.5 GHz materially;
2. the improvement at 11.5 GHz is at least comparable to or larger than at 9 GHz;
3. forbidden parity coupling remains below -30 dB;
4. no new propagating higher mode appears in-band;
5. local peak field remains within an acceptable enhancement factor.

### Reject or redesign this topology if

1. (|t_H|) improves mainly at 9 GHz but not at 11.5 GHz;
2. the throat only creates a narrow resonance without broad coupling improvement;
3. (K_E>3) before useful matching is obtained;
4. the three-parameter Jacobian is effectively rank deficient.

---

## 13. Relationship to published H-plane matching structures

Published X-band H-plane T-junction designs use broad junction steps as matching elements, and wideband magic-T designs generally require several conducting discontinuities rather than a single scalar taper adjustment.

The present candidate follows the same broad principle but chooses the throat width from the measured missing H coupling slope rather than copying a published dimension.

Therefore the 18.8 mm value is a data-driven seed, not a literature transplant.

---

## 14. Current design decision

The next H structure to investigate is

[
oxed{
a_H=18.8 {m mm},
quad
L_H=5.5 {m mm},
quad
g_t=5.8 {m mm},
quad
L_t=7.5 {m mm},
quad
w_t=4.572 {m mm}.
}
]

The E arm remains v2 for this H-only structural test.

Do not combine the H and E redesigns in the same first simulation.
