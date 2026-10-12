"""AEDT lifecycle and Touchstone export shared by 4-port cell and 8-port tree.

Keep solver interactions separate from pure dimensioned geometry.
"""
from __future__ import annotations

import math
from pathlib import Path
from .config import CellConfig


def launch(project: Path, design: str, version: str, non_graphical: bool):
    try:
        from ansys.aedt.core import Hfss
        modern = True
    except ImportError:
        from pyaedt import Hfss
        modern = False

    if modern:
        return Hfss(
            project=str(project),
            design=design,
            version=version,
            solution_type="Modal",
            non_graphical=non_graphical,
            new_desktop=True,
            close_on_exit=True,
            student_version=True,
        )
    return Hfss(
        projectname=str(project),
        designname=design,
        specified_version=version,
        solution_type="DrivenModal",
        non_graphical=non_graphical,
        new_desktop_session=True,
    )


def create_setup(hfss, config: CellConfig, *, points: int, four_way: bool):
    setup = hfss.create_setup("Setup1")
    setup.props["Frequency"] = f"{config.f_adapt_ghz:g}GHz"
    setup.props["MaximumPasses"] = 7 if four_way else 8
    setup.props["MinimumPasses"] = 2
    setup.props["MinimumConvergedPasses"] = 1
    setup.props["MaxDeltaS"] = 0.03 if four_way else 0.02
    setup.update()
    try:
        sweep = hfss.create_linear_count_sweep(
            setup=setup.name,
            unit="GHz",
            start_frequency=config.f_start_ghz,
            stop_frequency=config.f_stop_ghz,
            num_of_freq_points=points,
            name="Sweep_9_11p5GHz",
            sweep_type="Interpolating",
            interpolation_tol=0.75 if four_way else 0.5,
            save_fields=False,
        )
    except Exception:
        if four_way:
            raise
        sweep = setup.add_sweep("Sweep_9_11p5GHz", "Interpolating")
        sweep.props["RangeType"] = "LinearCount"
        sweep.props["RangeStart"] = f"{config.f_start_ghz:g}GHz"
        sweep.props["RangeEnd"] = f"{config.f_stop_ghz:g}GHz"
        sweep.props["RangeCount"] = points
        sweep.props["SaveFields"] = False
        sweep.update()
    return setup, sweep


def export_touchstone(hfss, setup_name: str, sweep_name: str, path: Path, ports: int):
    """Serialize the PyAEDT solution in the existing row-major MA format.

    All historical research inputs use this same convention; do not change
    port order here without updating downstream readers and tests.
    """
    if ports not in (4, 8):
        raise ValueError("Only four-port and eight-port exports are supported")
    expressions = [f"S({i},{j})" for i in range(1, ports+1) for j in range(1, ports+1)]
    data = hfss.post.get_solution_data(
        expressions=expressions,
        setup_sweep_name=f"{setup_name} : {sweep_name}",
    )
    if not data:
        raise RuntimeError("HFSS did not return solved scattering data")
    freq, _ = data.get_expression_data(expressions[0], formula="real")
    parts = {}
    for expr in expressions:
        fr, real = data.get_expression_data(expr, formula="real")
        fi, imag = data.get_expression_data(expr, formula="imag")
        if len(fr) != len(freq) or len(fi) != len(freq):
            raise RuntimeError(f"Wrong sweep shape for {expr}")
        parts[expr] = (real, imag)

    labels = ("P1 P2 H E" if ports == 4
              else "IN1 IN2 IN3 IN4 OUT DUMP_A DUMP_B DUMP_C")
    lines = [f"! {ports}-port HFSS model; port order: {labels}", "# GHz S MA R 50"]
    for k, f in enumerate(freq):
        tokens = [f"{float(f):.12g}"]
        for expr in expressions:
            real, imag = parts[expr]
            z = complex(float(real[k]), float(imag[k]))
            tokens.extend((f"{abs(z):.12g}", f"{math.degrees(math.atan2(z.imag,z.real)):.12g}"))
        lines.append(" ".join(tokens))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines)+"\n", encoding="ascii")
    return path
