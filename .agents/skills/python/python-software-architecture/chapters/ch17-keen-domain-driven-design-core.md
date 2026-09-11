# Chapter 17: Domain-Driven Design: Crafting the Core Business Logic

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 2: Implementing Clean Architecture Layers (Chapter 4)

## Core Idea
The Domain layer is the heart of Clean Architecture; using Domain-Driven Design tactical patterns (Entities, Value Objects, and Domain Services), it encapsulates core business rules and protects invariants independently of any technology.

## Frameworks Introduced
- **The Core DDD Tactical Triad**:
  - **Entities**: Objects possessing unique identity and a lifecycle of state mutations (e.g. `Account`, `Subscription`).
  - **Value Objects**: Immutable objects whose equality is based on attribute values, used to model descriptors and quantities (e.g. `Money`, `EmailAddress`).
  - **Domain Services**: Pure business algorithms or operations that naturally involve multiple entities or external calculations without belonging to a single entity.
- **Invariant Enforcement Framework**:
  - When to use: Ensuring domain objects cannot exist in an invalid state.
  - How: Enforce invariants inside entity constructors and state transition methods; raise domain exceptions immediately when invalid state is attempted.

## Key Concepts
- **Ubiquitous Language**: The domain vocabulary shared by developers and domain experts, reflected directly in class and method names.
- **Invariant**: A business condition that must always remain satisfied throughout an entity's lifecycle.
- **Domain Event**: A notification raised by the domain model when a significant state transition occurs.
- **Anemic Domain Model (Anti-pattern)**: A domain layer consisting solely of property getters/setters with zero business logic.
- **Rich Domain Model**: A domain model where entities contain both data and the operations that mutate that data.

## Mental Models
- **Entities Have Passports; Value Objects Are Currency**: Two passports with identical names are different people (Entity identity); two \$20 bills are completely interchangeable (Value Object).
- **Make Illegal States Unrepresentable**: Design constructors and types so that an object cannot even be created if its invariants are violated.

## Anti-patterns
- **Public State Mutation**: Exposing raw mutable properties (e.g. `account.balance = 500`) allowing outside code to bypass validation rules.
- **Business Logic in Services Only**: Treating entities as data structures and writing all business rules in service classes (procedural code disguised as OOP).
- **Injecting Repositories into Entities**: Letting an entity call `self.repo.save()`; persistence belongs strictly outside the domain model.

## Code Examples

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import List

class DomainException(Exception): ...
class InsufficientFunds(DomainException): ...
class InvalidAmount(DomainException): ...

# 1. Value Object: Immutable with self-validation
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < Decimal("0.00"):
            raise InvalidAmount("Amount cannot be negative")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

# 2. Entity: Unique Identity and Rich State Operations
class BankAccount:
    def __init__(self, account_id: str, owner_id: str, initial_balance: Money):
        self.id = account_id
        self.owner_id = owner_id
        self._balance = initial_balance
        self._is_active = True

    @property
    def balance(self) -> Money:
        return self._balance

    def deposit(self, money: Money) -> None:
        if not self._is_active:
            raise DomainException("Account is closed")
        self._balance = self._balance.add(money)

    def withdraw(self, money: Money) -> None:
        if not self._is_active:
            raise DomainException("Account is closed")
        if self._balance.amount < money.amount:
            raise InsufficientFunds(f"Cannot withdraw {money.amount}; balance is {self._balance.amount}")
        self._balance = Money(self._balance.amount - money.amount, self._balance.currency)
```
- **What it demonstrates**: Rich domain modeling with an immutable Value Object (`Money`) and an Entity (`BankAccount`) strictly guarding state mutations and invariants.

## Reference Tables

| Characteristic | Entity | Value Object | Domain Service |
|---|---|---|---|
| **Identity** | Persistent unique identifier | None (defined by attributes) | Stateless |
| **Mutability** | Mutable via explicit methods | Strictly immutable | No state |
| **Equality** | By ID (`self.id == other.id`) | By all fields (`a == b`) | By instance/function |
| **Example** | `User`, `Order`, `Account` | `Money`, `Address`, `DateRange` | `CurrencyConverter`, `TaxCalculator` |

## Worked Example
Modeling a domain transfer service involving multiple accounts:

```python
class TransferService:
    """Domain service: coordinates transfer logic between two accounts."""
    @staticmethod
    def transfer(source: BankAccount, destination: BankAccount, amount: Money) -> None:
        if source.id == destination.id:
            raise DomainException("Cannot transfer to the same account")
        # Both operations are verified against entity invariants
        source.withdraw(amount)
        destination.deposit(amount)
```
Testing this business rule runs in microseconds without mocking databases or external APIs:
```python
def test_transfer_moves_funds():
    acc1 = BankAccount("1", "Alice", Money(Decimal("100.00"), "USD"))
    acc2 = BankAccount("2", "Bob", Money(Decimal("50.00"), "USD"))
    
    TransferService.transfer(acc1, acc2, Money(Decimal("30.00"), "USD"))
    
    assert acc1.balance.amount == Decimal("70.00")
    assert acc2.balance.amount == Decimal("80.00")
```

## Key Takeaways
1. The domain layer must be isolated from databases, web frameworks, and third-party tools.
2. Distinguish clearly between identity-driven Entities and attribute-driven Value Objects.
3. Protect invariants inside entity methods; never expose raw state for external modification.
4. Use Domain Services for operations that naturally span multiple entities.

## Connects To
- **Ch 1**: Percival's domain modeling concepts in comparison.
- **Ch 18**: How the Application Layer invokes domain entities to execute use cases.
- **Ch 29**: Good class design and high cohesion.
