# v3.1 theory audit — corrections before the next HFSS geometry

## Executive result

Do **not** implement the previously merged v3 geometry unchanged.

Two structural issues were found in the second theory pass:

1. the E-arm two-section ridge synthesis used the wrong scalar load;
2. the proposed H iris occupies the existing H taper region, so the document's "separate matching cell" interpretation is not geometrically true.

The v2 parity correction remains valid. The Stage-A conclusion also remains valid: the old `g2/Lt` variables are insufficient. What changes is the next matching-network synthesis.

---

## 1. What remains valid

The natural modal basis is

[
c_+=(P_1+P_2)/sqrt2,qquad
c_-=(P_1-P_2)/sqrt2.
]

The corrected tee remains approximately block diagonal,

[
(c_+,H)oplus(c_-,E),
]

with forbidden parity terms typically around -50 to -70 dB in Stage-A.

The design should continue to preserve the X-mirror symmetry.

The completed Stage-A sweep also remains useful. In particular:

- increasing `g2` and `Lt` improves the H/even block only modestly;
- the E/odd block is almost insensitive to those H-side parameters;
- a new H matching mechanism and an independent E matching mechanism are required.

---

## 2. E-side correction: the old scalar-load synthesis was wrong

The previous v3 document formed

[
z_{m naive}=rac{1+r_-}{1-r_-}
]

from the odd-mode input reflection and treated this as an E-side load to be matched by a transformer.

That interpretation is incorrect.

The odd block is a reciprocal two-port,

[
S_E=
egin{pmatrix}
S_{--}&S_{-E}\
S_{E-}&S_{EE}
end{pmatrix}.
]

With the E port originally matched,

[
r_-=S_{--}.
]

The quantity

[
rac{1+r_-}{1-r_-}
]

is the driving-point impedance seen at the c- input **with the E port already matched**. It is not the termination that an E-arm matching network must synthesize at the E junction plane.

### 2.1 Correct matching condition

Let (Gamma_L) be the reflection presented by an E-arm matching network at the E-side junction plane.

Then

[
Gamma_{m in}
=
S_{--}
+
rac{S_{-E}S_{E-}Gamma_L}
{1-S_{EE}Gamma_L}.
]

Perfect matching requires

[
Gamma_{m in}=0,
]

hence

[
oxed{
Gamma_{L,E}^{*}
=
-rac{S_{--}}
{S_{-E}S_{E-}-S_{--}S_{EE}}.
}
]

This equation, after reference-plane de-embedding of both the c- and E ports, is the correct reduced-order E-side synthesis target.

### 2.2 Required E-side load trajectory from the v2 baseline

After de-embedding:

| f | (|Gamma_{L,E}^{*}|) | phase | equivalent normalized (z_L^*) |
|---:|---:|---:|---:|
| 9.0 GHz | 0.350 | +25.1 deg | 1.795 + j0.607 |
| 10.2 GHz | 0.436 | +33.0 deg | 1.766 + j1.035 |
| 11.5 GHz | 0.541 | +47.2 deg | 1.269 + j1.422 |

This is qualitatively different from the old naive trajectory, which was approximately

[
0.48+j0.02
ightarrow
0.30+j0.03.
]

The correct E-side requirement is **high-impedance and strongly inductive/reactive**, not a simple low-impedance transformer load.

### 2.3 Consequence for the old E double-ridge seed

The old v3 seed corresponded approximately to two low-impedance sections,

[
Z/Z_0sim0.50, 0.75.
]

When those values are placed into the correct full two-port loading equation, the reduced model predicts a band-worst RL of only about

[
oxed{2.1 {m dB}},
]

worse than the original v2 odd-block result of about 5.34 dB.

Therefore the old E seed

- (w_E=6.858) mm,
- (g_{E2}=4.299) mm,
- (L_{E2}=9.228) mm,
- (g_{E1}=6.544) mm,
- (L_{E1}=10.392) mm,

must **not** be used as the default v3 geometry.

### 2.4 Network-order diagnostic

A corrected idealized two-section lossless-line optimization, using the complete de-embedded odd two-port, can approach the target with a very different impedance character. One reduced-model candidate is roughly

[
Z_{m near}/Z_0sim4.8,qquad L_{m near}sim2.0 {m mm},
]

[
Z_{m outer}/Z_0sim1.39,qquad L_{m outer}sim13.3 {m mm},
]

with band-worst RL around 21.5 dB.

These are **not geometry dimensions**. They are an order/topology diagnostic only.

The result means that the E side likely needs a high-impedance/reactive element near the junction plus at least one additional phase/impedance section. A simple monotonic low-impedance double-ridge transformer is not the correct first topology.

Candidate physical families include:

- inductive/capacitive windows or irises plus a spacing section;
- stepped septum/window structures;
- a short reactive throat plus a transformer section;
- a three-element matching network.

The next E design should be synthesized from (Gamma_{L,E}^{*}(f)), not from (r_-(f)) alone.

---

## 3. H-side correction: the proposed iris is not a separate cell

For the Stage-A-informed H geometry:

[
L_t=7.5 {m mm}.
]

Therefore, measured from the H-arm mouth:

- terminal ridge occupies (0le sle7.5) mm;
- the longitudinal taper starts at (s=7.5) mm and extends for (L_1+L_2=18.729) mm.

The previously proposed iris seed was

[
d_i=8.5 {m mm},
qquad
t_i=3.0 {m mm}.
]

So the iris occupies

[
oxed{8.5le sle11.5 {m mm}},
]

which lies inside the existing ridge-taper region.

Thus the written topology

[
	ext{junction}	o	ext{iris}	o	ext{terminal ridge}	o	ext{taper}
]

was not the geometry actually specified.

The real geometry would be a combined sidewall-iris + double-ridge discontinuity. Standard empty-WR90 iris formulas and the simple aperture-cutoff argument are not directly applicable to that hybrid cross section.

---

## 4. What the Stage-A Jacobian actually says

Using finite differences from the completed Stage-A HFSS cases, the de-embedded H input-admittance sensitivity can be summarized using

[
x=rac{f-10.25}{1.25}.
]

For `g2`,

[
oxed{
rac{partial G_H}{partial g_2}
approx
0.03743
-0.02882x
-0.00471x^2
quad {m mm}^{-1}.
}
]

Representative values are approximately

- 9 GHz: +0.0579/mm,
- 10.2 GHz: +0.0387/mm,
- 11.5 GHz: +0.0073/mm.

So increasing `g2` helps the low-frequency end far more than the high-frequency end. It therefore does **not** supply the missing positive high-frequency correction.

For terminal length,

[
oxed{
rac{partial G_H}{partial L_t}
approx
0.00425
-0.00075x
+0.00074x^2
quad {m mm}^{-1},
}
]

which is nearly flat across the band.

Hence:

- `g2` mainly changes low-frequency coupling;
- `Lt` mainly changes overall level/phase;
- neither spans the missing broadband direction.

The next H parameter must provide a sensitivity with substantially more high-frequency leverage, or create a controlled cancellation/resonance that reshapes the response.

---

## 5. Revised H topology strategy

Do not designate the sidewall iris inside the taper as the canonical solution.

Instead evaluate one of two clean topology families.

### Family H-A: junction step/boss

Place a compact matching step directly at the H-plane T-junction.

This is consistent with published X-band H-plane T-junction designs that use a full-width step at the junction. Such structures use step height, thickness, and offset as matching variables.

This option is compact and avoids adding a long throat.

### Family H-B: cancelling inductive iris in a dedicated throat

Insert a short ordinary-guide throat between the junction region and the ridge transformer, then place a symmetric inductive iris in that throat.

The throat separates the iris from the double-ridge taper so that the iris has a clean electromagnetic interpretation.

A useful first phase scale is approximately

[
lambda_g/4approx9.5 {m mm}
]

near 10.25 GHz.

A published H-junction design improved the -20 dB bandwidth by placing a cancelling iris roughly a quarter guided wavelength from the primary discontinuity.

The throat/iris structure should be analyzed before the ridge taper is reattached.

---

## 6. The H driving-point admittance is descriptive, not a unique circuit decomposition

The de-embedded quantity

[
y_H=rac{1-Gamma_+}{1+Gamma_+}
]

is a valid driving-point admittance for a fixed reference plane and matched H-port termination.

However the decomposition

[
y_Hstackrel{?}{=}n_H^2+jb_H
]

is not unique.

Therefore statements such as "the physical coupling coefficient must increase by exactly 3x" are useful heuristics, but are not uniquely identifiable junction parameters.

Future synthesis must retain the full complex two-port

[
S_H(f)
]

or an equivalent ABCD/Y matrix, rather than fitting only (G_H(f)).

The (G_H/B_H) curves remain useful for sensitivity visualization.

---

## 7. Bandwidth-order implication

The required band is

[
9.0	ext{--}11.5 {m GHz},
]

which is approximately 24.4% fractional bandwidth around 10.25 GHz.

Published wideband X-band magic-T designs can exceed 20% bandwidth, so the requirement is physically plausible. However the wideband examples use several reactive degrees of freedom: stepped cones, multistep septa, posts, windows, or multiple irises.

Therefore the 22 dB requirement over 24.4% should be treated as a **multi-resonant/multi-element matching problem**, not as a one-iris fine tune.

---

## 8. High-power checkpoint

For 30 kW TE10 power in straight WR90, the dominant-mode peak electric field is approximately

[
0.49	ext{--}0.53 {m MV/m}
]

over 9--11.5 GHz.

Any proposed ridge/iris/window geometry must therefore report the field-enhancement ratio

[
K_E=
E_{max,m local}/E_{max,m straight}.
]

Peak-power qualification cannot be inferred from S parameters alone.

The 1 kW continuous-average requirement also needs finite conductivity and thermal analysis; the current PEC model cannot certify it.

---

## 9. Correct next sequence

Before writing `build_single_magictee_v3.py`:

1. preserve the solved v2 parity geometry;
2. form the complete de-embedded (2	imes2) H and E parity blocks;
3. synthesize the E matching network from (Gamma_{L,E}^{*}(f));
4. choose and analytically parameterize H-A or H-B;
5. verify that the proposed H variables span a missing Jacobian direction;
6. only then write the v3 HFSS builder;
7. run one structural full-wave case before any sweep.

This sequence replaces the previous direct implementation of the v3 seed.
