# Paper direction: symmetry-protected modal controllability for a broadband Magic-T combiner

Date: 2026-10-01

## 1. Paper-level question

The useful scientific question is not:

> Which post dimensions give a better S11?

It is:

> Why does a symmetry-preserving stepped-post / throat / ridge architecture provide a better-conditioned set of controls for the two natural Magic-T parity channels, and how can those controls be separated into modal and spectral roles?

The proposed paper should therefore be written around **modal controllability**, not around a parameter sweep.

A compact working title is:

**Symmetry-Protected Modal Controllability for Broadband X-Band Magic-T Power Combining**

A more engineering-oriented title is:

**A Parity-Decoupled Stepped-Post Magic-T With Jacobian-Guided Broadband Matching**

The second title should only be used after the v8 central-difference identification confirms that the upper-post radius contributes a genuinely non-redundant odd/E control direction at the final seed.

---

## 2. Core contribution chain

The paper should make four connected claims.

### Claim A: symmetry gives an exact modal decomposition

Let P exchange the two collinear ports. For an ideal mirror-symmetric geometry, the Maxwell operator and the scattering operator commute with P,

\[
[\mathcal L,P]=0,\qquad [S,P]=0.
\]

The collinear excitation space therefore decomposes into the two irreducible parity states

\[
c_+=\frac{P_1+P_2}{\sqrt2},
\qquad
c_-=\frac{P_1-P_2}{\sqrt2}.
\]

In the basis \((c_+,c_-,H,E)\), the ideal symmetric Magic-T is block diagonal,

\[
S_{\rm modal}
\sim
(c_+,H)\oplus(c_-,E).
\]

The practical consequence is stronger than a conventional even/odd-mode explanation:

**symmetry-preserving geometry changes can change matching inside a parity block without creating first-order coupling between the parity blocks.**

This is the mathematical reason that forbidden parity leakage can stay very small while the matching geometry is being changed.

### Claim B: the stepped post increases modal control rank

Let the two modal reflections be

\[
\Gamma_+(f)=S_{\rm modal,11}(f),
\qquad
\Gamma_-(f)=S_{\rm modal,22}(f).
\]

For geometry parameters \(p=(p_1,\ldots,p_m)\), define the full-band real response vector

\[
F(p)=
\begin{bmatrix}
\Re\Gamma_+(f_1)\\
\Im\Gamma_+(f_1)\\
\vdots\\
\Re\Gamma_+(f_N)\\
\Im\Gamma_+(f_N)\\
\Re\Gamma_-(f_1)\\
\Im\Gamma_-(f_1)\\
\vdots\\
\Re\Gamma_-(f_N)\\
\Im\Gamma_-(f_N)
\end{bmatrix},
\qquad
J=\frac{\partial F}{\partial p}.
\]

For a uniform through-post, the lower and upper post perturbations are tied together. In the simplest linearized picture,

\[
\delta r_L=\delta r_U,
\qquad
\delta F=(j_L+j_U)\delta r,
\]

so only one geometric direction is available.

For a stepped post,

\[
\delta F=j_L\delta r_L+j_U\delta r_U.
\]

If \(j_L\) and \(j_U\) are not collinear, the reachable response space expands. This is the precise sense in which a stepped post can be superior to a uniform post.

The paper should quantify this with:

- singular values of \(J\);
- condition number \(\kappa(J)\);
- the even block \(J_+\);
- the odd block \(J_-\);
- pairwise acute angles between step-normalized columns;
- modal selectivity ratios

\[
\rho_i^{(+)}=
\frac{\|\partial\Gamma_+/\partial p_i\|}
     {\|\partial\Gamma_-/\partial p_i\|},
\qquad
\rho_i^{(-)}=
\frac{\|\partial\Gamma_-/\partial p_i\|}
     {\|\partial\Gamma_+/\partial p_i\|}.
\]

### Claim C: modal rank and spectral rank are different problems

A design may have enough independent directions to move \(\Gamma_+\) and \(\Gamma_-\) at one frequency and still fail over 9--11.5 GHz.

Around \(f_0\),

\[
\Gamma_\pm(f)
=
\Gamma_\pm(f_0)
+
\Gamma_\pm'(f_0)(f-f_0)
+
\frac12\Gamma_\pm''(f_0)(f-f_0)^2+\cdots.
\]

A local post is primarily a local reactive / resonant control and tends to move a small number of spectral features.

A throat or distributed ridge transformer changes local propagation and the accumulated reflection phase. A useful first-order distributed-reflection picture is

\[
\Gamma(f)
\approx
\frac12
\int
\frac{d\ln Z(z)}{dz}
\exp\left[
-2j\int_0^z\beta(\xi,f)\,d\xi
\right]dz.
\]

This gives a physically distinct set of frequency-dependent basis functions.

The architecture should therefore be presented as two-layer control:

1. **stepped local geometry -> modal rank**;
2. **throat/ridge distribution -> spectral rank**.

This distinction is one of the most useful conceptual contributions of the paper.

### Claim D: the four-way tree preserves the useful coherent mode

The binary tree is not merely a cascade of three junctions. Under equal electrical paths, it implements a hierarchical sum/difference transform.

For coherent equal inputs,

\[
a=\frac12[1,1,1,1]^T,
\]

the desired state is the global sum mode and the difference channels ideally vanish.

This explains why the existing full-3D cascade already gives very small amplitude/phase spread while its efficiency and active return loss remain poor: the **tree topology is largely correct; cell broadband matching remains the bottleneck.**

---

## 3. What the existing repository already proves

### 3.1 Symmetry separation is already strong

The repository repeatedly shows extremely small forbidden parity leakage compared with the desired H/sum and E/difference channels. This supports the use of the parity basis as the natural design basis rather than optimizing physical-port S11 alone.

The physical-port relations are

\[
S_{11}=\frac{\Gamma_++\Gamma_-}{2},
\qquad
S_{12}=\frac{\Gamma_+-\Gamma_-}{2},
\]

hence

\[
|S_{11}|^2+|S_{12}|^2
=
\frac{|\Gamma_+|^2+|\Gamma_-|^2}{2}.
\]

Therefore a small physical \(S_{11}\) can result from cancellation and is not by itself proof that both modal channels are matched.

### 3.2 The old R11 parameterization was practically singular

The earlier R11 local identification had step-normalized singular values approximately

\[
[0.1646,\;0.07230,\;0.002146,\;0.000390],
\]

with

\[
\kappa\approx422.
\]

This is the correct negative control experiment: several nominal geometry variables existed, but they produced almost redundant directions in electromagnetic response space.

### 3.3 v5 showed the single-resonance limitation

The uniform junction post could produce a high local peak but also generated edge/deep notches as the height increased. This is the signature expected from a predominantly single-resonant matching control: it can translate a zero or peak, but it does not provide enough independent spectral degrees of freedom for a 24.4% fractional bandwidth.

### 3.4 v6 showed that splitting the post matters physically

The v6 screen changed the upper and lower post radii separately. The resulting H/sum and E/difference efficiencies did not move together. This already indicates that the two portions of the post overlap differently with the two parity fields.

This is qualitative evidence for non-collinear geometry sensitivities.

### 3.5 v7 improved the four-way tree but did not solve the matching problem

The v7 final single-cell PEC result is approximately:

- H/sum efficiency: min 0.7801, mean 0.8699;
- E/difference efficiency: min 0.7038, mean 0.7746.

The v7 complete four-way PEC tree gives approximately:

- combining efficiency: min 50.17%, mean 78.34%, max 99.97%;
- active return loss: min 2.95 dB;
- input isolation: min 6.94 dB;
- network-to-full-3D RMS efficiency discrepancy: about 1.22 percentage points.

Relative to v6 full 3D, minimum efficiency increased by about 13.8 percentage points and average efficiency by about 6.1 percentage points, while isolation did not improve materially.

This is consistent with the hypothesis that the design gained useful matching freedom but still lacks sufficient broadband odd/E control.

---

## 4. Important correction to the current Jacobian result

A strict three-parameter central-difference calculation can already be made from the existing v7 local-screen data.

However, its center is

\[
(r_L,h_s,r_U,H)
=
(2.0,10.16,0.9,16.25)\ {\rm mm},
\]

**not** the final optimized v7 seed \((1.4,6.2,0.9,16.25)\) mm.

At this legacy center, using lower radius, split height, and total height, the full-band per-mm Jacobian has singular values approximately

\[
\sigma(J)
=
[4.3147,\;2.6554,\;0.6205],
\]

so

\[
\kappa(J)\approx6.95.
\]

The modal blocks give approximately

\[
\kappa(J_+)\approx7.06,
\qquad
\kappa(J_-)\approx74.4.
\]

At the same legacy center, total post height is strongly even-selective:

\[
\frac{\|J_{+,H}\|}{\|J_{-,H}\|}
\approx47.
\]

Interpretation:

- the old v7 local-screen center already contains a relatively well-conditioned even/H control subspace;
- the odd/E subspace is much more poorly conditioned;
- this is evidence for the *type* of missing freedom, but it must not be presented as the Jacobian of the final v7 seed.

The strict final-seed result is the purpose of v8.

---

## 5. The v8 experiment: only six new HFSS solves

Final center:

\[
(r_L,h_s,r_U,H)
=
(1.4,6.2,0.9,16.25)\ {\rm mm}.
\]

Existing repository cases already provide:

- center;
- \(r_L=1.6\) mm;
- \(h_s=7.2\) mm.

The six missing cases are:

1. \(r_L=1.2\) mm;
2. \(h_s=5.2\) mm;
3. \(r_U=0.7\) mm;
4. \(r_U=1.1\) mm;
5. \(H=15.50\) mm;
6. \(H=17.00\) mm.

Run:

    python hfss/run_v8_modal_controllability.py --skip-existing

Then analyze:

    python hfss/analyze_v8_modal_controllability.py

The analyzer automatically writes JSON, CSV, and a Markdown summary under

    hfss/results/v8_modal_controllability/

The decisive quantities are not just S11 or efficiency. They are:

\[
\sigma_{\min}(J_-),
\qquad
\kappa(J_-),
\qquad
\angle(j_{r_L},j_{r_U}),
\qquad
\rho_{r_U}^{(-)}.
\]

The stepped-post claim is supported if opening \(r_U\) produces a substantial new odd/E direction at the final seed.

---

## 6. Why a local geometry perturbation can be mode selective

A rigorous full shape-calculus derivation is not required for a short microwave paper, but the physical argument can be made mathematically precise.

For a small normal boundary displacement \(V_n\), a scattering observable has a first-order variation with Hadamard / adjoint structure,

\[
\delta S
=
\int_{\partial\Omega}
G_S(\mathbf r,\omega)
V_n(\mathbf r)\,dS,
\]

where \(G_S\) is a sensitivity density built from forward and adjoint electromagnetic fields.

Thus a geometry parameter is not characterized only by its scalar size. It is characterized by **where its boundary perturbation is supported**.

For the stepped post,

\[
\frac{\partial\Gamma_\pm}{\partial r_L}
=
\int_{\Sigma_L}
G_\pm V_L\,dS,
\qquad
\frac{\partial\Gamma_\pm}{\partial r_U}
=
\int_{\Sigma_U}
G_\pm V_U\,dS.
\]

Because the even/H and odd/E fields have different spatial parity and localization near the lower junction and upper E-arm region, these overlap integrals need not be proportional.

This is the field-theoretic explanation of modal selectivity.

For the paper, finite-difference Jacobians are enough to measure the effect. The adjoint/shape-sensitivity literature is used to justify the interpretation.

---

## 7. Relation to prior Magic-T work

The literature strongly supports the idea that broadband Magic-T matching needs physically distinct elements rather than one tuning post.

Useful anchors:

1. **W. Peng et al., "An 18–40 GHz Ridge Waveguide Magic-T Using Stepped Conducting T-Junction Transition," Electronics, 2024, 13, 2407. DOI: 10.3390/electronics13122407.**
   - 18--40 GHz ridge Magic-T;
   - E- and H-plane dividers are designed separately before combination;
   - stepped transitions and ridge-waveguide bandwidth are central.

2. **C. A. Leal-Sevillano et al., "Compact broadband couplers based on the waveguide magic-T junction," EuMC 2013.**
   - combines an E-port iris, H-port width step, junction post, and reduced-height sections;
   - reports designs covering a full standard waveguide band with more than 25 dB return loss.

3. **"An H-Plane Groove Gap Waveguide Magic-T for X-Band Applications," Electronics 2022, 11, 4075. DOI: 10.3390/electronics11244075.**
   - explicitly treats the Magic-T as coupled H-plane and E-plane T-junction design problems with different matching mechanisms.

4. **X. Zhu and N. K. Nikolova, "Accuracy Improvement of the S-parameter Adjoint Sensitivity Analysis for Shape Parameters," IEEE MTT-S IMS, 2009. DOI: 10.1109/MWSYM.2009.5165750.**
   - directly relevant to S-parameter shape sensitivities and central forward/backward perturbations.

5. **M. S. Dadash and N. K. Nikolova, "Analytical S-Parameter Sensitivity Formula for the Shape Parameters of Dielectric Objects," IEEE Microwave and Wireless Components Letters, 2014. DOI: 10.1109/LMWC.2014.2306891.**
   - useful mathematical precedent for interpreting geometry derivatives of S parameters.

The novelty should **not** be claimed as "first stepped-post Magic-T" or "first ridge Magic-T." Those structures already exist.

The potentially publishable novelty is instead:

> a parity-basis, full-band Jacobian/SVD framework that identifies which geometry parameters provide independent even/H and odd/E matching directions, and uses this controllability diagnosis to guide a high-power four-way Magic-T combiner.

A final novelty search is still required before using "first" language.

---

## 8. Recommended short-paper structure

### I. Introduction

Problem:
- broadband 9--11.5 GHz Magic-T combining;
- conventional local tuning gives narrow resonant improvement;
- blind multi-parameter optimization can be ill conditioned.

Gap:
- existing broadband designs use multiple matching features, but usually describe them geometrically;
- our design question is whether those features span independent electromagnetic response directions.

Contribution:
- parity decomposition;
- modal controllability Jacobian;
- stepped-post modal-rank interpretation;
- full-3D four-way validation.

### II. Parity decomposition and controllability formulation

Include:
- symmetry operator;
- \(c_+\), \(c_-\);
- block form;
- relation between physical \(S_{11},S_{12}\) and modal reflections;
- full-band Jacobian and SVD.

### III. Geometry and physical interpretation

Explain roles separately:

- lower post radius;
- upper post radius;
- split height;
- total height;
- H throat;
- ridge transformer.

Do not describe them as six arbitrary optimization variables.

Describe them as candidate **modal basis** and **spectral basis** controls.

### IV. Numerical identification

Show:
- old R11 condition number about 422;
- legacy v7 center three-parameter Jacobian;
- strict v8 final-seed four-parameter Jacobian;
- parameter selectivity table;
- sensitivity-column angle plot.

### V. Four-way combiner validation

Show:
- two-stage binary tree;
- network model versus complete 3D;
- amplitude and phase balance;
- combining efficiency;
- active return loss;
- isolation.

The key argument is that network/full-3D agreement validates the topology and leaves cell matching as the dominant unresolved problem.

### VI. Discussion

Separate:
- modal rank;
- spectral rank;
- power handling not yet validated.

### VII. Conclusion

Do not claim final 22 dB compliance unless later simulations achieve it.

---

## 9. Figures that will make the paper work

Only a small number are needed.

### Fig. 1
Magic-T geometry with the lower and upper post regions highlighted separately.

### Fig. 2
Parity decomposition diagram:

\[
(P_1,P_2)\rightarrow(c_+,c_-)
\]

and the two blocks

\[
(c_+,H),\quad(c_-,E).
\]

### Fig. 3
Complex-plane trajectories of \(\Gamma_+(f)\) and \(\Gamma_-(f)\) over 9--11.5 GHz.

Overlay small geometry perturbations as arrows at selected frequencies.

### Fig. 4
Normalized Jacobian column correlation / angle matrix.

This is probably the most important new figure.

### Fig. 5
Singular-value comparison:

- R11;
- legacy v7 local center;
- final-seed v8.

### Fig. 6
Four-way network versus full-3D efficiency, plus amplitude/phase balance.

A short paper can probably stop at six figures.

---

## 10. Claims that are currently safe and unsafe

### Safe now

- parity decomposition is the natural basis of a symmetric Magic-T;
- physical-port cancellation alone is not sufficient to prove modal matching;
- old R11 controls were severely ill conditioned;
- a uniform post exhibits a narrow-resonance tradeoff in the current design;
- splitting the post produces measurably different H/even and E/odd responses;
- four-way network and full-3D results agree closely enough to validate the cascade topology;
- the current bottleneck is broadband cell matching rather than tree phasing.

### Wait for v8

- the final v7 seed has a well-conditioned four-parameter modal Jacobian;
- upper radius is a strong independent odd/E knob at the final seed;
- stepped-post architecture formally improves the final-seed odd-mode controllability.

### Not established

- 22 dB return loss and isolation across the full band;
- 90% or 95% combining efficiency across the full band;
- 30 kW peak-power handling;
- breakdown, multipactor, thermal margin, conductor loss;
- experimental validation.

These should remain explicit limitations, not hidden in the paper.
