# Chapter 18: The Application Layer: Orchestrating Use Cases

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 2: Implementing Clean Architecture Layers (Chapter 5)

## Core Idea
The Application Layer implements use cases: it receives input DTOs, coordinates domain entities and persistence ports, enforces transaction boundaries, and returns output DTOs without coupling to delivery mechanisms.

## Frameworks Introduced
- **Use Case Interactor Pattern**:
  - When to use: Implementing any user or system action in the application.
  - How:
    1. Define an explicit `RequestDTO` representing the inputs.
    2. Define an explicit `ResponseDTO` representing the outputs.
    3. Implement an Interactor class with a single public method (e.g. `execute(request: RequestDTO) -> ResponseDTO`).
    4. Inject required Ports (repositories, notification gateways) via constructor.
- **Ports Pattern (Input & Output Ports)**:
  - When to use: Defining the boundaries of the application core.
  - How:
    - **Input Port**: The interface the use case exposes to controllers (the Interactor itself).
    - **Output Port**: The interfaces the use case requires from infrastructure (repositories, email senders).

## Key Concepts
- **Use Case Interactor**: The class orchestrating the flow of data to and from entities, directing them to achieve the goals of the use case.
- **Request / Response DTO**: Simple immutable data structures carrying data across the boundary; prevents domain entities from leaking to outer layers.
- **Input Port**: The boundary interface called by controllers or CLI drivers.
- **Output Port**: The boundary interface implemented by gateways, databases, or presenters.
- **Application Exception**: Exceptions reflecting application errors (e.g. `EntityNotFound`) distinct from domain rule violations.

## Mental Models
- **Use Cases Are User Stories in Code**: A use case directly mirrors a single business requirement: *"As a customer, I want to cancel my order."*
- **DTOs as Diplomatic Envoys**: Entities never leave the country (domain/application layer). When foreign nations (web, UI) ask for information, a DTO is dispatched as an envoy.

## Anti-patterns
- **Returning Domain Entities to Controllers**: Returning `BankAccount` directly from a use case; the controller can now modify entity state or access lazy-loaded relationships.
- **Putting HTTP Concepts in Use Cases**: Accessing cookies, headers, status codes, or query parameters inside use case interactors.
- **Multi-Use-Case God Classes**: Creating a `UserService` with 25 methods instead of discrete use cases (`RegisterUser`, `ChangePassword`, `DeactivateAccount`).

## Code Examples

```python
from dataclasses import dataclass
from typing import Protocol, Optional
from domain.model import BankAccount, Money, DomainException

# 1. DTOs: Pure data carriers
@dataclass(frozen=True)
class TransferFundsRequest:
    source_account_id: str
    target_account_id: str
    amount: float
    currency: str

@dataclass(frozen=True)
class TransferFundsResponse:
    transaction_id: str
    success: bool
    message: str

# 2. Output Ports (Protocols)
class AccountRepository(Protocol):
    def get_by_id(self, account_id: str) -> Optional[BankAccount]: ...
    def save(self, account: BankAccount) -> None: ...

class NotificationService(Protocol):
    def notify_transfer(self, account_id: str, message: str) -> None: ...

# 3. Use Case Interactor (Input Port implementation)
class TransferFundsUseCase:
    def __init__(self, repo: AccountRepository, notifier: NotificationService):
        self._repo = repo
        self._notifier = notifier

    def execute(self, request: TransferFundsRequest) -> TransferFundsResponse:
        source = self._repo.get_by_id(request.source_account_id)
        target = self._repo.get_by_id(request.target_account_id)
        
        if not source or not target:
            raise ValueError("Account not found")

        transfer_money = Money(Decimal(str(request.amount)), request.currency)
        source.withdraw(transfer_money)
        target.deposit(transfer_money)

        self._repo.save(source)
        self._repo.save(target)
        self._notifier.notify_transfer(source.id, f"Transferred {request.amount}")

        return TransferFundsResponse(
            transaction_id="tx-999", success=True, message="Transfer complete"
        )
```
- **What it demonstrates**: A completely decoupled Use Case Interactor accepting a Request DTO, coordinating entities via injected Output Ports, and returning a Response DTO.

## Reference Tables

| Element | Responsibility | Allowed Dependencies |
|---|---|---|
| **Request DTO** | Data input format | Primitives, Value Objects |
| **Use Case Interactor** | Workflow coordination | Entities, Output Ports, DTOs |
| **Output Port** | Interface specification for I/O | Standard Python types, Entities |
| **Response DTO** | Data output format | Primitives, Value Objects |

## Worked Example
Testing the use case with mock/fake ports without a database:

```python
class FakeAccountRepo:
    def __init__(self, accounts):
        self.accounts = {a.id: a for a in accounts}
        self.saved = []

    def get_by_id(self, account_id):
        return self.accounts.get(account_id)

    def save(self, account):
        self.saved.append(account)

class FakeNotifier:
    def __init__(self):
        self.notifications = []

    def notify_transfer(self, account_id, message):
        self.notifications.append((account_id, message))

def test_transfer_use_case():
    acc1 = BankAccount("acc-1", "Alice", Money(Decimal("100"), "USD"))
    acc2 = BankAccount("acc-2", "Bob", Money(Decimal("20"), "USD"))
    repo = FakeAccountRepo([acc1, acc2])
    notifier = FakeNotifier()

    interactor = TransferFundsUseCase(repo, notifier)
    response = interactor.execute(TransferFundsRequest("acc-1", "acc-2", 40.0, "USD"))

    assert response.success is True
    assert acc1.balance.amount == Decimal("60")
    assert acc2.balance.amount == Decimal("60")
    assert len(notifier.notifications) == 1
```

## Key Takeaways
1. Use cases encapsulate application-specific business workflows.
2. Use Request and Response DTOs to prevent domain entities from crossing layer boundaries.
3. Define Output Ports using Protocols to specify required infrastructure capabilities.
4. Keep use case interactors focused on a single responsibility; prefer one class per use case.

## Connects To
- **Ch 4**: Percival's Service Layer compared with Keen's Use Case Interactors.
- **Ch 19**: How Interface Adapters (Controllers/Presenters) interact with Use Cases.
- **Ch 21**: Testing use cases with in-memory doubles.
