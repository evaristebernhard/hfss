"""Validated, immutable geometry configuration loaded from a single JSON source."""
from __future__ import annotations

from dataclasses import dataclass, replace, fields
import json
from pathlib import Path


DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "design" / "current_model.json"


@dataclass(frozen=True)
class CellConfig:
    a: float
    b: float
    ridge_w: float
    g1: float
    l1: float
    g2: float
    l2: float
    post_radius: float
    post_height: float
    post_y: float
    post_lower_radius: float
    post_lower_height: float
    post_upper_radius: float
    post_total_height: float
    h_throat_a: float
    h_throat_len: float
    h_terminal_ridge_w: float
    terminal_ridge_len: float
    screw_radius: float
    screw_tuner_offset: float
    screw_z1: float
    screw_z2: float
    screw_z3: float
    screw_p1: float
    screw_p2: float
    screw_p3: float
    tuner_section_len: float
    port_straight_len: float
    collinear_half_len: float
    e_arm_len: float
    n_taper_segments: int
    f_adapt_ghz: float
    f_start_ghz: float
    f_stop_ghz: float
    n_sweep: int

    @property
    def taper_total(self) -> float:
        return self.l1 + self.l2

    @property
    def h_arm_active_len(self) -> float:
        return (self.h_throat_len + self.terminal_ridge_len + self.taper_total
                + self.tuner_section_len + self.port_straight_len)

    @property
    def h_port_y(self) -> float:
        return self.a / 2 + self.h_arm_active_len

    def validate(self) -> None:
        if min(self.a, self.b, self.l1, self.l2, self.g1, self.g2,
               self.tuner_section_len, self.port_straight_len,
               self.collinear_half_len, self.e_arm_len, self.terminal_ridge_len) <= 0:
            raise ValueError("Waveguide lengths, gaps and dimensions must be positive")
        if not (0 < self.g1 <= self.b and 0 < self.g2 <= self.b):
            raise ValueError("ridge gaps must lie inside the waveguide")
        if not (0 < self.ridge_w <= self.a and 0 < self.h_terminal_ridge_w <= self.a):
            raise ValueError("ridge widths must be inside the broad dimension")
        if not (0 < self.h_throat_a <= self.a and self.h_throat_len > 0):
            raise ValueError("H throat dimensions are invalid")
        if not (0 <= self.post_height < self.b/2):
            raise ValueError("local post height must be less than half waveguide height")
        if self.post_radius <= 0 or self.post_y < self.post_radius:
            raise ValueError("local post must stay outside the collinear junction mouth")
        if self.post_y + self.post_radius > self.h_throat_len:
            raise ValueError("local post must stay within H throat")
        if not (0 < self.post_lower_radius and 0 < self.post_upper_radius):
            raise ValueError("stepped post radii must be positive")
        if not (0 < self.post_lower_height < self.post_total_height < self.b + self.e_arm_len):
            raise ValueError("stepped post heights invalid or exceed junction/E arm")
        if not (1 <= self.n_taper_segments <= 10000):
            raise ValueError("invalid taper segment count")
        if not (2 <= self.n_sweep <= 10001 and 0 < self.f_start_ghz < self.f_adapt_ghz < self.f_stop_ghz):
            raise ValueError("invalid frequency sweep")
        if self.screw_radius <= 0 or self.screw_tuner_offset < 0:
            raise ValueError("invalid screw dimensions")
        for z, p in zip((self.screw_z1,self.screw_z2,self.screw_z3),
                        (self.screw_p1,self.screw_p2,self.screw_p3)):
            y = self.screw_tuner_offset + z
            if y - self.screw_radius < 0 or y + self.screw_radius > self.tuner_section_len:
                raise ValueError("screw outside tuner straight")
            if not (0 <= p <= 2):
                raise ValueError("screw penetration must remain 0–2 mm")

    def updated(self, **changes) -> "CellConfig":
        result = replace(self, **changes)
        result.validate()
        return result


@dataclass(frozen=True)
class TreeConfig:
    interstage_length_mm: float
    sweep_points: int

    def validate(self) -> None:
        if not (self.interstage_length_mm > 0):
            raise ValueError("interstage length must be positive")
        if self.sweep_points < 2:
            raise ValueError("four-way sweep requires at least two points")


def load_config(path: Path | str = DEFAULT_CONFIG) -> tuple[CellConfig, TreeConfig]:
    source = json.loads(Path(path).read_text(encoding="utf-8"))
    if source.get("schema") != "magictee-current-model-v1":
        raise ValueError("unrecognized Magic-T model schema")
    expected = {f.name for f in fields(CellConfig)}
    if set(source["cell"]) != expected:
        raise ValueError(f"cell config mismatch; missing={sorted(expected-set(source['cell']))}, "
                         f"extra={sorted(set(source['cell'])-expected)}")
    cell = CellConfig(**source["cell"])
    tree = TreeConfig(**source["tree"])
    cell.validate()
    tree.validate()
    return cell, tree
