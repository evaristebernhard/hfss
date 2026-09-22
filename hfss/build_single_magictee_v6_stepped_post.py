#!/usr/bin/env python3
"""v6 wrapper replacing the uniform through-post with a two-radius post.

The lower section controls the discontinuity inside the collinear junction.
The upper section controls the continuation into the E arm.  Splitting these
radii adds a genuine junction-local degree of freedom without adding a remote
single-resonance tuner.
"""

from __future__ import annotations

import argparse
import sys

import build_single_magictee_v4_full as base


POST_LOWER_RADIUS = 2.4
POST_LOWER_HEIGHT = base.B
POST_UPPER_RADIUS = 2.4
POST_TOTAL_HEIGHT = 16.25


def _subtract_stepped_center_post(hfss):
    if POST_TOTAL_HEIGHT <= 0.0:
        return {"center_post_enabled": False}
    if not (0.0 < POST_LOWER_HEIGHT <= POST_TOTAL_HEIGHT < base.B + base.E_ARM_LEN):
        raise ValueError("require 0 < lower height <= total height inside junction/E arm")
    if POST_LOWER_RADIUS <= 0.0 or POST_UPPER_RADIUS <= 0.0:
        raise ValueError("stepped-post radii must be positive")

    names = []
    lower = base._cylinder(
        hfss,
        [0.0, 0.0, -base.B / 2.0],
        POST_LOWER_RADIUS,
        POST_LOWER_HEIGHT,
        "JunctionPost_Lower",
    )
    names.append(lower.name)
    upper_height = POST_TOTAL_HEIGHT - POST_LOWER_HEIGHT
    if upper_height > 1e-9:
        upper = base._cylinder(
            hfss,
            [0.0, 0.0, -base.B / 2.0 + POST_LOWER_HEIGHT],
            POST_UPPER_RADIUS,
            upper_height,
            "JunctionPost_Upper",
        )
        names.append(upper.name)
    hfss.modeler.subtract("AirWG", names, keep_originals=False)
    return {
        "center_post_enabled": True,
        "stepped_center_post": {
            "lower_radius_mm": POST_LOWER_RADIUS,
            "lower_height_mm": POST_LOWER_HEIGHT,
            "upper_radius_mm": POST_UPPER_RADIUS,
            "total_height_mm": POST_TOTAL_HEIGHT,
        },
    }


def parse_args():
    global POST_LOWER_RADIUS, POST_LOWER_HEIGHT, POST_UPPER_RADIUS, POST_TOTAL_HEIGHT
    own = argparse.ArgumentParser(add_help=False)
    own.add_argument("--post-lower-radius", type=float, default=POST_LOWER_RADIUS)
    own.add_argument("--post-lower-height", type=float, default=POST_LOWER_HEIGHT)
    own.add_argument("--post-upper-radius", type=float, default=POST_UPPER_RADIUS)
    own.add_argument("--post-total-height", type=float, default=POST_TOTAL_HEIGHT)
    custom, remaining = own.parse_known_args()
    POST_LOWER_RADIUS = custom.post_lower_radius
    POST_LOWER_HEIGHT = custom.post_lower_height
    POST_UPPER_RADIUS = custom.post_upper_radius
    POST_TOTAL_HEIGHT = custom.post_total_height

    original = sys.argv
    try:
        sys.argv = [original[0], *remaining]
        args = base.parse_args()
    finally:
        sys.argv = original
    # Keep the base validation enabled while using the custom post function.
    args.center_post_radius = POST_LOWER_RADIUS
    args.center_post_height = POST_TOTAL_HEIGHT
    return args


if __name__ == "__main__":
    base._subtract_center_post = _subtract_stepped_center_post
    base.build(parse_args())
