# Chapter 15: SOLID Foundations: Building Robust Python Applications

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 1: Foundations of Clean Architecture in Python (Chapter 2)

## Core Idea
The SOLID principles provide the foundational design rules for Python object-oriented systems, preventing software rot and enabling clean layer boundaries through cohesion and loose coupling.

## Frameworks Introduced
- **The SOLID Principles in Modern Python**:
  - **Single Responsibility Principle (SRP)**: A module or class should have one, and only one, reason to change.
  - **Open/Closed Principle (OCP)**: Software entities should be open for extension, but closed for modification (using Protocols, ABCs, or Strategy pattern).
  - **Liskov Substitution Principle (LSP)**: Subtypes must be substitutable for their base types without altering system correctness.
  - **Interface Segregation Principle (ISP)**: Clients should not be forced to depend upon interfaces they do not use (prefer small, client-specific Protocols).
  - **Dependency Inversion Principle (DIP)**: High-level modules should not depend on low-level modules; both should depend on abstractions.

## Key Concepts
- **Reason to Change**: The stakeholder or actor whose requirements dictate changes to a class. If multiple actors demand changes to the same file, SRP is violated.
- **Structural Subtyping (`typing.Protocol`)**: Python's static duck-typing mechanism; classes satisfy an interface implicitly by matching method signatures.
- **Nominal Subtyping (`abc.ABC`)**: Explicit inheritance from an abstract base class.
- **Fat Interface**: An interface with 20 methods where a client only needs two; violated ISP.
- **Inversion of Control (IoC)**: Transferring control of object creation and flow to a framework or composition root.

## Mental Models
- **SRP as Organizational Alignment**: Align code modules with the business department that requests changes (e.g. Finance changes `PayCalculator`, Logistics changes `DeliveryPlanner`).
- **ISP as Tailored Power Adapters**: Don't force a two-prong lamp to plug into a specialized industrial multi-phase socket; provide a simple two-prong socket.

## Anti-patterns
- **God Classes**: A class named `UserManager` or `OrderProcessor` that handles database access, password hashing, email notifications, and business calculations.
- **Fragile Base Class**: Altering a base class method and unexpectedly breaking subclasses that made implicit assumptions about execution order.
- **Broad Repository Interfaces**: Defining an `AllInOneRepository` with 30 methods, forcing all use cases to depend on methods they never call.

## Code Examples

```python
from typing import Protocol

# 1. ISP: Segregated Interfaces instead of one bloated repository
class Reader(Protocol):
    def read(self, item_id: str) -> dict | None:
        ...

class Writer(Protocol):
    def write(self, item: dict) -> None:
        ...

class Auditable(Protocol):
    def log_audit(self, action: str) -> None:
        ...

# A client that only needs to read does not depend on write or audit!
class ReadItemService:
    def __init__(self, reader: Reader):
        self._reader = reader

    def get_summary(self, item_id: str) -> str:
        data = self._reader.read(item_id)
        return f"Item: {data['name']}" if data else "Not Found"

# 2. OCP & DIP: Open for extension via Protocol
class NotificationSender(Protocol):
    def send(self, recipient: str, message: str) -> bool:
        ...

class EmailSender:
    def send(self, recipient: str, message: str) -> bool:
        # concrete SMTP sending
        return True

class SmsSender:
    def send(self, recipient: str, message: str) -> bool:
        # concrete Twilio sending
        return True

class AlertManager:
    """Closed for modification: supports new senders without code changes."""
    def __init__(self, sender: NotificationSender):
        self._sender = sender

    def trigger_alert(self, user: str, msg: str) -> None:
        self._sender.send(user, msg)
```
- **What it demonstrates**: Single responsibility with segregated protocols (ISP) and dependency inversion (DIP), allowing seamless extension without modifying existing classes (OCP).

## Reference Tables

| Principle | Core Python Mechanism | Architectural Impact |
|---|---|---|
| **SRP** | Small, focused modules & classes | High cohesion, minimal ripple effects |
| **OCP** | Protocols, composition, plugins | Adding features without touching existing code |
| **LSP** | True behavioral contracts, typing | Safe polymorphism without runtime type checks |
| **ISP** | Focused `typing.Protocol` classes | Decoupled consumers; easy test doubles |
| **DIP** | Dependency injection into constructors | Inverted dependency arrows; pure core layers |

## Worked Example
Refactoring an SRP violation in an invoice system:

Before (Violates SRP):
```python
class Invoice:
    def calculate_total(self): ...
    def save_to_database(self): ...
    def send_email_receipt(self): ...
    def export_pdf(self): ...
```
Any change to PDF styling, SMTP settings, database schema, or tax rates forces changes to `Invoice`.

After (SOLID Refactoring):
```python
class Invoice:
    """Only calculates totals and manages items (Domain Entity)."""
    def calculate_total(self) -> float: ...

class InvoiceRepository(Protocol):
    """Data persistence abstraction (ISP/DIP Port)."""
    def save(self, invoice: Invoice) -> None: ...

class InvoiceNotifier(Protocol):
    """Communication abstraction."""
    def send_receipt(self, invoice: Invoice) -> None: ...

class PdfExporter:
    """Dedicated export responsibility."""
    def export(self, invoice: Invoice) -> bytes: ...
```

## Key Takeaways
1. Design classes with a single reason to change tied to a specific business responsibility.
2. Prefer small, role-based protocols over monolithic interface contracts.
3. Depend on abstractions (Protocols/ABCs), never on concrete infrastructure classes.
4. Subclasses and implementations must honor the behavioral contract of their abstractions.

## Connects To
- **Ch 14**: Clean Architecture relies on DIP to enforce the inward dependency rule.
- **Ch 16**: Type-enhanced Python using `Protocol` to implement SOLID statically.
- **Ch 29**: Ronald Mak's principles of good class design.
