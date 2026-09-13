# Exercise — Registry and Strategy Plugin

## Goal

Implement P08 and P09 for a pluggable scheduler with explicit registration, duplicate detection, and a shared strategy contract.

## Starting point

A scheduler receives jobs with a priority and chooses the next job. Support FIFO and priority strategies selected by a string configuration key.

## Sequence

1. Start with a dictionary and two plain functions.
2. Add an explicit `register(name, builder)` API.
3. Add a protocol only if a strategy needs state or lifecycle.
4. Add lazy plugin loading with an explicit error for an unavailable plugin.
5. Wire the registry in a composition root rather than importing global state from tests.

## Tests to require

- both strategies satisfy the same behavior contract;
- duplicate registration fails deterministically;
- an unknown key reports the available choices;
- plugin import failure preserves the original cause;
- test order cannot leak registrations between tests;
- a strategy can be replaced with a fake policy.

## Production comparison

Study the registry/factory page and the Transformers, pytest, Django, vLLM, and smolagents dossiers. For each, record whether registration is explicit, import-time, entry-point based, or runtime, and what compatibility checks exist.

## Deliverable

A registry module, two strategies, a composition root, and a test fixture that resets or scopes registration. State when the dictionary-only version is preferable.

