# Chapter 33: The Template Method and Strategy Design Patterns

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 4: Design Patterns (Chapter 8)

## Core Idea
Template Method and Strategy both solve the problem of varying algorithms: Template Method uses inheritance to fix the skeleton of an algorithm in a base class while letting subclasses override specific steps; Strategy uses composition to encapsulate interchangeable algorithm families behind a common interface.

## Frameworks Introduced
- **Template Method Pattern (Behavioral)**:
  - When to use: When an algorithm follows an invariant multi-step sequence, but individual steps differ across variations.
  - How: Define the algorithm skeleton in a base class method (`template_method()`). Mark abstract or hook methods (`step1()`, `step2()`) for subclasses to override.
- **Strategy Pattern (Behavioral)**:
  - When to use: When an algorithm family must be interchangeable at runtime or when you want to avoid class explosion through composition.
  - How: Define a common Strategy interface (or `Protocol`). Implement concrete strategy classes. Pass the chosen strategy into the Context class via dependency injection.

## Key Concepts
- **Hollywood Principle**: "Don't call us, we'll call you." In Template Method, the high-level base class controls the workflow and calls low-level subclass hooks.
- **Context**: The class that uses a Strategy to execute a task.
- **Hook Method**: A method in a Template base class with a default (often empty) implementation that subclasses can optionally override.
- **First-Class Functions as Strategies**: In Python, functions are first-class objects; a simple function can serve as a strategy without needing a dedicated class!

## Mental Models
- **Template Method as a Tax Form**: The tax form layout is fixed: Step 1: Total income; Step 2: Deductions; Step 3: Compute tax. Subclasses fill in the specific blanks.
- **Strategy as Interchangeable Tires**: Your car doesn't care whether you bolt on summer tires, winter snow tires, or racing slicks; all share the same wheel hub interface.

## Anti-patterns
- **Sprawling `if/elif` Chains**: Switching on type strings (`if algo == "quick": ... elif algo == "merge": ...`) instead of injecting a strategy.
- **Overriding Template Skeletons**: Subclasses overriding the main `template_method()` itself, defeating the purpose of the pattern.
- **Over-Classifying in Python**: Creating 5 tiny Strategy classes when 5 simple lambda functions or standard functions would suffice.

## Code Examples

```python
from abc import ABC, abstractmethod
from typing import Protocol, Callable

# 1. Template Method Pattern (Inheritance)
class DataMiner(ABC):
    def mine(self, path: str):
        raw_data = self.open_file(path)
        data = self.parse_data(raw_data)
        analysis = self.analyze_data(data)
        self.send_report(analysis)

    @abstractmethod
    def open_file(self, path: str): ...

    @abstractmethod
    def parse_data(self, raw_data): ...

    def analyze_data(self, data):
        return f"Analyzed {len(data)} items"

    def send_report(self, analysis):
        print(f"Report: {analysis}")

# 2. Strategy Pattern (Composition + Python Callables)
class DiscountStrategy(Protocol):
    def calculate(self, total: float) -> float:
        ...

def no_discount(total: float) -> float:
    return total

def percentage_discount(percent: float) -> Callable[[float], float]:
    return lambda total: total * (1.0 - percent / 100.0)

class Checkout:
    def __init__(self, discount: Callable[[float], float] = no_discount):
        self._discount = discount

    def get_final_total(self, cart_total: float) -> float:
        return self._discount(cart_total)
```
- **What it demonstrates**: Template Method fixing an algorithmic skeleton via abstract base class, and Strategy utilizing lightweight Python callables.

## Reference Tables

| Aspect | Template Method | Strategy |
|---|---|---|
| **Mechanism** | Class inheritance (Static) | Object composition (Dynamic) |
| **Runtime Swapping** | No (fixed at class definition) | Yes (swap strategy on the fly) |
| **Granularity** | Varies individual steps of algorithm | Replaces the entire algorithm |
| **Coupling** | Tight coupling to base class | Loose coupling to strategy interface |
| **Pythonic Simplicity** | Requires `abc.ABC` | Can use simple first-class functions |

## Worked Example
Migrating from Template Method to Strategy when requirements demand runtime flexibility:
- *Problem*: A report exporter used Template Method (`PdfReport`, `HtmlReport`). Requirement changed: the user must be able to change formats on the fly from a dropdown menu without instantiating a new report object.
- *Solution*: Extract formatting into a Strategy Protocol `ReportFormatter`. Inject the chosen formatter into a single `ReportGenerator` context at runtime.

## Key Takeaways
1. Template Method varies steps within an algorithm using inheritance.
2. Strategy replaces an entire algorithm using composition and delegation.
3. In Python, first-class functions and callables provide the cleanest, lightest implementation of the Strategy pattern.
4. Prefer Strategy over Template Method when runtime algorithm swapping is required.

## Connects To
- **Ch 32**: Composition over inheritance.
- **Ch 34**: Factory patterns for creating strategies.
- **Ch 15**: Open/Closed Principle via polymorphic strategies.
