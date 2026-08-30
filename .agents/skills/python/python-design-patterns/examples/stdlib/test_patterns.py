from __future__ import annotations

import unittest

from patterns import (
    ALLOWED,
    EventBus,
    Status,
    WorkflowState,
    apply_strategy,
    compose_logger,
    counted,
    nonempty,
    registry,
)


class PatternTests(unittest.TestCase):
    def test_composition_combines_filter_and_output(self) -> None:
        output: list[str] = []
        log = compose_logger(output.append, lambda message: "keep" in message)

        log("drop")
        log("keep")

        self.assertEqual(output, ["keep"])

    def test_registry_rejects_duplicate_names(self) -> None:
        factories: dict[str, object] = {}
        register = registry(factories, "memory")
        register(lambda: "one")

        with self.assertRaisesRegex(ValueError, "duplicate"):
            register(lambda: "two")

    def test_strategy_is_replaceable(self) -> None:
        self.assertEqual(apply_strategy("hello", str.upper), "HELLO")
        self.assertEqual(apply_strategy("hello", lambda value: value[::-1]), "olleh")

    def test_decorator_preserves_metadata(self) -> None:
        @counted
        def add(left: int, right: int) -> int:
            return left + right

        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add.__name__, "add")
        self.assertEqual(add.__annotations__["return"], "int")

    def test_state_machine_rejects_invalid_transition(self) -> None:
        state = WorkflowState()
        self.assertIn(Status.RUNNING, ALLOWED[state.status])
        with self.assertRaisesRegex(ValueError, "invalid transition"):
            state.transition(Status.DONE)

    def test_event_bus_notifies_listeners(self) -> None:
        events: list[str] = []
        bus = EventBus()
        bus.subscribe(events.append)
        bus.publish("started")
        self.assertEqual(events, ["started"])

    def test_lazy_filter(self) -> None:
        self.assertEqual(list(nonempty(["", " a ", "  "])), [" a "])


if __name__ == "__main__":
    unittest.main()
