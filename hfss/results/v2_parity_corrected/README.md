# v2 parity-corrected baseline

Generated from `design/seed_v2.json` with `hfss/build_single_magictee_v2.py`.

Parameters:

- WR90: `22.86 x 10.16 mm`
- band: `9.0--11.5 GHz`
- `w=4.572 mm`, `g1/L1=7.672/9.872 mm`
- `g2/L2=4.984/8.857 mm`
- terminal ridge length: `6.0 mm`
- E arm: narrow dimension along X, broad dimension along Y
- wave ports: `renormalize=False`, `Zwave`

First full-wave result:

- `c-` minimum return loss: `5.343 dB`
- `c- <-> E` minimum desired coupling: `-1.501 dB`
- `c+` minimum return loss: `1.092 dB`
- `c+ <-> H` minimum desired coupling: `-6.529 dB`
- worst forbidden coupling: `-59.046 dB`

The parity correction is successful, but passive matching is not yet close to
the 22/25 dB targets. The next documented step is Stage A over `g2` and the
terminal ridge length.
