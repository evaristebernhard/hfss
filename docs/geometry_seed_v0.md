# Engineering geometry seed v0

## Purpose

This file converts the analytic two-section matching targets into a first manufacturable double-ridge geometry seed for local HFSS 2022 work.

It is a design initializer, not a claimed full-wave optimum.

## Fixed outer guide

WR90 air-filled internal dimensions:

- a = 22.86 mm
- b = 10.16 mm
- target band = 9.0–11.5 GHz
- nominal electrical center = 10.195 GHz

## Two-section ridge seed

The analytic reduced model gives the normalized target sequence

1.000 -> 0.8327 -> 0.6005 -> junction/load

for the conditional 2:1 transformer seed.

The physical double-ridge seed is:

| parameter | Section 1 | Section 2 |
|---|---:|---:|
| ridge width w | 5.8 mm | 9.2 mm |
| ridge gap g | 6.0 mm | 4.0 mm |
| ridge depth per wall h_r=(b-g)/2 | 2.08 mm | 3.08 mm |
| w/a | 0.2537 | 0.4024 |
| g/b | 0.5906 | 0.3937 |
| nominal electrical length | 9.601 mm | 9.601 mm |

Total nominal matching length:

L_T = 19.2025 mm.

These dimensions are a deliberately conservative geometry mapping of the two analytic impedance levels.

## Why these dimensions

Published double-ridge studies show the correct qualitative design direction:

- increasing ridge width and reducing ridge gap lowers dominant-mode cutoff and characteristic impedance;
- appropriate ridge ratios can increase higher-order-mode separation;
- very small gaps can yield very broad single-mode operation, but are unnecessary here and undesirable for the 30 kW peak-power requirement.

The first section uses w/a about 0.25 but a much larger gap than ultra-wideband horn-feed designs, because only moderate impedance reduction is required.

The second section increases ridge width to about 0.40a and reduces gap to about 0.39b, giving stronger capacitive loading without entering the very-small-gap regime.

References:

1. T. Isenlik, K. Yegin, D. E. Barkana, Near-constant beamwidth quadruple bandwidth double-ridged horn antenna design, IET Microwaves, Antennas & Propagation, 2019, DOI 10.1049/iet-map.2019.0199.
2. S. B. Cohn, Properties of Ridge Wave Guide, Proceedings of the IRE, 1947.

## High-power geometry screen

Use the crude local geometric concentration proxy

K_gap_proxy = b/g.

This is not an RF breakdown model; it is only an early geometry screen.

For Section 1:

K_gap_proxy = 10.16/6.0 = 1.69.

For Section 2:

K_gap_proxy = 10.16/4.0 = 2.54.

A preliminary geometric rule is g >= b/3 = 3.39 mm so that this proxy remains below about 3.

Therefore the nominal Section-2 gap is kept at 4.0 mm rather than pushed into the 1–2 mm range.

## Taper implementation

Use a monotone smooth ridge profile over the 19.2025 mm matching region.

Control stations:

| z | ridge width w | ridge gap g |
|---:|---:|---:|
| 0 mm | 0 mm | 10.16 mm |
| 9.601 mm | 5.8 mm | 6.0 mm |
| 19.203 mm | 9.2 mm | 4.0 mm |

For each interval use smoothstep interpolation:

s(t) = 3t^2 - 2t^3,  0 <= t <= 1

and

q(z) = q_A + (q_B-q_A)s(t)

for both ridge width and gap.

This keeps profile slope zero at the control stations and avoids a hard capacitive discontinuity.

## Edge radii

Nominal longitudinal ridge-edge fillet:

- r = 0.8 mm
- initial sweep = 0.5–1.2 mm

Avoid zero-radius edges in the high-power model.

## Optional tuning bolt seed

Do not include tuning bolts in the first matching run.

If residual susceptance remains after ridge optimization, use this starting range:

- shank diameter = 3.0 mm
- rounded tip radius = 1.5 mm
- nominal penetration = 0.8 mm
- penetration sweep = 0–2.5 mm
- axial-location sweep = 3–7 mm from the nearest junction reference plane

Prefer symmetric placement so the sum/difference symmetry is not broken.

## Recommended first local HFSS sweeps

Stage A — dominant geometry:

- w1 = 4.8–6.8 mm
- g1 = 5.0–7.0 mm
- w2 = 8.0–10.5 mm
- g2 = 3.5–5.0 mm
- L1 = 8.7–10.5 mm
- L2 = 8.7–10.5 mm

Stage B — shape:

- fillet radius = 0.5–1.2 mm
- smoothstep versus linear taper
- total taper length = 17–22 mm

Stage C — tuning only if required:

- bolt penetration
- bolt axial position
- optional second symmetric bolt

## Internal acceptance objectives

Use tighter optimization goals than the contractual limits:

- worst-band return loss > 25 dB
- input isolation > 25 dB
- coherent combining efficiency > 97%
- amplitude imbalance < 0.3 dB
- phase imbalance < 5 degrees
- local field enhancement ratio target < 3 relative to straight WR90 at the same transmitted power

## Seed summary

WR90:
a = 22.86 mm
b = 10.16 mm

Ridge section 1:
w1 = 5.8 mm
g1 = 6.0 mm
hr1 = 2.08 mm
L1 = 9.601 mm

Ridge section 2:
w2 = 9.2 mm
g2 = 4.0 mm
hr2 = 3.08 mm
L2 = 9.601 mm

Profile control stations:
(0, 0, 10.16)
(9.601, 5.8, 6.0)
(19.203, 9.2, 4.0)

Ridge fillet:
0.8 mm

Tuning bolt:
disabled initially

The next local HFSS step is to instantiate this profile, sweep 8.5–12.0 GHz, and inspect S parameters plus modal and field behavior before any bolt tuning.
