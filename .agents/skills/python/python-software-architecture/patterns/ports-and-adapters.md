# P05/P06 — Application Service, Ports, and Adapters

## Problem

A use case needs capabilities such as storage, clocks, model inference, or notifications, but should not know whether they are supplied by SQL, HTTP, a GPU runtime, or a test fake.

## Use when

- The same use case has multiple delivery mechanisms.
- An external dependency changes independently of policy.
- A boundary needs a contract that tests can implement cheaply.

## Book theory

Percival ch04 introduces a service layer and ch13 wires dependencies at startup. Keen ch14, ch16, and ch18–ch20 applies the inward dependency rule: inner code owns ports and outer code implements adapters. Mak ch35 describes translation of incompatible interfaces.

## Minimal standard-library implementation

~~~python
from dataclasses import dataclass
from typing import Protocol


class Catalog(Protocol):
    def price_for(self, sku: str) -> int: ...


class PaymentGateway(Protocol):
    def charge(self, cents: int, customer: str) -> str: ...


@dataclass(frozen=True)
class Checkout:
    catalog: Catalog
    payments: PaymentGateway

    def run(self, sku: str, customer: str) -> str:
        cents = self.catalog.price_for(sku)
        if cents <= 0:
            raise ValueError("invalid price")
        return self.payments.charge(cents, customer)
~~~

`Checkout` is the application service (P05); `Catalog` and `PaymentGateway` are ports (P06). SQL, HTTP, and in-memory implementations remain outside this code.

## Production evidence to inspect

Trace the port definition, adapter implementation, composition root, and a test that supplies a fake. Record whether the port is a `Protocol`, ABC, callable, or configuration object; the choice affects discoverability and runtime checks.

## Production compromise

Framework-heavy Python projects often let Pydantic models or transport response types cross an application boundary to avoid repeated mapping. Keep the leak at the edge, document it, and test the adapter’s translation and error mapping.

## When not to use it

For one stable library call with no replacement pressure, a direct function call is clearer. An interface for every helper is abstraction noise.

## Tests and practice

Test the use case with tiny fakes and test each adapter with a contract suite. The [provider-adapter exercise](../exercises/provider-adapter.md) adds a second provider without changing the use case.

## Related IDs

P03 (repository), P05 (use case), P07 (composition), P12 (adapter/router).

