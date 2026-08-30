from __future__ import annotations

import unittest
from fractions import Fraction

from coroutines import ResetStats, Snapshot, STOP, averager, stats_tracker
from delegation import flatten, report
from lazy_iterables import (
    Sentence,
    arithmetic_progression,
    chunked,
    fibonacci,
    read_until,
    take,
)


class Chapter17ExamplesTest(unittest.TestCase):
    def test_reusable_sentence_is_lazy_at_the_boundary(self) -> None:
        sentence = Sentence("one, two; three")

        self.assertEqual(list(sentence), ["one", "two", "three"])
        self.assertEqual(list(sentence), ["one", "two", "three"])

    def test_lazy_helpers_and_exact_progression(self) -> None:
        self.assertEqual(take(7, fibonacci()), [0, 1, 1, 2, 3, 5, 8])
        self.assertEqual(
            list(arithmetic_progression(Fraction(0), Fraction(1, 3), Fraction(1))),
            [Fraction(0), Fraction(1, 3), Fraction(2, 3)],
        )
        self.assertEqual(list(chunked(range(5), 2)), [(0, 1), (2, 3), (4,)])

        with self.assertRaisesRegex(ValueError, "positive"):
            list(chunked(range(3), 0))

    def test_iter_callable_sentinel(self) -> None:
        source = iter(["first", "second", ""])

        self.assertEqual(
            list(read_until(lambda: next(source), "")), ["first", "second"]
        )

    def test_flatten_and_yield_from_return_value(self) -> None:
        self.assertEqual(list(flatten([1, [2, (3, 4)], 5])), [1, 2, 3, 4, 5])
        self.assertEqual(list(report([1, 2, 3])), [1, 2, 3, {"total": 6}])

    def test_coroutine_return_value_and_stop_sentinel(self) -> None:
        coroutine = averager()
        next(coroutine)  # prime it before sending a non-None value
        coroutine.send(10)
        coroutine.send(30)

        with self.assertRaises(StopIteration) as exc_info:
            coroutine.send(STOP)

        self.assertEqual(exc_info.exception.value, (2, 20.0))

    def test_coroutine_throw_reset_and_close_cleanup_path(self) -> None:
        tracker = stats_tracker()

        self.assertEqual(next(tracker), Snapshot(0, 0.0))
        self.assertEqual(tracker.send(10), Snapshot(1, 10.0))
        self.assertEqual(tracker.throw(ResetStats), Snapshot(0, 0.0))
        self.assertEqual(tracker.send(5), Snapshot(1, 5.0))

        tracker.close()
        with self.assertRaises(StopIteration):
            next(tracker)


if __name__ == "__main__":
    unittest.main()
