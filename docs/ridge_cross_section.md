# Double-ridge cross-section theory and first HFSS geometry seed

## 1. Purpose

This note replaces the earlier purely normalized two-section transformer with a more self-consistent **ridged-waveguide** reduced model.

The external problem remains:

- WR90-class ports
- 9–11.5 GHz
- return loss > 22 dB
- isolation > 22 dB
- coherent combining efficiency > 95%
- peak output power > 30 kW
- CW average power > 1 kW

The objective here is narrower: obtain a physically meaningful first geometry for the two broadband matching sections before the complete 3-D magic-tee model is optimized in HFSS.

The result is still conditional because the actual magic-tee junction is not rigorously a scalar (Z_L/Z_0=0.5) load. The value 0.5 is retained only as the same reduced-model load used in the previous analytic note.

---

## 2. Geometry and notation

For a symmetric double-ridge section:

- (a=22.86) mm: full broad-wall width
- (b=10.16) mm: full narrow-wall height
- (w): ridge width
- (g): clear gap between the two opposing ridges
- (h_r=(b-g)/2): height of each ridge from its wall

The proposed manufacturing simplification is to use the **same ridge width in both transformer sections** and change mainly the ridge gap.

This has three advantages:

1. simpler milling;
2. fewer dimensional degrees of freedom;
3. a cleaner HFSS tolerance study.

---

## 3. Closed-form dominant-mode cutoff model

For a symmetric double-ridge guide, a useful closed-form approximation for the dominant-mode cutoff wavelength is

[
lambda_{cr}
=
2(a-w)
left[
1+
rac{4}{pi}
left(
1+0.2sqrt{rac{b}{a-w}}
ight)
rac{b}{a-w}
lncscleft(rac{pi g}{2b}ight)
+
left(
2.45+0.2rac{w}{a}
ight)
rac{wb}{g(a-w)}
ight]^{1/2}.
]

Then

[
f_c=rac{c}{lambda_{cr}},
]

and the dominant propagation constant is approximated by

[
eta(f)
=
rac{2pi f}{c}
sqrt{1-left(rac{f_c}{f}ight)^2}.
]

The commonly quoted validity window for the cutoff approximation is approximately

[
0.01<rac{g}{b}le 1,
qquad
0<rac{b}{a}le 1,
qquad
0lerac{w}{a}le0.45.
]

All seeds proposed below lie inside this range.

Reference background:

- S. B. Cohn, *Properties of Ridge Wave Guide*, Proc. IRE, 1947.
- W. J. R. Hoefer and M. N. Burton, *Closed-form expressions for the parameters of finned and ridged waveguides*, IEEE Trans. MTT, 1982.
- A. Misra and V. S. Pandit, *Studies on the coupling transformer to improve the performance of microwave ion source*, Rev. Sci. Instrum. 85, 063301 (2014).

---

## 4. Cohn voltage-current impedance model

Define

[
K_1=rac{b}{lambda_{cr}},
]

and

[
K_2
=
rac{b}{g}
sinleft(
pirac{w}{b}K_1
ight)
+
left[
2K_1
lncscleft(rac{pi g}{2b}ight)
+
	anleft(
rac{pi}{2}K_1rac{a-w}{b}
ight)
ight]
cosleft(
pirac{w}{b}K_1
ight).
]

The high-frequency voltage-current characteristic impedance is then approximated by

[
Z_{infty}
=
120pi^2rac{K_1}{K_2}.
]

At finite frequency,

[
Z(f)
=
rac{Z_{infty}}
{sqrt{1-(f_c/f)^2}}.
]

This is one specific non-TEM impedance definition. It must not be mixed with another HFSS impedance normalization without explicit renormalization/de-embedding.

For consistency, the reference rectangular WR90 impedance used in the reduced model is obtained from the **same Cohn definition** by taking the no-ridge limit:

[
wightarrow0,
qquad
gightarrow b.
]

At approximately 10.2 GHz this reference is about

[
Z_{mathrm{ref}}approx343 Omega
]

in this voltage-current normalization.

This number is not the familiar TE wave impedance (Z_{TE}); the two definitions serve different purposes.

---

## 5. Transverse-resonance check of modal separation

The closed-form cutoff expression is supplemented by a transverse-resonance model.

With

[
rac{B_c}{Y_{01}}
approx
rac{2b}{lambda_c}
lncscleft(rac{pi g}{2b}ight),
]

the odd quasi-TE mode equation can be written approximately as

[
cotleft(
rac{pi(a-w)}{lambda_c}
ight)
-
rac{b}{g}
	anleft(
rac{pi w}{lambda_c}
ight)
-
rac{B_c}{Y_{01}}
=0,
]

while the even quasi-TE mode is estimated from

[
cotleft(
rac{pi(a-w)}{lambda_c}
ight)
+
rac{b}{g}
cotleft(
rac{pi w}{lambda_c}
ight)
-
rac{B_c}{Y_{01}}
=0.
]

The first odd root estimates the dominant TE10-like cutoff and the first even root estimates the TE20-like cutoff.

This model reproduces the rectangular-guide limits well:

[
f_{10}ightarrow6.557 {m GHz},
qquad
f_{20}ightarrow13.114 {m GHz}
]

as the ridge vanishes.

The TRM values below are therefore useful for a first mode-separation check before HFSS eigenmode extraction.

---

## 6. Critical correction to the previous 9.601 mm seed

The previous normalized two-section transformer used the propagation constant of **plain WR90**. That gave a dispersion-symmetric length of about

[
L=9.601 {m mm}.
]

Once a real ridge is introduced, however,

[
f_c^{m ridge}<f_c^{m WR90},
]

so

[
eta_{m ridge}(f)
eeta_{m WR90}(f).
]

Therefore a mapped ridge section cannot simply inherit the 9.601 mm length.

This matters at the millimeter scale. For the final seed below, the two optimized physical lengths become approximately

[
9.872 {m mm}
quad	ext{and}quad
8.857 {m mm},
]

respectively.

The ridge geometry and the section electrical length must therefore be optimized **together**.

---

## 7. Self-consistent conditional transformer model

The improved reduced model uses, frequency by frequency:

1. Cohn (Z_{m ref}(f)) for plain WR90 in the same voltage-current normalization;
2. a conditional load

[
Z_L(f)=0.5Z_{m ref}(f);
]

3. Cohn (Z_1(f),Z_2(f)) for the two ridged sections;
4. each section's own (eta_1(f),eta_2(f));
5. exact lossless transmission-line recursion

[
Z_{in,k}
=
Z_k
rac{
Z_{in,k+1}+jZ_k	an(eta_kL_k)
}{
Z_k+jZ_{in,k+1}	an(eta_kL_k)
}.
]

The objective is

[
min
max_{fin[9,11.5] {m GHz}}
left|
rac{Z_{in}(f)-Z_{m ref}(f)}
{Z_{in}(f)+Z_{m ref}(f)}
ight|.
]

The same ridge width is imposed in both sections.

---

## 8. Ridge-width trade study

For each fixed (w/a), the two gaps and two physical lengths were optimized.

| (w/a) | reduced-model worst RL | (g_1) mm | (g_2) mm | (L_1) mm | (L_2) mm | TE20-like cutoff 1 | TE20-like cutoff 2 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 33.52 dB | 6.708 | 3.873 | 9.848 | 8.798 | 13.53 GHz | 13.92 GHz |
| 0.15 | 33.52 dB | 7.259 | 4.486 | 9.855 | 8.823 | 13.59 GHz | 14.11 GHz |
| **0.20** | **33.50 dB** | **7.672** | **4.984** | **9.872** | **8.857** | **13.58 GHz** | **14.15 GHz** |
| 0.25 | 33.46 dB | 7.975 | 5.393 | 9.901 | 8.901 | 13.52 GHz | 14.04 GHz |
| 0.30 | 33.39 dB | 8.188 | 5.728 | 9.942 | 8.956 | 13.44 GHz | 13.80 GHz |
| 0.35 | 33.28 dB | 8.325 | 5.999 | 9.996 | 9.024 | 13.34 GHz | 13.51 GHz |
| 0.40 | 33.13 dB | 8.394 | 6.210 | 10.065 | 9.107 | 13.23 GHz | 13.20 GHz |

Several observations follow.

### 8.1 Return loss is not very sensitive to ridge width in this range

All cases from (w/a=0.10) to 0.30 produce roughly 33.4–33.5 dB in the conditional reduced model.

Therefore ridge width can be chosen using manufacturing, field concentration, and higher-mode considerations rather than chasing a negligible fraction of a dB in the analytic transformer.

### 8.2 Wider ridges allow larger gaps for the same effective impedance

This is attractive for peak-power handling because the electric field is concentrated in the ridge gap.

### 8.3 Excessively wide ridges reduce higher-mode margin

Beyond about (w/a=0.30), the estimated TE20-like cutoff begins moving downward toward the top of the operating band.

This argues against simply maximizing ridge width.

---

## 9. Recommended first HFSS seed

A good compromise is

[
oxed{rac{w}{a}=0.20}
]

for both sections.

For WR90,

[
oxed{w=4.572 {m mm}}.
]

### Section 1

[
oxed{g_1=7.672 {m mm}},
]

[
oxed{h_{r1}=rac{b-g_1}{2}=1.244 {m mm}},
]

[
oxed{L_1=9.872 {m mm}}.
]

Closed-form dominant cutoff:

[
f_{c1}approx5.97 {m GHz}.
]

TRM dominant cutoff:

[
f_{10,1}^{TRM}approx6.08 {m GHz}.
]

TRM TE20-like cutoff:

[
oxed{f_{20,1}^{TRM}approx13.58 {m GHz}}.
]

At 10.2 GHz, the Cohn voltage-current impedance is approximately

[
Z_1approx289.5 Omega.
]

Relative to the same-definition WR90 reference,

[
Z_1/Z_{m ref}approx0.842.
]

### Section 2

[
oxed{g_2=4.984 {m mm}},
]

[
oxed{h_{r2}=rac{b-g_2}{2}=2.588 {m mm}},
]

[
oxed{L_2=8.857 {m mm}}.
]

Closed-form dominant cutoff:

[
f_{c2}approx5.12 {m GHz}.
]

TRM dominant cutoff:

[
f_{10,2}^{TRM}approx5.20 {m GHz}.
]

TRM TE20-like cutoff:

[
oxed{f_{20,2}^{TRM}approx14.15 {m GHz}}.
]

At 10.2 GHz,

[
Z_2approx209.3 Omega,
]

or

[
Z_2/Z_{m ref}approx0.609.
]

These values are close to, but not identical with, the earlier abstract minimax ratios 0.833 and 0.600 because the present optimization includes the ridge's own frequency-dependent impedance and dispersion.

---

## 10. Reduced-model predicted ripple

For the conditional (Z_L/Z_0=0.5) model, this geometry gives an approximately equal-ripple response with worst return loss

[
oxed{RL_{min}approx33.50 {m dB}}.
]

The three worst points occur approximately at

- 9.0 GHz,
- 10.154 GHz,
- 11.5 GHz.

Again, this is **not** a prediction that the complete HFSS magic tee will achieve 33.5 dB. It only shows that the two-section ridge transformer itself has enough analytic margin to justify this as an initial geometry.

---

## 11. Peak-field proxy for the ridge gap

Because the chosen Cohn impedance is a voltage-current definition, one can construct only a first-order gap-field proxy.

Using

[
V_{rms}simsqrt{PZ}
]

and

[
E_{gap,pk}
sim
rac{sqrt2V_{rms}}{g},
]

at 30 kW and approximately 10.2 GHz:

### Section 1

[
E_{gap,pk}^{proxy}
approx0.54 {m MV/m}.
]

### Section 2

[
E_{gap,pk}^{proxy}
approx0.71 {m MV/m}.
]

These are encouragingly below the multi-MV/m scale, but they do **not** include ridge-edge enhancement, junction enhancement, surface roughness, or bolt-tip enhancement.

Therefore the actual HFSS acceptance variable remains

[
K_E
=
rac{E_{local,max}}
{E_{straight-guide,max}},
]

with the preliminary screening goal

[
K_E<3.
]

---

## 12. How this should be built in HFSS

Do not begin with the complete four-way network.

### Step 1 — uniform section 1

Build a uniform WR90 double-ridge guide:

- (a=22.86) mm
- (b=10.16) mm
- (w=4.572) mm
- (g=7.672) mm

Extract:

- first 3–4 eigenmodes;
- dominant (eta(f));
- the impedance definition used by the selected HFSS port;
- peak field per normalized watt.

### Step 2 — uniform section 2

Repeat for

- (w=4.572) mm
- (g=4.984) mm.

### Step 3 — compare HFSS against analytic targets

The full-wave values should be compared with, not forced to equal, the theory:

- (f_{10}sim6.0) and 5.1 GHz;
- (f_{20}sim13.6) and 14.2 GHz;
- relative impedance trend (Z_1>Z_2);
- section 2 should show stronger central electric-field concentration.

### Step 4 — build a back-to-back two-section transformer

Use the analytic starting lengths

- (L_1=9.872) mm;
- (L_2=8.857) mm.

First use hard steps only to identify whether the two-section mechanism behaves as expected.

### Step 5 — replace hard steps by a smooth ridge profile

The final device should not necessarily retain two abrupt steps.

A smooth profile may interpolate the ridge height using, for example,

[
s(t)=3t^2-2t^3,
qquad
t=z/L.
]

The two-section geometry is best regarded as a discrete approximation to the desired continuous impedance trajectory.

### Step 6 — only then attach the magic-tee junction

Once the transition itself is understood, attach it to the single magic tee, de-embed, and retune.

The junction will shift the effective load away from the conditional scalar 0.5 case. The analytic seed should then be re-optimized using the extracted complex load.

---

## 13. What must be verified before calling the geometry valid

The first HFSS pass should reject the seed if any of the following occurs:

1. a higher propagating mode falls below 11.5 GHz;
2. the HFSS modal impedance trend is inconsistent with the analytic section ordering;
3. the full-wave two-section transition cannot reach at least 25 dB return loss before bolts;
4. the ridge-gap field enhancement is excessive;
5. the second section causes a narrow resonant response rather than broadband matching;
6. dimensional perturbations of approximately ±0.05–0.10 mm destroy the match.

If these tests pass, then the seed is strong enough to carry into the full magic-tee optimization.

---

## 14. Main conclusions

1. The ridge geometry and section length must be optimized together; plain-WR90 quarter-wave lengths are not valid after the ridge is introduced.
2. A common ridge width around (w/a=0.15)–0.25 is analytically attractive.
3. (w/a=0.20) gives a useful compromise between modal margin, machining simplicity, and gap size.
4. The resulting first-pass geometry is:
   - (w=4.572) mm;
   - section 1: (g=7.672) mm, (L=9.872) mm;
   - section 2: (g=4.984) mm, (L=8.857) mm.
5. The reduced-model equal-ripple return loss is about 33.5 dB, providing analytic margin over the required 22 dB.
6. The first estimated TE20-like cutoffs remain around 13.6 and 14.2 GHz, above the 11.5 GHz operating edge.
7. The conditional 0.5 load assumption remains the largest unresolved modeling approximation.
8. The next decisive step is therefore HFSS uniform-ridge eigenmode/wave-port extraction followed by de-embedding of a **single** magic-tee junction.
