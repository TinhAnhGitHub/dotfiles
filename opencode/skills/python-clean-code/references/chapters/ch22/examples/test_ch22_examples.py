from __future__ import annotations

import unittest

from dynamic_attributes import FrozenJSON, Product


class Chapter22ExamplesTest(unittest.TestCase):
    def test_property_validates_before_mutating(self) -> None:
        product = Product("beans", 2.0)
        with self.assertRaisesRegex(ValueError, "positive"):
            product.weight = 0
        self.assertEqual(product.weight, 2.0)

    def test_cached_property_is_stable_until_deleted(self) -> None:
        product = Product("beans", 2.0)
        first = product.shipping_label
        product._weight = 3.0
        self.assertIs(product.shipping_label, first)
        del product.shipping_label
        self.assertEqual(product.shipping_label, "beans:3kg")

    def test_dynamic_json_access_and_attribute_errors(self) -> None:
        feed = FrozenJSON({"class": "talk", "meta": {"room": 3}, "tags": ["python"]})
        self.assertEqual(feed.class_, "talk")
        self.assertEqual(feed.meta.room, 3)
        self.assertEqual(feed.tags, ["python"])
        self.assertIn("class_", dir(feed))
        with self.assertRaises(AttributeError):
            _ = feed.missing


if __name__ == "__main__":
    unittest.main()
