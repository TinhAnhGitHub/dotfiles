# P13 — State Machine, Workflow, and Saga

## Problem

Lifecycle-heavy work accumulates invalid transitions, implicit retries, and lost progress. P13 makes state, legal transitions, persistence, and compensation explicit.

## Use when

- Work can pause, resume, retry, or outlive one process.
- Failure requires a compensating action.
- Behavior depends on current state rather than only input.

## Book theory

Mak ch38 presents State as an alternative to conditionals. Keen ch18 and ch24 place workflow orchestration at the application/migration boundary. In an event-driven system, a Saga coordinates multiple transactions and compensates rather than pretending they are one atomic transaction.

## Minimal standard-library implementation

~~~python
from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    status: Status = Status.PENDING

    def transition(self, target: Status) -> None:
        allowed = {
            Status.PENDING: {Status.RUNNING},
            Status.RUNNING: {Status.DONE, Status.FAILED},
            Status.FAILED: {Status.RUNNING},
            Status.DONE: set(),
        }
        if target not in allowed[self.status]:
            raise ValueError(f"{self.status} -> {target} is invalid")
        self.status = target
~~~

Persist the transition or a durable event before acknowledging work that must survive process failure. A saga adds step records and compensations around this small state machine.

## Production evidence to inspect

Find typed state, transition validation, checkpoints, worker recovery, durable storage, and failure-injection tests. Separate an enum used for display from a real state machine with enforced transitions.

## Production compromise

Production workflows often allow idempotent repeat operations and use external orchestration systems instead of polymorphic state classes. This sacrifices some local elegance for observability, restartability, and operational control.

## When not to use it

For two states and one transition, a boolean or enum plus a guard is enough. Do not distribute a state machine before the lifecycle actually outlives a call.

## Tests and practice

Test the transition table, resume after each checkpoint, duplicate delivery, timeout, cancellation, and compensation. Use the [workflow-state exercise](../exercises/workflow-state.md).

## Related IDs

P10 (messages), P16 (scheduling), P17 (failure tests).

