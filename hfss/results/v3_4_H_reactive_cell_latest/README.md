# v3.4 H-reactive-cell latest solve

Generated on 2026-09-22 from branch
`origin/analysis/v3-4-h-reactive-cell` using
`build_single_magictee_v3_4_hreactive.py --solve` with AEDT Student 2025.2.4.

Parameters:

- H throat: `a = 20.4 mm`, `L = 5.5 mm`
- capacitive cell: `height = 9.0 mm`, `length = 2.5 mm`
- terminal ridge: `w/g/L = 4.572 / 5.8 / 7.5 mm`
- band: `9.0--11.5 GHz`, 101 points

## Modal result

| Metric | Result |
|---|---:|
| c+ worst modal return loss | 2.663 dB at 9.0 GHz |
| c− worst modal return loss | 5.431 dB at 11.5 GHz |
| c+ → H minimum coupling | −3.388 dB at 9.0 GHz |
| c− → E minimum coupling | −1.465 dB at 11.5 GHz |
| worst forbidden parity coupling | −48.728 dB at 11.375 GHz |

The solve completed normally and exported `single_magictee_v3_4_hreactive.s4p`.
This structural candidate does not yet meet the 22 dB return-loss target.
