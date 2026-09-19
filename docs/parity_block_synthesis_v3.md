# Parity-block synthesis v3 — updated after Stage-A HFSS

## 1. Purpose

This document is the theoretical basis for the next geometry revision.

It incorporates both:

- the parity-corrected v2 baseline;
- the completed 12-case Stage-A HFSS sweep on `g2` and terminal ridge length `Lt`.

The central conclusion is now supported by both symmetry analysis and full-wave sensitivity data:

[
oxed{
	ext{the H and E parity blocks must be matched with different physical mechanisms.}
}
]

The next design must not continue as a larger blind sweep of the old ridge variables.

---

## 2. Modal decomposition

Define

[
c_+ = rac{P_1+P_2}{sqrt2},
qquad
c_- = rac{P_1-P_2}{sqrt2}.
]

For the parity-corrected geometry the scattering matrix is numerically block diagonal:

[
S_m approx
egin{pmatrix}
r_+&0&t_H&0\
0&r_-&0&t_E\
t_H&0&r_H&0\
0&t_E&0&r_E
end{pmatrix}.
]

Thus the tee is well represented as

[
oxed{(c_+,H)oplus(c_-,E)}.
]

The forbidden terms remain below about -50 dB in all 12 Stage-A cases, and often below -60 dB. This is already far beyond the 22 dB isolation requirement and should be treated as a symmetry-protected constraint rather than an optimization objective.

---

## 3. Stage-A empirical result

The completed sweep was

[
g_2={4.6,5.0,5.4,5.8} {m mm},
]

[
L_t={4.5,6.0,7.5} {m mm}.
]

All 12 cases completed successfully over 9--11.5 GHz with 101 points.

The best H case was

[
oxed{g_2=5.8 {m mm},qquad L_t=7.5 {m mm}}.
]

Its band-worst H/even metrics were

[
RL_{c_+}=1.266 {m dB},
]

[
|t_H|_{min}=-5.971 {m dB}.
]

The best E/odd result anywhere in the sweep was only

[
RL_{c_-}=5.402 {m dB}.
]

Therefore Stage-A does not approach the 22 dB target.

### 3.1 What Stage-A did change

For the best H case, the de-embedded even-mode conductance changed from the v2 baseline approximately as follows:

| Frequency | v2 (G_H) | Stage-A best (G_H) |
|---:|---:|---:|
| 9.0 GHz | 0.1774 | 0.2351 |
| 10.2 GHz | 0.1169 | 0.1503 |
| 11.5 GHz | 0.0636 | 0.0738 |

So increasing (g_2) and (L_t) does raise H coupling.

However the percentage improvement falls strongly toward the high-frequency edge. The high-frequency coupling deficit remains dominant.

This means the old variables mainly change the coupling level and phase; they do not provide enough independent control over the frequency slope and curvature.

### 3.2 What Stage-A did not change

The E/odd block changed negligibly.

For example the de-embedded odd-mode resistance remained approximately

[
0.48ightarrow0.39ightarrow0.30
]

from 9 to 11.5 GHz, almost independent of the H-side ((g_2,L_t)) choices.

Hence

[
oxed{
rac{partial r_-}{partial g_2}approx0,
qquad
rac{partial r_-}{partial L_t}approx0.
}
]

This is direct numerical evidence that the H and E matching networks can be designed almost independently.

---

## 4. Correct optimization variables

For the present PEC model each parity block is nearly unitary. Therefore

[
|r|^2+|t|^2approx1.
]

The external 22 dB reflection target is

[
|r|<10^{-22/20}=0.07943.
]

The primary matching objective should therefore be

[
oxed{
J_{m match}
=
max_{fin[9,11.5]}
max{|r_+(f)|, |r_-(f)|}.
}
]

Forbidden parity terms should remain a constraint, not a weighted objective.

---

## 5. De-embedded H block

After removing the 35 mm collinear reference-plane phase, the even-mode admittance is well represented by

[
y_H(f)=G_H(f)+jB_H(f).
]

Using

[
x=rac{f-10.25}{1.25},
]

the v2 baseline is approximately

[
G_H(x)
=
0.11460-0.05847x+0.00631x^2,
]

[
B_H(x)
=
-0.08006-0.05614x+0.02664x^2.
]

The useful equivalent representation is

[
oxed{
y_H(f)approx n_H^2(f)+jb_H(f)
}
]

with

[
n_H(f)=sqrt{G_H(f)}.
]

The coupling-amplitude correction needed to move toward (G_H=1) is approximately

[
m_H(-1)approx2.36,
qquad
m_H(0)approx2.95,
qquad
m_H(+1)approx4.00.
]

Thus the missing H-side mechanism must not only increase coupling; it must make the coupling increase strongly enough with frequency to counteract the existing negative slope.

A single frequency-independent coupling multiplier cannot do this. Even with perfect reactive cancellation, the best possible constant rescaling of the extracted conductance gives only about 12 dB minimax return loss.

Therefore

[
oxed{
	ext{the new H geometry must change coupling level, slope, and curvature.}
}
]

---

## 6. H-side physical conclusion

The next H-side topology is

[
oxed{
	ext{tee junction}
ightarrow
	ext{symmetric H-plane matching cell}
ightarrow
	ext{terminal ridge}
ightarrow
	ext{existing H taper}.
}
]

The matching cell should preserve the mirror symmetry (xmapsto-x).

The preferred first implementation is a centered H-plane sidewall step/iris in the H arm.

Because the H arm propagates along (+Y), with broad dimension (A) along (X), the step is formed by two equal PEC sidewall intrusions from (x=pm A/2), leaving a centered clear opening (a_i).

The principal H design coordinates are

[
oxed{
p_H=(a_i,t_i,d_i,w_t)
}
]

where

- (a_i): centered clear H-plane opening along X;
- (t_i): longitudinal thickness along Y;
- (d_i): offset from the tee/H-arm junction along Y;
- (w_t): terminal ridge width.

The empirical Stage-A starting values are

[
oxed{
g_2=5.8 {m mm},
qquad
L_t=7.5 {m mm}
}
]

for the first v3 structural build. They are not final optimized values.

---

## 7. Conservative H-iris dimensional bounds

For a local rectangular opening of width (a_i), a TE10-like cutoff estimate is

[
f_capproxrac{c}{2a_i}.
]

To keep the local cutoff below the 9 GHz band edge requires

[
a_i>rac{c}{2(9,{m GHz})}approx16.65 {m mm}.
]

For more margin, requiring approximately (f_cle8) GHz gives

[
a_igtrsim18.74 {m mm}.
]

Therefore the first high-power-friendly design range is

[
oxed{
18.8 {m mm}le a_ile21.5 {m mm}
}
]

with an initial seed

[
oxed{a_i=20.0 {m mm}}.
]

This deliberately avoids a narrow high-field slot.

Use

[
oxed{
2.0le t_ile4.0 {m mm}
}
]

with seed

[
t_i=3.0 {m mm}.
]

At 10.25 GHz,

[
lambda_gapprox38.05 {m mm},
]

so a practical phase-control interval is

[
oxed{
6.5le d_ile10.5 {m mm}
}
]

with seed

[
d_i=8.5 {m mm}.
]

Use rounded edges later; a first radius range of roughly 0.8--1.5 mm is suitable for the high-power study.

---

## 8. Terminal ridge width

The terminal ridge width should no longer be forced to equal the upstream width.

Keep the empirical Stage-A gap and length initially:

[
g_t=5.8 {m mm},
qquad
L_t=7.5 {m mm}.
]

Expose

[
oxed{
4.57le w_tle8.0 {m mm}.
}
]

This allows the local H-arm impedance/coupling to be changed without aggressively shrinking the high-field ridge gap.

---

## 9. De-embedded E block

The odd-mode load is nearly real and slowly varying:

[
z_E(x)
approx
(0.3896-0.09175x)
+j(0.0196+0.0025x).
]

This is primarily a broadband resistive transformer problem.

A one-section reduced model is insufficient for 22 dB across 9--11.5 GHz.

A two-section reduced model is sufficient in the present approximation.

Including the repository Cohn ridge impedance model and ridge dispersion gives the preferred theory seed

[
oxed{
w_E=6.858 {m mm}
}
]

with the section nearest the junction

[
oxed{
g_{E2}=4.299 {m mm},
qquad
L_{E2}=9.228 {m mm}
}
]

and the outer section

[
oxed{
g_{E1}=6.544 {m mm},
qquad
L_{E1}=10.392 {m mm}.
}
]

The reduced-model worst return loss is about 24.6 dB.

This is an initializer, not an HFSS-qualified prediction.

---

## 10. E-matcher orientation

The parity-corrected E arm propagates along (+Z), with

- narrow dimension (B) along X;
- broad dimension (A) along Y.

Therefore the E-arm double ridges must:

- intrude from (x=pm B/2);
- leave their clear gap along X;
- have ridge width along Y;
- extend longitudinally along Z.

The physical ordering from the junction outward is

[
oxed{
	ext{junction}
	o
(g=4.299,L=9.228)
	o
(g=6.544,L=10.392)
	o
	ext{straight WR90 port section}.
}
]

This preserves the odd parity of the E channel.

---

## 11. Design/tolerance coordinate separation

For every mirrored nominal feature define

[
p_+=rac{p_L+p_R}{2},
qquad
p_-=rac{p_L-p_R}{2}.
]

Use (p_+) for nominal matching design.

Use (p_-) only for tolerance/isolation analysis.

The current parity isolation is valuable and should not be spent to improve return loss.

---

## 12. Stop conditions for the old design path

The following work should stop:

- extending the old ((g_2,L_t)) Stage-A sweep;
- reopening all five old ridge parameters at once;
- adding asymmetric bolts/posts to cure the nominal mismatch;
- optimizing physical (S_{11}) without checking (r_+) and (r_-).

The next geometry must introduce new H-junction coupling control and an independent E-arm broadband transformer.

---

## 13. Next full-wave sequence

When HFSS work resumes, use this order:

1. build v3 geometry only;
2. verify parity/port orientation before optimization;
3. run one structural v3 baseline;
4. check that the H iris changes (G_H(f)) substantially;
5. check that the E matcher changes only the odd block to first order;
6. run a small H sensitivity set on ((a_i,t_i,d_i,w_t));
7. compute a Jacobian/SVD in low-order modal coefficients;
8. optimize passive geometry;
9. only after passive RL is reasonable, add mirrored residual tuning bolts;
10. then add finite conductivity and 30 kW field scaling.

This sequence is the design path supported by the current theory and the latest HFSS data.
