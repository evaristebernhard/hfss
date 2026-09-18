# Analytic baseline: 9–11.5 GHz four-way magic-tee combiner

## 1. Scope and status

This note develops an analytic starting point for a four-way X-band coherent power combiner built from cascaded magic tees, WR90-class waveguide, impedance-transforming/ridged transitions, and optional tuning bolts.

The calculations below are intended to:

- define the correct multiport target;
- establish useful frequency/length scales;
- quantify amplitude/phase error sensitivity;
- provide a reduced two-section matching seed;
- define what must be extracted from HFSS before assigning ridge dimensions;
- define high-power screening metrics.

They are **not** a substitute for the final 3-D full-wave solution.

---

## 2. Requirements

External specification:

\[
f \in [9,11.5]\ \mathrm{GHz},
\]

\[
RL > 22\ \mathrm{dB},
\]

\[
Isolation > 22\ \mathrm{dB},
\]

\[
\eta_{comb} > 95\%,
\]

with

\[
P_{peak}>30\ \mathrm{kW},
\qquad
P_{CW}>1\ \mathrm{kW}.
\]

The arithmetic center is

\[
f_{arith}=10.25\ \mathrm{GHz},
\]

and the fractional bandwidth is

\[
FBW=\frac{11.5-9}{10.25}=24.39\%.
\]

This is a genuinely broadband matching problem; tuning bolts should be treated as residual-reactance controls, not as the primary mechanism that creates the full bandwidth.

---

## 3. WR90 baseline and modal window

Use nominal WR90 internal dimensions

\[
a=22.86\ \mathrm{mm},
\qquad
b=10.16\ \mathrm{mm}.
\]

For a rectangular waveguide,

\[
f_{c,mn}
=
\frac{c}{2}
\sqrt{
\left(\frac{m}{a}\right)^2+
\left(\frac{n}{b}\right)^2
}.
\]

Numerically,

- \(f_{c,10}=6.55714\) GHz,
- \(f_{c,20}=13.11428\) GHz,
- \(f_{c,01}=14.75357\) GHz,
- \(f_{c,11}=16.14509\) GHz.

Therefore the straight WR90 feed sections remain below the first higher-order rectangular-waveguide cutoff throughout 9–11.5 GHz. The dominant concern is not straight-guide multimoding, but local excitation of evanescent/higher-order content inside the magic-tee junction, ridge transition, steps, and tuning-bolt regions.

For TE10,

\[
\beta(f)
=
\frac{2\pi f}{c}
\sqrt{1-\left(\frac{f_{c,10}}{f}\right)^2},
\]

\[
\lambda_g=\frac{2\pi}{\beta},
\]

and the TE wave impedance is

\[
Z_{TE}=\frac{\eta_0}
{\sqrt{1-(f_{c,10}/f)^2}}.
\]

Representative values:

| frequency | \(\lambda_g\) | \(\lambda_g/4\) | \(Z_{TE}\) |
|---:|---:|---:|---:|
| 9.00 GHz | 48.630 mm | 12.158 mm | 549.995 ohm |
| 10.25 GHz | 38.053 mm | 9.513 mm | 490.147 ohm |
| 11.50 GHz | 31.733 mm | 7.933 mm | 458.580 ohm |

The large change in quarter guided wavelength across the band explains why a single narrowband quarter-wave correction is not an adequate broadband strategy.

### 3.1 Dispersion-symmetric electrical center

For a physical length \(L\), choose the two band-edge electrical lengths symmetric about \(\pi/2\):

\[
\beta(9)L+\beta(11.5)L=\pi.
\]

This gives

\[
\boxed{L=9.60125\ \mathrm{mm}}
\]

and

\[
\theta(9)=71.0761^\circ,
\qquad
\theta(11.5)=108.9239^\circ.
\]

The corresponding electrical center is

\[
\boxed{f_{ec}=10.19465\ \mathrm{GHz}},
\]

slightly below the arithmetic center because of waveguide dispersion.

For initial parametric models, \(10.20\) GHz is therefore a better nominal electrical center than blindly using 10.25 GHz.

---

## 4. Ideal magic-tee and four-way coherent transform

With the two collinear arms used as the pair inputs, an ideal magic tee performs a sum/difference transform. For one pair,

\[
s_A=\frac{a_1+a_2}{\sqrt2},
\qquad
d_A=\frac{a_1-a_2}{\sqrt2}.
\]

A second first-stage tee gives

\[
s_B=\frac{a_3+a_4}{\sqrt2},
\qquad
d_B=\frac{a_3-a_4}{\sqrt2}.
\]

A final tee combines \(s_A,s_B\):

\[
b_{\Sigma}
=
\frac{a_1+a_2+a_3+a_4}{2},
\]

\[
b_{\Delta3}
=
\frac{a_1+a_2-a_3-a_4}{2}.
\]

Thus the complete ideal transform is

\[
\begin{bmatrix}
b_\Sigma\\
b_{\Delta1}\\
b_{\Delta2}\\
b_{\Delta3}
\end{bmatrix}
=
\begin{bmatrix}
1/2&1/2&1/2&1/2\\
1/\sqrt2&-1/\sqrt2&0&0\\
0&0&1/\sqrt2&-1/\sqrt2\\
1/2&1/2&-1/2&-1/2
\end{bmatrix}
\begin{bmatrix}
a_1\\a_2\\a_3\\a_4
\end{bmatrix}.
\]

The transform is unitary, so

\[
\sum_{i=1}^4|a_i|^2
=
|b_\Sigma|^2
+
|b_{\Delta1}|^2
+
|b_{\Delta2}|^2
+
|b_{\Delta3}|^2.
\]

For equal coherent inputs,

\[
a_1=a_2=a_3=a_4=A,
\]

all differential outputs vanish and

\[
b_\Sigma=2A.
\]

This is the primary architecture-level correctness check for the HFSS model.

---

## 5. Combining efficiency and amplitude/phase imbalance

For arbitrary complex input amplitudes,

\[
\boxed{
\eta_{comb}
=
\frac{
\left|a_1+a_2+a_3+a_4\right|^2
}{
4\sum_{i=1}^4|a_i|^2
}
}
\]

for the ideal lossless unitary combiner.

For small amplitude and phase errors,

\[
a_i=(1+\delta_i)e^{j\phi_i},
\]

after removing common amplitude and common phase, a useful second-order approximation is

\[
\eta_{comb}
\approx
1-\operatorname{Var}(\delta)-\operatorname{Var}(\phi).
\]

Thus a 95% efficiency requirement alone is not especially restrictive on phase balance; the 22 dB isolation/difference-mode requirement is normally tighter.

### 5.1 Pairwise phase-error limit from 22 dB difference suppression

For equal-amplitude pair inputs separated by phase \(\phi\),

\[
\frac{P_\Delta}{P_\Sigma}
=
\tan^2\frac{\phi}{2}.
\]

Requiring

\[
\frac{P_\Delta}{P_\Sigma}<10^{-22/10}
\]

gives

\[
\boxed{|\phi|<9.08^\circ}.
\]

This is a mathematical limit, not a recommended internal target.

A practical internal target should be tighter, for example

\[
\boxed{\Delta\phi<5^\circ}
\]

over the full band after de-embedding equal reference planes.

### 5.2 Pairwise amplitude-error limit

With zero phase error and amplitude ratio \(r\),

\[
\frac{P_\Delta}{P_\Sigma}
=
\left(\frac{1-r}{1+r}\right)^2.
\]

A 22 dB suppression limit alone permits approximately

\[
0.853<r<1.173,
\]

or about \(\pm 1.38\) dB.

Again, this is only the mathematical boundary. A more useful internal full-wave target is approximately

\[
\boxed{\Delta A<0.3\ \mathrm{dB}}.
\]

---

## 6. Important correction: do not identify the magic-tee junction with a literal scalar 2:1 load

It is tempting to argue that two equal combining branches are simply “parallel,” hence the next stage sees

\[
Z_L=Z_0/2.
\]

That is not a rigorous model of a magic-tee junction.

Reasons:

1. a magic tee is a 3-D multiport waveguide discontinuity;
2. HFSS wave ports use modal/power-wave normalization;
3. the TE wave impedance \(Z_{TE}=\omega\mu/\beta\) is not, by itself, a unique transmission-line characteristic impedance for arbitrary discontinuity matching;
4. ridge sections change modal field distribution, cutoff, propagation constant, and impedance definition simultaneously;
5. the junction reactance and higher-order evanescent modes are part of the match.

Therefore the reduced 2:1 model below must be treated as a **conditional seed only**.

The correct production sequence is to extract/de-embed the actual junction behavior first, then design the ridge/transformer around that extracted load.

---

## 7. Conditional two-section matching seed

Assume, only for the reduced model,

\[
Z_0=1,
\qquad
Z_L=0.5,
\]

and two lossless transformer sections. Recursively,

\[
Z_{in,k}
=
Z_k
\frac{
Z_{in,k+1}+jZ_k\tan\theta_k
}{
Z_k+jZ_{in,k+1}\tan\theta_k
},
\]

with

\[
\Gamma(f)=\frac{Z_{in}(f)-1}{Z_{in}(f)+1}.
\]

### 7.1 Binomial seed

A two-section binomial transformer for the 2:1 ratio gives approximately

\[
Z_1/Z_0=0.84090,
\qquad
Z_2/Z_0=0.59460.
\]

Using \(L_1=L_2=9.60125\) mm and the WR90 TE10 phase law gives a useful broadband starting point.

### 7.2 Minimax/equal-ripple seed

Direct minimization of

\[
\max_{f\in[9,11.5]\,GHz}|\Gamma(f)|
\]

for two equal-length sections gives

\[
\boxed{Z_1/Z_0=0.832686}
\]

\[
\boxed{Z_2/Z_0=0.600466}
\]

\[
\boxed{L_1=L_2=9.60125\ \mathrm{mm}}.
\]

For this reduced model,

\[
\boxed{RL_{min}\approx34.15\ \mathrm{dB}}
\]

with an approximately equal-ripple worst case near the two band edges and the central ripple peak.

This result is useful because it provides margin over the required 22 dB **inside the reduced model**. It must not be interpreted as a predicted HFSS return loss.

### 7.3 Reduced-model sensitivity

Single-parameter perturbations around the minimax seed:

| perturbation | worst in-band RL |
|---|---:|
| \(Z_1+1\%\) | 30.85 dB |
| \(Z_1-1\%\) | 30.55 dB |
| \(Z_2+1\%\) | 30.58 dB |
| \(Z_2-1\%\) | 30.82 dB |
| \(L_1+0.5\) mm | 29.16 dB |
| \(L_1-0.5\) mm | 30.76 dB |
| \(L_2+0.5\) mm | 29.16 dB |
| \(L_2-0.5\) mm | 30.76 dB |

A corner sweep with simultaneous \(\pm2\%\) perturbations of the two effective section impedances reduces the worst case to about

\[
24.50\ \mathrm{dB},
\]

while \(\pm3\%\) corners can fall to approximately

\[
22.00\ \mathrm{dB}.
\]

This is a useful message for geometry extraction: if the final ridge sections are being designed by an equivalent-impedance map, a few-percent error in the effective impedance is enough to consume the entire return-loss margin.

---

## 8. How to map the analytic seed into a ridged waveguide

Do **not** convert \(0.832686 Z_0\) and \(0.600466 Z_0\) directly into ridge gap by an ad-hoc formula.

Instead build a separate uniform-ridge cross-section study in HFSS.

For each candidate ridge geometry

\[
\mathbf q=(w_r,g,h_r,\ldots),
\]

extract at least

\[
\beta(f,\mathbf q),
\qquad
Z_{mode}(f,\mathbf q),
\qquad
f_{c,1}(\mathbf q),
\qquad
f_{c,2}(\mathbf q).
\]

The exact impedance quantity must be kept consistent between all sections and the de-embedded junction. For non-TEM waveguides, “wave impedance,” “voltage/current characteristic impedance,” and HFSS port-normalized impedance are not automatically interchangeable.

The geometry selection should then solve, approximately,

\[
Z_{mode}(f_{ec},\mathbf q_1)
\approx
Z_1,
\]

\[
Z_{mode}(f_{ec},\mathbf q_2)
\approx
Z_2,
\]

while also keeping the next higher mode safely above 11.5 GHz and avoiding an excessively small ridge gap.

### 8.1 Why a smooth ridge transition is preferred

A continuous impedance profile reduces distributed reflection. In the small-reflection approximation,

\[
\Gamma(\beta)
\approx
\frac12
\int_0^L
\frac{d\ln Z}{dz}
e^{-j2\beta z}\,dz.
\]

This shows directly why a smooth taper is broadband: the local reflections are distributed and can cancel in phase.

A practical parameterization can start from a smoothstep or cubic profile rather than a hard staircase,

\[
t=z/L,
\]

\[
s(t)=3t^2-2t^3,
\]

and map

\[
g(z)=g_0+(g_1-g_0)s(t),
\]

with a similar expression for ridge width if both quantities are varied.

For the present band, a first search region of roughly

\[
L_{ridge}\sim18\text{–}22\ \mathrm{mm}
\]

is physically sensible, but this is only a starting range. The full-wave optimization decides the final value.

---

## 9. Tuning-bolt role

A tuning bolt should be modeled as a local reactive perturbation,

\[
Y_s\approx jB_s(f,x,d,r_{tip},\ldots).
\]

Its primary role is to cancel residual junction susceptance and flatten ripple after the broadband transformer/ridge geometry is already close.

Recommended order of design:

1. optimize the bare magic-tee junction;
2. add the broadband ridge/impedance transition;
3. only then introduce one tuning bolt;
4. add a second bolt only if the first cannot meet the full-band requirement without excessive field concentration.

More bolts increase optimization freedom but also add:

- local electric-field enhancement,
- conductor-current concentration,
- manufacturing tolerance sensitivity,
- possible narrow resonances,
- extra thermal hot spots.

---

## 10. Peak-power scaling

For TE10 in a rectangular waveguide,

\[
P
=
\frac{ab}{4Z_{TE}}E_{max}^2.
\]

At 10.25 GHz in WR90,

\[
Z_{TE}\approx490.147\ \Omega.
\]

Representative ideal straight-guide field levels are:

- 7.5 kW: \(E_{max}\approx0.252\) MV/m,
- 15 kW: \(E_{max}\approx0.356\) MV/m,
- 30 kW: \(E_{max}\approx0.503\) MV/m,
- 1 kW: \(E_{max}\approx0.0919\) MV/m.

For a four-way 30 kW output, the last-stage junction/output region therefore deserves the most stringent field-hot-spot check.

Define a local enhancement factor

\[
K_E=
\frac{E_{local,max}}
{E_{straight,TE10}}.
\]

A useful **screening target** for early optimization is

\[
\boxed{K_E<3}.
\]

This is not a hardware breakdown qualification limit. Actual RF breakdown depends on gas pressure, surface condition, pulse width, contamination, edge radius, gap size, and other factors.

Sharp bolt tips and tiny ridge gaps should therefore be avoided even if they improve S-parameters.

---

## 11. CW conductor-loss quantities

For copper conductivity

\[
\sigma\approx5.8\times10^7\ \mathrm{S/m},
\]

at 10.25 GHz,

\[
\delta
=
\sqrt{\frac{2}{\omega\mu_0\sigma}}
\approx
0.653\ \mu\mathrm{m},
\]

and

\[
R_s
=
\sqrt{\frac{\pi f\mu_0}{\sigma}}
\approx
0.0264\ \Omega.
\]

The 1 kW CW requirement should therefore be checked with finite-conductivity walls and surface-loss density, not PEC alone.

Particular hot spots:

- magic-tee junction corners,
- ridge edges,
- tuning-bolt contact region,
- flange/contact surfaces,
- any narrow current-return path.

The final CW assessment should export conductor loss into a thermal model or at least bound the local temperature rise.

---

## 12. Recommended internal HFSS targets

The contractual limits are 22 dB / 22 dB / 95%. The design model should aim higher to preserve tolerance margin.

Suggested internal targets:

\[
RL>25\ \mathrm{dB},
\]

\[
Isolation>25\ \mathrm{dB},
\]

\[
\eta_{comb}>97\%,
\]

\[
\Delta A<0.3\ \mathrm{dB},
\]

\[
\Delta\phi<5^\circ,
\]

and, as an early peak-power screen,

\[
K_E<3.
\]

All amplitude/phase comparisons must use equal de-embedded reference planes.

---

## 13. HFSS work sequence

### Phase A — single magic tee

Build one tee first.

Outputs to save:

- all S-parameters over at least 8.5–12 GHz;
- sum-port insertion balance;
- difference-port leakage;
- port-to-port isolation;
- field maps at 9, 10.2, and 11.5 GHz;
- junction input impedance/admittance after de-embedding.

### Phase B — uniform ridge extraction

Sweep ridge geometry separately.

Create a table

\[
(w_r,g,\ldots)
\mapsto
(\beta,Z_{mode},f_{c1},f_{c2},K_E).
\]

This table is the correct bridge from analytic impedance targets to physical ridge dimensions.

### Phase C — ridge transition

Use the extracted table to initialize a two-section or smooth taper.

First optimize without bolts.

### Phase D — residual tuning

Add one or two rounded tuning bolts only if necessary.

### Phase E — four-way cascade

Cascade two first-stage tees and one final tee.

Drive all four input ports simultaneously with the intended coherent phase state and compute

\[
\eta_{comb}
=
\frac{P_{desired\ output}}
{\sum_iP_{available,i}}.
\]

Also inspect the three difference-mode/termination powers. They are a direct diagnostic of imbalance.

### Phase F — high-power verification

Use finite conductivity and the actual input excitation levels.

Check:

- \(E_{max}\) and hot-spot location at 30 kW equivalent output;
- surface loss and current density at 1 kW CW;
- sensitivity to bolt depth, ridge gap, and machining errors;
- thermal implications.

---

## 14. Current conclusions

1. WR90 is a sensible straight-guide baseline for 9–11.5 GHz.
2. The electrical center for equal band-edge phase error is about 10.195 GHz, not exactly 10.25 GHz.
3. The four-way network should be treated primarily as a unitary sum/difference multiport system.
4. The 22 dB differential/isolation goal makes phase tracking more restrictive than the 95% combining-efficiency condition alone.
5. A two-section broadband transformer is a better reduced-model starting point than a single quarter-wave section.
6. For the conditional 2:1 model, the minimax seed is approximately \(0.832686 Z_0\), \(0.600466 Z_0\), with 9.601 mm electrical-section lengths.
7. The literal 2:1 assumption is not a rigorous magic-tee load model; actual effective/modal impedance must be extracted from the HFSS junction and ridge cross-section.
8. The ridge should carry the broadband matching burden; tuning bolts should correct residual reactance.
9. Peak-power design must optimize field enhancement in addition to S-parameters.
10. CW verification requires finite-conductivity loss and thermal attention.

---

## 15. Reference pointers

Useful background for later formal referencing:

- ideal magic-tee scattering matrix and sum/difference behavior;
- classical transverse-resonance/Cohn treatment for double-ridged waveguide;
- consistent non-TEM waveguide impedance definitions;
- small-reflection and Chebyshev/Klopfenstein transformer synthesis.

The next quantitative task is to generate the HFSS uniform-ridge extraction table and use it to replace the conditional scalar 2:1 assumption with a geometry-calibrated model.
