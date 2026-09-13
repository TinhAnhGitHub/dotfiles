# P17 — Testing Seams, Fitness Tests, ACL, and Strangler Migration

## Problem

Architecture decays when boundaries are only intentions. P17 makes seams replaceable, tests contracts and dependency direction, and lets a legacy system be migrated incrementally behind an anti-corruption layer (ACL).

## Use when

- A port needs fast fake-first tests.
- Import/dependency rules must remain true as the code grows.
- A legacy path must coexist with a new implementation during migration.

## Book theory

Percival ch03 and ch05 emphasize coupling-aware abstractions and high/low gear testing. Keen ch21 and ch25 cover clean test boundaries and architecture fitness tests; ch24 describes Strangler Fig and ACL migration. Mak ch26–ch27 supplies a feedback loop for improving design safely.

## Minimal standard-library implementation

~~~python
from typing import Protocol


class Clock(Protocol):
    def now(self) -> int: ...


def expires_at(clock: Clock, ttl: int) -> int:
    return clock.now() + ttl


class FakeClock:
    def __init__(self, value: int) -> None:
        self.value = value

    def now(self) -> int:
        return self.value
~~~

The same port can receive a fake, a contract-tested adapter, or a legacy ACL. A fitness test can scan imports and fail when domain code imports a framework.

## Production evidence to inspect

Record fakes, fixtures, contract/plugin harnesses, integration tests, failure-injection/performance tests, and import-boundary checks. A green unit suite does not prove an adapter contract or dependency direction.

## Production compromise

Mature projects mix unit, integration, golden, performance, and end-to-end tests. They often permit carefully documented framework imports in performance-critical or generated modules. The useful question is whether the exception is isolated and observable, not whether the repository is perfectly pure.

## When not to use it

Do not mock every collaborator or write a fitness rule that encodes incidental directory layout. Test externally visible contracts and high-risk boundaries.

## Tests and practice

Start with a fake port test, add one adapter contract test, one integration test, and one architecture check. Practice in the [provider-adapter exercise](../exercises/provider-adapter.md) and compare the pytest/HTTPX dossiers.

## Related IDs

All IDs can benefit from P17; it is especially important for P03, P06, P12, P13, and P16.

