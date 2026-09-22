# v4 mathematical and physical synthesis

## 1. Purpose

This note turns the R11 full-wave data into explicit design equations for v4.
The goal is to stop treating HFSS as a blind optimizer.

The main result is that R11 does not show four equally difficult matching
problems. It shows one important missing physical control direction.

## 2. Mixed-mode decomposition

For collinear input waves a1 and a2 define

```text
a+ = (a1 + a2)/sqrt(2)
a- = (a1 - a2)/sqrt(2)
```

A symmetric Magic-T separates into two parity blocks:

```text
c+ <-> H/sum
c- <-> E/difference
```

The measured forbidden parity leakage in R11 is about -48.7 dB, so the present
dominant design problem is matching, not symmetry isolation.

For an approximately lossless reciprocal H/even two-port,

```text
|Gamma_H| = |cos(theta_H)|
|t_H|     = |sin(theta_H)|
```

The 22 dB return-loss target requires

```text
|Gamma| <= 0.07943
|t| >= 0.99684
theta >= 85.44 deg
```

R11 remains far from this target, but its Jacobian identifies why.

## 3. R11 weak-direction diagnosis

The R11 center feature is

```text
F = [0.4656, 0.4488, 0.6864, -0.8864]
```

for

```text
[Re Gamma0, Im Gamma0, Re Gamma1, Im Gamma1].
```

The step-normalized singular values are

```text
[0.1646, 0.07230, 0.002146, 0.000390].
```

The old coordinate system is therefore practically rank deficient.

Projection of the present error onto the weakest output direction leaves
approximately 0.260 unresolved error. The new junction-local element is useful
only if it can directly control this direction.

For the new post half-step sensitivity columns c_h and c_y define

```text
g_h = |u4^T c_h|
g_y = |u4^T c_y|
```

where u4 is the weakest R11 left singular vector.

If each post coordinate may move by two identification half-steps, the maximum
first-order weak-direction correction is approximately

```text
C4 = 2 (g_h + g_y).
```

The first gate is therefore

```text
g_h + g_y >= 0.130
```

which gives

```text
C4 >= 0.260.
```

This direct controllability condition is more meaningful than merely asking
whether sigma_min rises by a factor of five.

## 4. Junction-local post model

A short local symmetric discontinuity may be approximated near the design
frequency by a normalized shunt susceptance

```text
y = j b.
```

Its local reflection is

```text
Gamma_b = -j b / (2 + j b).
```

For weak loading,

```text
Gamma_b ~= -j b/2.
```

When placed a distance l from a reference plane,

```text
Gamma_ref ~= Gamma_b exp(-2 j beta l).
```

This gives two physically distinct controls:

- post height -> mainly reflection magnitude / susceptance strength;
- post longitudinal position -> mainly reflection phase.

The R11 unresolved center reflection is of order 0.25 in magnitude, so the
required local loading is moderate rather than an extreme resonator. The first
v4 post seed is therefore intentionally close to the junction:

```text
radius = 1.5 mm
height = 0.70 mm
axis position = 1.50 mm from the H-junction mouth
```

with half-steps

```text
height +/- 0.20 mm
position +/- 0.50 mm.
```

## 5. Ridge transformer synthesis

The current physical taper length is already roughly one-half guided wavelength
near band center, so the main missing step is not simply making it longer.

For a slowly varying impedance transformer, the small-reflection approximation
has the form

```text
Gamma(f) ~= 1/2 integral [d ln Z(z) / dz] exp(-2j integral beta dz) dz.
```

Therefore the ridge profile should eventually be generated from a target
impedance trajectory rather than by a large Cartesian geometry sweep.

Recommended workflow:

1. run a small 2D/eigenmode table for ridge gap and width;
2. extract effective Z(g,w,f) and beta(g,w,f);
3. choose a smooth broadband target impedance profile;
4. invert Z(g,w) to obtain the physical ridge profile;
5. verify the resulting full 3D transformer.

The present smoothstep/log-gap taper is retained only as the initial geometry
until this impedance map exists.

## 6. Three-screw wideband residual basis

For shallow screws,

```text
Gamma_screw(f) ~= sum_i c_i(f) p_i
```

with

```text
c_i(f) proportional to exp(-2 j beta(f) z_i).
```

The original positions

```text
[0, 8.4, 17.6] mm
```

were motivated by near-quarter-wave single-frequency cancellation. They are
not the best basis for broadband three-parameter fitting.

Using nine equally spaced frequencies over 9--11.5 GHz, form the complex basis

```text
A_ki = exp(-2 j beta(f_k) z_i)
```

and stack its real and imaginary parts, normalizing each column.

For the old positions:

```text
singular values ~= [1.6179, 0.6029, 0.1382]
condition number ~= 11.70
sigma_min/sigma_max ~= 0.08545
```

For

```text
[0, 5.0, 19.5] mm
```

the same calculation gives

```text
singular values ~= [1.2883, 1.0053, 0.5741]
condition number ~= 2.244
sigma_min/sigma_max ~= 0.4456.
```

The new positions therefore provide a much better-conditioned broadband basis.

Once passive return loss reaches approximately 18--20 dB, identify each screw
column with one small HFSS penetration perturbation and solve

```text
min sum_k |Gamma_passive(f_k) + sum_i c_i(f_k) p_i|^2
```

subject to

```text
0 <= p_i <= 1.5 mm
```

for the preferred high-power range.

## 7. Four-way tree equations

For ideal first-stage Magic-T cells,

```text
sA = (a1 + a2)/sqrt(2)
sB = (a3 + a4)/sqrt(2)
```

and the final output is

```text
bout = [sA exp(-j beta LA) + sB exp(-j beta LB)] / sqrt(2).
```

With equal interstage electrical paths,

```text
bout = (a1 + a2 + a3 + a4)/2.
```

For equal-amplitude inputs with phase errors phi_i,

```text
eta_phase = |sum_i exp(j phi_i)|^2 / 16.
```

Thus small phase errors are not the dominant 95% efficiency risk. The harder
system budget is dissipative loss plus mismatch.

The 95% target permits only

```text
IL_total <= -10 log10(0.95) = 0.223 dB.
```

A two-stage path has only roughly 0.11 dB per stage if the budget is shared
equally.

## 8. High-power implication

At 30 kW, straight WR90 TE10 field scale is about 0.5 MV/m over this band.
Therefore the design variable of interest is the local field enhancement

```text
K_E = Emax_local / Emax_WR90.
```

The rounded post pair and shallow, blunt tuning screws are intentionally chosen
to avoid unnecessary local enhancement. Final power qualification still needs
finite-conductivity, rounded geometry, field extraction, and thermal analysis.

## 9. Next decision sequence

1. run exactly five v4 passive post cases;
2. evaluate direct u4 controllability using g_h + g_y;
3. if the direct gate passes, re-identify a complete v4 passive Jacobian;
4. use regularized/trust-region updates to reach 10, 15, then 18--20 dB;
5. identify the three screw penetration columns at [0, 5.0, 19.5] mm;
6. solve screw penetrations by constrained complex least squares;
7. close the three-Magic-T tree with S-parameter network analysis;
8. confirm one full 3D four-way model;
9. switch to finite conductivity and power/thermal validation.

This is the frozen mathematical workflow for v4.
