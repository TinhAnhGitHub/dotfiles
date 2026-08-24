from __future__ import annotations

import unittest

from concurrent_executors import collect_failures, completed_map, ordered_map


class Chapter20ExamplesTest(unittest.TestCase):
    def test_ordered_map_preserves_input_order(self) -> None:
        self.assertEqual(ordered_map(lambda value: value * 2, [3, 1, 2]), [6, 2, 4])

    def test_completed_map_returns_same_values_in_completion_order(self) -> None:
        result = completed_map(lambda value: value * 2, [3, 1, 2])
        self.assertEqual(set(result), {2, 4, 6})

    def test_worker_failures_are_observed(self) -> None:
        def fail_on_two(value: int) -> int:
            if value == 2:
                raise ValueError("bad value")
            return value

        failures = collect_failures(fail_on_two, [1, 2, 3])
        self.assertEqual([str(error) for error in failures], ["bad value"])


if __name__ == "__main__":
    unittest.main()
