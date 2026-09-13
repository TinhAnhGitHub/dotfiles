# P03/P04 — Repository and Unit of Work

## Problem

Use cases become coupled to SQL sessions, ORM models, and transaction APIs when they perform persistence directly. P03 hides collection access behind a port; P04 owns the transaction boundary and makes commit/rollback behavior explicit.

## Use when

- Business code must run against a fake or more than one persistence mechanism.
- Several repository writes must commit or roll back together.
- Database lifecycle currently leaks into handlers.

## Book theory

Percival & Gregory develop Repository in ch02 and Unit of Work in ch06, then wire them in ch13. Keen (ch18, ch20) puts ports in the application layer and concrete drivers outside it. Mak ch35 frames the concrete repository as an adapter.

## Minimal standard-library implementation

~~~python
from contextlib import AbstractContextManager
from typing import Protocol


class OrderRepository(Protocol):
    def get(self, order_id: str) -> object | None: ...
    def add(self, order: object) -> None: ...


class UnitOfWork(AbstractContextManager["UnitOfWork"]):
    orders: OrderRepository

    def __enter__(self) -> "UnitOfWork":
        return self

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False
~~~

The protocol is the seam; the concrete UoW owns a session and repository implementations. Always use it as `with uow:` so exceptional paths are visible.

## Production evidence to inspect

Find the port definition, concrete construction, use-case call site, and tests that prove rollback or fake substitution. A direct `session.commit()` in a handler is evidence against a clean UoW, not evidence for one.

## Production compromise

Read-heavy systems often bypass a repository with direct queries, and high-throughput workers may batch or checkpoint instead of committing every entity. Those are valid choices when documented as read/write or lifecycle boundaries; they should not be disguised as a domain repository.

## When not to use it

For one immutable read or a tiny script, a query function is clearer. Do not add a generic repository that merely forwards every ORM method; it adds indirection without protecting a boundary.

## Tests and practice

Use a fake repository for use-case tests, then one integration test for the real adapter and one failure test for rollback. The [repository/UoW exercise](../exercises/repository-uow.md) walks through both.

## Related IDs

P02 (aggregate scope), P05 (use case), P06 (ports), P17 (test seams).

