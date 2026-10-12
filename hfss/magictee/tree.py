"""Four-way geometry assembly: three exact clones of the same single-cell solid.

The binary tree adds only rigid transformations and interstage WR90 links.
All local solids come from CellGeometry.create_cell(), never duplicated code.
External port order: IN1, IN2, IN3, IN4, OUT, DUMP_A, DUMP_B, DUMP_C.
"""
from __future__ import annotations

from .config import CellConfig, TreeConfig
from .geometry import CellGeometry


def assemble_tree(hfss, builder: CellGeometry, tree: TreeConfig):
    config = builder.config
    cell_c, geom = builder.create_cell(hfss)
    cell_c.name = "CellC_Air"
    h_port = geom["h_port_y"]
    left_join = -config.collinear_half_len - tree.interstage_length_mm
    right_join = config.collinear_half_len + tree.interstage_length_mm

    cell_a = cell_c.clone()
    cell_b = cell_c.clone()
    if not cell_a or not cell_b:
        raise RuntimeError("failed to clone the seed cell")
    cell_a.name = "CellA_Air"
    cell_b.name = "CellB_Air"

    # Local +Y H arm becomes global +X for A and global -X for B.
    if not cell_a.rotate("Z", -90.0):
        raise RuntimeError("failed to rotate Cell A")
    if not cell_b.rotate("Z", 90.0):
        raise RuntimeError("failed to rotate Cell B")
    center_a_x = left_join - h_port
    center_b_x = right_join + h_port
    if not cell_a.move([center_a_x, 0.0, 0.0]):
        raise RuntimeError("failed to move Cell A")
    if not cell_b.move([center_b_x, 0.0, 0.0]):
        raise RuntimeError("failed to move Cell B")

    link_a = builder._box(
        hfss,
        [left_join, -config.a / 2.0, -config.b / 2.0],
        [tree.interstage_length_mm, config.a, config.b],
        "Interstage_A",
    )
    link_b = builder._box(
        hfss,
        [config.collinear_half_len, -config.a / 2.0, -config.b / 2.0],
        [tree.interstage_length_mm, config.a, config.b],
        "Interstage_B",
    )
    hfss.modeler.unite([cell_c.name, cell_a.name, cell_b.name, link_a.name, link_b.name])
    air = hfss.modeler[cell_c.name]
    air.name = "AirWG"
    return {
        "h_port": h_port,
        "e_port": config.b / 2.0 + config.e_arm_len,
        "center_a_x": center_a_x,
        "center_b_x": center_b_x,
    }

def _face(hfss, position):
    face = hfss.modeler.get_faceid_from_position(position, assignment="AirWG")
    if face is None or face < 0:
        raise RuntimeError(f"could not find external port face at {position}")
    return face

def _wave_port(hfss, face, line, name):
    return hfss.wave_port(
        face,
        integration_line=line,
        modes=1,
        name=name,
        renormalize=False,
        characteristic_impedance="Zwave",
    )

def assign_tree_ports(hfss, geom, config: CellConfig):
    xa = geom["center_a_x"]
    xb = geom["center_b_x"]
    hp = geom["h_port"]
    ep = geom["e_port"]
    positions = [
        [xa, config.collinear_half_len, 0.0],
        [xa, -config.collinear_half_len, 0.0],
        [xb, -config.collinear_half_len, 0.0],
        [xb, config.collinear_half_len, 0.0],
        [0.0, hp, 0.0],
        [xa, 0.0, ep],
        [xb, 0.0, ep],
        [0.0, 0.0, ep],
    ]
    faces = [_face(hfss, position) for position in positions]

    zline = lambda x, y: [[x, y, -config.b / 2.0], [x, y, config.b / 2.0]]
    _wave_port(hfss, faces[0], zline(xa, config.collinear_half_len), "P1_IN1")
    _wave_port(hfss, faces[1], zline(xa, -config.collinear_half_len), "P2_IN2")
    _wave_port(hfss, faces[2], zline(xb, -config.collinear_half_len), "P3_IN3")
    _wave_port(hfss, faces[3], zline(xb, config.collinear_half_len), "P4_IN4")
    _wave_port(hfss, faces[4], zline(0.0, hp), "P5_OUT")
    _wave_port(
        hfss,
        faces[5],
        [[xa, -config.b / 2.0, ep], [xa, config.b / 2.0, ep]],
        "P6_DUMP_A",
    )
    _wave_port(
        hfss,
        faces[6],
        [[xb, -config.b / 2.0, ep], [xb, config.b / 2.0, ep]],
        "P7_DUMP_B",
    )
    _wave_port(
        hfss,
        faces[7],
        [[-config.b / 2.0, 0.0, ep], [config.b / 2.0, 0.0, ep]],
        "P8_DUMP_C",
    )

    port_faces = set(faces)
    walls = [face.id for face in hfss.modeler["AirWG"].faces if face.id not in port_faces]
    hfss.assign_perfect_e(walls, name="PEC_WaveguideWalls")
