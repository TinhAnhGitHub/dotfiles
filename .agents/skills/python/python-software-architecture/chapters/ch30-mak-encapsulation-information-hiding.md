# Chapter 30: Hide Class Implementations

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 3: Design the Application Right (Chapter 5)

## Core Idea
Information hiding and encapsulation conceal internal implementation details behind stable public interfaces, allowing developers to change data structures, algorithms, and storage mechanisms without affecting client code.

## Frameworks Introduced
- **The Information Hiding Principle (Parnas)**:
  - When to use: Designing classes, modules, and library packages.
  - How: Identify design decisions that are most likely to change (data representation, algorithm choice, third-party libraries). Encapsulate each changeable decision inside a dedicated class or module.
- **Python Encapsulation Protocol**:
  - When to use: Exposing attributes and operations in Python classes.
  - How:
    1. Default all state attributes to protected with a leading underscore (`_attribute`).
    2. Expose read access via `@property` getters.
    3. Provide `@attribute.setter` only when mutation is necessary, enforcing validation within the setter.
    4. Return defensive copies of mutable internal collections (tuples, copied lists, frozen sets).

## Key Concepts
- **Information Hiding**: Designing modules so internal details are hidden from outside callers.
- **Encapsulation**: Bundling data with the methods that operate on that data and restricting direct access to components.
- **Interface vs. Implementation**: The interface is the *what* (method signatures, return types); the implementation is the *how* (data structures, algorithms).
- **Defensive Copy**: Returning a copy of an internal collection so that outside callers cannot mutate the internal state.

## Mental Models
- **The Car Dashboard Interface**: The driver turns the steering wheel and presses the gas pedal (interface). They do not directly manipulate fuel injectors or rack-and-pinion gears (implementation). You can swap a gas engine for an electric motor without changing the driver's interface.
- **Underscores Are Social Contracts in Python**: While Python doesn't enforce private fields with compiler errors, a leading underscore `_` establishes an inviolable boundary for professional developers.

## Anti-patterns
- **Public Mutable Collections**: Exposing a raw list (`self.items = []`) directly; callers can bypass validation by calling `order.items.append(None)`.
- **Java-Style Getter/Setter Proliferation**: Writing redundant `get_x()` and `set_x()` for every single field before any validation logic is needed; use `@property` when needed.
- **Leaking Data Structures**: Naming methods after internal representations, such as `get_user_hashmap()`.

## Code Examples

```python
from typing import List, Tuple

class BankLedger:
    def __init__(self):
        # Implementation detail: stored as a list of tuples
        self._entries: list[tuple[str, float]] = []

    def record_transaction(self, description: str, amount: float) -> None:
        if amount == 0.0:
            raise ValueError("Transaction amount cannot be zero")
        self._entries.append((description, amount))

    @property
    def balance(self) -> float:
        # Computed property; callers don't know entries are summed on the fly
        return sum(amount for _, amount in self._entries)

    @property
    def entries(self) -> Tuple[tuple[str, float], ...]:
        # Defensive copy: callers cannot append or pop from outside!
        return tuple(self._entries)
```
- **What it demonstrates**: Complete information hiding: `_entries` is protected, `balance` is a computed property, and `entries` returns an immutable tuple.

## Reference Tables

| Python Convention | Meaning | Intended Usage |
|---|---|---|
| `name` | Public API | Safe for clients to call and depend on |
| `_name` | Internal / Protected | Implementation detail; subject to change |
| `__name` | Name-mangled | Used rarely to avoid name clashes in subclasses |
| `@property` | Computed Attribute | Exposes read access with optional validation |

## Worked Example
Changing an internal data structure without breaking client code:
- *Initial Design*: `StudentRecord` stores grades in a flat Python list `self._grades = [90, 85, 92]`.
- *Requirement Change*: Grades now require timestamps and course codes. We change internal storage to a dictionary `self._grades = {"MATH101": [(90, '2025-01-10')]}`.
- *Preserved Public Interface*:
```python
@property
def average_grade(self) -> float:
    # We update the calculation internally to traverse the dictionary
    all_scores = [score for records in self._grades.values() for score, _ in records]
    return sum(all_scores) / len(all_scores) if all_scores else 0.0
```
Callers invoking `student.average_grade` continue to function without modifying a single line of client code!

## Key Takeaways
1. Hide design decisions that are likely to change behind stable interfaces.
2. Use leading underscores (`_field`) to mark internal implementation details.
3. Leverage `@property` for computed attributes and validation.
4. Always return defensive copies of mutable internal collections to prevent external state corruption.

## Connects To
- **Ch 29**: Good class design and high cohesion.
- **Ch 31**: The Principle of Least Astonishment.
- **Ch 5**: Information hiding across Clean Architecture layers.
