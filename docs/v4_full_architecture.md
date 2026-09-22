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

Use a mirror-symmetric rounded partial-height boss pair / local post structure.
Its purpose is to supply the missing R11 weak singular direction.

Primary variables:
- boss height hb
- boss longitudinal position yb

Secondary frozen seed dimensions:
- boss width wb
- boss length lb
- internal corner radius rb

The boss is not a tuning screw. It is a permanent broadband junction element.

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

Nominal axial seeds from the existing ridge-guided wavelength estimate:
- screw 1: z1 = 0 mm reference
- screw 2: z2 = 8.4 mm
- screw 3: z3 = 17.6 mm

Thus:
- d12 = 8.4 mm
- d23 = 9.2 mm

The slight nonuniform spacing avoids making all screw phasors redundant over the
24.4% fractional bandwidth.

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
- hb = 0.70 mm
- yb = 1.00 mm from the H-plane junction mouth
- wb = 5.5 mm
- lb = 3.0 mm
- rb = 0.6 mm

First local identification half-steps:
- hb +/- 0.20 mm
- yb +/- 0.50 mm

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

Acceptance:
- the smallest useful singular value must rise by at least ~5x over R11, or
- sigma_min/sigma_max should move toward >= 0.01 as a first gate.

If the boss fails this test, replace it with a partial-height post rather than
sweeping its dimensions widely.

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
