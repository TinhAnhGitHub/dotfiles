# P09 — Strategy, Policy, and Template Method

## Problem

One workflow contains several independently changing algorithms. P09 moves the variation behind a callable or small protocol while keeping orchestration stable.

## Use when

- A behavior has a real variation axis.
- Users or deployments select a policy at runtime.
- An algorithm needs isolated tests and metrics.

## Book theory

Mak ch33 compares Template Method inheritance with Strategy composition and favors the latter when behavior varies independently. Keen ch15 reinforces small interfaces and composition. A first-class function is the Python baseline.

## Minimal standard-library implementation

~~~python
from collections.abc import Callable, Iterable

Score = Callable[[str], float]


def choose(items: Iterable[str], score: Score) -> str:
    candidates = list(items)
    if not candidates:
        raise ValueError("no candidates")
    return max(candidates, key=score)


def shortest_name(value: str) -> float:
    return -len(value)
~~~

Use a `Protocol` or class only when the strategy needs state, lifecycle, or more than one operation. Do not force a class hierarchy around a one-line function.

## Production evidence to inspect

Identify the selection point, strategy contract, configuration source, and tests that run at least two strategies. Explain whether the abstraction improves testability or merely makes configuration dynamic.

## Production compromise

Training and serving projects often combine configuration flags, backend classes, and scheduler policies. This supports hardware-specific tuning but can produce many interacting axes. Keep capability validation near selection and expose the chosen strategy in logs/telemetry.

## When not to use it

Do not extract a strategy before two concrete behaviors exist or when the branch is a single stable business rule. A local conditional is more honest.

## Tests and practice

Use contract tests shared by every strategy, plus focused tests for policy-specific edge cases. Practice by adding FIFO and priority policies to the [registry-plugin exercise](../exercises/registry-plugin.md).

## Related IDs

P08 (selection), P13 (state), P14 (middleware), P16 (scheduling).

