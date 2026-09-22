# v3 builder checklist — BLOCKED pending v3.1 synthesis

Do not implement the old v3 seed.

## Safe items to copy from v2

- coordinate convention;
- four wave-port definitions;
- parity-correct E-arm orientation;
- 9--11.5 GHz sweep;
- modal parity post-processing;
- existing solved v2 geometry as the comparison baseline.

## Do not copy from old v3

Do not implement as defaults:

- the old E two-section low-impedance ridge matcher;
- the H iris at offset 8.5 mm inside the existing taper;
- the interpretation of (r_-) as a scalar E-side load.

## Required before builder work resumes

1. compute complete de-embedded H/E 2-port modal blocks;
2. synthesize the E network using the required load reflection (Gamma_{L,E}^{*});
3. choose H-A junction step or H-B dedicated-throat cancelling iris;
4. issue a new machine-readable v3.1 seed;
5. then create `hfss/build_single_magictee_v3.py`.

The current repository should continue using v2 for all solved comparisons until these steps are complete.
