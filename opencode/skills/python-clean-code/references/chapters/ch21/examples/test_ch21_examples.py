from __future__ import annotations

import asyncio
import unittest

from asynchronous_programming import bounded_map, consume


class Chapter21ExamplesTest(unittest.TestCase):
    def test_bounded_async_map(self) -> None:
        self.assertEqual(asyncio.run(bounded_map([1, 2, 3])), [2, 4, 6])

    def test_async_generator_and_context_cleanup(self) -> None:
        values, is_open = asyncio.run(consume([1, 2, 3]))
        self.assertEqual(values, [1, 2, 3])
        self.assertFalse(is_open)

    def test_bound_is_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            asyncio.run(bounded_map([1], 0))


if __name__ == "__main__":
    unittest.main()
