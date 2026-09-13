# P08 — Factory, Registry, and Plugin Architecture

## Problem

Construction and capability selection become a central `if/elif` switch. A factory hides creation; a registry makes supported implementations discoverable and extensible; a plugin boundary defines how third parties enter the system.

## Use when

- Implementations are selected by a stable external key.
- Extensions should be added without editing the core dispatch path.
- Construction includes validation, version checks, or lifecycle policy.

## Book theory

Mak ch34 describes Factory Method and Abstract Factory; in Python a module-level function or dictionary is often the better first step. Keen ch20 places plugin mechanics at the framework boundary. The registry is a practical extension of those ideas, not permission for hidden global state.

## Minimal standard-library implementation

~~~python
from collections.abc import Callable


class DuplicateKey(ValueError):
    pass


ModelBuilder = Callable[[str], object]
_builders: dict[str, ModelBuilder] = {}


def register(name: str, builder: ModelBuilder) -> None:
    if name in _builders:
        raise DuplicateKey(name)
    _builders[name] = builder


def build(name: str, checkpoint: str) -> object:
    try:
        return _builders[name](checkpoint)
    except KeyError as exc:
        raise ValueError(f"unknown model: {name}") from exc
~~~

Explicit registration is easier to test than import-time magic. If discovery is needed, validate plugin metadata and report import/version failures at startup.

## Production evidence to inspect

Inspect registration, discovery timing, construction, missing-plugin errors, and duplicate-key tests. Record whether the registry is process-global, scoped, or injected, and whether entry-point/package versions are checked.

## Production compromise

Transformers, pytest, Django, and vLLM use dynamic maps or registries for extensibility. This keeps public APIs stable but adds import-order, startup, and compatibility complexity. Production code commonly combines a registry with explicit allow-lists, lazy loading, and smoke tests.

## When not to use it

If there are only two implementations and selection is local, use a dictionary or conditional in the composition root. A global registry is harmful when hidden mutation or import order can change behavior.

## Tests and practice

Test duplicate registration, unknown keys, lazy import failure, and a plugin contract. Use the [registry-plugin exercise](../exercises/registry-plugin.md).

## Related IDs

P07 (composition), P09 (strategy), P12 (provider router), P17 (test harness).

