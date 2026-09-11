# Chapter 26: The Path to Well-Designed Software

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 1: Introduction (Chapter 1)

## Core Idea
Good software design is an ongoing discipline that prioritizes maintainability, flexibility, and comprehensibility, actively combating software rot and the insidious leaking of changes across module boundaries.

## Frameworks Introduced
- **The Design Evaluation Framework**:
  - When to use: Assessing existing code or proposed designs before implementing features.
  - How: Evaluate against five criteria:
    1. **Maintainability**: Can bugs be fixed and changes made without breaking unrelated features?
    2. **Extensibility**: Can new capabilities be added with minimal changes to existing code?
    3. **Comprehensibility**: Can a new developer understand the codebase without consulting the author?
    4. **Reusability**: Can components be repurposed in different contexts?
    5. **Robustness**: Does the software handle unexpected inputs and failures gracefully?
- **The Leaking Changes Diagnostic**:
  - When to use: Detecting hidden coupling in a software system.
  - How: If modifying a business rule in Component A requires edits in Component B, C, and D, changes are leaking; introduce abstractions and boundaries to encapsulate the variation.

## Key Concepts
- **Software Rot (Software Decay)**: The gradual degradation of software quality over time caused by ad-hoc patches, accumulating technical debt, and compromised boundaries.
- **Accidental vs. Essential Complexity**: Essential complexity inheres in the business domain; accidental complexity is self-inflicted by poor design choices, bloated abstractions, and tight coupling.
- **Leaking Changes**: A architectural flaw where internal implementation alterations force ripple-effect modifications across callers.
- **Principle of Separation of Concerns**: Isolating distinct features and responsibilities so each can be developed, tested, and modified independently.

## Mental Models
- **Think of Code as a Living City, Not a Finished Monument**: A codebase requires continuous zoning (boundaries), road maintenance (refactoring), and infrastructure upgrades to prevent slums (software rot).
- **The Ripple Effect Gauge**: The quality of an architecture is inversely proportional to the number of files touched when fulfilling a new single requirement.

## Anti-patterns
- **The Fix-It-Later Trap**: Writing rushed, unmodular code with the promise of "refactoring later"; deadlines ensure "later" never comes.
- **Copy-Paste Architecture**: Duplicating logic across functions or files rather than parameterizing or abstracting shared behavior.
- **Shotgun Surgery**: A single business requirement change forces dozens of micro-edits scattered throughout the codebase.

## Code Examples

```python
# Before: Leaking Changes (Data structures and business rules exposed directly)
class OrderManager:
    def __init__(self):
        # Raw nested dictionaries exposed to all callers
        self.orders = {}

    def add_item(self, order_id: str, item_name: str, price: float):
        if order_id not in self.orders:
            self.orders[order_id] = {"items": [], "total": 0.0}
        self.orders[order_id]["items"].append((item_name, price))
        # Leaking change: Every caller that calculates tax or discounts must repeat this logic!
        self.orders[order_id]["total"] += price

# After: Encapsulated Design (Business rules contained within entity boundaries)
class OrderItem:
    def __init__(self, name: str, price: float):
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.name = name
        self.price = price

class Order:
    def __init__(self, order_id: str):
        self.id = order_id
        self._items: list[OrderItem] = []

    def add_item(self, item: OrderItem) -> None:
        self._items.append(item)

    @property
    def total(self) -> float:
        return sum(item.price for item in self._items)

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self._items)  # Defensive copy protects internal list
```
- **What it demonstrates**: Transition from primitive dictionary manipulation that leaks calculation changes to an encapsulated object model with immutable exposure.

## Reference Tables

| Attribute | Poorly Designed Software | Well-Designed Software |
|---|---|---|
| **Adding New Feature** | Touches dozens of files (Shotgun Surgery) | Adds new class/module; minimal edits |
| **Locating Bugs** | Tracing intertwined global state | Isolated to a single class or module |
| **Testing** | Requires running full app with live DB | Fast unit tests with clear boundaries |
| **Onboarding** | Requires tribal knowledge / guidance | Code reads like ubiquitous domain language |

## Worked Example
Diagnosing and fixing leaking changes in tax calculations:
Problem: Sales tax was calculated in 4 places: checkout web handler, invoice generator, PDF receipt printer, and admin summary.
Refactoring step:
1. Extract tax rule into a dedicated `TaxCalculator` strategy or domain function.
2. Direct all 4 components to depend on `TaxCalculator.calculate(order.total)`.
3. When tax regulations change, edit only `TaxCalculator.py`; the 4 callers require zero changes.

## Key Takeaways
1. Software design is not an afterthought; maintainability must be built in from day one.
2. Measure design quality by the locality of changes: touching one feature should touch one file.
3. Guard against software rot by eliminating accidental complexity and keeping boundaries sharp.
4. Protect internal state with defensive copies and clean properties.

## Connects To
- **Ch 27**: Iterative approaches to refining software design.
- **Ch 29**: Good class design to build the application right.
- **Ch 14**: Clean Architecture fundamentals.
