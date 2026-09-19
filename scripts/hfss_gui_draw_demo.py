"""Draw a small WR90 double-ridge seed in the Windows HFSS GUI.

This file is edited and launched from WSL2, while AEDT and its GUI run on
Windows through the Windows PyAEDT environment.
"""

from __future__ import annotations

import os
from pathlib import Path

from ansys.aedt.core import Hfss


version = os.environ.get("AEDT_VERSION", "2025.2")
student_version = os.environ.get("AEDT_STUDENT", "1") != "0"
project_path = Path(
    os.environ.get(
        "HFSS_PROJECT_PATH",
        str(Path.home() / "Documents" / "wsl_hfss_gui_demo.aedt"),
    )
)

# WR90-like dimensions. All dimensions are explicit strings so that the
# script remains independent of the AEDT model-unit default.
width = "22.86mm"
height = "10.16mm"
length = "40mm"
ridge_width = "4.572mm"
ridge_height = "4.08mm"
ridge_gap = "2.0mm"

hfss = Hfss(
    version=version,
    non_graphical=False,
    new_desktop=True,
    student_version=student_version,
)

try:
    modeler = hfss.modeler

    # Main air volume. In a production model, assign wave ports and a
    # radiation/PEC boundary according to the intended excitation scheme.
    air = modeler.create_box(
        origin=["0mm", "0mm", "0mm"],
        sizes=[width, height, length],
        name="WR90_Air",
        matname="air",
    )

    # Two opposing ridges. These are intentionally simple primitives so the
    # local Python file can be modified quickly during geometry exploration.
    x0 = "9.144mm"
    lower_y = "0mm"
    upper_y = "6.08mm"
    lower_ridge = modeler.create_box(
        origin=[x0, lower_y, "0mm"],
        sizes=[ridge_width, ridge_height, length],
        name="Lower_Ridge",
        matname="copper",
    )
    upper_ridge = modeler.create_box(
        origin=[x0, upper_y, "0mm"],
        sizes=[ridge_width, ridge_height, length],
        name="Upper_Ridge",
        matname="copper",
    )

    hfss.modeler.fit_all()
    hfss.save_project(str(project_path))

    print("HFSS_GUI_MODEL_OK", flush=True)
    print("PROJECT:", project_path, flush=True)
    print("OBJECTS:", air.name, lower_ridge.name, upper_ridge.name, flush=True)
    print("GUI is open. Press Enter here to close the AEDT session.", flush=True)
    try:
        input()
    except EOFError:
        # Non-interactive runners have no stdin. The model is already saved.
        pass
finally:
    hfss.release_desktop()
