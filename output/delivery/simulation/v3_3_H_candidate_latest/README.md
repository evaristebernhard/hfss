# v3.3 H-candidate latest solve

Generated on 2026-09-22 with Ansys Electronics Desktop Student 2025.2.4
from `hfss/build_single_magictee_v3_hcandidate.py --solve`.

Parameters:

- H throat broad dimension: `18.8 mm`
- H throat length: `5.5 mm`
- terminal ridge width: `4.572 mm`
- terminal ridge gap/length: `5.8 mm / 7.5 mm`
- band: `9.0--11.5 GHz`, 101 points

## Modal result

| Metric | Result |
|---|---:|
| c+ worst modal return loss | 2.098 dB at 9.0 GHz |
| c− worst modal return loss | 5.268 dB at 11.5 GHz |
| c+ → H minimum coupling | −4.167 dB at 9.0 GHz |
| c− → E minimum coupling | −1.532 dB at 11.5 GHz |
| worst forbidden parity coupling | −63.034 dB at 11.5 GHz |

The solve completed normally and exported `single_magictee_v3_hcandidate.s4p`.
The candidate does not yet meet the 22 dB return-loss target.
