"""Open an existing AEDT/HFSS project in the Windows GUI via WSL2."""

from __future__ import annotations

import argparse
from pathlib import Path

from ansys.aedt.core import Hfss


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--design", default="SingleMagicT_v4_Full")
    parser.add_argument("--version", default="2025.2")
    args = parser.parse_args()

    project = args.project.resolve()
    if not project.exists():
        raise FileNotFoundError(project)

    hfss = Hfss(
        project=str(project),
        design=args.design,
        version=args.version,
        non_graphical=False,
        new_desktop=True,
        student_version=True,
    )
    try:
        hfss.modeler.fit_all()
        print(f"OPENED: {project}", flush=True)
        print("HFSS GUI is open. Press Enter here only when you want to close this session.", flush=True)
        try:
            input()
        except EOFError:
            pass
    finally:
        hfss.release_desktop()


if __name__ == "__main__":
    main()
