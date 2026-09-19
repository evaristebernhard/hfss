# Parity-block network synthesis v3

## 1. Scope

This note continues the v2 parity-corrected analysis without running a new HFSS solve.

The starting point is the latest full-wave result in

- `hfss/results/v2_parity_corrected/single_magictee_v2_baseline.s4p`

for the geometry

- WR90: 22.86 x 10.16 mm
- w = 4.572 mm
- g1/L1 = 7.672/9.872 mm
- g2/L2 = 4.984/8.857 mm
- terminal ridge length = 6.0 mm
- E arm rotated to the parity-correct orientation.

The purpose here is to answer a narrower theoretical question:

> What is the minimum network order and what physical mechanism is missing in each parity block?

No new HFSS result is assumed below.

---

## 2. Exact parity reduction

Define

[
c_+ = rac{P_1+P_2}{sqrt 2},
qquad
c_- = rac{P_1-P_2}{sqrt 2}.
]

For the corrected symmetric geometry, the full-wave S matrix is numerically block diagonal to very high accuracy:

[
S_m
approx
egin{pmatrix}
r_+ & 0 & t_H & 0\
0 & r_- & 0 & t_E\
t_H & 0 & r_H & 0\
0 & t_E & 0 & r_E
end{pmatrix}.
]

Across 9--11.5 GHz, the worst forbidden coupling in the current result is about -59 dB.

Therefore the single tee can be treated as two nearly independent reciprocal two-ports,

[
(c_+,H)
oplus
(c_-,E).
]

This is the correct reduced model for all subsequent synthesis.

---

## 3. Unitary two-port parameterization

The present model is PEC and is numerically almost lossless. The largest observed column-power error is only about

[
7.3	imes 10^{-6}.
]

Thus each parity block is approximately a reciprocal unitary two-port.

A reciprocal lossless two-port can be written as

[
S_q
=
e^{jchi}
egin{pmatrix}
e^{jdelta}cos	heta & jsin	heta\
jsin	heta & e^{-jdelta}cos	heta
end{pmatrix}.
]

Hence

[
|r_1|=|r_2|=|cos	heta|,
qquad
|t|=|sin	heta|.
]

The 22 dB reflection requirement is

[
|Gamma|<10^{-22/20}=0.07943,
]

so

[
	heta > arccos(0.07943)
approx 85.44^circ.
]

The internal 25 dB target requires

[
	heta > arccos(0.05623)
approx 86.78^circ.
]

Therefore the core design objective can be reduced to

[
J
=
max_{fin[9,11.5]}
max{|r_+(f)|,|r_-(f)|}.
]

The desired transmission magnitude is then fixed automatically by losslessness.

---

---

## 3.1 Symmetry theorem behind the block diagonalization

The parity decomposition is not merely a convenient basis change.

Let (mathcal P_x) denote the mirror operation

[
xmapsto -x
]

together with the corresponding vector transformation of the electromagnetic fields.

If the geometry, materials and boundary conditions are invariant under this reflection, the Maxwell operator commutes with (mathcal P_x).

The scattering operator must therefore commute with the induced port-parity operator:

[
[S,mathcal P_x]=0.
]

Hence (S) preserves the eigenspaces of (mathcal P_x).

For the corrected v2 geometry,

[
mathcal P_x c_+=+c_+,
qquad
mathcal P_x H=+H,
]

while

[
mathcal P_x c_-=-c_-,
qquad
mathcal P_x E=-E.
]

Therefore, in the exact symmetric problem,

[
S_{c_+,c_-}
=
S_{c_+,E}
=
S_{H,c_-}
=
S_{H,E}
=
0.
]

The observed -59 dB level is therefore best interpreted as numerical/meshing residual rather than a physical coupling mechanism.

This gives an important design rule:

[
oxed{
	ext{preserve }xmapsto-x	ext{ symmetry during matching optimization.}
}
]

---

## 3.2 Common-mode design variables versus differential tolerance variables

Suppose a tuning feature is introduced in a mirrored pair with parameters (p_L) and (p_R).

Define

[
p_+
=
rac{p_L+p_R}{2},
qquad
p_-
=
rac{p_L-p_R}{2}.
]

The common-mode variable (p_+) preserves mirror symmetry.

To first order it may change

[
r_+, r_-, t_H, t_E,
]

but it does not create cross-parity scattering.

The differential variable (p_-) is odd under the mirror operation and therefore is the leading parameter that generates forbidden coupling.

Near a symmetric design,

[
S_{+-}
approx
left.
rac{partial S_{+-}}{partial p_-}
ight|_{p_-=0}
p_-,
]

while

[
left.
rac{partial S_{+-}}{partial p_+}
ight|_{p_-=0}
=0.
]

The same statement applies to (S_{H,E}), (S_{c_+,E}), and (S_{c_-,H}).

Thus future tuning bolts, posts, irises or machining features should be parameterized in two different categories:

### Design coordinates

Use symmetric/common-mode combinations such as

[
p_+
]

to improve matching.

### Tolerance coordinates

Use antisymmetric/differential combinations such as

[
p_-
]

to quantify isolation degradation from machining and assembly error.

This separation prevents an optimizer from improving return loss by accidentally sacrificing the parity protection that currently gives more than 50 dB of modal isolation.


## 4. Why the physical-port RL can be misleading

In the physical basis,

[
S_{11}
=
rac{r_+ + r_-}{2},
qquad
S_{12}
=
rac{r_+ - r_-}{2}.
]

So a moderate physical-port return loss can arise from partial cancellation between two large modal reflections.

For the current v2 result the physical P1 return loss is around 14 dB, while the P1--P2 isolation is only a few dB.

Therefore the correct acceptance variables are not just physical (S_{11}) and (S_{12}), but directly

[
r_+(f),qquad r_-(f).
]

If both satisfy

[
|r_+|,|r_-|<0.07943,
]

then by the triangle inequality both physical return loss and collinear-port isolation automatically satisfy the 22 dB amplitude bound.

---

## 5. De-embedding the 35 mm collinear arms

The two collinear wave ports are 35 mm from the junction center.

For plain WR90,

[
eta_{10}(f)
=
rac{2pi f}{c}
sqrt{1-left(rac{f_c}{f}ight)^2},
qquad
f_c=rac{c}{2a}.
]

The junction-plane reflection coefficient is therefore

[
Gamma_J(f)
=
Gamma_{m port}(f)
e^{+2jeta_{10}(f)L_c},
qquad
L_c=35 {m mm}.
]

The normalized junction-plane impedance is then

[
z_J(f)
=
rac{1+Gamma_J(f)}
     {1-Gamma_J(f)}.
]

This step is essential. Direct conversion of the port-plane reflection to impedance mixes the actual mismatch with 35 mm of propagation phase.

---

## 6. Odd/E block: nearly pure real, slowly varying load

After de-embedding the common collinear length, the odd block is unusually simple.

Let

[
x
=
rac{f-10.25 {m GHz}}{1.25 {m GHz}},
qquad
xin[-1,1].
]

A linear fit over all 101 HFSS frequency points gives

[
oxed{
z_-(x)
approx
(0.389605-0.091749x)
+
j(0.019580+0.002532x)
}
]

with maximum fitting errors of about

[
6.2	imes10^{-4}
]

in the real part and

[
3.4	imes10^{-3}
]

in the imaginary part.

Thus the E block is not primarily a reactive-resonance problem.

Its dominant behavior is

[
R_-(f):
quad
0.482 {m at} 9 {m GHz}
ightarrow
0.298 {m at} 11.5 {m GHz},
]

while the normalized reactance remains only about 0.02.

So the correct interpretation is

[
oxed{
	ext{E block}
approx
	ext{frequency-varying resistive transformer problem}.
}
]

This is much cleaner than the H block.

---

## 7. Minimum matching order for the E block

Using the extracted linear load model above, consider an idealized lossless transmission-line transformer with frequency-independent normalized characteristic impedances but WR90 dispersion in the electrical lengths.

This is not yet a realizable ridge geometry. It is only a network-order test.

### One-section family

Optimizing one section gives approximately

[
Z_1/Z_0 approx 0.629,
qquad
L_1approx8.49 {m mm},
]

but the best minimax return loss is only about

[
oxed{15.3 {m dB}}.
]

Therefore one simple quarter-wave-like section is not sufficient for the full 9--11.5 GHz band.

### Two-section family

For two sections, the reduced model gives approximately

[
oxed{
Z_1/Z_0approx0.753,
qquad
Z_2/Z_0approx0.497
}
]

with

[
oxed{
L_1approx11.34 {m mm},
qquad
L_2approx9.69 {m mm}.
}
]

The corresponding minimax result is about

[
oxed{24.9 {m dB}}.
]

This crosses the 22 dB external target and is very close to the 25 dB internal target.

### Three-section family

A three-section idealized model can push the same fitted load above roughly 30 dB in the reduced model.

The key conclusion is therefore not the exact dimensions, but the order:

[
oxed{
	ext{E block requires two broadband matching degrees of freedom;
one is not enough.}
}
]

This strongly argues against using a single bolt or a single short throat as the main E-arm matcher.

---

## 8. First geometry translation for the E block

The target ratios above can be mapped only heuristically through the repository's Cohn double-ridge model, because the HFSS `Zwave` normalization and the Cohn voltage-current normalization are not identical.

Therefore the following numbers are geometry seeds, not rigorous impedance identities.

For a common ridge-width ratio

[
w_E/a=0.30,
qquad
w_Eapprox6.858 {m mm},
]

the Cohn model maps the two target impedance ratios approximately to

[
Z_1/Z_{m ref}approx0.753
quadRightarrowquad
g_{E1}approx7.20 {m mm},
]

[
Z_2/Z_{m ref}approx0.497
quadRightarrowquad
g_{E2}approx4.59 {m mm}.
]

The corresponding first TE20-like cutoff estimates remain approximately

[
13.58 {m GHz}
quad	ext{and}quad
14.02 {m GHz},
]

both above the 11.5 GHz operating edge.

This wider ridge is attractive because it achieves the lower effective impedance without forcing the second gap as small as the (w/a=0.20) geometry.

The numbers above should be treated as a high-power-friendly E-arm initializer only.

---

## 9. Even/H block: use admittance, not impedance

The H block is more naturally represented by the de-embedded normalized admittance

[
y_+(f)=rac{1}{z_+(f)}.
]

Over all 101 frequency points, a compact quadratic fit is

[
oxed{
Re y_+
approx
0.114602
-0.058474x
+0.006306x^2
}
]

and

[
oxed{
Im y_+
approx
-0.080057
-0.056137x
+0.026638x^2.
}
]

The maximum component-wise fitting error is about (2.3	imes10^{-3}).

At the band center this gives approximately

[
y_+(10.25 {m GHz})
approx
0.115-j0.080.
]

Two facts follow immediately.

First, the conductance is much smaller than unity:

[
G_+approx0.115.
]

Second, there is a substantial residual susceptance.

So the H problem is not a simple phase correction.

It requires both

1. a large conductance transformation;
2. a compensating susceptance.

---

## 10. H block as a frequency-varying inverter

If the susceptance were first cancelled, the center-frequency equivalent resistance would be roughly

[
R_{m eq}
approx
rac{1}{G_+}
approx
8.7.
]

A single quarter-wave impedance-transformer estimate would then require

[
Z_t/Z_0
approx
sqrt{R_{m eq}}
approx
2.95.
]

This is qualitatively very different from the old scalar (0.5Z_0) picture.

Equivalently, define an effective impedance-inverter strength

[
K_{m eff}(f)
sim
rac{1}{sqrt{G_+(f)}}.
]

Using the fitted conductance, (K_{m eff}) rises strongly across the band, from roughly the mid-2 range near 9 GHz toward about 4 near 11.5 GHz.

Thus the even-mode problem is well summarized as

[
oxed{
	ext{H block}
approx
	ext{strongly frequency-dependent inverter}
+
	ext{junction susceptance}.
}
]

This is why a small change of (g_2) or terminal ridge length cannot be expected to solve the full 24.4% bandwidth problem.

---

## 11. Why a downstream H taper alone is unlikely to be enough

Using the fitted de-embedded H load as a conditional target, the same idealized transmission-line family gives only about

- 9.4 dB minimax return loss for one section;
- 13.2 dB for two sections.

These are reduced-model figures, not rigorous bounds, but they are important diagnostically.

By contrast, the same synthesis family gives about 24.9 dB for the E load with two sections.

Therefore the two blocks behave fundamentally differently.

The E block is compatible with ordinary transformer synthesis.

The H block is not.

The theoretical conclusion is

[
oxed{
	ext{before adding more H-arm transformer sections,
modify the H-plane junction coupling itself.}
}
]

Candidate physical mechanisms include

- H-plane iris/aperture shaping;
- a broad-wall step near the junction;
- a local inductive/capacitive post or ridge termination;
- changing the terminal ridge shape rather than only its length;
- a short high-impedance throat before the existing ridge transformer.

The exact mechanism should be selected only after its symmetry class is checked: it must preserve the even/odd block separation.

---

## 12. Revised role of g2 and terminal ridge length

The current Stage-A variables

[
(g_2,L_t)
]

remain useful, but their role must be stated more narrowly.

They are best regarded as local controls for

[
(c_+,H)
]

and mainly for the even-channel terminal susceptance and phase.

They should not be expected to solve the E block.

Nor should a successful change in physical-port (S_{11}) be accepted unless it also reduces

[
|r_+|
]

directly.

A theoretically cleaner H-stage sequence is

[
oxed{
	ext{junction-coupling parameter}
ightarrow
L_t
ightarrow
g_2
ightarrow
	ext{remaining ridge taper}.
}
]

The first parameter must alter the effective conductance, not only the electrical phase.

---

---

## 12.5 A lower-order impossibility check from the conductance range

There is a useful result that does not depend on the detailed transmission-line realization.

Assume first that the H susceptance can be cancelled perfectly, and suppose the only remaining control is a frequency-independent conductance scale (s):

[
G_{m new}(f)=s,G_+(f).
]

For a real normalized admittance (G), the reflection magnitude is

[
|Gamma|
=
left|
rac{1-G}{1+G}
ight|.
]

If the original conductance ranges over

[
G_{min}le G_+(f)le G_{max},
]

the minimax constant scale is obtained by balancing the two endpoint reflections:

[
(sG_{min})(sG_{max})=1.
]

Hence

[
oxed{
s_*=rac{1}{sqrt{G_{min}G_{max}}}.
}
]

From the de-embedded v2 data,

[
G_{min}approx0.0636,
qquad
G_{max}approx0.1774,
]

so

[
s_*approx9.42.
]

Even under the optimistic assumption of perfect reactive cancellation, the optimally rescaled endpoint admittances are only about

[
0.599
quad	ext{and}quad
1.670,
]

giving

[
oxed{
RL_{m best, constant H scale}
approx12.0 {m dB}.
}
]

This is a genuine structural statement for the extracted conductance trajectory:

[
oxed{
	ext{one frequency-independent H coupling parameter cannot reach 22 dB.}
}
]

The H-side design therefore needs a parameter that changes the frequency dependence of the coupling, not merely its overall strength.

The same test can be applied to the nearly real E load.

Using

[
R_{E,min}approx0.2985,
qquad
R_{E,max}approx0.4820,
]

the best possible frequency-independent impedance scaling gives only

[
oxed{
RL_{m best, constant E scale}
approx18.5 {m dB}.
}
]

This independently confirms the transmission-line synthesis result that the E block needs at least one additional frequency-shaping degree of freedom beyond a single transformer ratio.

---

## 12.6 How many effective H-side degrees of freedom are indicated?

Write the fitted H conductance as

[
G_+(x)
=
g_0+g_1x+g_2x^2
]

with

[
g_0=0.114602,
qquad
g_1=-0.058474,
qquad
g_2=0.006306.
]

Suppose a junction modification produces a low-order frequency-dependent coupling multiplier

[
M(x)
=
a(1+bx+cx^2).
]

To flatten the transformed conductance

[
widetilde G(x)=M(x)G_+(x)
]

around the center, choose the first coefficients so that the constant, linear and quadratic terms equal (1,0,0).

This gives approximately

[
a=rac1{g_0}approx8.73,
]

[
b=-rac{g_1}{g_0}approx0.510,
]

[
capprox0.205.
]

With this purely algebraic conductance flattening, the residual endpoint mismatch corresponds to a return-loss scale of roughly 27--29 dB before accounting for the susceptance.

By contrast:

- overall scale only -> about 12 dB;
- scale plus first-order tilt -> still only about 18--20 dB;
- scale plus curvature control -> potentially enough margin for the 22/25 dB target.

This does **not** mean three literal tuning screws are required.

It means the H-plane geometry must provide approximately three independent effects:

1. set the coupling level;
2. correct its first-order frequency slope;
3. correct enough curvature to keep the band edges from separating.

The existing variables can now be interpreted more usefully:

- a new H-junction aperture/throat variable: mainly coupling level;
- terminal ridge length (L_t): mainly phase / susceptance and some slope;
- (g_2) or terminal ridge shape: coupling slope/curvature.

This makes

[
oxed{
p_H
=
(p_{m aperture},L_t,g_2)
}
]

a more defensible first three-parameter H model than blindly reopening all five ridge variables.

The susceptance fit

[
B_+(x)
=
-0.080057
-0.056137x
+0.026638x^2
]

is comparatively easier: cancelling only its constant and linear terms leaves a quadratic residual of order (0.027), small enough that the corresponding reflection scale is already well below the main conductance error.

Therefore the principal H-side difficulty is conclusively the **frequency dependence of the coupling conductance**, not merely junction reactance.


## 13. Recommended reduced-order design hierarchy

The analysis now suggests the following hierarchy.

### E block

Use a genuine two-degree-of-freedom broadband transformer:

[
(c_-,E):
qquad
	ext{junction}
ightarrow
	ext{section 2}
ightarrow
	ext{section 1}
ightarrow
	ext{WR90}.
]

The reduced target is approximately

[
(Z_1/Z_0,Z_2/Z_0)
sim
(0.75,0.50).
]

### H block

Do not begin by adding more taper sections.

First alter the local junction so that the de-embedded conductance becomes order unity:

[
G_+(f)sim1
]

instead of

[
G_+(f)sim0.06	ext{--}0.18.
]

Only after the conductance trajectory is corrected should the existing ridge taper be used to flatten the remaining broadband reflection.

---

## 14. Consequence for the optimization objective

Because the parity leakage is already below about -59 dB, the next optimizer does not need to spend objective weight on forbidden couplings.

A more efficient objective is

[
J_{m match}
=
max_f
max{|r_+(f)|,|r_-(f)|}
]

subject to

[
max_f |S_{m forbidden}(f)|
<
10^{-25/20}
]

as a constraint rather than a primary objective.

For high power, add

[
J_E
=
max_f
rac{E_{max,m local}}
     {E_{max,m straight,WR90}}
]

and reject geometries with excessive field concentration.

This separates three mechanisms cleanly:

1. modal symmetry;
2. broadband matching;
3. peak-field control.

---

## 15. Current theoretical conclusions

1. The v2 parity correction is successful and should not be altered casually.
2. The single tee is now accurately modeled as two independent lossless two-ports.
3. The E block is almost purely resistive after de-embedding and has a nearly linear load trajectory across the band.
4. A one-section E matcher is theoretically insufficient; a two-section matcher is sufficient in the reduced model.
5. A useful E-arm impedance-space target is roughly ((0.75,0.50)).
6. A wider E ridge around (w/aapprox0.30) is attractive because it realizes those lower impedance levels with larger gaps.
7. The H block has low conductance plus substantial susceptance and cannot be interpreted as the old (0.5Z_0) scalar load.
8. A two-section downstream transformer family does not come close to the 22 dB target for the extracted H load.
9. Therefore the next H-side theoretical degree of freedom should change junction coupling, not merely taper length.
10. The previous port-plane conclusion of a huge H reactance was contaminated by the 35 mm reference-plane phase; all future load interpretations should use de-embedded quantities.

The next theory task is to construct a minimal even-mode junction model

[
Y_H(f)
=
G_H(f)+jB_H(f)
]

with one explicit coupling parameter and one explicit reactive parameter, then solve analytically for the values required to move the fitted H trajectory toward (Y=1) over the band.

---

## 16. Explicit H-block transformer + shunt-admittance interpretation

A useful minimal even-mode equivalent circuit is

[
oxed{
y_H(f)
approx
n_H^2(f)+jb_H(f)
}
]

where

- (n_H(f)) is an effective transformer/coupling coefficient between the even collinear mode and the H branch;
- (b_H(f)) is the residual normalized shunt susceptance of the junction and nearby discontinuities.

This is consistent with standard H-plane T-junction equivalent-network descriptions based on ideal-transformer and admittance representations.

From the fitted v2 admittance,

[
G_H(x)
=
0.114602
-0.058474x
+0.006306x^2,
]

so

[
n_H(x)=sqrt{G_H(x)}.
]

Representative values are

[
n_H(-1)approx0.424,
qquad
n_H(0)approx0.339,
qquad
n_H(+1)approx0.250.
]

Thus the effective coupling is not only too small; it also decreases strongly with frequency.

The amplitude correction required to move the conductance toward unity is

[
m_H(x)=rac1{n_H(x)}.
]

At the same three points,

[
oxed{
m_H(-1)approx2.36,quad
m_H(0)approx2.95,quad
m_H(+1)approx4.00.
}
]

A quadratic expansion around band center is

[
oxed{
m_H(x)
approx
2.954
+0.754x
+0.207x^2.
}
]

Equivalently, in logarithmic form,

[
oxed{
ln m_H(x)
approx
1.08295
+0.26026x
+0.03948x^2,
}
]

whose maximum approximation error over the fitted band is only about (4.2	imes10^{-3}).

This is a compact target for future geometry-Jacobian fitting.

The reactive correction target is simply

[
b_{m corr}(x)
=
-B_H(x),
]

hence

[
oxed{
b_{m corr}(x)
approx
0.080057
+0.056137x
-0.026638x^2.
}
]

The H matching geometry therefore has a clear reduced-order target:

1. increase mean coupling by roughly a factor 3 in amplitude;
2. make the coupling increase with frequency strongly enough to compensate the present negative slope;
3. supply an opposite effective susceptance with modest curvature.

---

## 17. Why a symmetric H-plane step/iris cell is the preferred new structure

Standard rectangular-waveguide discontinuity theory models H-plane discontinuities as primarily inductive elements, while E-plane discontinuities are primarily capacitive. A symmetric H-plane discontinuity is attractive here because it can be placed near the sidewalls, where the TE10 electric field is small.

For the present 30 kW peak-power requirement this is preferable, as a first choice, to a sharp center post or thin probe located near an electric-field maximum.

Published X-band magic-T designs also demonstrate that an H-plane T-junction can be matched by a broad step at the junction, with its height, thickness and longitudinal offset used as optimization variables. Separate high-power work has reported that sharp matching-probe / phase-plate tips can become the limiting high-field features, reinforcing the preference for broad, rounded matching geometry rather than relying on a deep sharp probe.

For the present geometry, the proposed H-side matching cell is therefore:

[
oxed{
	ext{symmetric H-plane step/iris}
+
	ext{short terminal ridge}
}
]

with all metal features mirrored under (xmapsto-x).

A useful abstract parameter set is

[
oxed{
p_H
=
(a_i,t_i,d_i,w_t)
}
]

where

- (a_i): centered iris opening / effective H-plane aperture;
- (t_i): longitudinal thickness of the step/iris;
- (d_i): distance from the tee reference plane;
- (w_t): terminal-ridge width, allowed to differ from the upstream taper width.

The existing (g_2) and (L_t) remain available but should not all be released at the same time.

### Intended control roles

The intended first-order roles are

[
a_i
ightarrow
	ext{coupling level},
]

[
t_i
ightarrow
	ext{coupling dispersion / curvature},
]

[
d_i
ightarrow
	ext{effective reflection phase and susceptance},
]

[
w_t
ightarrow
	ext{local H-arm impedance with less need to shrink the ridge gap}.
]

These are not exact one-to-one mappings; the future Jacobian will quantify the cross-coupling.

---

## 18. H-side scale estimates before simulation

At 10.25 GHz the plain-WR90 guided wavelength is approximately

[
lambda_gapprox38.05 {m mm},
qquad
lambda_g/4approx9.51 {m mm}.
]

Therefore a matching discontinuity located within roughly

[
0.18lambda_g
lesssim d_i
lesssim
0.27lambda_g
]

corresponds to about

[
oxed{
6.8 {m mm}
lesssim d_i
lesssim
10.3 {m mm}.
}
]

This range is large enough to rotate the discontinuity reflection phasor substantially while remaining compact.

A published X-band H-plane tee using a broad matching step used, at 9.25 GHz, a full-width step with dimensions of order 2.9 mm height, 3.2 mm thickness and 8.23 mm offset. These values are not transferable directly because that design used a different reduced-height topology, but after electrical scaling they support a first-order dimensional scale of a few millimeters for step thickness/depth and roughly 7--10 mm for offset.

Accordingly, a theory-only initial range is

[
oxed{
t_isim2.0	ext{--}4.0 {m mm},
}
]

[
oxed{
d_isim6.5	ext{--}10.5 {m mm}.
}
]

The aperture (a_i) should initially be kept broad; the goal is not to create a narrow high-field slot.

All exposed edges should ultimately be rounded. A first mechanical radius scale of roughly 0.8--1.5 mm is more consistent with the high-power objective than a sharp corner.

---

## 19. Terminal ridge width as a separate high-power variable

The current model forces the terminal ridge width to remain

[
w_t=4.572 {m mm}.
]

The Cohn model shows that, at fixed gap (gapprox4.984) mm and 10.2 GHz, increasing the local ridge-width ratio changes the approximate impedance ratio as follows:

| (w_t/a) | (Z_t/Z_{m ref}) |
|---:|---:|
| 0.20 | 0.609 |
| 0.25 | 0.570 |
| 0.30 | 0.536 |
| 0.35 | 0.508 |
| 0.40 | 0.484 |

Thus widening the terminal ridge can lower the local impedance by roughly 20% without shrinking the gap.

This is not enough by itself to cure the H coupling deficit, but it is a useful high-power-friendly fine-control variable.

A reasonable later range is

[
oxed{
4.57 {m mm}
le w_t
le
8.0 {m mm}
}
]

while retaining (g_t) near 5 mm until peak-field calculations justify any smaller gap.

---

## 20. E-block geometry synthesis with ridge dispersion included

The previous ((0.75,0.50)) E-block result used idealized transmission-line sections.

A second reduced-model optimization was performed using

1. the extracted de-embedded E-load fit;
2. the repository Cohn ridge impedance model;
3. each ridge section's own frequency-dependent propagation constant.

For several common E-ridge widths, the resulting minima are:

| (w_E/a) | reduced worst RL | (g_{E1}) mm | (g_{E2}) mm | (L_{E1}) mm | (L_{E2}) mm |
|---:|---:|---:|---:|---:|---:|
| 0.20 | 24.68 dB | 5.768 | 3.518 | 10.206 | 9.211 |
| 0.25 | 24.63 dB | 6.195 | 3.935 | 10.294 | 9.218 |
| **0.30** | **24.57 dB** | **6.544** | **4.299** | **10.392** | **9.228** |
| 0.35 | 24.50 dB | 6.821 | 4.614 | 10.505 | 9.243 |

The small RL differences are not important. The important tradeoff is gap size versus higher-mode margin.

For

[
oxed{w_E/a=0.30},
]

the first approximate TE20-like cutoffs are

[
f_{20,E1}approx13.68 {m GHz},
qquad
f_{20,E2}approx14.09 {m GHz}.
]

This provides a useful margin above 11.5 GHz while keeping the smaller gap above 4.2 mm.

Therefore the recommended primary E-arm theoretical seed is

[
oxed{
w_E=0.30a=6.858 {m mm},
}
]

[
oxed{
g_{E1}=6.54 {m mm},
quad
L_{E1}=10.39 {m mm},
}
]

[
oxed{
g_{E2}=4.30 {m mm},
quad
L_{E2}=9.23 {m mm}.
}
]

A high-power alternative is (w_E/a=0.35), which increases the minimum gap to about 4.61 mm but reduces the TE20-like margin to approximately 13.5--13.6 GHz.

The (w_E/a=0.30) case is the better first compromise.

---

## 21. Physical orientation of the new E double-ridge matcher

The v2 E arm propagates along (+Z), with

- narrow dimension (B) along (X);
- broad dimension (A) along (Y).

Therefore the E-arm double ridges must be rotated consistently:

- the two ridges protrude inward from the (x=pm B/2) walls;
- the clear ridge gap is measured along (X);
- ridge width (w_E) is measured along (Y);
- the two sections extend longitudinally along (Z).

This construction preserves the (xmapsto-x) mirror symmetry and therefore preserves the odd parity of the E channel.

The new E matcher should not use an off-center ridge, single-sided post or asymmetric screw as a nominal design variable.

