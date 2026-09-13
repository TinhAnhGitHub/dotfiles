# P12 — Adapter, Façade, and Provider Router

## Problem

External providers expose incompatible request shapes, capabilities, error types, and retry semantics. P12 gives the application a stable contract and translates provider-specific behavior at one boundary.

## Use when

- Callers should switch providers without changing use cases.
- Several APIs are semantically similar but not identical.
- Fallback, capability checks, and error normalization need one owner.

## Book theory

Mak ch35 distinguishes Adapter (interface translation) from Façade (simplifying a subsystem). Percival ch02 and Keen ch19–ch20 apply the same boundary idea to repositories and gateways.

## Minimal standard-library implementation

~~~python
from dataclasses import dataclass
from typing import Protocol


class ProviderError(RuntimeError):
    pass


class TextProvider(Protocol):
    def generate(self, prompt: str) -> str: ...


@dataclass
class ProviderRouter:
    providers: tuple[TextProvider, ...]

    def generate(self, prompt: str) -> str:
        failures: list[Exception] = []
        for provider in self.providers:
            try:
                return provider.generate(prompt)
            except (TimeoutError, ProviderError) as exc:
                failures.append(exc)
        raise ProviderError(f"all providers failed: {len(failures)}")
~~~

The router is a façade over multiple adapters. It must not silently retry non-idempotent operations or hide useful error context.

## Production evidence to inspect

Identify the normalized interface, translation layer, provider selection, error mapping, retry/fallback rules, and contract tests. Capture the exact external capabilities that are lost or represented as optional fields.

## Production compromise

Universal LLM routers commonly expose a broad lowest-common-denominator API and provider escape hatches. This improves portability but can hide quality, cost, streaming, and tool-call differences. Make provider choice and fallback visible in telemetry.

## When not to use it

Do not build a universal abstraction around one provider or APIs with no meaningful semantic overlap. A thin provider wrapper is clearer.

## Tests and practice

Run a shared contract suite against each adapter; inject timeout, rate-limit, and malformed-response failures. Practice in the [provider-adapter exercise](../exercises/provider-adapter.md).

## Related IDs

P06 (ports), P08 (registry), P09 (strategy), P14 (middleware), P16 (lifecycle).

