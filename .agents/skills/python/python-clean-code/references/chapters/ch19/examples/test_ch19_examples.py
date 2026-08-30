from __future__ import annotations

import asyncio
import unittest

from concurrency_models import async_map, threaded_map


class Chapter19ExamplesTest(unittest.TestCase):
    def test_threaded_map_preserves_input_order(self) -> None:
        self.assertEqual(
            threaded_map(lambda value: value * 2, range(5)), [0, 2, 4, 6, 8]
        )

    def test_threaded_map_rejects_invalid_worker_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            threaded_map(str, [1], workers=0)

    def test_threaded_map_preserves_none_results(self) -> None:
        self.assertEqual(threaded_map(lambda _value: None, [1, 2]), [None, None])

    def test_async_map_is_cooperative(self) -> None:
        self.assertEqual(
            asyncio.run(async_map(lambda value: value + 1, [1, 2, 3])), [2, 3, 4]
        )


if __name__ == "__main__":
    unittest.main()
