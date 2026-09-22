# Mixed-mode / impedance-taper design v1

## 1. Purpose

This is the **first practical HFSS design model**, not a hardware-qualified
solution.  The goal is to replace the obsolete scalar-only seed by a model that
is still simple enough to implement quickly but respects the main physics:

1. the magic-tee/four-way combiner is a multiport sum/difference network;
2. the ridge taper should be designed in impedance space before geometry space;
3. tuning bolts are small residual-reflection controls, not the main broadband
   matching mechanism;
4. peak field must be tracked together with S parameters.

The current geometry baseline is

[
w=4.572 {m mm},
]

[
(g_1,L_1)=(7.672, 9.872) {m mm},
]

[
(g_2,L_2)=(4.984, 8.857) {m mm}.
]

The old 5.8/9.2 mm ridge-width seed is no longer the active baseline.

---

## 2. Sum/difference basis for one symmetric tee

For the two collinear arms define

[
a_Sigma={a_1+a_2oversqrt2},
qquad
a_Delta={a_1-a_2oversqrt2}.
]

If the collinear-port reflection/coupling block is

[
S_c=
egin{bmatrix}
r & c\
c & r
end{bmatrix},
]

then the symmetric and antisymmetric excitations diagonalize it:

[
Gamma_Sigma=r+c,
qquad
Gamma_Delta=r-c.
]

Conversely,

[
S_{11}={Gamma_Sigma+Gamma_Deltaover2},
qquad
S_{12}={Gamma_Sigma-Gamma_Deltaover2}.
]

This is the first important correction to the old scalar-load picture.
A good (Sigma)-mode match alone does not guarantee input isolation; the
(Delta) channel must also be controlled.

### First HFSS target

For v1, simulate one tee twice:

- equal-phase collinear excitation -> (Sigma) case;
- 180-degree collinear excitation -> (Delta) case.

Record over 9--11.5 GHz:

[
Gamma_Sigma(f),qquad Gamma_Delta(f).
]

The first-pass internal target is

[
|Gamma_Sigma|, |Gamma_Delta|
<10^{-25/20}approx0.0562.
]

This is intentionally tighter than the external 22 dB requirement.

---

## 3. Four-way modal basis

For four input waves (mathbf a=[a_1,a_2,a_3,a_4]^T), use the orthogonal
basis

[
U={1over2}
egin{bmatrix}
1&1&1&1\
sqrt2&-sqrt2&0&0\
0&0&sqrt2&-sqrt2\
1&1&-1&-1
end{bmatrix}.
]

Then

[
mathbf a_m=Umathbf a
]

contains

[
(Sigma,Delta_1,Delta_2,Delta_3).
]

A first reduced reflection model is

[
R_{m port}
=
U^T
operatorname{diag}
(Gamma_Sigma,Gamma_{Delta1},Gamma_{Delta2},Gamma_{Delta3})
U.
]

This gives a much cleaner optimization target than independently chasing many
port S parameters.

For the symmetric first version one may initially set

[
Gamma_{Delta1}approxGamma_{Delta2}
]

and allow (Gamma_{Delta3}) to be determined by the second-stage tee.

---

## 4. Efficiency budget

For equal coherent inputs,

[
eta_{m comb}
=
{left|a_1+a_2+a_3+a_4ight|^2
over
4sum_i |a_i|^2}.
]

The complete four-way tree has approximately two combining stages per signal
path.  If the two stages have similar efficiency (eta_s),

[
eta_{m total}approxeta_s^2.
]

Therefore the external requirement

[
eta_{m total}>0.95
]

implies roughly

[
eta_s>sqrt{0.95}=0.9747.
]

This corresponds to only about 0.11 dB allowable loss per combining stage
before additional margin is included.  Hence v1 uses the internal target

[
eta_{m comb}>0.97.
]

---

## 5. Impedance-space taper

The old longitudinal profile directly smooth-stepped ridge width/gap.
That is not the preferred design variable because

[
Z=Z(w,g,f)
]

is nonlinear.

For a slowly varying guide, a useful first-order reflection picture is

[
Gamma(f)
approx
{1over2}
int
{dln Z(z)over dz}
expleft[
-2jint_0^zeta(z',f),dz'
ight]dz.
]

So v1 defines a desired (Z(z)) first.

For each segment use

[
s(t)=3t^2-2t^3,
qquad 0le tle1,
]

and

[
ln Z(t)
=
(1-s)ln Z_A+sln Z_B.
]

Current control points are

| z (mm) | target (Z/Z_{m ref}) | gap (mm) |
|---:|---:|---:|
| 0.000 | 1.000 | 10.160 |
| 9.872 | 0.842 | 7.672 |
| 18.729 | 0.609 | 4.984 |

For **v1 only**, the gap between these calibrated stations is still obtained
with a smooth geometry interpolation.  This is deliberately approximate.

The next calibration step is:

1. HFSS uniform-ridge sweep in (g);
2. extract the chosen modal impedance definition;
3. build a numerical table (Z_{m HFSS}(g,f_0));
4. invert it to obtain (g(Z));
5. regenerate the taper.

This gives an incremental path from the current analytic seed to the real
full-wave geometry without discarding the existing work.

---

## 6. Two-bolt residual-reflection model

Tuning bolts are introduced only after the passive ridge/tee structure already
has a broadband match.

For small local perturbations,

[
Gamma_{m total}(f)
approx
Gamma_0(f)
+
sum_i
gamma_i(f)e^{-2jeta(f)z_i}.
]

Thus each bolt provides two useful controls:

- penetration -> mainly changes (|gamma_i|);
- axial position -> changes reflected-wave phase.

At the electrical center (f_0approx10.195) GHz, the current two ridge
sections give approximate guided wavelengths

[
lambda_{g1}approx36.28 {m mm},
qquad
lambda_{g2}approx34.01 {m mm}.
]

Hence

[
lambda_{g1}/4approx9.07 {m mm},
qquad
lambda_{g2}/4approx8.50 {m mm}.
]

Because the reflection phase contains (2eta z), spacing two weak tuning
perturbations by approximately (lambda_g/4) makes their reflected phasors
approximately opposite at the center frequency.

Therefore the first two-bolt seed is

[
oxed{Delta z_{m bolt}=8.8 {m mm}}
]

with an initial sweep

[
7.5leDelta z_{m bolt}le10.0 {m mm}.
]

Use shallow penetration first:

[
0le dle2.0 {m mm},
qquad
d_{m initial}approx0.6 {m mm}.
]

This is not a final high-power bolt geometry; it is only a controlled
full-wave tuning seed.

---

## 7. High-power normalization

Do not compare only normalized HFSS field plots.

Define

[
k_E(f)
=
{E_{max}(f)oversqrt{P_{m accepted}(f)}}
quad
[{m V/m}/sqrt{m W}].
]

Then for a requested accepted power (P),

[
E_{max}(P,f)=k_E(f)sqrt P.
]

For 30 kW,

[
E_{max,30kW}=k_Esqrt{30000}.
]

Retain the simpler field-enhancement diagnostic

[
K_E=
{E_{m local,max}over E_{m straight,max}}
]

with a first screening target

[
K_E<3,
]

but report the absolute scaled field as well.

---

## 8. Compactness versus evanescent coupling

The device should be compact, but the junctions cannot be treated as
independent scalar blocks when placed arbitrarily close.

At the high end of the band the first higher WR90 modes are still evanescent,
yet their decay distance is not negligible compared with an 8--20 mm
transition.

Therefore the v1 simulation hierarchy is:

1. uniform ridge sections;
2. passive ridge transformer;
3. single magic tee in (Sigma) and (Delta) excitation;
4. **tee + nearest ridge transition as one full-wave block**;
5. two-stage four-way model;
6. only then add tuning bolts;
7. finite conductivity + field scaling.

This is sufficient for the first engineering version.  A rigorous multimode
network extraction can be added after a working HFSS geometry exists.

---

## 9. First-pass optimization variables

Keep the first search intentionally small:

[
win[4.0,5.5] {m mm},
]

[
g_1in[6.8,8.4] {m mm},
qquad
g_2in[4.3,5.8] {m mm},
]

[
L_1in[9.0,10.7] {m mm},
qquad
L_2in[8.0,9.7] {m mm}.
]

Only after the passive structure approaches the target add

[
Delta z_{m bolt}in[7.5,10.0] {m mm},
qquad
d_{m bolt}in[0,2.0] {m mm}.
]

For the first deliverable, a reasonable coarse acceptance gate is:

- return loss better than 20 dB over most of the band and approaching 22 dB;
- isolation approaching 22 dB;
- coherent efficiency above 95% in the useful band;
- no unexpected propagating higher mode below 11.5 GHz;
- no severe field hot spot.

The final version should restore the stricter 22/25 dB targets and tolerance
analysis.

---

## 10. Current interpretation

The design is now best viewed as

[
oxed{
	ext{mixed-mode tee}
ightarrow
	ext{impedance-space ridge taper}
ightarrow
	ext{small residual bolt tuning}
}
]

rather than

[
	ext{scalar }0.5Z_0
ightarrow
	ext{two arbitrary ridge steps}
ightarrow
	ext{large bolt correction}.
]

This v1 is intentionally approximate, but its free parameters now correspond
to physically distinct mechanisms and are suitable for the first HFSS 2022
parameterized model.
