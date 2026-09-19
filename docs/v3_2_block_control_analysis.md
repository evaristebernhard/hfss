# v3.2 block-control theory — topology selection before new HFSS geometry

## 1. Purpose

This note continues the v3.1 audit and does not introduce a new HFSS geometry.

The goal is to decide which matching mechanism should act on each parity block before any new builder is written.

The analysis uses the solved v2 parity-corrected S4P and the completed Stage-A sweep.

---

## 2. Lossless block parameterization and control leverage

Each parity block is approximately reciprocal and lossless:

[
S_q=
egin{pmatrix}
r_1&t\
t&r_2
end{pmatrix},
qquad
|r_1|^2+|t|^2approx1.
]

If a matching network presents a load reflection (Gamma_L) at the second port,

[
Gamma_{m in}
=
r_1+
rac{t^2Gamma_L}{1-r_2Gamma_L}.
]

At a matched load, (Gamma_L=0),

[
oxed{
left|
rac{partialGamma_{m in}}
{partialGamma_L}
ight|
=
|t|^2.
}
]

Thus (|t|^2) is the first-order control leverage available to a remote arm-side matcher.

For an exactly lossless reciprocal block, the load reflection required for perfect matching satisfies

[
oxed{
|Gamma_L^*|=|r_1|.
}
]

This provides a useful conditioning diagnostic:

[
oxed{
D(f)=rac{|r(f)|}{|t(f)|^2}.
}
]

Large (D) means that the block is poorly conditioned for remote matching: a large reflected wave must be generated through a weak transmission channel.

---

## 3. H block is poorly conditioned for remote matching

For the v2 baseline:

| f | (|t_H|^2) | (|r_+|) | required-load VSWR | target amplitude factor |
|---:|---:|---:|---:|---:|
| 9.0 GHz | 0.512 | 0.699 | 5.64 | 1.39 |
| 10.2 GHz | 0.373 | 0.792 | 8.61 | 1.63 |
| 11.5 GHz | 0.222 | 0.882 | 15.92 | 2.11 |

For the best Stage-A case (g_2=5.8) mm, (L_t=7.5) mm:

| f | (|t_H|^2) | (|r_+|) | required-load VSWR | target amplitude factor |
|---:|---:|---:|---:|---:|
| 9.0 GHz | 0.616 | 0.620 | 4.26 | 1.27 |
| 10.2 GHz | 0.452 | 0.740 | 6.70 | 1.48 |
| 11.5 GHz | 0.253 | 0.864 | 13.75 | 1.98 |

The high-frequency problem remains severe.

At 11.5 GHz the best Stage-A geometry transmits only about 25.3% of the even-mode power into the H arm. To satisfy a 22 dB return-loss target in a lossless block requires

[
|t|>sqrt{1-10^{-22/10}}
approx0.99684.
]

So the Stage-A H transmission amplitude still needs to increase by almost a factor of two at 11.5 GHz.

### Consequence

A remote H-arm matching network is not the preferred primary correction.

The new H structure should act at the junction and change the direct coupling (t_H(f)), especially its high-frequency slope.

---

## 4. Direct test of remote H matching

Several idealized arm-side networks were attached to the solved H block without changing the junction.

The following are minimax reduced-model results, not HFSS results:

- one ideal shunt iris: about 1.42 dB worst RL;
- two ideal shunt irises: about 1.56 dB;
- generic series + shunt reactive pair: about 1.64 dB;
- three-section ideal transmission-line transformer: about 1.68 dB.

The exact values depend on the simplified element model, but the common conclusion is robust:

[
oxed{
	ext{remote H matching does not span the missing control direction.}
}
]

This agrees with the Stage-A Jacobian, where increasing (g_2) helps low frequency much more strongly than high frequency.

---

## 5. H topology decision

The primary H topology should therefore be junction-local.

The first candidate family is:

[
oxed{
	ext{H-junction multi-reactive matching cell}
}
]

with at least two physically distinct effects:

1. a junction-local element that increases direct even-mode coupling and has useful high-frequency leverage;
2. a second reactive/phase degree of freedom that flattens the residual band-edge reflection.

Candidate geometries include:

- a broad symmetric H-plane junction step;
- a symmetric junction iris/window;
- a broad rounded matching boss;
- a junction element followed by a cancelling iris in a dedicated short throat.

A single remote iris should not be treated as the primary H solution.

Published X-band H-plane T-junction examples also use multiple local matching features when wider bandwidth is required.

---

## 6. E block is much better conditioned

For the v2 E/odd block:

| f | (|t_E|^2) | (|r_-|) | required-load VSWR | target amplitude factor |
|---:|---:|---:|---:|---:|
| 9.0 GHz | 0.878 | 0.350 | 2.08 | 1.06 |
| 10.2 GHz | 0.810 | 0.436 | 2.55 | 1.11 |
| 11.5 GHz | 0.708 | 0.541 | 3.35 | 1.18 |

The E block is therefore qualitatively different.

Its direct transmission is already strong. The main task is to synthesize the correct phase-dependent load reflection, not to repair a severe coupling deficit.

This makes an E-arm matching network near the junction physically reasonable.

---

## 7. Correct E-side synthesis target

After de-embedding the collinear and E-arm reference-plane phases, the perfect-match termination is

[
Gamma_{L,E}^{*}
=
-rac{S_{--}}
{S_{-E}S_{E-}-S_{--}S_{EE}}.
]

Representative equivalent normalized impedances are

[
z_E^*(9,{m GHz})
approx
1.795+j0.607,
]

[
z_E^*(10.2,{m GHz})
approx
1.766+j1.035,
]

[
z_E^*(11.5,{m GHz})
approx
1.269+j1.422.
]

The old low-impedance two-ridge seed is therefore withdrawn.

---

## 8. Exact pointwise E L-section decomposition

At each frequency, the required (z_E^*) can be realized by an ideal L-section.

For the topology

[
	ext{input shunt susceptance }b
quadightarrowquad
	ext{series reactance }x
quadightarrowquad
Z_0,
]

one solution branch is approximately:

| f | (x) | (b) |
|---:|---:|---:|
| 9.0 GHz | +1.000 | +0.331 |
| 10.2 GHz | +1.172 | +0.247 |
| 11.5 GHz | +1.365 | +0.085 |

The alternative branch is:

| f | (x) | (b) |
|---:|---:|---:|
| 9.0 GHz | -1.000 | -0.669 |
| 10.2 GHz | -1.172 | -0.741 |
| 11.5 GHz | -1.365 | -0.868 |

These are exact pointwise circuit decompositions of the target load, not yet realizable geometry.

The positive-(x) branch has a notable property: when converted using the WR90 TE10 wave impedance, the required series inductance is roughly 9 nH over most of the band.

However the associated shunt term is strongly dispersive. A single fixed simple iris does not reproduce the complete trajectory.

---

## 9. Low-order E topology tests

Several simplified physically motivated models were tested against the full de-embedded E two-port.

Reduced-model minimax results were approximately:

- one shunt iris at the external E port: 6.1 dB;
- two external shunt irises: 6.8 dB;
- one internal reactive iris + one moderate high-impedance throat: 13.9 dB;
- two simple shunt irises around one moderate throat: 12.9 dB;
- unconstrained ideal two-line network at the junction plane: about 21.5 dB.

The last result requires an unrealistically high near-junction characteristic impedance if interpreted as an ordinary propagating waveguide section.

Therefore the large near-junction impedance should be interpreted as an **evanescent/reactive discontinuity**, not as a uniform propagating line.

### Consequence

The E topology should contain at least:

1. a strong local reactive window/iris/step near the junction;
2. a second independent phase/impedance-shaping feature.

A simple monotonic double-ridge transformer is not the correct topology.

---

## 10. Revised E topology family

The preferred design family is now

[
oxed{
	ext{junction}
ightarrow
	ext{reactive E-arm window/iris}
ightarrow
	ext{short shaping section}
ightarrow
	ext{second reactive/step feature}
ightarrow
WR90.
}
]

Candidate implementations include:

- inductive window + E-plane step;
- capacitive window + inductive step;
- bridge iris + short narrowed section;
- two-window resonant matching cell;
- short stepped septum/window structure.

The exact physical mapping should be selected using mode matching / full-wave sensitivity rather than by assigning one ideal lumped element to one metal feature.

Waveguide discontinuities are inherently multimode; standard equivalent circuits are useful for topology selection but not sufficient for final dimensions.

---

## 11. H versus E: final topology split from this theory pass

### H / even block

Primary task:

[
oxed{
	ext{increase direct junction coupling, especially at high frequency.}
}
]

Therefore modify the junction itself.

Recommended hierarchy:

[
	ext{junction step/window}
ightarrow
	ext{secondary cancelling element}
ightarrow
	ext{existing ridge taper}.
]

### E / odd block

Primary task:

[
oxed{
	ext{synthesize a moderate but strongly phase-shaped load reflection.}
}
]

Therefore keep the parity-correct E orientation and add a local multi-reactive matching cell in the E arm.

---

## 12. High-power implication

The high-power constraint reinforces this split.

A remote H matcher would need a large reflection magnitude at the H arm, reaching roughly 0.86--0.88 near 11.5 GHz. This corresponds to a standing-wave VSWR above 13 and pushes the design toward strong resonant energy storage.

That is undesirable for a 30 kW peak-power component.

By contrast the E required load reflection is moderate, with VSWR roughly 2--3.4.

High-power literature on X-band hybrids emphasizes avoiding small apertures and strong field-enhancing bends or probe tips. High-power magic-T work has also shown that matching probes can become the field-limiting feature.

Therefore the future H junction cell should use broad, rounded metal geometry where possible, and any E matching window must be checked by field-enhancement ratio rather than S parameters alone.

---

## 13. Design status after v3.2 theory

No new dimensional seed is authorized yet.

The theory now supports the following topology decision:

[
oxed{
H:
	ext{junction-local multi-reactive correction}
}
]

[
oxed{
E:
	ext{local multi-reactive arm matching cell}
}
]

The next mathematical task is to construct reduced-order generalized scattering matrices for:

- an H-junction step/window perturbation;
- an E-arm two-discontinuity matching cell;

and fit their sensitivity directions to the required modal trajectories before new HFSS geometry is written.
