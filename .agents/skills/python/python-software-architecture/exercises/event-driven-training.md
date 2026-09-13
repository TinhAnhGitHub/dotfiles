# Exercise — Event-Driven Training and Projection

## Goal

Implement P10, P11, P15, and P17 as a small training-run event system with an independent read projection.

## Starting point

A training run emits `RunStarted`, `CheckpointSaved`, and `RunFinished` events. A dashboard projection tracks status and latest checkpoint.

## Sequence

1. Define immutable event types and one command handler per command.
2. Implement an in-process bus with explicit ordering and failure policy.
3. Add an idempotent projection that can rebuild from an event list.
4. Add a staged pipeline for validation, enrichment, and export.
5. Add an integration event adapter only after local semantics are tested.

## Tests to require

- commands have one handler and events can fan out;
- event handlers have documented retry/isolation behavior;
- duplicate events do not corrupt the projection;
- replay produces the same projection as live processing;
- a failed export does not invalidate the committed training state;
- the pipeline exposes stage failures and preserves cancellation.

## Production comparison

Compare the P10/P11/P15 pages with OpenRLHF, Ray, AutoGen, CrewAI, Home Assistant, MCP Python SDK, and the evaluation/tooling dossiers. Separate in-process events from durable broker delivery and state which guarantees are actually present.

## Deliverable

A bus, event schema, projection, replay command, pipeline, and tests. Write a short theory-versus-practice note describing why production systems often keep the control plane in Python while moving the hot path to native code.

