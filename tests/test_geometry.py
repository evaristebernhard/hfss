"""Fast geometry invariant tests; no HFSS/PyAEDT import or license required."""
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hfss"))
from magictee.config import load_config
from magictee.geometry import CellGeometry
from magictee.tree import assemble_tree
import build_model


class Solid:
    def __init__(self, modeler, name):
        self.modeler = modeler
        self._name = name
        self.moves = []
        self.rotations = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.modeler.objects[name] = self

    def clone(self):
        result = Solid(self.modeler, self.name + "_clone")
        self.modeler.objects[result.name] = result
        return result

    def rotate(self, axis, angle):
        self.rotations.append((axis, angle))
        return True

    def move(self, distance):
        self.moves.append(distance)
        return True


class FakeModeler:
    def __init__(self):
        self.objects = {}
        self.boxes = []
        self.cylinders = []
        self.subtractions = []
        self.unions = []

    def create_box(self, origin, sizes, name, material):
        self.boxes.append((name, tuple(origin), tuple(sizes), material))
        result = Solid(self, name)
        self.objects[name] = result
        return result

    def create_cylinder(self, **kwargs):
        self.cylinders.append(kwargs)
        result = Solid(self, kwargs["name"])
        self.objects[result.name] = result
        return result

    def unite(self, names):
        self.unions.append(tuple(names))
        return True

    def subtract(self, solid, tools, keep_originals=False):
        self.subtractions.append((solid, tuple(tools)))
        return True

    def __getitem__(self, name):
        return self.objects[name]


class FakeHFSS:
    def __init__(self):
        self.modeler = FakeModeler()


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.cell, self.tree = load_config()
        self.builder = CellGeometry(self.cell)

    def test_dimensions_match_paper(self):
        self.assertAlmostEqual(self.cell.h_port_y, 73.159, places=6)
        self.assertAlmostEqual(self.cell.taper_total, 18.729, places=6)
        self.assertEqual((self.cell.post_lower_radius, self.cell.post_lower_height,
                          self.cell.post_upper_radius, self.cell.post_total_height),
                         (1.4, 6.2, 0.9, 16.25))
        self.assertEqual(self.tree.interstage_length_mm, 1.38)

    def test_updates_are_isolated(self):
        changed = self.cell.updated(post_upper_radius=1.1)
        self.assertEqual(self.cell.post_upper_radius, 0.9)
        self.assertEqual(changed.post_upper_radius, 1.1)
        with self.assertRaises(ValueError):
            self.cell.updated(post_total_height=3.0)

    def test_nominal_primitives(self):
        hfss = FakeHFSS()
        solid, geom = self.builder.create_cell(hfss)
        self.assertEqual(solid.name, "AirWG")
        self.assertAlmostEqual(geom["h_port_y"], 73.159)
        boxes = {box[0]: box for box in hfss.modeler.boxes}
        self.assertEqual(boxes["AirWG"][2], (70.0, 22.86, 10.16))
        self.assertEqual(boxes["HArmAir"][2][1], self.cell.h_arm_active_len)
        self.assertIn("HThroat1Wall_Left", boxes)
        self.assertIn("RidgeTop_terminal", boxes)
        self.assertIn("RidgeTop_00", boxes)
        self.assertIn("RidgeBot_23", boxes)
        post = {obj["name"]: obj for obj in hfss.modeler.cylinders}
        self.assertEqual(len(post), 4)  # lower, upper, local top/bottom
        self.assertAlmostEqual(post["JunctionPost_Lower"]["height"], 6.2)
        self.assertAlmostEqual(post["JunctionPost_Upper"]["height"], 10.05)
        self.assertAlmostEqual(post["JunctionPost_Lower"]["radius"], 1.4)
        self.assertAlmostEqual(post["JunctionPost_Upper"]["radius"], 0.9)
        self.assertFalse(any(name.startswith("TuneScrew") for name in post))

    def test_four_way_uses_same_cell_geometry(self):
        single = FakeHFSS()
        self.builder.create_cell(single)
        tree = FakeHFSS()
        geometry = assemble_tree(tree, self.builder, self.tree)
        self.assertEqual(single.modeler.cylinders, tree.modeler.cylinders)
        self.assertEqual(single.modeler.boxes, tree.modeler.boxes[:len(single.modeler.boxes)])
        links = [x for x in tree.modeler.boxes if x[0].startswith("Interstage_")]
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0][2], (1.38, 22.86, 10.16))
        self.assertAlmostEqual(geometry["h_port"], 73.159)
        self.assertIn("AirWG", tree.modeler.objects)

    def test_cli_dry_run_and_overrides(self):
        self.assertEqual(build_model.main(["--mode","tree","--dry-run"]), 0)
        cell, tree, points = build_model.resolve(build_model.parser().parse_args(
            ["--post-lower-radius", "1.6", "--interstage-length", "2.0", "--dry-run"]))
        self.assertEqual(cell.post_lower_radius, 1.6)
        self.assertEqual(tree.interstage_length_mm, 2.0)
        self.assertEqual(points, 101)


if __name__ == "__main__":
    unittest.main()
