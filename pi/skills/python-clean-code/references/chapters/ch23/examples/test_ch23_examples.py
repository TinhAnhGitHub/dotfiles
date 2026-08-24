from __future__ import annotations

import unittest

from descriptors import LineItem, NonBlank, Positive


class Chapter23ExamplesTest(unittest.TestCase):
    def test_set_name_and_class_access(self) -> None:
        self.assertEqual(LineItem.weight.storage_name, "_LineItem__weight")
        self.assertIsInstance(LineItem.weight, Positive)
        self.assertIsInstance(LineItem.description, NonBlank)

    def test_descriptor_validation_and_normalization(self) -> None:
        item = LineItem("  coffee  ", 2)
        self.assertEqual(item.description, "coffee")
        self.assertEqual(item.weight, 2.0)
        with self.assertRaises(ValueError):
            item.weight = 0
        with self.assertRaises(ValueError):
            item.description = "  "
        with self.assertRaises(TypeError):
            item.description = 42


if __name__ == "__main__":
    unittest.main()
