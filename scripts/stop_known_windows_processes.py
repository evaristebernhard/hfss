#!/usr/bin/env python3
"""Terminate only explicitly listed Windows process IDs."""

from __future__ import annotations

import argparse
import os
import signal


parser = argparse.ArgumentParser()
parser.add_argument("pid", nargs="+", type=int)
args = parser.parse_args()

for pid in args.pid:
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"terminated {pid}")
    except ProcessLookupError:
        print(f"not running {pid}")
    except PermissionError as exc:
        print(f"permission denied {pid}: {exc}")
    except OSError as exc:
        print(f"not terminated {pid}: {exc}")
