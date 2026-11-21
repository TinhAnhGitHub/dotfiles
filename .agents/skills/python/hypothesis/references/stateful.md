# Stateful testing

Stateful testing explores sequences of operations against a model. Use it for
protocols, caches, data structures, and APIs where the interesting behavior is
the order of calls, not a single call.

## RuleBasedStateMachine

```python
from hypothesis import strategies as st
from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    initialize,
    invariant,
    precondition,
    rule,
)


class QueueMachine(RuleBasedStateMachine):
    items = Bundle("items")

    def __init__(self) -> None:
        super().__init__()
        self.queue: list[int] = []
        self.model: list[int] = []

    @initialize(target=items)
    def seed(self) -> int:
        return 0

    @rule(target=items, value=st.integers(min_value=0, max_value=100))
    def push(self, value: int) -> int:
        self.queue.append(value)
        self.model.append(value)
        return value

    @rule(items=items)
    def pop(self, items: int) -> None:
        if self.queue:
            assert self.queue.pop(0) == self.model.pop(0)

    @precondition(lambda self: len(self.queue) > 0)
    @rule()
    def pop_when_nonempty(self) -> None:
        assert self.queue.pop(0) == self.model.pop(0)

    @invariant()
    def matches_model(self) -> None:
        assert self.queue == self.model


TestQueueMachine = QueueMachine.TestCase
```

## Key concepts

- `@rule(...)` defines a step. Arguments are strategies; `target=Bundle` returns a
  value into a bundle for later steps.
- `@initialize(target=...)` seeds bundles at the start of a run.
- `@precondition(lambda self: ...)` gates a rule; use it instead of `assume()` in
  rules.
- `@invariant()` runs after every step — the main place to compare the system under
  test with a simple model.
- `Bundle` values are drawn from previous steps; declare one bundle per value kind.
- Export `Machine.TestCase` as `TestMachine` so pytest collects it.
- `settings(stateful_step_count=...)` controls the number of steps per run.

## Gotchas

- Keep the model simple and obviously correct; a complex model can hide bugs in
  both implementations.
- Do not use function-scoped pytest fixtures inside a state machine — the machine
  runs many steps in one test function.
- Shrinking a state-machine failure produces a step sequence; turn it into a
  permanent regression test.
- Prefer `@precondition` over early returns in rules — an early return silently
  skips the step and weakens the property.
