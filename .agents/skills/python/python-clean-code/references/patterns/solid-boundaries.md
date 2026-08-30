# SOLID boundaries in Python

## Use when

Use SOLID as a diagnostic when a class has several reasons to change, a branch grows with every
feature, a subtype cannot honor its parent contract, or high-level code constructs concrete
infrastructure directly.

## Why

SOLID turns vague 'this is hard to change' feedback into local questions: which responsibility
changes, which extension should be additive, which contract is substitutable, which interface is
needed, and which dependency should point inward.

## When not to use

Do not create an interface, abstract base class, or dependency-injection container for a stable
one-implementation function. SOLID is guidance for change pressure, not a requirement to split every
small module into layers.

## Trade-offs

Narrow boundaries improve testing and extension but introduce names, adapters, and indirection.
Too many interfaces make simple code harder to follow. Prefer a small Protocol and one composition
root over a hierarchy or service locator.

## Tests

Test each responsibility in isolation, contract tests for every adapter, substitutability of
implementations, and the composition root with real wiring. Also test failure behavior at each
boundary and ensure side effects occur only in the owning adapter.

## Python code

The [ArjanCodes 2026 `coupling` examples](https://github.com/ArjanCodes/examples/tree/main/2026/coupling)
and [`god` examples](https://github.com/ArjanCodes/examples/tree/main/2026/god) are practical
diagnostics. A use case depends on small ports, while adapters own infrastructure:

```python
from typing import Protocol


class InventoryPort(Protocol):
    def get_stock(self, sku: str) -> int: ...

    def reserve(self, sku: str, quantity: int) -> int: ...


class ReserveStock:
    def __init__(self, inventory: InventoryPort) -> None:
        self.inventory = inventory

    def execute(self, sku: str, quantity: int) -> int:
        if self.inventory.get_stock(sku) < quantity:
            raise ValueError("not enough stock")
        return self.inventory.reserve(sku, quantity)
```

This is dependency inversion and interface segregation in a small form: the use case needs only
inventory behavior, not a god repository. The [2026 ports source](https://github.com/ArjanCodes/examples/blob/main/2026/ports/domain/ports.py)
shows the same port/adapter split.

A policy pipeline is an additive open/closed boundary:

```python
from collections.abc import Callable


Policy = Callable[[Request], Request]


def apply_policies(request: Request, policies: list[Policy]) -> Request:
    for policy in policies:
        request = policy(request)
    return request
```

Each policy has one responsibility and can be tested without the pipeline. The [2026 policy
tree](https://github.com/ArjanCodes/examples/tree/main/2026/policy) and [policy video](https://www.youtube.com/watch?v=wYeDGkdMi3g)
show the configured registry form. The [zedr clean-code-python table of contents](https://github.com/zedr/clean-code-python#table-of-contents)
provides the complementary SRP, OCP, LSP, ISP, DIP checklist: use it to diagnose coupling, not to
justify abstractions without a change axis.

## Framework examples

### FastAPI dependency boundary

FastAPI dependencies make the composition root visible while the route depends on behavior:

```python
from typing import Annotated, Protocol
from fastapi import Depends, FastAPI, HTTPException


class UserReader(Protocol):
    def find(self, user_id: int) -> User | None: ...


def get_user_reader() -> UserReader:
    return SqlUserReader()


app = FastAPI()


@app.get("/users/{user_id}")
def get_user(user_id: int, reader: Annotated[UserReader, Depends(get_user_reader)]) -> User:
    user = reader.find(user_id)
    if user is None:
        raise HTTPException(status_code=404)
    return user
```

The route is testable with a fake reader, while the SQL adapter owns the database side effect. See
the [FastAPI dependencies documentation](https://fastapi.tiangolo.com/tutorial/dependencies/).
