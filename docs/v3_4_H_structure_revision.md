# v3.4 H-block structural revision: orthogonal reactive matching cell

## 1. Purpose

This note revises the v3.3 H-only candidate after the first full-wave result.

The v3.3 reduced-width throat successfully created the missing high-frequency H/even coupling direction, but it did not improve the H block uniformly. Instead, it reversed the coupling slope across the band:

| f | v2 Stage-A best | v3.3 throat |
|---:|---:|---:|
| 9.0 GHz | |t_H| = 0.785 | 0.619 |
| 10.2 GHz | 0.672 | 0.668 |
| 11.5 GHz | 0.503 | 0.785 |

Thus the throat is a strong spectral-shape control, not a general matching solution.

The goal of v3.4 is to separate:

1. coupling spectral slope;
2. center-frequency reactive compensation;
3. coupling / resistance level;
4. phase.

A v3.4 baseline HFSS result is now available in `hfss/results/v3_4_H_reactive_cell_latest/`. It improves the H/even worst-band return loss from 2.098 dB (v3.3) to 2.663 dB and improves the minimum desired H coupling from -4.167 dB to -3.388 dB. The remaining decision is the measured 4x4 Jacobian rank from the eight perturbation solves.

---

## 2. Lossless H/even two-port extraction

With the parity-correct symmetry still intact, the H/even sub-network is numerically lossless to the precision of the PEC solve. It can be written as

\[
S_H=e^{j\chi}
\begin{pmatrix}
e^{j\delta}\cos\theta & j\sin\theta\\
j\sin\theta & e^{-j\delta}\cos\theta
\end{pmatrix}.
\]

Therefore

\[
|t_H|=|\sin\theta|,
\qquad
|r_H|=|\cos\theta|.
\]

The final 22 dB return-loss requirement implies

\[
|\Gamma|\le 10^{-22/20}=0.07943
\]

and therefore

\[
|t_H|\ge 0.99684,
\qquad
\theta_H\ge 85.44^\circ.
\]

The present v3.3 values are only

\[
\theta_H(9)=38.24^\circ,
\quad
\theta_H(10.2)=41.93^\circ,
\quad
\theta_H(11.5)=51.75^\circ.
\]

The first structural gate remains

\[
|t_H|_{\min}\ge0.85,
\]

not the final 22 dB target.

---

## 3. What the v3.3 throat actually changed

At 10.25 GHz the parity-basis reflection is approximately

\[
\Gamma_H^{(v3.3)}
\approx
0.499+j0.549,
\qquad
|\Gamma|\approx0.742.
\]

The corresponding normalized input impedance is

\[
z_{in}
=
\frac{1+\Gamma}{1-\Gamma}
\approx
\boxed{0.815+j1.988}.
\]

For the v2 Stage-A best case the same quantities were approximately

\[
\Gamma_H^{(v2)}
\approx
0.280+j0.692,
\]

\[
z_{in}^{(v2)}
\approx
\boxed{0.445+j1.388}.
\]

This is the key v3.3 result:

- the throat moved the real part from 0.445 toward 1;
- but it increased the positive reactive term from about +j1.39 to +j1.99.

So the reduced-width throat partly repairs the impedance-transformation / coupling-level problem while worsening the center-frequency reactive mismatch.

This explains why the H transmission at 10.2 GHz barely changed even though the two band edges moved strongly.

---

## 4. First-order broadband matching requires four real controls

Expand the complex H reflection around

\[
f_0=10.25\ \mathrm{GHz}
\]

as

\[
\Gamma_H(f;p)
=
\Gamma_0(p)
+
\Gamma_1(p)(f-f_0)
+
O((f-f_0)^2).
\]

A first-order maximally-flat broadband match requires approximately

\[
\Gamma_0=0,
\qquad
\Gamma_1=0.
\]

These are two complex conditions, hence four real conditions:

\[
\Re\Gamma_0=0,
\quad
\Im\Gamma_0=0,
\quad
\Re\Gamma_1=0,
\quad
\Im\Gamma_1=0.
\]

For the v3.3 baseline,

\[
\Gamma_0
\approx
0.499+j0.549,
\]

and a centered finite-difference estimate gives

\[
\Gamma_1
\approx
0.953-j0.931
\quad \mathrm{GHz}^{-1}.
\]

Thus the structure is far from both center matching and first-order flattening.

A robust topology should therefore expose at least four reasonably independent effective geometric directions before residual tuning bolts are introduced.

---

## 5. Why the existing Stage-A controls are insufficient by themselves

Using the completed v2 Stage-A S4P grid, define

\[
F=
[
\Re\Gamma_0,
\Im\Gamma_0,
\Re\Gamma_1,
\Im\Gamma_1
]^T.
\]

Representative finite-difference sensitivities are

\[
\frac{\partial F}{\partial g_2}
\approx
[
-0.036,
-0.048,
-0.096,
+0.112
]^T
\ \mathrm{mm}^{-1},
\]

while

\[
\frac{\partial F}{\partial L_t}
\approx
[
+0.0028,
-0.0081,
-0.0165,
-0.0035
]^T
\ \mathrm{mm}^{-1}.
\]

The terminal-length direction is roughly an order of magnitude weaker in norm than the gap direction.

The v3.3 throat adds a strong new direction, but one throat parameter is visibly mixing spectral slope and reactive phase.

Therefore simply extending the old g2/Lt sweep is not a convincing path to a 22 dB broadband solution.

---

## 6. Weak-throat seed from the measured slope reversal

The v2 band-edge coupling angles are

\[
\theta_H(9)=51.69^\circ,
\qquad
\theta_H(11.5)=30.19^\circ.
\]

The v3.3 throat changes them to

\[
38.24^\circ,
\qquad
51.75^\circ.
\]

Assume only for seed generation that the throat correction scales approximately with sidewall intrusion depth

\[
d=\frac{A-a_H}{2}.
\]

The current v3.3 depth is

\[
d_{v3.3}
=
\frac{22.86-18.8}{2}
=
2.03\ \mathrm{mm}.
\]

To remove the band-edge slope rather than reverse it requires about 0.614 of the present correction. This gives

\[
d_*\approx1.25\ \mathrm{mm},
\]

hence

\[
\boxed{a_H\approx20.37\ \mathrm{mm}}.
\]

Use

\[
\boxed{a_H=20.4\ \mathrm{mm}}
\]

as the v3.4 mild-throat seed.

This is a linearized full-wave interpolation, not a final optimum.

Suggested first range:

\[
\boxed{19.8\le a_H\le21.0\ \mathrm{mm}}.
\]

Keep

\[
L_H=5.5\ \mathrm{mm}
\]

for the first structural comparison so that the effect of weakening the throat is identifiable.

---

## 7. Structural change: add an orthogonal E-plane capacitive cell

### 7.1 Motivation

The H-plane width reduction changes the broad dimension a and therefore directly changes TE10 cutoff:

\[
f_c=\frac{c}{2a}.
\]

It is naturally a strong dispersive / spectral-slope control.

By contrast, ideal TE10 cutoff is independent of the narrow dimension b. Therefore a short symmetric reduced-height section can supply a strong local discontinuity susceptance while perturbing the TE10 propagation law much less strongly at first order.

This suggests using orthogonal geometric controls:

- broad-dimension reduction -> spectral slope / impedance transformation;
- narrow-dimension reduction -> localized reactive compensation.

### 7.2 Proposed v3.4 ordering

Measured outward from the H-plane tee mouth:

\[
\boxed{
\text{tee}
\rightarrow
\text{mild H-plane throat}
\rightarrow
\text{short E-plane capacitive cell}
\rightarrow
\text{terminal double ridge}
\rightarrow
\text{existing taper}
\rightarrow
\text{WR90 port}.
}
\]

The capacitive cell is a symmetric top/bottom broad-wall intrusion, not a thin screw.

Preserve symmetry in x so the c+/c- parity block decomposition remains valid.

---

## 8. First v3.4 geometry seed

### H0 — mild width throat

\[
a_H=20.4\ \mathrm{mm},
\qquad
L_H=5.5\ \mathrm{mm}.
\]

Sidewall intrusion:

\[
d_H=\frac{22.86-20.4}{2}
=1.23\ \mathrm{mm}.
\]

### H1 — localized reduced-height capacitive cell

Use a short symmetric height-reduced section:

\[
\boxed{b_C=9.0\ \mathrm{mm}}
\]

from the WR90 value

\[
B=10.16\ \mathrm{mm}.
\]

Thus each broad wall intrudes by only

\[
d_C
=
\frac{10.16-9.0}{2}
=
0.58\ \mathrm{mm}.
\]

Use

\[
\boxed{L_C=2.5\ \mathrm{mm}}.
\]

At 10.25 GHz this is only about

\[
L_C/\lambda_g\approx0.066,
\]

so it is intended to behave as a localized reactive cell rather than a long resonator.

First ranges:

\[
8.5\le b_C\le9.6\ \mathrm{mm},
\]

\[
1.5\le L_C\le3.5\ \mathrm{mm}.
\]

### H2 — terminal ridge

Retain initially

\[
g_t=5.8\ \mathrm{mm},
\qquad
L_t=7.5\ \mathrm{mm},
\qquad
w_t=4.572\ \mathrm{mm}.
\]

Expose w_t as an independent level-control variable:

\[
4.0\le w_t\le6.5\ \mathrm{mm}.
\]

Do not change g_t or L_t in the first v3.4 structural solve.

---

## 9. Four primary synthesis coordinates

Use

\[
p=
(a_H,L_H,b_C,w_t).
\]

The intended first-order roles are

\[
a_H
\rightarrow
\text{spectral slope / real-part transformation},
\]

\[
L_H
\rightarrow
\text{phase},
\]

\[
b_C
\rightarrow
\text{localized capacitive compensation},
\]

\[
w_t
\rightarrow
\text{coupling level / residual impedance}.
\]

These are hypotheses to be measured, not assumptions to be enforced.

The correct object to identify is

\[
J_{H,4}
=
\frac{
\partial(
\Re\Gamma_0,
\Im\Gamma_0,
\Re\Gamma_1,
\Im\Gamma_1
)}
{\partial(
a_H,L_H,b_C,w_t
)}.
\]

If this 4x4 Jacobian is numerically full-rank with useful singular values, the topology is structurally controllable to first order.

If it remains rank deficient, then add a fifth genuinely junction-local element such as a rounded cuboid boss / partial-height post rather than continuing to enlarge the parameter grid.

---

## 10. Minimum HFSS program

Do not start with a Cartesian sweep.

Run one v3.4 baseline and central-difference perturbations:

- a_H = 20.4 +/- 0.4 mm;
- L_H = 5.5 +/- 1.0 mm;
- b_C = 9.0 +/- 0.4 mm;
- w_t = 4.572 +/- 0.5 mm.

This is 9 total solves including the center case. Because the center case is already committed, the next HFSS batch can run only the 8 perturbation cases if exact builder/solver settings are preserved.

For every solve extract:

1. full complex Gamma_H(f), not only return-loss magnitude;
2. theta_H(f)=asin|t_H|;
3. Gamma_0 and Gamma_1 at 10.25 GHz;
4. worst forbidden parity coupling;
5. maximum local E field per accepted watt if practical.

The first decision is Jacobian rank, not the best single RL number.

---

## 11. High-power reason for preferring a broad reduced-height cell

A thin tuning screw or small cylindrical post can create strong local field enhancement.

The present project eventually requires 30 kW peak power, so the first passive matching topology should avoid unnecessarily sharp or small-radius conductors.

The proposed capacitive cell uses broad symmetric shoulders with shallow intrusion. For later power qualification, use rounded internal edges and report

\[
K_E=
E_{max,local}/E_{max,WR90}.
\]

Do not claim the 30 kW rating from PEC S parameters.

A conventional post/boss remains a fallback if the reduced-height cell does not provide an independent reactive direction.

---

## 12. Relation to published structures

The revised topology is consistent with established wideband waveguide-junction practice:

- H-plane T-junction matching commonly uses local iris/post elements rather than only a remote transformer;
- wideband magic-T designs combine multiple local conducting discontinuities;
- recent ridge-waveguide Magic-T work uses a conductive H-junction wall together with local height compression / stepped transitions;
- recent H-plane T-junction work explicitly adds extra post geometry degrees of freedom to improve broadband matching.

Relevant examples:

- DOI 10.3390/electronics11244075
- DOI 10.3390/electronics13122407
- DOI 10.2478/jee-2025-0038
- DOI 10.1109/APS.2010.5561941

The dimensions above are not copied from those designs; they are derived from the current WR90 full-wave response.

---

## 13. Decision

The v3.3 topology should remain as the solved reference, but it should not be treated as the preferred final H structure.

The next structural candidate is

\[
\boxed{
\text{mild width throat}
+
\text{localized reduced-height capacitive cell}
+
\text{independent terminal ridge}.
}
\]

This change is justified by:

1. the measured v3.3 slope reversal;
2. the extracted center impedance 0.815+j1.988;
3. the four-real-condition broadband matching requirement;
4. the weak old Lt sensitivity;
5. the need for a high-power-compatible local reactive control.

The next decision point is the measured rank and conditioning of J_H,4.


---

## 14. Post-baseline update (2026-09-22)

The committed v3.4 center solve uses:

- a_H = 20.4 mm;
- L_H = 5.5 mm;
- b_C = 9.0 mm;
- L_C = 2.5 mm;
- w_t = 4.572 mm;
- g_t/L_t = 5.8/7.5 mm.

Measured full-band values are:

- H/even worst return loss: 2.663 dB at 9.0 GHz;
- H/even minimum desired coupling: -3.388 dB at 9.0 GHz, |t_H|min = 0.677;
- E/odd worst return loss: 5.431 dB;
- worst forbidden parity coupling: -48.728 dB.

At 10.25 GHz the H/even reflection is approximately

\[
\Gamma_0 \approx 0.466 + j0.449,
\]

which corresponds to

\[
z_{in} \approx 1.195 + j1.843.
\]

Compared with v3.3, the real part has moved through unity while the positive reactive mismatch remains large. Therefore the next question is not another broad Cartesian sweep. It is whether the four selected controls provide four independent first-order directions.

The terminal-ridge-width finite-difference half-step is revised from 0.8 mm to 0.5 mm because the former produces a lower sample at 3.772 mm, outside the documented 4.0--6.5 mm geometry range.

The next program is therefore:

1. reuse or re-run the exact center case;
2. run the eight central-difference perturbations;
3. build both the raw Jacobian and a perturbation-step-normalized Jacobian;
4. inspect singular values and effective rank;
5. only after full-rank control is demonstrated, compute a trust-limited Newton candidate;
6. keep tuning bolts out of the loop until the passive H block reaches the staged 10/15/20 dB gates.
