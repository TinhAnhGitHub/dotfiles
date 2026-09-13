# Exercise — Durable Workflow State

## Goal

Implement P13 and P16 for a resumable job that can pause, retry, and compensate after failure.

## Starting point

A job downloads data, validates it, and publishes a result. It must not publish twice, and a worker may die after any step.

## Sequence

1. Define typed states and a legal transition table.
2. Add a checkpoint store port and an in-memory fake.
3. Make each step idempotent and persist the checkpoint before acknowledgment.
4. Add cancellation and bounded worker ownership with a context manager.
5. Add a compensation step for a published-but-invalid result.

## Tests to require

- illegal transitions fail;
- restart resumes from the last checkpoint;
- duplicate delivery does not duplicate the result;
- cancellation releases worker resources;
- one failed step is retried according to policy;
- compensation is observable and itself idempotent.

## Production comparison

Compare the P13/P16 pages with verl, LangGraph, CrewAI, Ray, OpenAI Agents, and Home Assistant dossiers. Identify whether state is in memory, serialized, broker-backed, or database-backed, and what happens after worker failure.

## Deliverable

A state model, durable-shaped port, worker lifecycle, failure-injection tests, and a state-transition diagram. Explain when an enum plus a table is better than polymorphic State classes.

