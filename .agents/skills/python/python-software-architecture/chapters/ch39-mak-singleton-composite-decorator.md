# Chapter 39: The Singleton, Composite, and Decorator Design Patterns

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 4: Design Patterns (Chapter 14)

## Core Idea
Three structural and creational patterns address object organization: Singleton restricts a class to a single instance (with significant caveats in Python); Composite composes objects into tree structures to treat individual items and groups uniformly; Decorator dynamically attaches additional responsibilities without subclassing.

## Frameworks Introduced
- **The Pythonic Singleton Spectrum**:
  - When to use: When exactly one instance of a coordinator or registry must exist globally.
  - How: Prefer a Python **module** as a natural singleton (modules are imported once and cached in `sys.modules`). If using a class, override `__new__()` or use a metaclass.
  - *Warning*: Singletons introduce hidden global state and make unit testing difficult; prefer Dependency Injection.
- **The Composite Pattern (Structural)**:
  - When to use: When modeling tree-like part-whole hierarchies (filesystems, GUI widget trees, organizational charts).
  - How: Define a common `Component` interface. `Leaf` classes implement behavior for terminal items; `Composite` classes maintain child components and delegate operations recursively.
- **The Decorator Pattern (Structural)**:
  - When to use: Adding responsibilities (caching, logging, encryption) dynamically to an object without subclassing.
  - How: Create a Decorator class that implements the Component interface and wraps a Component instance, augmenting its behavior before or after delegating.

## Key Concepts
- **Part-Whole Hierarchy**: A tree structure where nodes can contain either leaves or further nested subtrees.
- **Uniformity**: In Composite, client code treats a single leaf and a compound container with 1,000 leaves identically.
- **Dynamic Extension**: Adding features at runtime per object instance, rather than at compile-time for an entire class.
- **Metaclass Singleton**: Overriding `__call__` on a metaclass to manage class instantiation caching.

## Mental Models
- **Composite as Russian Nesting Dolls**: Opening a doll reveals either a solid wooden doll (Leaf) or another doll that can be opened in turn (Composite).
- **Decorator as Warm Winter Clothing**: You don't surgically alter your skin (subclassing) when it gets cold; you put on a sweater (Decorator), and over that, an overcoat (another Decorator).

## Anti-patterns
- **Using Singleton as a Global Variable Dump**: Turning singletons into dumping grounds for uncoordinated global variables, breaking test isolation.
- **Type Checking Inside Composite Clients**: Writing `isinstance(node, Composite)` in client code; the entire purpose of Composite is uniform interface treatment!
- **Over-Decorating with Confusing Layers**: Wrapping an object in 10 layers of decorators, making debugging and stack trace analysis difficult.

## Code Examples

```python
from abc import ABC, abstractmethod
from typing import List

# 1. COMPOSITE PATTERN: Filesystem Hierarchy
class FileSystemComponent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_size(self) -> int: ...

class File(FileSystemComponent):
    def __init__(self, name: str, size: int):
        super().__init__(name)
        self._size = size

    def get_size(self) -> int:
        return self._size

class Directory(FileSystemComponent):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: List[FileSystemComponent] = []

    def add(self, component: FileSystemComponent) -> None:
        self._children.append(component)

    def get_size(self) -> int:
        # Uniform recursive calculation
        return sum(child.get_size() for child in self._children)

# 2. DECORATOR PATTERN: Text Formatting
class Notifier(Protocol):
    def send(self, message: str) -> str: ...

class BasicEmailNotifier:
    def send(self, message: str) -> str:
        return f"Email: {message}"

class EncryptionDecorator:
    def __init__(self, wrappee: Notifier):
        self._wrappee = wrappee

    def send(self, message: str) -> str:
        encrypted = f"ENC({message})"
        return self._wrappee.send(encrypted)
```
- **What it demonstrates**: Composite treating files and directories uniformly, and Decorator augmenting message sending with encryption without inheritance.

## Reference Tables

| Pattern | Category | Primary Purpose | Python Alternative |
|---|---|---|---|
| **Singleton** | Creational | Guarantee 1 instance globally | Python module-level instance |
| **Composite** | Structural | Part-whole recursive trees | Standard lists/dicts or Generators |
| **Decorator** | Structural | Attach behavior dynamically | Python function decorators (`@wrap`) |

## Worked Example
Calculating shipping weight for nested packaging:
- An order contains `Box` (Composite) which holds `Item` (Leaf: 2 kg) and another `Box` (holds two `Item`s: 3 kg each, plus 0.5 kg box weight).
- Client simply calls `main_box.get_weight()`.
- Recursion naturally cascades through all nested containers without any conditional type checks.

## Key Takeaways
1. Avoid class-based Singletons; prefer Python modules or dependency injection.
2. Composite enables uniform treatment of individual objects and compositions of objects.
3. Decorator attaches new responsibilities dynamically without creating brittle subclass explosions.
4. Python's language features (modules, `@decorators`) provide idiomatic alternatives to classical GoF patterns.

## Connects To
- **Ch 32**: Composition over inheritance.
- **Ch 23**: Boundary observability implemented via decorators.
- **Ch 36**: Visiting composite structures using the Visitor pattern.
