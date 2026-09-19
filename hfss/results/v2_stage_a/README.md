# v2 Stage-A sweep

This directory is populated by `hfss/run_v2_stage_a.py` using the latest v2
design note. The fixed parameters are the v2 baseline; the swept parameters
are:

- `g2 = 4.6, 5.0, 5.4, 5.8 mm`
- terminal ridge length `Lt = 4.5, 6.0, 7.5 mm`

Each case contains the exported S4P and its run log. `summary.json` is written
after all cases finish.

## Completed run

All 12 cases completed successfully at 9.0--11.5 GHz with 101 frequency
points. The sweep confirms that the v2 parity correction works: the forbidden
modal terms remain below -50 dB in every case. However, changing only `g2`
and `Lt` does not meet the matching/transfer targets in the design note.

| Criterion | Best case | Result |
|---|---|---:|
| c+ / H return loss | `g2=5.8, Lt=7.5 mm` | 1.266 dB |
| c+ -> H desired coupling | `g2=5.8, Lt=7.5 mm` | -5.971 dB |
| c- / E return loss | `g2=5.4, Lt=4.5 mm` | 5.402 dB |
| c- -> E desired coupling | `g2=5.4, Lt=4.5 mm` | -1.477 dB |
| Worst forbidden coupling | all cases | <= -50.0 dB |

Conclusion: the modal parity and isolation direction are now correct, but the
junction is still strongly mismatched. The next design iteration should add a
matching degree of freedom around the junction/iris/diaphragm; changing `g2`
and the terminal ridge length alone is insufficient. The raw results are in
`summary.json`, with one S4P and one log per case.
