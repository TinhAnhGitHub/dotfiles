# Exercise — Provider Adapter and Fallback Router

## Goal

Implement P06, P07, P12, P14, and P17 for a normalized text-generation port backed by two incompatible providers.

## Starting point

Define a `TextProvider.generate(prompt)` port. Provider A returns a string; provider B returns a response object with a nested text field and different timeout/error types.

## Sequence

1. Define the application-facing port and result/error vocabulary.
2. Write one adapter per provider; translate names, response shape, and retryable errors.
3. Add a router with ordered fallback and an explicit policy for non-retryable errors.
4. Compose providers from configuration in one `build_app()` function.
5. Add timing and provider-selection middleware without logging secrets or prompts.

## Tests to require

- both adapters satisfy one contract suite;
- provider-specific errors map to stable application errors;
- timeout falls back exactly once;
- non-idempotent operations are not silently retried;
- the router preserves the final cause chain;
- telemetry records provider and latency while redacting payloads.

## Production comparison

Read the P12 and P14 pages and compare LiteLLM, HTTPX, smolagents, Transformers, and TensorRT-LLM dossiers. Document which provider differences are normalized and which remain escape hatches.

## Deliverable

A pure application port, two adapters, a router, composition root, contract tests, and a paragraph explaining why a universal lowest-common-denominator API can reduce capability.

