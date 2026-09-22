# v4 local-control identification

Solved with AEDT Student 2025.2SV, PEC walls, 9.0--11.5 GHz, 101 points.
The three screws were fully retracted for every case.

Center geometry:

- rounded partial-height post pair: radius 1.5 mm, height 0.7 mm;
- post axis: 2.0 mm from the H-plane junction mouth;
- H throat: 20.4 mm × 5.5 mm;
- terminal ridge: 4.572 mm / 5.8 mm / 7.5 mm.

The original 1.5 mm post-axis seed was corrected to 2.0 mm because its
negative 0.5 mm perturbation intersected the junction volume.

## Center metrics

| Metric | Result |
|---|---:|
| c+ worst return loss | 2.770 dB @ 9.0 GHz |
| c− worst return loss | 5.406 dB @ 11.5 GHz |
| c+ → H minimum coupling | −3.265 dB |
| c− → E minimum coupling | −1.475 dB |
| worst forbidden coupling | −45.11 dB |

## Direction decision

The post-height and post-position columns increase the R11 smallest singular
value by only 2.23×, below the 5× direction gate. The augmented
sigma-min/sigma-max ratio is 0.00526, below the 0.01 screening target.

Decision: do not activate tuning bolts or perform a bolt sweep yet. Replace or
redesign the junction-local control before residual tuning; the current cell
is still far below the passive return-loss gate.

An additional radius probe at 1.0/2.0 mm was also solved. Its step-normalized
column raised the R11 smallest singular value by only 1.32×, with
sigma-min/sigma-max = 0.00312. Increasing or decreasing the post radius is
therefore not a useful missing control direction.

The Touchstone files were written from PyAEDT SolutionData because AEDT
2025.2SV's ExportNetworkData call reported the solved sweep as unavailable.
