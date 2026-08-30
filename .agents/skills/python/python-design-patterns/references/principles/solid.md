# SOLID as Python boundary diagnostics

## Intent

Use the SOLID principles as questions about change pressure, ownership, and behavioral contracts.
They are a way to find a useful boundary, not a requirement to create an abstract base class for
every noun in a domain.

## Use when

Use this pattern when:

- a class has several independent reasons to change;
- a branch or switch grows whenever a feature is added;
- a subtype cannot honor the behavior or signature promised by its parent;
- consumers depend on methods they do not use; or
- a use case constructs concrete databases, SDK clients, or transports directly.

## Why

SOLID gives names to common coupling problems:

- Single Responsibility Principle (SRP) separates responsibilities with different change owners.
- Open/Closed Principle (OCP) makes a new policy or adapter additive at a stable extension point.
- Liskov Substitution Principle (LSP) protects the behavioral contract callers rely on.
- Interface Segregation Principle (ISP) keeps a protocol as small as the consumer's needs.
- Dependency Inversion Principle (DIP) points application code at behavior and puts construction in
  a composition root.

In Python, the smallest useful boundary is often a function, a `Protocol`, or a callable parameter.
An interface hierarchy is only one possible implementation.

## Example

The common pressure is a god service that reads data, calculates metrics, formats a report, and
writes it. Extract responsibilities, then inject the changing behavior:

```python
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Sale:
    amount: float


class SalesReader(Protocol):
    def read(self) -> Iterable[Sale]: ...


class ReportWriter(Protocol):
    def write(self, report: str) -> None: ...


def total_sales(sales: Iterable[Sale]) -> float:
    return sum(sale.amount for sale in sales)


def build_report(reader: SalesReader) -> str:
    return f"total={total_sales(reader.read()):.2f}"


def publish_report(reader: SalesReader, writer: ReportWriter) -> None:
    writer.write(build_report(reader))
```

The use case depends only on the two operations it consumes. A database reader, an in-memory fake,
or a queue writer can satisfy the protocols without inheriting from a shared framework class. The
composition root owns concrete construction.

## When not to use

Do not split a stable, one-implementation function into five interfaces. Do not introduce a
container or service locator when passing one dependency is clear. Do not use OCP to preserve a
bad abstraction: if a second implementation does not exist and no change axis is visible, a direct
function or module is usually better.

## Trade-offs

Narrow boundaries improve testing and make extension safer, but they add names, wiring, and
indirection. Protocols provide structural flexibility but do not validate runtime behavior by
themselves. Splitting a class can make control flow harder to follow if the responsibilities
always change together. Revisit a boundary when it starts accumulating convenience methods or
leaking infrastructure types.

## Tests

Test each responsibility with a small fake or pure input. Add contract tests for every adapter that
implements a protocol. Test that all substitutable implementations preserve return values,
exceptions, ordering, and side effects. Test the composition root once with real wiring, and keep
infrastructure failures at the adapter boundary.

## ArjanCodes and clean-code examples (adapted)

The [ArjanCodes SOLID video](https://www.youtube.com/watch?v=uxwjXLjJOoM) progressively extracts
metrics, readers, writers, and filters from a report class, then shows the same principles with
callables and a configuration dataclass. The [2026 `coupling` example](https://github.com/ArjanCodes/examples/tree/main/2026/coupling)
uses narrow flight, hotel, email, analytics, and repository ports, while the [`god` example](https://github.com/ArjanCodes/examples/tree/main/2026/god)
separates orchestration from transformation, evaluation, persistence, and reporting.

The supplied [zedr clean-code-python guide](https://github.com/zedr/clean-code-python#table-of-contents)
provides the complementary SRP/OCP/LSP/ISP/DIP and DRY checklist. Its useful Python lesson is to
keep these as diagnostics for a real reason to change; the direct `Protocol` boundaries above are
the smallest reusable form.

## Framework examples

### PydanticAI — typed dependency inversion (adapted)

PydanticAI lets an agent declare the dependency type its tools consume. The agent and tool depend
on `AppDeps`, while the composition root decides which database or service implementation to put in
the dependency object:

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext


class AccountReader:
    def balance(self, account_id: str) -> str:
        return "100.00"


@dataclass
class AppDeps:
    accounts: AccountReader


agent = Agent("openai:gpt-4o", deps_type=AppDeps)


@agent.tool
def account_balance(ctx: RunContext[AppDeps], account_id: str) -> str:
    return ctx.deps.accounts.balance(account_id)
```

This solves the problem of tools reaching into global SDK clients or databases. A test can pass a
fake `AccountReader`, and the production composition root can pass a real adapter. The example is
adapted from the [PydanticAI dependency documentation](https://pydantic.dev/docs/ai/core-concepts/dependencies/).
