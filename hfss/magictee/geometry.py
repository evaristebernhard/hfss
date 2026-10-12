"""Single source of truth for the active Magic-T solid geometry.

All operations create/subtract the same primitives as the archived v4 + stepped
post model, but no mutable module globals or monkey-patched functions remain.
One CellGeometry instance owns one immutable CellConfig. No AEDT import at import time.
"""
from __future__ import annotations

import math
from .config import CellConfig


class CellGeometry:
    def __init__(self, config: CellConfig):
        config.validate()
        self.config = config

    def smoothstep(self, t: float) -> float:
        return 3.0 * t * t - 2.0 * t * t * t

    def log_interp(self, a: float, b: float, t: float) -> float:
        s = self.smoothstep(t)
        return math.exp((1.0 - s) * math.log(a) + s * math.log(b))

    def taper_gap_from_port_distance(self, s_mm: float) -> float:
        B = self.config.b
        G1 = self.config.g1
        L1 = self.config.l1
        G2 = self.config.g2
        L2 = self.config.l2
        TAPER_TOTAL = self.config.taper_total
        if s_mm <= 0.0:
            return B
        if s_mm >= TAPER_TOTAL:
            return G2
        if s_mm <= L1:
            return self.log_interp(B, G1, s_mm / L1)
        return self.log_interp(G1, G2, (s_mm - L1) / L2)

    def _box(self, hfss, origin, sizes, name, material="vacuum"):
        return hfss.modeler.create_box(
            origin=origin,
            sizes=sizes,
            name=name,
            material=material,
        )

    def _cylinder(self, hfss, origin, radius, height, name, material="pec"):
        # Modern PyAEDT uses orientation/origin; older versions accept the same
        # positional ordering.  Keep the call simple for HFSS 2022 compatibility.
        try:
            return hfss.modeler.create_cylinder(
                orientation="Z",
                origin=origin,
                radius=radius,
                height=height,
                name=name,
                material=material,
            )
        except TypeError:
            return hfss.modeler.create_cylinder(
                "Z", origin, radius, height, 0, name, material
            )

    def _make_air_volume(self, hfss):
        A = self.config.a
        B = self.config.b
        COLLINEAR_HALF_LEN = self.config.collinear_half_len
        E_ARM_LEN = self.config.e_arm_len
        H_ARM_ACTIVE_LEN = self.config.h_arm_active_len
        self._box(
            hfss,
            [-COLLINEAR_HALF_LEN, -A / 2.0, -B / 2.0],
            [2.0 * COLLINEAR_HALF_LEN, A, B],
            "AirWG",
        )
        self._box(
            hfss,
            [-A / 2.0, A / 2.0, -B / 2.0],
            [A, H_ARM_ACTIVE_LEN, B],
            "HArmAir",
        )
        self._box(
            hfss,
            [-B / 2.0, -A / 2.0, B / 2.0],
            [B, A, E_ARM_LEN],
            "EArmAir",
        )
        hfss.modeler.unite(["AirWG", "HArmAir", "EArmAir"])
        return hfss.modeler["AirWG"]

    def _subtract_h_width_throat(self, hfss):
        """One reduced-width H throat (no legacy second-throat branch)."""
        A = self.config.a
        B = self.config.b
        width = self.config.h_throat_a
        length = self.config.h_throat_len
        y0 = A / 2
        side = (A - width) / 2
        if side > 1e-9:
            left = self._box(hfss, [-A/2, y0, -B/2],
                             [side, length, B], "HThroat1Wall_Left", material="pec")
            right = self._box(hfss, [width/2, y0, -B/2],
                              [side, length, B], "HThroat1Wall_Right", material="pec")
            hfss.modeler.subtract("AirWG", [left.name, right.name], keep_originals=False)
        return {
            "h_throat_start_y": y0,
            "h_throat_end_y": y0 + length,
            "h_throat_side_depth": side,
        }

    def _subtract_local_post_pair(self, hfss):
        A = self.config.a
        B = self.config.b
        POST_RADIUS = self.config.post_radius
        POST_HEIGHT = self.config.post_height
        POST_Y = self.config.post_y
        """Symmetric rounded top/bottom partial-height posts near the H junction."""
        y = A / 2.0 + POST_Y
        if POST_HEIGHT <= 0.0:
            return {"post_axis_y": y, "local_post_pair_enabled": False}

        top = self._cylinder(
            hfss,
            [0.0, y, B / 2.0 - POST_HEIGHT],
            POST_RADIUS,
            POST_HEIGHT,
            "JunctionPost_Top",
        )
        bot = self._cylinder(
            hfss,
            [0.0, y, -B / 2.0],
            POST_RADIUS,
            POST_HEIGHT,
            "JunctionPost_Bottom",
        )
        hfss.modeler.subtract("AirWG", [top.name, bot.name], keep_originals=False)
        return {"post_axis_y": y, "local_post_pair_enabled": True}

    def _subtract_terminal_and_taper(self, hfss, throat_geom):
        A = self.config.a
        B = self.config.b
        RIDGE_W = self.config.ridge_w
        G2 = self.config.g2
        H_TERMINAL_RIDGE_W = self.config.h_terminal_ridge_w
        TERMINAL_RIDGE_LEN = self.config.terminal_ridge_len
        TUNER_SECTION_LEN = self.config.tuner_section_len
        PORT_STRAIGHT_LEN = self.config.port_straight_len
        N_TAPER_SEGMENTS = self.config.n_taper_segments
        TAPER_TOTAL = self.config.taper_total
        H_ARM_ACTIVE_LEN = self.config.h_arm_active_len
        tools = []

        terminal_start_y = throat_geom["h_throat_end_y"]
        depth = 0.5 * (B - G2)
        top = self._box(
            hfss,
            [-H_TERMINAL_RIDGE_W / 2.0, terminal_start_y, G2 / 2.0],
            [H_TERMINAL_RIDGE_W, TERMINAL_RIDGE_LEN, depth],
            "RidgeTop_terminal",
            material="pec",
        )
        bot = self._box(
            hfss,
            [-H_TERMINAL_RIDGE_W / 2.0, terminal_start_y, -B / 2.0],
            [H_TERMINAL_RIDGE_W, TERMINAL_RIDGE_LEN, depth],
            "RidgeBot_terminal",
            material="pec",
        )
        tools.extend([top.name, bot.name])

        taper_start_y = terminal_start_y + TERMINAL_RIDGE_LEN
        ds = TAPER_TOTAL / float(N_TAPER_SEGMENTS)
        for i in range(N_TAPER_SEGMENTS):
            s0 = i * ds
            s1 = (i + 1) * ds
            smid = 0.5 * (s0 + s1)
            # s=0 is near the tee; reverse the old port-distance definition.
            gap = self.taper_gap_from_port_distance(TAPER_TOTAL - smid)
            ridge_depth = max(0.0, 0.5 * (B - gap))
            if ridge_depth <= 1e-6:
                continue

            y0 = taper_start_y + s0
            dy = s1 - s0
            top = self._box(
                hfss,
                [-RIDGE_W / 2.0, y0, gap / 2.0],
                [RIDGE_W, dy, ridge_depth],
                "RidgeTop_%02d" % i,
                material="pec",
            )
            bot = self._box(
                hfss,
                [-RIDGE_W / 2.0, y0, -B / 2.0],
                [RIDGE_W, dy, ridge_depth],
                "RidgeBot_%02d" % i,
                material="pec",
            )
            tools.extend([top.name, bot.name])

        hfss.modeler.subtract("AirWG", tools, keep_originals=False)

        taper_end_y = taper_start_y + TAPER_TOTAL
        tuner_start_y = taper_end_y
        h_port_y = (
            tuner_start_y
            + TUNER_SECTION_LEN
            + PORT_STRAIGHT_LEN
        )

        expected_port_y = A / 2.0 + H_ARM_ACTIVE_LEN
        if abs(h_port_y - expected_port_y) > 1e-6:
            raise RuntimeError("H-arm longitudinal layout bookkeeping error")

        return {
            "terminal_start_y": terminal_start_y,
            "taper_start_y": taper_start_y,
            "taper_end_y": taper_end_y,
            "tuner_start_y": tuner_start_y,
            "h_port_y": h_port_y,
        }

    def _subtract_three_screws(self, hfss, geom):
        B = self.config.b
        SCREW_RADIUS = self.config.screw_radius
        SCREW_TUNER_OFFSET = self.config.screw_tuner_offset
        SCREW_Z1 = self.config.screw_z1
        SCREW_Z2 = self.config.screw_z2
        SCREW_Z3 = self.config.screw_z3
        SCREW_P1 = self.config.screw_p1
        SCREW_P2 = self.config.screw_p2
        SCREW_P3 = self.config.screw_p3
        tuner_start_y = geom["tuner_start_y"]
        rel = [SCREW_Z1, SCREW_Z2, SCREW_Z3]
        pen = [SCREW_P1, SCREW_P2, SCREW_P3]
        names = []

        for i, (zrel, p) in enumerate(zip(rel, pen), start=1):
            if p <= 1e-9:
                continue
            y = tuner_start_y + SCREW_TUNER_OFFSET + zrel
            obj = self._cylinder(
                hfss,
                [0.0, y, B / 2.0 - p],
                SCREW_RADIUS,
                p,
                "TuneScrew_%d" % i,
            )
            names.append(obj.name)

        if names:
            hfss.modeler.subtract("AirWG", names, keep_originals=False)

    def _port_face(self, hfss, position):
        face_id = hfss.modeler.get_faceid_from_position(position, assignment="AirWG")
        if face_id is None or face_id < 0:
            raise RuntimeError("Could not find port face at %r" % (position,))
        return face_id

    def _assign_ports_and_walls(self, hfss, geom):
        B = self.config.b
        COLLINEAR_HALF_LEN = self.config.collinear_half_len
        E_ARM_LEN = self.config.e_arm_len
        h_port_y = geom["h_port_y"]
        e_port_z = B / 2.0 + E_ARM_LEN

        f1 = self._port_face(hfss, [-COLLINEAR_HALF_LEN, 0.0, 0.0])
        f2 = self._port_face(hfss, [COLLINEAR_HALF_LEN, 0.0, 0.0])
        f3 = self._port_face(hfss, [0.0, h_port_y, 0.0])
        f4 = self._port_face(hfss, [0.0, 0.0, e_port_z])
        port_faces = {f1, f2, f3, f4}

        zline_1 = [
            [-COLLINEAR_HALF_LEN, 0.0, -B / 2.0],
            [-COLLINEAR_HALF_LEN, 0.0, B / 2.0],
        ]
        zline_2 = [
            [COLLINEAR_HALF_LEN, 0.0, -B / 2.0],
            [COLLINEAR_HALF_LEN, 0.0, B / 2.0],
        ]
        zline_3 = [
            [0.0, h_port_y, -B / 2.0],
            [0.0, h_port_y, B / 2.0],
        ]
        xline_4 = [
            [-B / 2.0, 0.0, e_port_z],
            [B / 2.0, 0.0, e_port_z],
        ]

        hfss.wave_port(
            f1,
            integration_line=zline_1,
            modes=1,
            name="P1_CollinearMinusX",
            renormalize=False,
            characteristic_impedance="Zwave",
        )
        hfss.wave_port(
            f2,
            integration_line=zline_2,
            modes=1,
            name="P2_CollinearPlusX",
            renormalize=False,
            characteristic_impedance="Zwave",
        )
        hfss.wave_port(
            f3,
            integration_line=zline_3,
            modes=1,
            name="P3_HArm_v4",
            renormalize=False,
            characteristic_impedance="Zwave",
        )
        hfss.wave_port(
            f4,
            integration_line=xline_4,
            modes=1,
            name="P4_EArm",
            renormalize=False,
            characteristic_impedance="Zwave",
        )

        air = hfss.modeler["AirWG"]
        wall_faces = [face.id for face in air.faces if face.id not in port_faces]
        hfss.assign_perfect_e(wall_faces, name="PEC_WaveguideWalls")

    def _subtract_stepped_post(self, hfss):
        """Coaxial lower/upper cylinders, exactly matching the solved stepped cell."""
        p = self.config
        objects = [self._cylinder(hfss, [0.0, 0.0, -p.b/2],
                                  p.post_lower_radius, p.post_lower_height,
                                  "JunctionPost_Lower")]
        top_height = p.post_total_height - p.post_lower_height
        objects.append(self._cylinder(
            hfss, [0.0, 0.0, -p.b/2 + p.post_lower_height],
            p.post_upper_radius, top_height, "JunctionPost_Upper"))
        hfss.modeler.subtract("AirWG", [o.name for o in objects], keep_originals=False)
        return {"stepped_center_post": {
            "lower_radius_mm": p.post_lower_radius,
            "lower_height_mm": p.post_lower_height,
            "upper_radius_mm": p.post_upper_radius,
            "total_height_mm": p.post_total_height,
        }}

    def create_cell(self, hfss):
        """Build a single four-port air solid; used unchanged in the four-way tree."""
        self._make_air_volume(hfss)
        throat = self._subtract_h_width_throat(hfss)
        post = self._subtract_stepped_post(hfss)
        local = self._subtract_local_post_pair(hfss)
        geometry = self._subtract_terminal_and_taper(hfss, throat)
        geometry.update(post)
        geometry.update(local)
        self._subtract_three_screws(hfss, geometry)
        return hfss.modeler["AirWG"], geometry

    def define_design_variables(self, hfss):
        """Record dimensions in AEDT for inspection; geometry coordinates are explicit."""
        from dataclasses import asdict
        for name, value in asdict(self.config).items():
            if isinstance(value, (int, float)):
                try:
                    unit = "GHz" if "ghz" in name else ("" if name.startswith("n_") else "mm")
                    hfss[name] = f"{value:g}{unit}"
                except Exception:
                    pass
