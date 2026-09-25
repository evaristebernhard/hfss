# v3.4 Jacobian simulation program

## Purpose

The committed v3.4 center solve improves the H/even block but remains far from
the staged passive matching gates. The next decision is whether the four
selected geometric controls provide four independent first-order directions.

Feature vector at f0 = 10.25 GHz:

[
F = [ReGamma_0, ImGamma_0, ReGamma_1, ImGamma_1]^T
]

with

[
Gamma_1 = rac{dGamma}{df}igg|_{f_0}.
]

Primary coordinates:

- h_throat_a = 20.4 mm, half-step 0.4 mm
- h_throat_len = 5.5 mm, half-step 1.0 mm
- h_cap_height = 9.0 mm, half-step 0.4 mm
- h_terminal_ridge_w = 4.572 mm, half-step 0.5 mm

The terminal-ridge half-step is 0.5 mm so both samples remain inside the
documented 4.0--6.5 mm range.

## HFSS batch

The committed center result can be reused, so only eight new solves are
required:

```bash
python hfss/run_v3_4_jacobian.py \
  --version 2025.2 \
  --solve \
  --skip-center
```

For headless AEDT operation add:

```bash
--non-graphical
```

To resume an interrupted batch without rerunning completed cases:

```bash
python hfss/run_v3_4_jacobian.py \
  --version 2025.2 \
  --solve \
  --skip-center \
  --skip-existing
```

Each case is written to:

```text
hfss/output_v3_4_jacobian/<case-name>/
```

and the runner writes a manifest with exact parameters and commands.

## Jacobian analysis

After all eight perturbation S4P files exist:

```bash
python hfss/analyze_v3_4_jacobian.py
```

The analyzer forms:

[
J =
rac{partial(ReGamma_0,ImGamma_0,ReGamma_1,ImGamma_1)}
{partial(a_H,L_H,b_C,w_t)}
]

and also the step-normalized matrix

[
J_s = J,mathrm{diag}(Delta a_H,Delta L_H,Delta b_C,Delta w_t).
]

The step-normalized SVD is the primary conditioning diagnostic because the
coordinates have different practical perturbation scales.

Reported quantities include:

- all four singular values;
- sigma_min / sigma_max;
- condition number;
- numerical rank;
- effective rank using 5% and 1% relative thresholds;
- full-band H/even and E/odd metrics for every case;
- forbidden parity coupling;
- a pseudoinverse Newton step;
- a trust-limited candidate clipped to 0.75 perturbation units per coordinate.

The Newton candidate is diagnostic only. It must not be accepted without a
new HFSS solve.

## Decision rule

1. If the step-normalized Jacobian retains four useful singular directions,
   keep the v3.4 topology and test the trust-limited Newton candidate.
2. If the fourth singular direction collapses, do not enlarge the Cartesian
   sweep. Add one genuinely local fifth control such as a rounded boss or
   partial-height post and re-identify the Jacobian.
3. Do not introduce tuning bolts until the passive structure has progressed
   through the staged 10 dB, 15 dB and approximately 20 dB return-loss gates.
