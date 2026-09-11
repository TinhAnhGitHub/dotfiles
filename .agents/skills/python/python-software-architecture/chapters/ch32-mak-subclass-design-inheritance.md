# Chapter 32: Design Subclasses Right

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 3: Design the Application Right (Chapter 7)

## Core Idea
Inheritance is the strongest coupling relationship in object-oriented programming; subclasses must strictly adhere to the Liskov Substitution Principle (LSP), and developers should favor object composition over class inheritance whenever reuse is desired without an authentic *is-a* relationship.

## Frameworks Introduced
- **The Liskov Substitution Principle (LSP) Verification**:
  - When to use: Designing class hierarchies and subclass relationships.
  - How: If $S$ is a subtype of $T$, then objects of type $T$ may be replaced with objects of type $S$ without altering any desirable properties of the program:
    - Subclasses must accept all arguments the superclass accepts (cannot strengthen preconditions).
    - Subclasses must return at least what the superclass promises (cannot weaken postconditions).
    - Subclasses must not throw new unexpected exceptions not thrown by the superclass.
- **Composition Over Inheritance (Favor Composition)**:
  - When to use: Sharing behavior across classes without creating rigid hierarchies.
  - How: Instead of subclassing `class Car(Engine)`, give `Car` an instance of `Engine` (`self._engine = Engine()`) and delegate operations.

## Key Concepts
- **Is-a vs. Has-a Relationship**: Inheritance models *is-a* (a `Sparrow` is a `Bird`); composition models *has-a* (a `Car` has an `Engine`).
- **Fragile Base Class Problem**: Changes to a superclass inadvertently break subclasses because subclasses depend on base class implementation details.
- **Liskov Substitution Principle (LSP)**: Subtypes must be completely substitutable for their supertypes.
- **Delegation**: Passing a method call from an outer object to an internal composed object.

## Mental Models
- **The Square-Rectangle Dilemma**: In mathematics, a Square is a Rectangle. In software, if a `Rectangle` allows setting width and height independently (`rect.set_width(5); rect.set_height(10)`), a `Square` cannot inherit from it without breaking caller expectations (LSP violation).
- **Inheritance as Marriage, Composition as Employment**: Inheritance binds you for life; changes to the base class affect all descendants. Composition is an employment contract: if an employee isn't working out, hire a new one that satisfies the interface.

## Anti-patterns
- **Inheritance for Code Reuse Alone**: Subclassing `list` or `dict` just to get convenient helper methods, exposing 40 irrelevant methods to callers.
- **Overriding Methods with `pass`**: Inheriting from a base class and implementing a method as `raise NotImplementedError("This subclass doesn't support that")`; immediate LSP violation!
- **Deep Inheritance Hierarchies**: Creating class trees 5 or 6 levels deep (`Animal -> Mammal -> Carnivore -> Canine -> Dog -> Bulldog`).

## Code Examples

```python
# LSP Violation: Square inherits from Rectangle
class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def set_width(self, width: float):
        self.width = width

    def set_height(self, height: float):
        self.height = height

    @property
    def area(self) -> float:
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width: float):
        self.width = width
        self.height = width  # Mutates height unexpectedly!

    def set_height(self, height: float):
        self.width = height
        self.height = height

# Fails client expectation:
def verify_area(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(4)
    # Caller expects area == 20! If Square is passed, area is 16!
    assert rect.area == 20, f"Expected 20, got {rect.area}"

# Composition Over Inheritance (The Solution)
class Stack:
    """Composes a list instead of inheriting from it."""
    def __init__(self):
        self._items = []

    def push(self, item) -> None:
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def __len__(self) -> int:
        return len(self._items)
```
- **What it demonstrates**: The classic Square/Rectangle LSP violation alongside a clean composition example where `Stack` encapsulates a Python `list` without exposing 40 list methods.

## Reference Tables

| Criteria | Inheritance (`class B(A)`) | Composition (`B has instance of A`) |
|---|---|---|
| **Relationship** | "Is-a" | "Has-a" / "Uses-a" |
| **Coupling** | Tight (compile-time / definition-time) | Loose (runtime delegation) |
| **Flexibility** | Static; cannot change superclass at runtime | Dynamic; collaborators can be swapped |
| **Interface Exposure** | Exposes all superclass public methods | Exposes only methods explicitly chosen |
| **Refactoring Risk**| High (Fragile base class problem) | Low (Implementation hidden behind boundary) |

## Worked Example
Refactoring a payroll system from inheritance to strategy composition:
- *Before (Inheritance)*: `Employee -> HourlyEmployee`, `SalariedEmployee`, `CommissionedEmployee`.
  - Problem: What happens if an employee transitions from hourly to salaried? You must instantiate a new object and migrate history. What if an employee is salaried AND commissioned? Multiple inheritance explosion!
- *After (Composition)*:
```python
class Employee:
    def __init__(self, name: str, pay_strategy):
        self.name = name
        self.pay_strategy = pay_strategy

    def calculate_pay(self) -> float:
        return self.pay_strategy.compute()
```
An employee can now change pay strategies dynamically at runtime with zero class explosions.

## Key Takeaways
1. Favor object composition over class inheritance.
2. Ensure all subclasses satisfy the Liskov Substitution Principle.
3. Never subclass a data structure solely to reuse code; compose it and delegate.
4. Keep inheritance hierarchies shallow (maximum 1–2 levels).

## Connects To
- **Ch 15**: Liskov Substitution Principle in SOLID.
- **Ch 33**: Template Method (inheritance) vs Strategy (composition).
- **Ch 34**: Factory patterns for instantiating polymorphic hierarchies.
