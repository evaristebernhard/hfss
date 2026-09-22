# v4 full Magic-T four-way combiner architecture

## 1. Objective

Freeze one complete architecture and stop changing topology after every local solve.

Target system:
- 4 coherent WR90 inputs
- two first-stage Magic-T combiners feeding one second-stage Magic-T
- 9.0--11.5 GHz
- return loss >= 22 dB at all driven ports
- isolation >= 22 dB after full-tree assembly and tolerance checks
- coherent combining efficiency >= 95%
- peak output power > 30 kW
- CW average power > 1 kW
- compact mechanical envelope

HFSS target environment: AEDT / HFSS 2022.x.

## 2. System architecture

```text
IN1 ─┐
     ├─ MT-A ─ interstage H-arm transformer ─┐
IN2 ─┘                                       │
                                             ├─ MT-C ─ output transformer ─ OUT
IN3 ─┐                                       │
     ├─ MT-B ─ interstage H-arm transformer ─┘
IN4 ─┘

Each difference/E port -> matched high-power load / dump termination
```

All three Magic-T cells use the same nominal electromagnetic core. MT-C may later
receive a different output transition only if required by peak-field or thermal
constraints.

## 3. Frozen single-cell functional zoning

From the H/sum junction outward:

```text
J0 junction-local matching cell
 -> J1 mild H-plane throat
 -> J2 terminal double ridge
 -> J3 smooth double-ridge broadband transformer
 -> J4 three-screw residual tuner
 -> J5 straight WR90 reference section
```

E/difference arm:

```text
junction stepped septum
 -> short E-plane impedance step
 -> compact height transformer
 -> straight WR90 difference-port reference plane
```

### J0: junction-local matching cell

Use a mirror-symmetric rounded partial-height cylindrical post pair.
Its purpose is to supply the missing R11 weak singular direction.

Primary variables:
- post height hp
- post longitudinal position yp

Frozen first seed:
- post radius rp = 1.5 mm
- post height hp = 0.70 mm
- post axis yp = 1.50 mm from the H-plane junction mouth

The post pair is not a tuning screw. It is a permanent broadband junction
element and remains symmetric about the collinear parity plane.

### J1: mild H-plane throat

Retain the proven spectral-shaping coordinate from v3.4/R11.

Primary variables:
- aH: reduced broad dimension
- LH: throat length

R11 shows LH is the strongest first-order slope/phase coordinate.

### J2/J3: terminal ridge + smooth ridge transformer

These sections convert the locally matched junction to ordinary WR90.

Primary variables:
- terminal ridge width wt
- terminal gap gt
- terminal length Lt
- one taper curvature parameter ktaper

The transformer is not allowed to become arbitrarily long. Compactness is a hard
design objective.

### J4: three-screw residual tuner

Three screws are included in the geometry from the beginning but remain retracted
during passive synthesis.

Nominal relative axial seeds are now chosen as a broadband basis rather than
as a single-frequency quarter-wave cancellation pair:
- screw 1: z1 = 0 mm reference
- screw 2: z2 = 5.0 mm
- screw 3: z3 = 19.5 mm

Using nine equally spaced frequencies over 9--11.5 GHz and the weak-reflection
basis exp(-2j beta(f) z_i), column-normalized real/imag SVD gives:

- old [0, 8.4, 17.6] mm: condition number about 11.70,
  sigma_min/sigma_max about 0.0855;
- new [0, 5.0, 19.5] mm: condition number about 2.24,
  sigma_min/sigma_max about 0.4456.

Therefore the new positions are preferred for broadband three-parameter
residual fitting. They are not claimed to be the final mechanical optimum.

Penetration variables:
- p1, p2, p3

Initial passive state:
- p1 = p2 = p3 = 0

Residual-tuning range:
- preferred 0--1.5 mm
- hard exploration ceiling 2.0 mm

Use rounded/blunt screw tips for the high-power version.

## 4. Parameter hierarchy

Do not optimize every variable at once.

### Passive structural coordinates

[
p_s = [h_b, y_b, a_H, L_H, w_t, g_t, L_t, k_{taper}]
]

### Residual tuning coordinates

[
p_t = [p_1,p_2,p_3]
]

### Interstage tree coordinates

[
p_{tree} = [L_{A	o C}, L_{B	o C}, Delta L, 	ext{transition dimensions}]
]

The tree phase lengths are solved only after a single Magic-T cell reaches the
passive return-loss gate.

## 5. R11 diagnosis carried into v4

At the v3.4 center point:

[
F=[ReGamma_0,ImGamma_0,ReGamma_1,ImGamma_1]^T
]

was approximately:

[
[0.466, 0.449, 0.686, -0.886]^T.
]

The step-normalized singular values were:

[
[0.1646, 0.0723, 0.00215, 0.000390]
]

with condition number about 422.

Therefore the old four-coordinate system is formally full-rank but practically
rank-deficient. The v4 boss must increase the weak singular directions instead
of merely improving one scalar return-loss point.

## 6. Boss seed

Initial geometry:
- post radius = 1.50 mm
- post height hp = 0.70 mm
- post axis yp = 1.50 mm from the H-plane junction mouth

First local identification half-steps:
- hp +/- 0.20 mm
- yp +/- 0.50 mm

This is deliberately small: the first decision is whether the two new boss
columns project onto the old weak output directions.

## 7. Minimal identification program

Do not launch a Cartesian sweep.

### Phase A: boss direction test

Five full-wave solves:
1. v4 center with screws retracted
2. hb -
3. hb +
4. yb -
5. yb +

Compare the two new step-normalized sensitivity columns against the existing R11
subspace.

Primary acceptance is direct weak-direction controllability.

R11 leaves approximately 0.260 error along its weakest output direction u4.
For the two new step-normalized post columns c_h and c_y define

    g_h = |u4^T c_h|,
    g_y = |u4^T c_y|.

If each coordinate is allowed to move by at most two identification half-steps,
the first-order upper-bound correction is

    C4 = 2 (g_h + g_y).

Require

    g_h + g_y >= 0.130

so that C4 >= 0.260.

The augmented singular values are still reported as a secondary diagnostic,
but a 5x increase of sigma_min alone is not sufficient. If the post pair fails
the direct weak-direction gate, replace the local matching concept immediately
rather than performing a wide Cartesian sweep.

### Phase B: passive synthesis

With a validated local control direction, use trust-region / regularized
least-squares updates on the passive coordinates.

Staged gates:
- RL >= 10 dB
- RL >= 15 dB
- passive RL >= 18--20 dB

Do not activate screws before the passive cell enters this range.

### Phase C: three-screw residual synthesis

For weak screws use the first-order model:

[
Gamma_{screw}(f)
approx
sum_{i=1}^3 gamma_i(p_i)e^{-2jeta(f)z_i}
]

Identify the three penetration derivatives with only local perturbation solves.
Then solve p1,p2,p3 in a least-squares sense against the remaining broadband
reflection residual.

Final nominal target:
- RL >= 22 dB across 9--11.5 GHz
- isolation >= 30 dB nominal internal target
- keep all screw penetrations shallow

## 8. Four-way network closure

Only after the single cell is stable:

1. export the full 4-port S-matrix of one cell;
2. build a reduced network model of MT-A, MT-B, MT-C plus interstage lines;
3. solve interstage electrical lengths for coherent phase addition;
4. check the complete 4-input to 1-output S/network response;
5. then build one full 3D four-way HFSS assembly for confirmation.

Required full-tree outputs:
- driven-port return loss
- input-input isolation
- output combining efficiency
- amplitude imbalance
- phase imbalance
- difference-port dump power under source mismatch

## 9. Efficiency budget

95% combining efficiency corresponds to only:

[
IL_{total} le -10log_{10}(0.95)=0.223	ext{ dB}.
]

A two-stage input path therefore has only about 0.11 dB/stage if losses are
distributed evenly.

PEC solves cannot prove this requirement.

After nominal matching closes:
- switch to finite-conductivity copper/plating;
- include flange/contact losses where practical;
- compute per-stage dissipative loss;
- verify the complete two-stage path remains inside the 0.223 dB system budget.

## 10. High-power rules

The 30 kW peak requirement is not inferred from S parameters.

For all new metal features:
- no sharp boss corners;
- rounded ridge terminations;
- rounded/blunt screw tips;
- avoid narrow gaps introduced only for matching;
- report local field enhancement factor
  K_E = Emax_local / Emax_straight_WR90.

Use peak-field screening before any final hardware claim.

The 1 kW CW requirement additionally needs:
- finite conductivity;
- dissipated-loss map;
- thermal boundary conditions;
- steady-state temperature rise.

## 11. Frozen decision

The v4 architecture is now the design frame:

[
oxed{
	ext{local rounded boss/post}
+	ext{mild H throat}
+	ext{terminal double ridge}
+	ext{smooth ridge transformer}
+	ext{three-screw residual tuner}
}
]

inside a three-Magic-T binary 4-to-1 tree.

Future work should optimize this architecture rather than repeatedly invent new
topologies.


---

## 12. Mathematical synthesis update after R11

The v4 workflow is explicitly split into orthogonal physical jobs:

1. the junction-local post pair targets the R11 weak output direction and the
   center-frequency complex mismatch;
2. H-throat length/width remain spectral-slope and phase controls;
3. the double-ridge transformer should be synthesized from a target impedance
   trajectory instead of treated as a large free sweep;
4. the three screws are a residual broadband basis and should be solved by
   constrained complex least squares after the passive structure reaches the
   18--20 dB return-loss region;
5. the three-Magic-T four-way tree is first closed as an S-parameter network,
   then confirmed by one full 3D assembly.

For small screw penetrations,

    Gamma_screw(f) ~= sum_i c_i(f) p_i,

where c_i(f) is measured from one small HFSS penetration perturbation per screw.
The tuning problem is then

    min || Gamma_passive(f_k) + sum_i c_i(f_k) p_i ||_2

subject to

    0 <= p_i <= 1.5 mm

for the preferred range.

This replaces blind screw sweeps with a directly identified linear residual
model.

The complete derivation and quantitative R11 control target are documented in
`docs/v4_mathematical_synthesis.md`.
