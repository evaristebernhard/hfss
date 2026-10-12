# Refactor HFSS regression — 2026-10-12

The unified cell and four-way tree builders were solved with Ansys Electronics Desktop **2025.2 Student** and PyAEDT **1.6.0**. Their complex Touchstone matrices were compared element by element with the retained nominal v7 HFSS results over the common 9–11.5 GHz band.

| Model | Points | Reference | Maximum complex-S error | RMS error | Result |
|---|---:|---|---:|---:|---|
| Cell, 4-port | 101 | `v7_stepped_post_local/joint_l1p4_s6p2/single_magictee_v4_full.s4p` | 0.0 | 0.0 | Pass |
| Four-way tree, 8-port | 51 | `v7_four_way_3d_optimized/four_way_magictee_v6_3d.s8p` | 0.0 | 0.0 | Pass |

The configured maximum error bound was 0.02. The rebuilt Touchstone files are `magictee_cell.s4p` and `magictee_tree.s8p`; `comparison.json` records paths, SHA-256 hashes, software versions, and metrics. The retained reference files were not modified.

This is a nominal PEC solver regression check. It does not establish conductor loss, thermal performance, breakdown limits, or high-power operation.
