# Modal-area and spectral-basis analysis

## Stepped-post reachable area

For the full-band lower- and upper-radius sensitivity columns,

[
\mathcal A_{LU}=\sqrt{\det(J_{LU}^T J_{LU})}
=\|j_L\|\,\|j_U\|\sin\theta_{LU}.
]

Numerical values:

- angle: **78.871 deg**
- lower full-band norm: **1.80506 per mm**
- upper full-band norm: **2.45536 per mm**
- Gram area: **4.34873 per mm^2**
- Gram determinant: **18.91146 per mm^4**
- step-normalized area: **0.173949**
- uniform-post two-dimensional area: **0**

The uniform-post constraint `dr_L = dr_U` collapses this two-control plane to one direction, so its 2-D reachable area is zero.

## Discrete Legendre spectral energy

Energy fractions for orders k=0,1,2, and k>=3:

| control | mode | k=0 | k=1 | k=2 | k>=3 |
|---|---|---:|---:|---:|---:|
| r_L | even | 0.336 | 0.146 | 0.304 | 0.215 |
| r_L | odd | 0.101 | 0.531 | 0.300 | 0.067 |
| h_s | even | 0.272 | 0.160 | 0.301 | 0.266 |
| h_s | odd | 0.097 | 0.541 | 0.299 | 0.063 |
| r_U | even | 0.100 | 0.551 | 0.290 | 0.059 |
| r_U | odd | 0.037 | 0.467 | 0.379 | 0.118 |
| H | even | 0.086 | 0.616 | 0.280 | 0.018 |
| H | odd | 0.002 | 0.348 | 0.450 | 0.200 |

Interpretation: the local post controls are not merely broadband-offset knobs. Their sensitivities contain substantial slope-like and curvature-like content, especially in the odd/E block. However, these spectral shapes remain structured and correlated, motivating distributed throat/ridge controls for additional broadband shaping.
