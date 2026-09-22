# v3.3 H-junction candidate baseline

This is the first full-wave solve of the new v3.3 H-junction candidate from
`design/seed_v3_3_H_candidate.json`.

Parameters:

- H throat broad dimension: `18.8 mm`
- H throat length: `5.5 mm`
- terminal ridge width: `4.572 mm`
- terminal ridge gap/length: `5.8 mm / 7.5 mm`
- band: `9.0--11.5 GHz`, 101 points

## Modal result

| Metric | Result |
|---|---:|
| H return loss, worst band point | 2.098 dB |
| E return loss, worst band point | 5.268 dB |
| H coupling at 9.0 GHz | -4.167 dB |
| H coupling at 11.5 GHz | -2.099 dB |
| E coupling, worst band point | -1.532 dB |
| Worst forbidden parity coupling | -63.034 dB |

Compared with the v2 Stage-A best case, H coupling changes from
`-2.106/-5.971 dB` at `9.0/11.5 GHz` to `-4.167/-2.099 dB`. The new throat
therefore supplies the intended high-frequency correction direction, but the
minimum H transmission is still only `0.619`, below the v3.3 structural gate
of `0.85`. The next sensitivity study should vary throat width, throat length,
and terminal ridge width around this candidate.

The AEDT project remains at:

`C:\Users\chaoy\Documents\single_magictee_v3_3_H_candidate_baseline`
