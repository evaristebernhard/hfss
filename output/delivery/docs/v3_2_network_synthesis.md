# v3.2 network synthesis — topology targets before new HFSS geometry

## 1. Purpose

This note continues the v3.1 theory audit using the solved v2 parity baseline and Stage-A HFSS data.

The goal is no longer to guess geometry directly.  Instead, each parity block is reduced to a small set of **effective matching targets** that a future geometry must reproduce.

No new HFSS solve is included here.

---

## 2. Lossless parity-block identity and the high-power penalty of remote cancellation

For either parity block, use the reciprocal lossless representation

[
S_q
=
e^{jchi}
egin{pmatrix}
e^{jdelta}cos	heta & jsin	heta\
jsin	heta & e^{-jdelta}cos	heta
end{pmatrix}.
]

Then

[
|r|=|cos	heta|,
qquad
|t|=|sin	heta|.
]

If a lossless branch matching network presents a reflection (Gamma_L) to force the input reflection to zero,

[
Gamma_{m in}
=
S_{11}
+
rac{S_{12}S_{21}Gamma_L}
{1-S_{22}Gamma_L}=0,
]

the required termination magnitude satisfies

[
oxed{|Gamma_L^*|=|r|}.
]

At exact cancellation, the wave incident on the branch matching network is amplified by

[
oxed{|b_2|=rac1{|t|}},
]

so the corresponding travelling-wave power scale is

[
oxed{P_{m circ}/P_{m in}=rac1{|t|^2}}.
]

This is a key high-power discriminator.

### 2.1 Numerical consequence

At 30 kW input:

| case | f | (|t|) | (1/|t|^2) | equivalent travelling-wave scale |
|---|---:|---:|---:|---:|
| H v2 baseline | 9.0 | 0.715 | 1.95 | 58.6 kW |
| H v2 baseline | 10.2 | 0.611 | 2.68 | 80.4 kW |
| H v2 baseline | 11.5 | 0.472 | 4.50 | 134.9 kW |
| H Stage-A best | 9.0 | 0.785 | 1.62 | 48.7 kW |
| H Stage-A best | 10.2 | 0.672 | 2.21 | 66.4 kW |
| H Stage-A best | 11.5 | 0.503 | 3.95 | 118.6 kW |
| E v2 baseline | 9.0 | 0.937 | 1.14 | 34.2 kW |
| E v2 baseline | 10.2 | 0.900 | 1.23 | 37.0 kW |
| E v2 baseline | 11.5 | 0.841 | 1.41 | 42.4 kW |

Therefore:

[
oxed{	ext{H must be improved primarily at the junction itself.}}
]

Using a highly reflective remote network to cancel the present H mismatch is undesirable for the 30 kW peak-power requirement.

By contrast, E remains compatible with an arm-side matching network.

---

## 3. H block: use coupling angle as the invariant design variable

The 22 dB reflection target corresponds to

[
|r|<0.07943
quadLongleftrightarrowquad
	heta>85.444^circ.
]

For the Stage-A best case ((g_2=5.8 {m mm},L_t=7.5 {m mm})),

| f | (|t_H|) | (	heta_H=arcsin|t_H|) | extra angle to 22 dB |
|---:|---:|---:|---:|
| 9.0 GHz | 0.785 | 51.69 deg | 33.75 deg |
| 10.2 GHz | 0.672 | 42.24 deg | 43.21 deg |
| 11.5 GHz | 0.503 | 30.19 deg | 55.26 deg |

Using

[
x=rac{f-10.25}{1.25},
]

these three points are already well represented by

[
oxed{
Delta	heta_H(x)
approx
44.21^circ+10.76^circ x
}
]

with residual below about (0.6^circ) at the sampled frequencies.

Thus the dominant missing H physics has two coupling components:

1. coupling **level**;
2. positive coupling **slope versus frequency**.

A third variable is still needed for phase/reactive alignment.

This gives the minimum useful H design-coordinate count:

[
oxed{
p_H
sim
(p_{m level},p_{m slope},p_{m phase}).
}
]

---

## 4. H topology direction: junction-local high-pass coupling throat

The Stage-A best H transmission falls from

[
0.785ightarrow0.503
]

between 9 and 11.5 GHz.

Suppose a new junction-local coupling feature supplies a multiplicative correction with the frequency dependence of a near-cutoff TE10 propagation factor,

[
q(f)
=
sqrt{1-left(rac{f_c}{f}ight)^2}.
]

To flatten only the **relative** Stage-A coupling slope, require

[
rac{q(11.5)}{q(9.0)}
approx
rac{0.785}{0.503}
approx1.5605.
]

Solving gives

[
oxed{
f_capprox7.99 {m GHz}.
}
]

The corresponding rectangular broad dimension is

[
a_H=rac{c}{2f_c}
approx
oxed{18.77 {m mm}}.
]

This is not a final dimension. It is a physics-based seed for a junction-local high-pass coupling throat/aperture.

### 4.1 High-power scale

For a uniform (a_Happrox18.77) mm throat, the ideal straight-guide peak-field ratio relative to WR90 at equal power is approximately

- 1.35 at 9 GHz;
- 1.22 at 10.2 GHz;
- 1.18 at 11.5 GHz.

That increase is significant but not automatically prohibitive. It is much more favorable than the 3.7--4.0 wave-amplitude factor produced by remote H cancellation at the high-frequency edge.

---

## 5. Recommended H architecture

The next H topology should be treated as a **two-stage match**.

### Stage H1: repair junction coupling

Use a clean junction-local structure with three effective controls:

- a high-pass coupling throat/aperture with broad-dimension scale near (18.8) mm to control frequency slope;
- a broad symmetric step/boss/aperture-depth variable to control coupling level;
- a short throat/offset length to control phase.

A useful first throat length scale is several millimeters, not a remote quarter-wave section. For the (18.8) mm throat the guided wavelength near 10.2 GHz is roughly 47 mm, so 4--7 mm gives substantial phase control without creating a long resonator.

### Stage H2: residual broadband cancellation

Only after the junction itself reaches approximately

[
oxed{|t_H|_{min}gtrsim0.85}
]

and preferably

[
|t_H|_{min}gtrsim0.90
]

should a symmetric cancelling iris / paired tuning element be used to finish the 22 dB match.

This gate keeps the internal circulating-power factor close to the present E-block level.

---

## 6. E block: exact termination target

For the de-embedded odd two-port

[
S_E=
egin{pmatrix}
S_{--}&S_{-E}\
S_{E-}&S_{EE}
end{pmatrix},
]

the E-arm network must present

[
oxed{
Gamma_{L,E}^{*}
=
-rac{S_{--}}
{S_{-E}S_{E-}-S_{--}S_{EE}}.
}
]

The corresponding target impedance is smooth but complex. Representative values are

[
z_E^*(9,{m GHz})
approx1.795+j0.607,
]

[
z_E^*(10.2,{m GHz})
approx1.766+j1.035,
]

[
z_E^*(11.5,{m GHz})
approx1.269+j1.422.
]

The target is therefore not a low-impedance double-ridge transformer.

---

## 7. Pointwise L-section interpretation of the E target

Write the target admittance as

[
y_E^*=G+jB.
]

A useful L-section ordering is

[
	ext{junction}
ightarrow
	ext{shunt }jb
ightarrow
	ext{series }jx
ightarrow
	ext{matched port}.
]

For this topology

[
G=rac1{1+x^2},
]

so

[
x=sqrt{rac1G-1},
qquad
b=B+xG.
]

Taking the continuous positive branch gives approximately

| f | (x) | (b) |
|---:|---:|---:|
| 9.0 GHz | 1.000 | 0.331 |
| 10.2 GHz | 1.172 | 0.247 |
| 11.5 GHz | 1.365 | 0.085 |

The series term looks naturally inductive and grows with frequency.

The shunt term, however, decreases strongly with frequency. A fixed lumped C or L does not have the required broadband law.

Therefore a simple nondispersive L-section is not sufficient. The missing third degree of freedom must be **dispersive**.

---

## 8. Minimal effective E model that crosses 22 dB

A much simpler effective model is obtained by representing the E-arm network as

[
oxed{
z_{m eff}(f)
=
r_E(f)+jx_L(f).
}
]

Let

[
x=rac{f-10.25}{1.25}.
]

Use a linearly dispersive effective transformation ratio

[
oxed{
r_E(x)
=
1.5895-0.2204x
}
]

and a series-inductive normalized reactance

[
oxed{
x_L(f)
=
1.0629
left(rac{f}{10.2,{m GHz}}ight)
left(rac{Z_{m TE}(10.2)}{Z_{m TE}(f)}ight).
}
]

When this three-degree model is inserted into the **complete de-embedded E two-port**, the reduced-model band-worst return loss is approximately

[
oxed{23.84 {m dB}}.
]

This is the first reduced-order E model in the current analysis that crosses the 22 dB requirement while retaining a simple physical interpretation.

At 10.2 GHz the series-reactance scale is about

[
X_Lapprox1.063,Z_{m TE}approx522 Omega,
]

equivalent to roughly 8 nH only as a lumped scale reference. The real structure should remain all-waveguide.

---

## 9. What this says about E geometry

The three effective E controls are:

1. average impedance transformation;
2. **negative frequency slope** of that transformation;
3. series inductive reactance.

A fixed transformer ratio plus series inductance already gives about

[
19.5 {m dB}
]

band-worst RL.

Adding ordinary fixed shunt C/L does not improve the minimax result.

A one-section narrowed-width propagating throat plus series inductance gives only about

[
16.1 {m dB},
]

and two propagating throat sections give only about

[
17.8 {m dB}.
]

The problem is the extra propagation phase.

Therefore the preferred E topology is **not** a long multi-section transformer.

The geometry should instead provide a **localized, dispersive transformer action with little electrical length**, followed or accompanied by an inductive discontinuity.

Candidate families:

- short stepped window;
- multistep septum;
- compact symmetric window + short inductive post/shoulder;
- very short near-cutoff transformer cell whose phase is independently compensated.

The key is to reproduce the target effective law (r_E(f)), not any particular old ridge dimensions.

---

## 10. Design decision from v3.2

The topology split is now:

[
oxed{
H:
	ext{junction coupling redesign first}
ightarrow
	ext{residual symmetric cancellation later}
}
]

and

[
oxed{
E:
	ext{retain the parity-correct junction}
ightarrow
	ext{localized dispersive arm matcher}.
}
]

This is stronger than the previous statement that H and E merely need separate optimizers.

They require **different classes of matching physics**.

---

## 11. Next theory task before HFSS

Before creating the v3 builder:

1. parameterize an H junction throat/step with approximately (a_Hsim18.8) mm and independent level/phase controls;
2. parameterize one localized E transformer family with three controls corresponding to ((r_0,r_1,x_L));
3. derive first-order geometry-to-effective-parameter Jacobians;
4. reject any geometry family that cannot independently control the required directions;
5. then create one structural HFSS baseline for each block.

The v2 solved model remains the reference until those two topology parameterizations are complete.
