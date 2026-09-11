# Chapter 38: The State Design Pattern

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 4: Design Patterns (Chapter 13)

## Core Idea
The State pattern allows an object to alter its behavior when its internal state changes, encapsulating state-dependent behavior into separate State classes and eliminating sprawling conditional (`if/elif/else`) state machines.

## Frameworks Introduced
- **The State Pattern Hierarchy**:
  - When to use: When an object's behavior changes dramatically based on its state, and its methods are riddled with matching `if state == ...` statements.
  - How:
    1. Define an abstract `State` interface with methods for all possible actions.
    2. Create a concrete class for each distinct state (`DraftState`, `ReviewState`, `PublishedState`).
    3. The `Context` object maintains a reference to its current `State` instance.
    4. Client actions delegate directly to the current state: `self._state.handle_action(self)`.
    5. State transitions occur by reassigning the context's state reference: `context.change_state(NewState())`.

## Key Concepts
- **Finite State Machine (FSM)**: A mathematical computation model consisting of a finite number of states, transitions between them, and actions.
- **Context**: The object whose behavior changes as its internal state changes.
- **Concrete State**: A class encapsulating the behaviors associated with one specific state of the context.
- **State Transition**: Moving from one valid state to another in response to an event or action.

## Mental Models
- **The Vending Machine**: In `NoCoinState`, pushing the dispense button does nothing. In `HasCoinState`, pushing the button dispenses a drink and transitions to `SoldState`. The machine delegates its buttons to its current state.
- **Polymorphism Over Conditionals**: Instead of asking *"What state am I in?"* with an if-statement, let polymorphic state objects respond to the call directly.

## Anti-patterns
- **Sprawling `if self.state ==` Blocks**: Having 10 methods in an entity, each containing identical 5-branch `if/elif` blocks switching on an enum.
- **Invalid State Transitions**: Allowing transitions that bypass business rules (e.g. jumping directly from `Draft` to `Archived` without review).
- **Leaking State Objects to Callers**: Letting client code manipulate state objects directly rather than calling methods on the Context.

## Code Examples

```python
from abc import ABC, abstractmethod

# 1. State Interface
class DocumentState(ABC):
    @abstractmethod
    def publish(self, doc: "Document") -> None: ...
    @abstractmethod
    def review(self, doc: "Document") -> None: ...

# 2. Context
class Document:
    def __init__(self):
        self._state: DocumentState = DraftState()

    def set_state(self, state: DocumentState) -> None:
        self._state = state

    def publish(self) -> None:
        self._state.publish(self)

    def review(self) -> None:
        self._state.review(self)

# 3. Concrete States encapsulating transitions
class DraftState(DocumentState):
    def review(self, doc: Document) -> None:
        print("Document submitted for review.")
        doc.set_state(ModerationState())

    def publish(self, doc: Document) -> None:
        print("Cannot publish directly from Draft; must be reviewed first.")

class ModerationState(DocumentState):
    def review(self, doc: Document) -> None:
        print("Already in moderation review.")

    def publish(self, doc: Document) -> None:
        print("Document approved and published!")
        doc.set_state(PublishedState())

class PublishedState(DocumentState):
    def review(self, doc: Document) -> None:
        print("Published document cannot be reviewed.")

    def publish(self, doc: Document) -> None:
        print("Already published.")
```
- **What it demonstrates**: Eliminating state conditionals by encapsulating `Draft`, `Moderation`, and `Published` behaviors and transition logic in dedicated state classes.

## Reference Tables

| Approach | Conditional Enum Switches | State Pattern |
|---|---|---|
| **Adding New State** | Must edit every single method (violates OCP) | Add 1 new State subclass (satisfies OCP) |
| **Method Clarity** | Obscured by massive `if/elif` trees | Clean, 1-line delegation to state |
| **Transition Logic** | Scattered across multiple methods | Explicitly defined in state classes |
| **Maintainability** | Degrades exponentially with new states | Scales linearly; states isolated |

## Worked Example
Implementing an Order state machine with cancellation rules:
- States: `PendingPayment`, `Processing`, `Shipped`, `Delivered`, `Cancelled`.
- Rule: An order can be cancelled *only* if it is in `PendingPayment` or `Processing`. Once `Shipped`, cancellation is forbidden.
- In `ShippedState`:
```python
class ShippedState(OrderState):
    def cancel(self, order: Order) -> None:
        raise DomainException("Cannot cancel an order that has already shipped")
```
No if-statements needed; the active state enforces the invariant automatically.

## Key Takeaways
1. State pattern replaces complex conditionals with polymorphic state classes.
2. Encapsulate state-specific behavior and transitions in dedicated classes.
3. Adding new states satisfies the Open/Closed Principle: existing state classes remain untouched.
4. Clients interact exclusively with the Context object; state management is internal.

## Connects To
- **Ch 33**: Strategy pattern has identical UML structure but different intent (swapping algorithms vs altering behavior across state changes).
- **Ch 7**: Enforcing aggregate invariants across state transitions.
- **Ch 17**: Domain entity lifecycles.
