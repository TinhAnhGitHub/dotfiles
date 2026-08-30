# State machine

## Intent

Represent legal lifecycle changes as an explicit mapping from `(state, event)` to `(next state,
action)`, with invalid transitions rejected at one boundary.

## Use when

Use a State Machine when behavior depends on a current lifecycle state and only some events are
legal there: payments, jobs, approvals, retries, sessions, or device modes. Use a small enum or
dataclass instead when there is no meaningful transition table.

## Why

Enums make the vocabulary finite and serializable. A transition table makes legal behavior visible,
while a generic context keeps the machine reusable across domains. Actions can remain ordinary
callables, and a decorator is a compact way to register several states for one event. The machine
should check the table before running an action, so an invalid event cannot partially perform work.

## Example

```python
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Generic, TypeVar

StateT = TypeVar("StateT", bound=Enum)
EventT = TypeVar("EventT", bound=Enum)
ContextT = TypeVar("ContextT")
Action = Callable[[ContextT], None]

class InvalidTransition(RuntimeError):
    pass

@dataclass
class StateMachine(Generic[StateT, EventT, ContextT]):
    transitions: dict[tuple[StateT, EventT], tuple[StateT, Action[ContextT]]] = field(
        default_factory=dict
    )

    def add_transition(self, source: StateT, event: EventT, target: StateT,
                       action: Action[ContextT]) -> None:
        key = (source, event)
        if key in self.transitions:
            raise ValueError(f"duplicate transition: {source.name}/{event.name}")
        self.transitions[key] = (target, action)

    def transition(self, sources: StateT | Iterable[StateT], event: EventT,
                   target: StateT):
        states = (sources,) if isinstance(sources, Enum) else tuple(sources)

        def decorator(action: Action[ContextT]) -> Action[ContextT]:
            for source in states:
                self.add_transition(source, event, target, action)
            return action
        return decorator

    def handle(self, context: ContextT, state: StateT, event: EventT) -> StateT:
        try:
            next_state, action = self.transitions[(state, event)]
        except KeyError as exc:
            raise InvalidTransition(
                f"cannot {event.name} when in {state.name}"
            ) from exc
        action(context)
        return next_state

class PayState(Enum):
    NEW = auto()
    AUTHORIZED = auto()
    CAPTURED = auto()
    FAILED = auto()
    REFUNDED = auto()

class PayEvent(Enum):
    AUTHORIZE = auto()
    CAPTURE = auto()
    FAIL = auto()
    REFUND = auto()

@dataclass
class PaymentContext:
    payment_id: str
    audit: list[str] = field(default_factory=list)

pay_sm: StateMachine[PayState, PayEvent, PaymentContext] = StateMachine()

@pay_sm.transition(PayState.NEW, PayEvent.AUTHORIZE, PayState.AUTHORIZED)
def authorize(ctx: PaymentContext) -> None:
    ctx.audit.append(f"{ctx.payment_id}: authorized")

@pay_sm.transition((PayState.NEW, PayState.AUTHORIZED), PayEvent.FAIL, PayState.FAILED)
def fail(ctx: PaymentContext) -> None:
    ctx.audit.append(f"{ctx.payment_id}: failed")

@pay_sm.transition(PayState.AUTHORIZED, PayEvent.CAPTURE, PayState.CAPTURED)
def capture(ctx: PaymentContext) -> None:
    ctx.audit.append(f"{ctx.payment_id}: captured")

@pay_sm.transition((PayState.AUTHORIZED, PayState.CAPTURED), PayEvent.REFUND, PayState.REFUNDED)
def refund(ctx: PaymentContext) -> None:
    ctx.audit.append(f"{ctx.payment_id}: refunded")
```

The decorators above define an explicit table such as `AUTHORIZED + CAPTURE -> CAPTURED`; the
generic machine does not know anything about payments. A `Payment` context can store the current
`PayState` and call `pay_sm.handle(context, state, event)`. This is adapted from the
[ArjanCodes state examples](https://github.com/ArjanCodes/examples/tree/main/2026/state), including
the [generic state-machine implementation](https://github.com/ArjanCodes/examples/blob/main/2026/state/sm.py)
and [state video](https://www.youtube.com/watch?v=OeirQdzYdnc) (2026 source, fetched 2026-08-30;
adapted).

Class-based state objects are justified when a state owns substantial behavior, entry/exit hooks,
state-specific collaborators, or invariants that would make table actions unwieldy. For a small
finite lifecycle, an enum, table, and context are easier to inspect and serialize than one class
per state; the [traditional ArjanCodes version](https://github.com/ArjanCodes/examples/blob/main/2026/state/traditional.py)
is the heavier alternative.

## When not to use

Do not build a machine for one boolean or a handful of unconditional method calls. Avoid a class
per state when states only name phases and actions are short. If branching, persistence, replay,
human approval, or parallel work is the main concern, use a workflow/graph abstraction around the
state machine rather than encoding the whole workflow as state methods.

## Trade-offs and tests

The table centralizes correctness but can grow with the product. Decide whether actions run before
or after persistence, whether repeated events are idempotent, and how state is serialized across
versions. Reject duplicate registrations at startup and keep transition errors domain-specific.

Test every allowed `(state, event)` pair and representative rejected pairs. Also test that an
invalid transition does not run its action, actions receive the same typed context, decorator
registration handles multiple source states, duplicate entries fail, and persisted enum values
remain compatible after a restart.

## Framework examples

### LangGraph — explicit graph state and edges

LangGraph solves the problem of coordinating stateful agent or workflow steps. Its `StateGraph`
uses a typed state schema, node functions, and edges; this is a workflow-level analogue of a state
machine. Use graph edges for routing and durable execution, but retain a domain transition table
when an event must be rejected for a particular enum state.

```python
from typing_extensions import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    status: str

def authorize(state: State) -> State:
    return {"status": "authorized"}

builder = StateGraph(State)
builder.add_node("authorize", authorize)
builder.add_edge(START, "authorize")
builder.add_edge("authorize", END)
graph = builder.compile()
```

Adapted from [LangGraph's graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
(current Python documentation, fetched 2026-08-30; adapted).
