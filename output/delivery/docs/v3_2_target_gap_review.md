# v3.2 design target and gap review

## 1. Purpose

This document answers two questions:

1. How far is the current design from the requested system targets?
2. Which targets should remain final requirements, and which should be converted into staged engineering gates?

The current requested system intent is interpreted as:

- band: 9.0--11.5 GHz;
- return loss: better than 22 dB;
- isolation: better than 22 dB;
- combining efficiency: at least 95%;
- peak power: at least 30 kW;
- continuous average power: at least 1 kW;
- compact size.

The current repository only contains PEC electromagnetic matching work. It does **not** yet contain a validated finite-conductivity, thermal, multipactor/breakdown, fabrication-tolerance, or complete four-way cascade model.

---

## 2. Current status by requirement

| Requirement | Current evidence | Gap classification | Design implication |
|---|---|---|---|
| 9--11.5 GHz operating band | All v2/Stage-A solves use full 9--11.5 GHz band | Green | keep unchanged |
| parity / H-E isolation | forbidden parity terms typically ~-50 to -70 dB | Green | symmetry concept is already stronger than requirement |
| 22 dB H/even return loss | Stage-A best band-worst RL ~1.27 dB | Red / structural | H junction coupling must be redesigned |
| 22 dB E/odd return loss | v2 band-worst RL ~5.34 dB; corrected effective 3-DOF model predicts ~23.84 dB | Amber | physics target is plausible; geometry still missing |
| amplitude balance | symmetry strongly helps, but no final four-way tolerance budget exists | Amber | must define explicit dB tolerance |
| phase balance | reference-plane/de-embedding issue not yet finalized | Amber | must define explicit degree tolerance at common reference planes |
| isolation >22 dB | present parity isolation is much better in ideal symmetric PEC model | Green/Amber | final tolerance and assembly asymmetry still untested |
| 95% combining efficiency | not defined precisely; PEC cannot validate ohmic efficiency | Red / requirements definition | define whether this is single tee or full four-way network and what losses are included |
| 30 kW peak power | straight-WR90 field scale estimated; no v3 peak-field solution yet | Red / validation | require field-enhancement and breakdown-margin workflow |
| 1 kW continuous average | no conductor-loss or thermal model | Red / validation | requires copper conductivity, joints, cooling and temperature boundary conditions |
| compact size | not numerically defined | Red / requirements definition | convert to measurable envelope or added-length limit |

---

## 3. H-side gap

The H/even block is the dominant electromagnetic gap.

For the best completed Stage-A case,

[
g_2=5.8 {m mm},
qquad
L_t=7.5 {m mm},
]

the band-worst return loss is only

[
RL_{c_+}approx1.27 {m dB}.
]

The coupling magnitudes are approximately

[
|t_H|=
0.785, 0.672, 0.503
]

at 9, 10.2 and 11.5 GHz.

The 22 dB lossless target corresponds to

[
|t|>sqrt{1-10^{-22/10}}approx0.99684.
]

Therefore the H block still requires a major junction-coupling redesign.

This is not a tuning-margin problem.

### 3.1 H design gate

Do not ask the first new H geometry to meet 22 dB immediately.

Use the following structural gate:

[
oxed{|t_H|_{min}ge0.85}
]

over 9--11.5 GHz before adding residual cancellation elements.

Preferred gate:

[
oxed{|t_H|_{min}ge0.90}.
]

Only after this gate is reached should residual iris / bolt / phase tuning be introduced.

---

## 4. E-side gap

The E/odd block is substantially closer to a solvable arm-matching problem.

The current v2 block has approximately

[
|t_E|=
0.937, 0.900, 0.841
]

at 9, 10.2 and 11.5 GHz.

A corrected complete-two-port reduced model with three effective degrees of freedom,

1. average transformation ratio;
2. transformation-ratio slope versus frequency;
3. series inductive reactance,

reaches approximately

[
oxed{RL_{min}approx23.84 {m dB}}.
]

Therefore the E target should not be relaxed yet.

The gap is geometry realization, not network-order feasibility.

---

## 5. Isolation target

The nominal ideal-symmetry isolation target does not need to be relaxed.

The present solved structures already show forbidden parity terms far below -22 dB.

However the final requirement should be split into:

### Nominal simulation

[
oxed{	ext{isolation}ge30 {m dB}}
]

as an internal nominal design target.

### Tolerance / fabricated requirement

[
oxed{	ext{isolation}ge22 {m dB}}
]

under the agreed machining and assembly tolerances.

This gives useful margin for symmetry-breaking error.

The tolerance model must later include left/right geometric mismatch, bolt penetration mismatch, flange misalignment and assembly offsets.

---

## 6. Return-loss target

Keep

[
oxed{RLge22 {m dB}}
]

as the final customer-facing band target for now.

Do not use it as the first structural gate.

Recommended staged gates:

### Gate R0 — topology direction

A new topology must improve the correct modal block over the previous best case without degrading parity.

### Gate R1 — structural viability

[
oxed{RL_{min}ge10 {m dB}}
]

over the full band.

### Gate R2 — optimization-ready

[
oxed{RL_{min}ge15 {m dB}}
]

over the full band.

### Gate R3 — engineering target

[
oxed{RL_{min}ge20 {m dB}}
]

over the full band with passive geometry only.

### Gate R4 — final nominal target

[
oxed{RL_{min}ge22 {m dB}}
]

with final residual tuning and common reference planes.

This prevents a structurally promising geometry from being discarded simply because the first baseline does not immediately meet 22 dB.

---

## 7. Combining-efficiency requirement needs clarification

A 95% power efficiency corresponds to total excess insertion loss

[
IL_{m total}
le
-10log_{10}(0.95)
approx
oxed{0.223 {m dB}}.
]

For a four-way binary tree with two comparable magic-T stages in each path, if the loss is split equally,

[
IL_{m tee}
lesssim
0.111 {m dB}
]

per stage.

This is a demanding target.

A reported wideband X-band magic-T achieved insertion loss below about 0.15 dB per port while also exceeding 36% 20-dB RL bandwidth. A separate X-band magic-T power-combiner network has reported sub-0.15 dB magic-tee-network loss over a narrower band.

Therefore 95% **overall four-way** efficiency is materially stronger than merely requiring one magic-T to have low loss.

### 7.1 Recommended requirement wording

Replace the ambiguous statement

> combining efficiency >=95%

with two explicit quantities:

#### PEC / mismatch combining efficiency

[
eta_{m match}
=
P_{m desired,output}/P_{m accepted,input}
]

target:

[
oxed{eta_{m match}ge97%}
]

for the single-tee nominal design.

This is a topology/matching metric.

#### Real four-way RF efficiency

[
eta_{m RF}
=
P_{m combined,output}/sum P_{m source,ports}
]

including mismatch, conductor loss, junction loss and network cascade.

Final system target may remain

[
oxed{eta_{m RF}ge95%}
]

but it must be validated only after finite-conductivity simulation of the complete cascade.

If 95% was intended for a **single magic-T** rather than the full four-way combiner, the requirement is significantly less restrictive and should be stated explicitly.

---

## 8. Peak-power target

Keep

[
oxed{P_{m peak}ge30 {m kW}}
]

as the final target.

Do not claim it from S parameters.

For straight WR90 at 30 kW, the present theoretical TE10 peak-electric-field scale is roughly

[
0.49	ext{--}0.53 {m MV/m}
]

over 9--11.5 GHz.

The matching geometry must therefore report

[
K_E=
rac{E_{max,m local}}
{E_{max,m straight,WR90}}.
]

Recommended internal screening:

- preferred: (K_Ele2);
- review: (2<K_Ele3);
- reject/rework before power qualification: (K_E>3).

These are design-screening ratios, not universal breakdown thresholds.

Final peak-power qualification must include pressure, gas, pulse width, surface finish, corner radius and multipactor/breakdown assumptions.

---

## 9. Continuous 1 kW requirement

The 1 kW continuous-average requirement cannot currently be accepted or rejected.

The missing inputs are:

- metal material and conductivity;
- plating;
- flange/contact resistance;
- ambient temperature;
- cooling boundary conditions;
- allowed wall temperature;
- duty cycle if "continuous" is not literal CW;
- mechanical thermal path.

The repository must later add:

1. finite-conductivity HFSS loss;
2. surface-loss density;
3. steady-state thermal model;
4. temperature rise / deformation check.

Therefore 1 kW CW remains a final target but is outside the current PEC matching phase.

---

## 10. Compactness target must become measurable

"Volume not too large" is not an engineering acceptance criterion.

Until a customer envelope is supplied, use it as a soft optimization objective.

Recommended provisional internal rule:

- do not add more than approximately (0.5lambda_g) of matching length to either side arm at 10.25 GHz unless the RF gain is substantial;
- (0.5lambda_g) is approximately 19 mm in WR90 near band center;
- prefer localized junction/window/septum structures over long transformer chains.

This is an internal compactness rule, not a customer specification.

Final documentation should replace it with an actual maximum bounding box.

---

## 11. Missing amplitude and phase requirements

A four-way combiner cannot be fully specified by return loss and isolation alone.

The final requirement set should include amplitude and phase balance.

Recommended internal nominal targets per tee:

[
oxed{Delta Ale0.2 {m dB}}
]

and

[
oxed{Deltaphile3^circ}
]

over the band after de-embedding to common reference planes.

These are proposed internal engineering targets, not yet customer-confirmed requirements.

The tolerance/fabricated limits can be relaxed later if the complete four-way cascade demonstrates adequate combining efficiency.

---

## 12. Recommended target hierarchy

### Final targets retained

- band: 9--11.5 GHz;
- return loss: >=22 dB;
- isolation: >=22 dB under tolerance;
- peak power: >=30 kW;
- continuous average power: >=1 kW;
- complete-system RF combining efficiency: >=95%, **if this is confirmed as the intended definition**.

### Internal stricter targets

- nominal isolation >=30 dB;
- H/E parity leakage kept well below final tolerance limit;
- passive-geometry RL >=20 dB before residual tuning;
- peak-field screening preferably (K_Ele2);
- nominal amplitude imbalance <=0.2 dB;
- nominal phase imbalance <=3 degrees.

### Staged targets

- H junction: (|t_H|_{min}ge0.85), preferably >=0.90, before remote cancellation;
- E localized matcher: reduced/full-wave topology should demonstrate >=20 dB before detailed high-power optimization;
- finite-conductivity / thermal validation only after PEC topology is stable.

---

## 13. Current project gaps ranked by severity

### G1 — H junction coupling topology

**Severity: critical.**

The solved H block is still far from the required coupling angle, especially at the high-frequency edge.

### G2 — E geometry realization

**Severity: high but bounded.**

A three-effective-DOF network model crosses the 22 dB target, but no physical waveguide geometry has yet demonstrated the required effective law.

### G3 — real efficiency definition and validation

**Severity: critical requirements/validation gap.**

The 95% requirement is ambiguous and cannot be validated in PEC.

### G4 — high-power field qualification

**Severity: high.**

The design has no solved final-geometry peak-field map.

### G5 — 1 kW CW thermal design

**Severity: high.**

No finite-conductivity/thermal model exists.

### G6 — amplitude/phase balance and common reference planes

**Severity: medium-high.**

Required for a real four-way combiner and not yet formalized.

### G7 — fabrication tolerance

**Severity: medium-high.**

Nominal parity isolation is excellent, but symmetry-breaking sensitivity has not been quantified.

### G8 — compactness definition

**Severity: requirements gap.**

No bounding-box requirement exists.

### G9 — complete four-way cascade

**Severity: later-system gap.**

Current work is still on one magic-T cell. The four-way tree has not yet been simulated with phase lengths, conductor loss and source/load tolerances.

---

## 14. Design decision

Do not reduce the headline RF bandwidth or 22 dB return-loss target yet.

The evidence supports keeping them as final targets.

Instead, modify the **engineering process**:

[
oxed{
	ext{single final target set}
ightarrow
	ext{staged electromagnetic + power + thermal acceptance gates}
}
]

The only target that must be rewritten immediately is "95% combining efficiency", because its current definition is ambiguous.

The compactness requirement also needs a numerical envelope before final acceptance.
