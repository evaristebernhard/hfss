"""Start a minimal Windows AEDT Student session from WSL2 via Windows PyAEDT."""

from __future__ import annotations

import os

from ansys.aedt.core import Hfss


version = os.environ.get("AEDT_VERSION", "2025.2")
student_version = os.environ.get("AEDT_STUDENT", "1") != "0"
non_graphical = os.environ.get("AEDT_NON_GRAPHICAL", "1") != "0"

hfss = Hfss(
    version=version,
    non_graphical=non_graphical,
    new_desktop=True,
    student_version=student_version,
)

try:
    box = hfss.modeler.create_box(
        origin=[0, 0, 0],
        sizes=[1, 1, 1],
        name="WSL2SmokeBox",
    )
    print("HFSS_SESSION_OK")
    print("AEDT_VERSION:", version)
    print("DESKTOP_PORT:", hfss.desktop_class.port)
    print("OBJECT:", box.name)
finally:
    hfss.release_desktop()
