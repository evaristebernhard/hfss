# Mixed-mode / impedance-space design v1

## 1. Why this replaces the old scalar-only picture

The current double-ridge geometry is a useful broadband seed, but the historical
assumption

[
Z_L = 0.5 Z_0
]

must not be treated as the physical load of a real magic-tee junction.  A
magic tee is a symmetric multiport discontinuity with evanescent content, and
the natural variables are its **sum and difference eigenchannels**.

For a symmetric pair of collinear arms, write the same-reference-plane
two-port reflection/coupling block as

[
S_c =
egin{bmatrix}
r & c\\
c & r
end{bmatrix}.
]

The orthogonal transformation

[
a_Sigma = rac{a_1+a_2}{sqrt 2},
qquad
a_Delta = rac{a_1-a_2}{sqrt 2}
]

diagonalizes this block:

[
Gamma_Sigma = r+c,
qquad
Gamma_Delta = r-c.
]

Equivalently,

[
S_{11} = rac{Gamma_Sigma+Gamma_Delta}{2},
qquad
S_{12} = rac{Gamma_Sigma-Gamma_Delta}{2}.
]

This is the correct analytic bridge between port return/isolation and the two
physical symmetry channels.  In HFSS, the useful first extraction is therefore
not a guessed scalar load.  It is the frequency-dependent complex data

[
Gamma_Sigma(f),quad
Gamma_Delta(f),
]

plus the corresponding transmission coefficients and reference-plane
information.

If the manufactured/full 3-D geometry is not exactly symmetric, the same
basis is still useful: off-diagonal terms in the mixed-mode scattering matrix
directly measure symmetry-breaking mode conversion.

---

## 2. Four-way tree as a modal transform

For the ideal four-way binary tree, the natural orthogonal basis is

[
U =
rac12
egin{bmatrix}
1&1&1&1\\
sqrt2&-sqrt2&0&0\\
0&0&sqrt2&-sqrt2\\
1&1&-1&-1
end{bmatrix}.
]

The rows correspond to one global sum mode and three independent difference
modes.  The ideal network maps four coherent input amplitudes into

[
b_m = U a.
]

For equal-amplitude equal-phase excitation, only the global sum mode is
occupied.

If the mixed-mode reflection operator is approximately diagonal,

[
R_m approx
operatorname{diag}
(Gamma_Sigma,Gamma_{Delta1},
 Gamma_{Delta2},Gamma_{Delta3}),
]

then the physical-port reflection/coupling block is

[
R_p = U^dagger R_m U.
]

This suggests a cleaner HFSS objective than blindly optimizing every physical
S-parameter independently: minimize all four modal reflections and monitor the
off-diagonal mixed-mode terms.

The external 22 dB requirement corresponds to the amplitude bound

[
10^{-22/20} approx 0.07943.
]

For design margin, the repository keeps 25 dB as the internal return/isolation
target.

---

## 3. Efficiency budget of a two-level four-way tree

The total allowed dissipative/mismatch loss associated with 95% combining
efficiency is

[
IL_{m total}
=
-10log_{10}(0.95)
approx 0.2228 {m dB}.
]

A signal from each source traverses two combining levels.  If the two levels
share the loss budget equally,

[
eta_{m stage} > sqrt{0.95}
= 0.97468,
]

or

[
IL_{m stage}
<
0.1114 {m dB}.
]

This is not a complete efficiency model because coherent imbalance and
difference-mode leakage must also be included, but it is a useful hard budget:
there is not much insertion-loss margin available per level.

---

## 4. Current geometry seed

The legacy geometry in the old JSON/profile script has been removed.  The
current analytic seed is

[
w = 4.572 {m mm},
]

[
(g_1,L_1) = (7.672, 9.872) {m mm},
]

[
(g_2,L_2) = (4.984, 8.857) {m mm}.
]

At the electrical center

[
f_0 = 10.19465 {m GHz},
]

the Cohn reduced model gives approximately

[
Z_1 = 289.55 Omega,
qquad
Z_2 = 209.39 Omega.
]

The dominant guided wavelengths are approximately

[
lambda_{g1}=36.27 {m mm},
qquad
lambda_{g2}=34.01 {m mm}.
]

Therefore

[
lambda_{g1}/4 approx 9.07 {m mm},
qquad
lambda_{g2}/4 approx 8.50 {m mm}.
]

These values are useful as first phase-spacing scales for residual tuning
elements, not as universal quarter-wave transformer lengths.

---

## 5. Why geometry-space smoothstep is not enough

The old script directly interpolated ridge width and gap with a smoothstep.
That produces a visually smooth solid, but it does not imply a smooth
electromagnetic transformation because

[
Z = Z(w,g,f)
]

is nonlinear.

A first-order slowly varying line model gives

[
Gamma(f)
approx
rac12
int_0^L
rac{dln Z(z,f)}{dz}
expleft[
-2jint_0^zeta(z',f),dz'
ight]
dz.
]

The quantity to shape is therefore the impedance trajectory, not merely the
geometry trajectory.

The new profile seed constructs a smooth path in log impedance,

[
ln Z_{m target}(z)
=
(1-s)ln Z_A + sln Z_B,
]

with

[
s(t)=3t^2-2t^3,
]

and then inverts the Cohn reduced model for the required gap.

For the first segment, the ridge width grows from zero to 4.572 mm while the
gap is solved to satisfy the target impedance.  For the second segment, ridge
width is fixed and only the gap is inverted.

This is still only a center-frequency initializer; the eventual objective is a
bandwise HFSS-calibrated impedance/mode trajectory.

---

## 6. Gap sensitivity and tolerance implication

At (f_0), numerical differentiation of the present Cohn model gives

[
left.rac{partialln Z}{partial g}ight|_1
approx 0.0895 {m mm}^{-1},
]

[
left.rac{partialln Z}{partial g}ight|_2
approx 0.1571 {m mm}^{-1}.
]

Thus the second section is about 1.75 times more impedance-sensitive to the
same absolute gap error.

A local (pm0.05) mm gap perturbation corresponds, before full-wave
re-optimization, to characteristic-impedance perturbations of order

[
0.45% quad	ext{(section 1)},
]

and

[
0.79% quad	ext{(section 2)}.
]

This supports putting tighter tolerance/filleting attention on the smaller-gap
second section.

---

## 7. Multi-bolt tuning as a phasor problem

For weak residual discontinuities, the reflected wave can be linearized as

[
Gamma_{m total}(f)
approx
Gamma_0(f)
+
sum_i
gamma_i(f)e^{-2jeta(f)z_i}.
]

Each tuning bolt therefore provides at least two useful controls:

- penetration/depth, mainly changing (gamma_i);
- axial position, changing the reflection phase.

Because reflection acquires a round-trip phase, two weak tuning elements
separated by about (lambda_g/4) acquire approximately 180 degrees relative
reflection phase near the design frequency.  Hence the current first spacing
seed is roughly 8.5--9.1 mm depending on the local guide section.

Bolts should be introduced only after the passive tee+taper geometry is already
broadband.  Their role is cancellation of residual susceptance/ripple, not
creation of the full 24.4% bandwidth.

---

## 8. Evanescent-mode coupling sets a compactness limit

The first higher rectangular WR90 mode is TE20 with

[
f_{c,20}approx13.114 {m GHz}.
]

At the upper operating edge 11.5 GHz it is below cutoff but not infinitely
short-ranged.  Its evanescent decay constant is approximately

[
alpha_{20}approx132.1 {m m}^{-1},
]

so

[
1/alpha_{20}approx7.57 {m mm}.
]

An amplitude reduction of 20 dB requires approximately

[
L_{20{m dB}}
=
rac{ln 10}{alpha_{20}}
approx17.43 {m mm}.
]

This is comparable with the complete 18.729 mm analytic ridge-transition
length.  Therefore a compact tee placed very close to the taper cannot always
be represented accurately as

[
S_{m tee}^{TE10}	imes S_{m taper}^{TE10}.
]

The production model should include a **tee + nearest taper** joint 3-D HFSS
block after the isolated components have been understood.

---

## 9. Peak-field normalization

For straight WR90 TE10,

[
P =
rac{ab}{4Z_{TE}}E_{max}^2.
]

At 30 kW, the straight-guide peak electric-field scale is approximately

- 0.533 MV/m at 9 GHz,
- 0.504 MV/m near 10.195 GHz,
- 0.487 MV/m at 11.5 GHz.

A more reusable HFSS output than a single field-enhancement ratio is

[
k_E(f)
=
rac{E_{max}(f)}
{sqrt{P_{m accepted}(f)}}.
]

After a normalized-power simulation,

[
E_{max}(P)=k_Esqrt P.
]

This lets the same model be rescaled to 30 kW or another requested peak power.
The existing (K_E<3) target remains a useful screening metric, but the
absolute (k_E) curve should also be exported.

---

## 10. Updated HFSS sequence

The preferred sequence is now:

1. uniform ridge-1 eigenmode/wave-port extraction;
2. uniform ridge-2 eigenmode/wave-port extraction;
3. impedance-space taper alone;
4. single magic tee, extracted in Sigma/Delta basis;
5. de-embed equal reference planes and obtain complex modal data;
6. tee + nearest taper as one 3-D multimode block;
7. only then add one or more tuning bolts;
8. build the full four-way tree and transform its physical S matrix into the
   four-mode basis;
9. optimize broadband modal return, physical isolation, amplitude/phase
   balance and insertion loss together;
10. repeat with finite conductivity, peak-field and thermal-loss checks.

The current theory therefore changes the design question from

> what scalar impedance should the magic tee see?

to

> what broadband modal scattering operator must the tee+taper block realize,
> and what geometry gives that operator with acceptable field stress?
