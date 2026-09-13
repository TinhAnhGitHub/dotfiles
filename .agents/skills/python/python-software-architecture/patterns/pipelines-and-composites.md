# P15 — Composite, Iterator, Visitor, and Pipelines

## Problem

Tree-shaped data and multi-stage transformations become tangled when traversal, operation, and composition are inseparable. P15 gives uniform child behavior or explicitly ordered stages.

## Use when

- Callers should treat a group and an item uniformly.
- Processing is naturally staged and each step needs isolation.
- Multiple operations traverse the same tree.

## Book theory

Mak ch36 covers Python iterators and Visitor; ch39 covers Composite. In Python, an iterator or a list of callables is often preferable to a named class pattern.

## Minimal standard-library implementation

~~~python
from collections.abc import Callable, Iterable
from typing import TypeVar


T = TypeVar("T")


def pipeline(value: T, steps: Iterable[Callable[[T], T]]) -> T:
    for step in steps:
        value = step(value)
    return value


class Group:
    def __init__(self, children: Iterable["Group | str"]) -> None:
        self.children = tuple(children)

    def walk(self) -> Iterable[str]:
        for child in self.children:
            if isinstance(child, Group):
                yield from child.walk()
            else:
                yield child
~~~

The pipeline makes stage order explicit; the composite provides one traversal interface. Use Visitor only when operations vary more often than the tree shape.

## Production evidence to inspect

Find stage registration/order, data contracts between stages, traversal ownership, short-circuit behavior, and tests for partial or failing stages.

## Production compromise

Data and ML systems commonly mix Python orchestration with native parsers, vectorized kernels, or external queues. The Python pipeline remains a useful control-plane seam even when individual stages are not pure Python.

## When not to use it

For three fixed transformations, a straight-line function is clearer. Do not introduce Visitor or Composite just to demonstrate a GoF name.

## Tests and practice

Test each stage independently, order and cancellation, empty trees, and one integration path. The event-driven training exercise includes a staged projection variant.

## Related IDs

P09 (policy), P10 (events), P14 (middleware), P16 (resource lifecycle).

