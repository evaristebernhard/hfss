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
