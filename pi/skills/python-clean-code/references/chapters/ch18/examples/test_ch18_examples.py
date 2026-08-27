from __future__ import annotations

import unittest

from context_and_match import (
    Click,
    KeyPress,
    TypeText,
    captured_text,
    describe_action,
    find_first_even,
    suppress_zero_division,
)


class Chapter18ExamplesTest(unittest.TestCase):
    def test_context_manager_closes_on_normal_exit(self) -> None:
        with captured_text() as buffer:
            buffer.write("hello")
            self.assertEqual(buffer.getvalue(), "hello")
        self.assertTrue(buffer.closed)

    def test_context_manager_suppresses_only_expected_exception(self) -> None:
        with suppress_zero_division():
            1 / 0

        with self.assertRaises(NameError):
            with suppress_zero_division():
                raise NameError("bug")

    def test_structural_match_dispatch(self) -> None:
        self.assertEqual(describe_action(Click(3, 4)), "click(3, 4)")
        self.assertEqual(describe_action(TypeText("hi")), "type('hi')")
        self.assertEqual(describe_action(KeyPress("ENTER")), "press(ENTER)")
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            describe_action(TypeText(""))

    def test_for_else_not_found_semantics(self) -> None:
        self.assertEqual(find_first_even([1, 3, 4]), 4)
        self.assertIsNone(find_first_even([1, 3]))


if __name__ == "__main__":
    unittest.main()
