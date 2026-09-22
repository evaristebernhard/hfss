# v3.4 R #11 Jacobian simulation

Generated from `origin/analysis/v3-4-jacobian-program` at commit `4ff1979`.
The eight central-difference perturbation cases were solved with AEDT Student
2025.2 / PyAEDT 1.6.0, PEC walls, 9.0--11.5 GHz, 101 points. The committed
center S4P was reused from `v3_4_H_reactive_cell_latest`.

## Center result

| Metric | Result |
|---|---:|
| c+ worst return loss | 2.663 dB @ 9.0 GHz |
| c− worst return loss | 5.431 dB @ 11.5 GHz |
| c+ → H minimum coupling | −3.388 dB, 0.677 linear @ 9.0 GHz |
| c− → E minimum coupling | −1.465 dB @ 11.5 GHz |
| worst forbidden parity coupling | −48.728 dB @ 11.375 GHz |

The center model fails the 22 dB return-loss target and the staged H-coupling
gate (`|t_H| >= 0.85`, preferred `>= 0.90`), while the parity-leakage gate
(`<= -30 dB`) passes.

## Jacobian result

Feature vector:

`[Re(Gamma_H(f0)), Im(Gamma_H(f0)), Re(dGamma_H/df), Im(dGamma_H/df)]`,
with `f0 = 10.25 GHz` and half-steps `[0.4, 1.0, 0.4, 0.5] mm`.

- step-normalized singular values: `0.164612, 0.072303, 0.002146, 0.000390`
- numerical rank: `4`
- effective rank at 5%: `2`; at 1%: `3`
- condition number: `421.6`
- `sigma_min / sigma_max`: `0.00237`

The controls are formally full-rank but poorly conditioned; the fourth
direction has effectively collapsed. The unconstrained Newton step is
`[+145.0, -70.6, +616.1, -193.3]` half-step units and is nonphysical. The
trust-limited candidate `[20.7, 4.75, 9.3, 4.197] mm` is diagnostic only and
was not accepted or re-solved.

## Decision

Do not enlarge the existing Cartesian sweep or introduce tuning bolts yet.
Add one genuinely local fifth H-control (for example a rounded boss or
partial-height post), re-identify the Jacobian, and only then test a new
candidate. The eight Touchstone files, exact run manifest, and machine-readable
analysis are in this directory.
