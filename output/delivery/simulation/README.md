# HFSS calculation results

This directory contains selected, reproducible calculation artifacts intended
for later theoretical analysis. Large AEDT result databases are excluded.

The current baseline uses:

- WR90: `a=22.86 mm`, `b=10.16 mm`
- band: `9.0--11.5 GHz`
- common ridge width: `4.572 mm`
- `g1/L1 = 7.672/9.872 mm`
- `g2/L2 = 4.984/8.857 mm`
- wave-port renormalization disabled, so the exported result remains in the
  waveguide modal normalization rather than being forced to 50 ohms

These are first-pass single magic-tee results, not hardware-qualified results.
