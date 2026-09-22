# HFSS v3 design revision — theory-audit status

## STATUS: HOLD FOR v3.1 SYNTHESIS

Do **not** implement the previously documented v3 E double-ridge matcher as the default geometry.

The second theory audit found that the E-side transformer was synthesized from the wrong scalar quantity. See:

- `docs/v3_theory_audit.md`

The parity-corrected v2 geometry and Stage-A data remain valid.

## Valid design conclusions

- keep the v2 E-arm orientation;
- preserve X-mirror symmetry;
- stop the standalone `g2/Lt` Stage-A sweep;
- design H and E matching mechanisms separately;
- keep `g2=5.8 mm, Lt=7.5 mm` only as an empirical Stage-A reference, not as a final v3 baseline.

## E side

The old default values

- `wE=6.858 mm`
- `gE_near=4.299 mm`
- `LE_near=9.228 mm`
- `gE_outer=6.544 mm`
- `LE_outer=10.392 mm`

are **withdrawn as implementation defaults**.

The new E target is the required junction-plane termination

[
Gamma_{L,E}^{*}
=
-rac{S_{--}}
{S_{-E}S_{E-}-S_{--}S_{EE}}.
]

The next E geometry must be synthesized to approximate this complex trajectory.

## H side

The old iris coordinates `offset=8.5 mm, thickness=3 mm` overlap the current ridge taper and therefore do not define a clean separate iris cell.

Choose one clean H topology before coding:

- H-A: compact junction step/boss;
- H-B: symmetric cancelling iris in a dedicated ordinary-guide throat.

Do not mix the iris into the taper unless the hybrid cross section is intentionally treated as a new full-wave topology.

## Builder status

`hfss/build_single_magictee_v3.py` is **not yet authorized by the theory model**.

The next coding input must come from a v3.1 synthesis document after H-A/H-B and the corrected E network are selected.
