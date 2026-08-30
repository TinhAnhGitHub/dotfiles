from __future__ import annotations

import unittest

from class_metaprogramming import Lower, Plugin, Upper, make_record


class Chapter24ExamplesTest(unittest.TestCase):
    def test_init_subclass_registers_and_class_getitem_looks_up(self) -> None:
        self.assertIs(Plugin["upper"], Upper)
        self.assertIs(Plugin["lower"], Lower)
        self.assertEqual(Plugin["upper"]().run("hello"), "HELLO")

    def test_unknown_plugin_is_explicit(self) -> None:
        with self.assertRaisesRegex(KeyError, "unknown plugin"):
            Plugin["missing"]

    def test_dynamic_record_factory_validates_arity_and_slots(self) -> None:
        Point = make_record("Point", ("x", "y"))
        point = Point(1, 2)
        self.assertEqual((point.x, point.y), (1, 2))
        with self.assertRaises(TypeError):
            Point(1)
        with self.assertRaises(AttributeError):
            point.z = 3


if __name__ == "__main__":
    unittest.main()
