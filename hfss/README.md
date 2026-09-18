# HFSS 2022 first full-wave model

This directory contains the first deliberately rough HFSS implementation of
the 9--11.5 GHz four-way-combiner work.

It is intended to answer one question first:

> Can the current WR90 + double-ridge seed be connected to a real 3-D
> magic-tee-like junction and produce a sensible broadband S-matrix?

It is **not** yet the final high-power mechanical design.

## 1. Software

Recommended first route:

- Ansys Electronics Desktop / HFSS 2022 R1 or R2
- PyAEDT
- Python 3
- optional: scikit-rf for mixed-mode post-processing

Install the Python packages in the environment that controls AEDT:

~~~bash
pip install pyaedt scikit-rf numpy
~~~

Recent PyAEDT releases use the import path `ansys.aedt.core`; older ones use
`pyaedt`.  The builder tries both.

## 2. Build only first

From this directory:

~~~bash
python build_single_magictee_v1.py --version 2022.2
~~~

For HFSS 2022 R1:

~~~bash
python build_single_magictee_v1.py --version 2022.1
~~~

The default behavior is **build only**.

It creates:

~~~text
output_v1/
    single_magictee_v1.aedt
~~~

Open the project and inspect:

1. four wave ports;
2. the unioned WR90 air channel;
3. the H-arm double-ridge taper;
4. the Perfect-E wall assignment;
5. the central orthogonal junction.

Do not solve until the geometry looks correct.

## 3. What geometry is generated

Coordinate convention:

~~~text
               P4 E-arm (+Z)
                    |
                    |
P1 (-X) -------- junction -------- P2 (+X)
                    |
                    |
             P3 H-arm (+Y)
             double-ridge taper
~~~

The active ridge seed is:

~~~text
WR90 a = 22.86 mm
WR90 b = 10.16 mm

common ridge width w = 4.572 mm

section 1:
    g1 = 7.672 mm
    L1 = 9.872 mm

section 2:
    g2 = 4.984 mm
    L2 = 8.857 mm
~~~

The taper is approximated by 20 short ridge segments.  This is intentionally
coarse.  The purpose is to get the first electromagnetic result, not to create
the final milling profile.

A 6 mm uniform g2 ridged section is retained directly before the tee junction
so the taper does not terminate in an immediate WR90 step.

## 4. Solve

After visually checking the model:

~~~bash
python build_single_magictee_v1.py --version 2022.2 --solve
~~~

The script uses:

~~~text
adaptive frequency: 10.20 GHz
frequency sweep: 9.0 -- 11.5 GHz
points: 101
solution: HFSS Driven Modal
~~~

It then attempts to export:

~~~text
output_v1/single_magictee_v1.s4p
~~~

The standard PyAEDT wave-port and driven-sweep APIs are used.

## 5. Mixed-mode analysis

After obtaining the S4P file:

~~~bash
python postprocess_mixed_mode_v1.py \
    output_v1/single_magictee_v1.s4p \
    --csv output_v1/mixed_mode_v1.csv
~~~

The port S matrix is transformed to

~~~text
Sigma
Delta1
Delta2
Delta3
~~~

using

[
S_m = U S_p U^H.
]

The script reports the minimum in-band modal return loss and the largest modal
conversion term.

This is more informative than looking only at S11.

## 6. Expected first result

Do **not** expect the bare first geometry to immediately satisfy

~~~text
return loss > 22 dB
isolation > 22 dB
efficiency > 95 %
~~~

The central junction currently contains no optimized diaphragm, iris, post, or
multi-bolt matching structure.

A useful first run is one in which:

- all four ports excite the expected dominant mode;
- no accidental propagating higher mode appears below 11.5 GHz;
- the S matrix is smooth rather than dominated by a narrow numerical resonance;
- the Sigma/Delta decomposition behaves sensibly;
- the current ridge taper improves at least one relevant mode versus a plain
  bare junction.

## 7. Next geometry correction after the first solve

Use the first S4P result to classify the error.

### Broad smooth mismatch

If the response is smooth but return loss is poor across most of 9--11.5 GHz,
change the ridge impedance trajectory / terminal gap before adding bolts.

### One or two broad ripple peaks

If the passive match is already reasonable and there are residual ripple
peaks, add two shallow tuning bolts with the current seed:

~~~text
initial center spacing: 8.8 mm
spacing sweep: 7.5 -- 10.0 mm
penetration sweep: 0 -- 2.0 mm
~~~

### Strong narrow resonances

If narrow resonances dominate, first inspect the central junction and local
higher-order fields.  Do not try to cure a trapped-mode resonance with a large
bolt penetration.

## 8. High-power work is later

The first solve uses PEC walls to isolate geometry/matching behavior.

After the S-parameter structure is credible:

1. replace PEC by finite-conductivity metal;
2. compute loss;
3. extract peak E field per accepted watt;
4. scale to 30 kW peak;
5. inspect ridge edges and bolt tips;
6. then address the 1 kW CW thermal requirement.

The present model is a design seed, not a hardware power-rating claim.
