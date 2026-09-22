# v3.2 proposed engineering requirements

## Final customer-facing requirements to retain provisionally

| Item | Proposed final requirement |
|---|---|
| Frequency band | 9.0--11.5 GHz |
| Return loss | >=22 dB over band |
| Isolation | >=22 dB over band after tolerances |
| Peak RF power | >=30 kW |
| Continuous average RF power | >=1 kW |
| Four-way RF combining efficiency | >=95%, pending definition confirmation |
| Compactness | customer envelope required |

## Internal design targets

| Item | Internal target |
|---|---|
| Nominal isolation | >=30 dB |
| Passive-geometry RL before residual tuning | >=20 dB |
| Final nominal RL | >=22 dB |
| H junction transmission before remote tuning | >=0.85 amplitude, preferably >=0.90 |
| Peak-field enhancement | preferred <=2; review 2--3 |
| Nominal amplitude imbalance per tee | <=0.2 dB |
| Nominal phase imbalance per tee | <=3 deg |
| Added matching length per side arm | soft target <= ~19 mm unless justified |

## Required metric definitions

### Return loss

Evaluate in the parity basis and physical-port basis at common de-embedded reference planes.

### Isolation

Report both nominal symmetry isolation and tolerance-degraded isolation.

### Efficiency

Report separately:

1. mismatch / modal combining efficiency in PEC;
2. conductor-loss efficiency of one tee;
3. total RF efficiency of the complete four-way cascade.

Do not use one number called "efficiency" for all three.

### Power

Peak power and continuous average power are separate qualification problems.

Peak power requires local E/H field and breakdown-margin analysis.

Continuous average power requires conductor loss and thermal boundary conditions.

## Stage gates

- Gate 0: correct parity and no geometry failure.
- Gate 1: new topology improves its intended modal block.
- Gate 2: full-band RL >=10 dB.
- Gate 3: full-band RL >=15 dB.
- Gate 4: passive full-band RL >=20 dB.
- Gate 5: tuned nominal RL >=22 dB.
- Gate 6: finite-conductivity efficiency and 30 kW field validation.
- Gate 7: 1 kW CW thermal validation.
- Gate 8: tolerance + complete four-way cascade validation.

The current project is between Gate 1 and Gate 2 for H, and between network synthesis and Gate 1 for E.
