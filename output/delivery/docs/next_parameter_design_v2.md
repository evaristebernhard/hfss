# Magic-tee v2: parity diagnosis and next parameter design

## 1. Why the current v1 cannot be fixed by ridge tuning alone

The current four physical ports are

- P1, P2: the two collinear WR90 arms,
- P3: the H arm with the double-ridge taper,
- P4: the nominal E arm.

For a single magic tee the natural basis is not the four-vector Hadamard basis used by the v1 postprocessor.  The correct first reduction is

[
c_+ = rac{P_1+P_2}{sqrt 2},qquad
c_- = rac{P_1-P_2}{sqrt 2},
]

with H=P3 and E=P4 left unchanged.  In the ordered basis
((c_+,c_-,H,E)), an ideal reciprocal magic tee is approximately two
decoupled two-port channels,

[
c_+ leftrightarrow H,qquad c_- leftrightarrow E,
]

up to port phase conventions.

At 10.2 GHz the current baseline transforms approximately to

[
|S_m| approx
egin{pmatrix}
0.691 & 9.4	imes10^{-4} & 0.685 & 0.231\
9.4	imes10^{-4} & 0.999999 & 9.6	imes10^{-4} & 9.1	imes10^{-4}\
0.685 & 9.6	imes10^{-4} & 0.541 & 0.488\
0.231 & 9.1	imes10^{-4} & 0.488 & 0.842
end{pmatrix}.
]

The decisive number is

[
|S_{c_-c_-}|simeq 0.999999,
]

while both couplings from (c_-) into the side arms are below about -60 dB.
The odd collinear mode is therefore almost perfectly reflected.

This is a symmetry obstruction, not a small impedance error.

## 2. Geometry reason

The v1 E arm propagates along +Z but was built with

- broad dimension A along X,
- narrow dimension B along Y.

Its dominant TE10 electric field is then directed mainly along Y.  Under the
mirror operation X -> -X that exchanges P1 and P2, this port mode has even
electromagnetic parity.  It therefore cannot couple to the odd collinear
combination (c_-) in a symmetric junction.

The v2 E arm is rotated by 90 degrees about its propagation axis:

- narrow dimension B along X,
- broad dimension A along Y.

For a Z-propagating WR90 arm this makes the dominant electric field point along
X.  Under X -> -X the vector component changes sign, so this port carries the
required odd parity and coupling to (c_-) is symmetry-allowed.

The E-arm integration line is changed consistently from Y-directed to
X-directed.

## 3. What the existing parameter checks actually say

The current one-factor checks do not show a useful ridge optimum because the
junction dominates:

| case | min RL P1 | min RL P2 | min RL P3 | min RL P4 |
|---|---:|---:|---:|---:|
| baseline | 12.61 | 12.60 | 4.40 | 1.23 |
| g2=4.30 mm | 13.18 | 13.20 | 3.75 | 1.04 |
| g2=5.50 mm | 12.12 | 12.12 | 4.61 | 1.38 |
| L2=8.00 mm | 12.73 | 12.68 | 4.28 | 1.19 |
| w=4.00 mm | 12.58 | 12.51 | 4.43 | 1.24 |

Changing (w) or (L_2) barely moves the dominant mismatch.  Increasing
(g_2) slightly improves the H/E branch return loss, but the effect is much
smaller than the junction error.  Therefore the old sweep space

[
(w,g_1,g_2,L_1,L_2)
]

must not be treated as the primary optimization space until the E-arm parity is
correct.

## 4. v2 first run: isolate the geometry correction

The first v2 solve should keep the current ridge seed unchanged:

[
w=4.572	ext{ mm},quad
g_1=7.672	ext{ mm},quad
L_1=9.872	ext{ mm},
]
[
g_2=4.984	ext{ mm},quad
L_2=8.857	ext{ mm},quad
L_t=6.0	ext{ mm}.
]

Only rotate the E-arm cross section and its integration line.

This run is a structural acceptance test.  Before tuning any impedance
parameter, require the following qualitative behavior:

1. (c_-) is no longer almost perfectly reflected;
2. (c_-leftrightarrow E) becomes an allowed strong channel;
3. (c_+leftrightarrow E) and (c_-leftrightarrow H) remain small;
4. the H and E channels can then be matched independently to first order.

If condition 1 or 2 fails, do not start a numerical optimizer; inspect port
orientation and junction geometry first.

## 5. Correct optimization objective

Let

[
W=
egin{pmatrix}
1/sqrt2&1/sqrt2&0&0\
1/sqrt2&-1/sqrt2&0&0\
0&0&1&0\
0&0&0&1
end{pmatrix},
qquad
S_m = WSW^T.
]

Define the two desired channels

[
t_H=S_{H,c_+},qquad t_E=S_{E,c_-}.
]

The external 22 dB requirement corresponds to

[
|Gamma| < 10^{-22/20}=0.07943.
]

The internal 25 dB design target corresponds to

[
|Gamma| < 10^{-25/20}=0.05623.
]

A useful full-wave minimax objective is

[
J(p)=
max_{fin[9,11.5]}
maxleft{
|S_{c_+c_+}|,,
|S_{c_-c_-}|,,
|S_{HH}|,,
|S_{EE}|,,
|S_{c_+,E}|,,
|S_{c_-,H}|,,
|S_{HE}|,,
|S_{c_+,c_-}|
ight},
]

with a secondary penalty that drives (|t_H|) and (|t_E|) toward unity.

For the 97% internal efficiency target, the equivalent single-channel
magnitude target is roughly

[
|t|>sqrt{0.97}=0.9849
]

when mismatch, leakage and conductor loss are considered separately.

## 6. Next parameter space

### Stage A: corrected geometry, no new tuning element

Keep (w,g_1,L_1,L_2) fixed initially and use only

[
p_A=(g_2,L_t),
]

where (L_t) is the terminal g2 ridge length adjacent to the H-plane junction.

Recommended coarse region:

- g2: 4.6--6.0 mm,
- terminal ridge length Lt: 4.0--8.0 mm.

The reason for moving g2 upward rather than downward is twofold: the existing
checks show a weak improvement in branch match for larger g2, and the larger
gap is also favorable for peak-field margin.  This is only a search direction;
the corrected E arm changes the junction enough that the old g2 trend must be
re-measured.

Suggested first grid after the corrected baseline:

- g2 = 4.6, 5.0, 5.4, 5.8 mm,
- Lt = 4.5, 6.0, 7.5 mm.

Do not vary every ridge parameter at the same time.

### Stage B: local Jacobian fit

After Stage A identifies a reasonable region, estimate the complex residual
vector at several band frequencies,

[
r(p)=
left(
S_{c_+c_+},
S_{c_-c_-},
S_{HH},
S_{EE},
S_{c_+,E},
S_{c_-,H}
ight),
]

and finite-difference the Jacobian

[
A_{kj}=rac{partial r_k}{partial p_j}.
]

Then solve a bounded damped least-squares step

[
Delta p
=
argmin_{Delta p}
|W_r(ADelta p+r)|_2^2
+lambda|DDelta p|_2^2
]

subject to manufacturing and high-power bounds.

This is preferable to a blind high-dimensional sweep because it reveals which
geometric parameter actually controls each symmetry channel.

### Stage C: tuning bolts / iris only after passive geometry is reasonable

Only when the passive corrected tee reaches roughly 12--15 dB or better across
most of the band should tuning bolts be activated.

The bolt penetration remains a small residual-susceptance control.  A useful
initial region is still

- diameter 3 mm,
- penetration 0--2 mm,
- pair spacing 7.5--10 mm.

Do not use bolts to compensate for a parity or topology error.

## 7. High-power constraint

The 30 kW peak-power requirement makes small gaps and sharp metallic tips
expensive.  During optimization add a field penalty

[
J_E = max_f rac{E_{max,mathrm{junction}}}{E_{max,mathrm{straight,WR90}}}.
]

The existing first screening target (J_E<3) is retained.  Therefore any
candidate that gains return loss by forcing g2 much below about 4.5 mm should
be treated with suspicion until field scaling is checked.

## 8. Decision rule for the next HFSS run

The next run should answer exactly one question:

> After rotating the E arm to the correct WR90 orientation, does the odd
> collinear mode (c_-) couple strongly to the E arm?

If yes, proceed to the ((g_2,L_t)) coarse sweep and then Jacobian fitting.
If no, stop parameter tuning and re-check the junction topology and port modal
orientation.
