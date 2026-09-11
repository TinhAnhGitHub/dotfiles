# Chapter 34: The Factory Method and Abstract Factory Design Patterns

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 4: Design Patterns (Chapter 9)

## Core Idea
Factory patterns encapsulate object creation: Factory Method delegates instantiation to subclasses, while Abstract Factory provides an interface for creating entire families of related or dependent objects without specifying concrete classes.

## Frameworks Introduced
- **Factory Method Pattern (Creational)**:
  - When to use: When a class cannot anticipate the class of objects it must create, delegating creation to subclasses.
  - How: Define an abstract creator with a `create_product()` method. Concrete creator subclasses implement this method to return concrete products.
- **Abstract Factory Pattern (Creational)**:
  - When to use: When a system must configure families of matching products (e.g. DarkTheme vs LightTheme UI widgets).
  - How: Define an abstract factory interface with creation methods for each family member (`create_button()`, `create_dialog()`). Concrete factories produce matching product suites.
- **Pythonic Factory with Dictionaries (Registry Factory)**:
  - When to use: Dynamic instantiation based on configuration keys or string names.
  - How: Map type strings to constructor callables in a dictionary registry.

## Key Concepts
- **Creational Encapsulation**: Isolating `new` / instantiation operations so client code depends only on product interfaces.
- **Product Family**: A set of related objects designed to work together (e.g. `MacButton` and `MacCheckbox`).
- **Virtual Constructor**: Another name for Factory Method; invoking a creation method whose concrete return type is determined by subclasses.
- **Dependency Decoupling**: Clients never mention concrete product class names.

## Mental Models
- **Factory Method as a Cookie Cutter**: The dough recipe and baking oven are standardized; subclasses provide the specific cookie cutter shape (Stars vs Trees).
- **Abstract Factory as an Interior Decorator**: If you choose the "Victorian" decorator, you get Victorian chairs, sofas, and lamps that visually harmonize; you don't accidentally get a neon cyberpunk coffee table.

## Anti-patterns
- **Hardcoding Class Names Across Code**: Writing `button = WindowsButton()` directly in 50 application controllers.
- **Mismatched Product Families**: Mixing `MacScrollBar` with `WindowsButton` because classes were instantiated directly without a coordinating factory.
- **Over-Engineering with 10 Factory Layers**: Introducing factories when a simple direct instantiation `User(name)` would suffice without polymorphism.

## Code Examples

```python
from abc import ABC, abstractmethod
from typing import Protocol

# 1. Product Interfaces
class Button(Protocol):
    def render(self) -> str: ...

class Dialog(Protocol):
    def show(self) -> str: ...

# 2. Abstract Factory Interface
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_dialog(self) -> Dialog: ...

# 3. Concrete Families
class LightButton:
    def render(self) -> str: return "[Light Button]"

class LightDialog:
    def show(self) -> str: return "Light Dialog Window"

class LightThemeFactory(GUIFactory):
    def create_button(self) -> Button: return LightButton()
    def create_dialog(self) -> Dialog: return LightDialog()

class DarkButton:
    def render(self) -> str: return "[Dark Button]"

class DarkDialog:
    def show(self) -> str: return "Dark Dialog Window"

class DarkThemeFactory(GUIFactory):
    def create_button(self) -> Button: return DarkButton()
    def create_dialog(self) -> Dialog: return DarkDialog()

# 4. Client Code depends ONLY on abstract factory
class Application:
    def __init__(self, factory: GUIFactory):
        self.button = factory.create_button()
        self.dialog = factory.create_dialog()

    def run(self):
        print(self.button.render())
        print(self.dialog.show())
```
- **What it demonstrates**: Abstract Factory guaranteeing that UI buttons and dialogs are created from the same visual theme family without concrete class coupling.

## Reference Tables

| Pattern | Scope | Key Intent | Mechanism |
|---|---|---|---|
| **Factory Method** | Class-based | Creates one product | Inheritance (subclass overrides creation) |
| **Abstract Factory** | Object-based | Creates families of products | Composition (client holds factory object) |
| **Registry Factory** | Function-based | Instantiates by string/key | Dictionary mapping to constructors |

## Worked Example
A Pythonic registry factory for database connectors:

```python
class DatabaseConnector(Protocol):
    def connect(self) -> None: ...

class PostgresConnector: ...
class MongoConnector: ...
class SQLiteConnector: ...

CONNECTOR_REGISTRY = {
    "postgres": PostgresConnector,
    "mongo": MongoConnector,
    "sqlite": SQLiteConnector,
}

def get_connector(db_type: str, **kwargs) -> DatabaseConnector:
    creator = CONNECTOR_REGISTRY.get(db_type.lower())
    if not creator:
        raise ValueError(f"Unsupported database type: {db_type}")
    return creator(**kwargs)
```

## Key Takeaways
1. Encapsulate object creation to decouple clients from concrete classes.
2. Factory Method uses inheritance to vary a single product.
3. Abstract Factory uses composition to produce matching product families.
4. Python dictionaries mapping strings to callables offer a simple, powerful factory alternative.

## Connects To
- **Ch 13**: Bootstrapping and Dependency Injection as the ultimate factory.
- **Ch 33**: Using factories to instantiate strategies.
- **Ch 35**: Abstracting adapter creation.
