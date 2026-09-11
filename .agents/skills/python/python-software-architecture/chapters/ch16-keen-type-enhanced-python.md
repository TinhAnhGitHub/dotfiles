# Chapter 16: Type-Enhanced Python: Strengthening Clean Architecture

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 1: Foundations of Clean Architecture in Python (Chapter 3)

## Core Idea
Modern Python typing (type annotations, Generics, Protocols, and Pydantic) transforms Python from a loose scripting language into a robust architectural platform, enforcing layer boundaries at static analysis time.

## Frameworks Introduced
- **The Type Safety Spectrum Framework**:
  - When to use: Deciding where to apply static vs. runtime validation across Clean Architecture layers.
  - How:
    - **Outer Boundary (Frameworks/Adapters)**: Runtime validation via Pydantic (`BaseModel`) to sanitize untrusted external input (HTTP JSON, CLI flags, CSV files).
    - **Inner Core (Application/Domain)**: Static typing via Python standard types, dataclasses, and `typing.Protocol`, verified by `mypy`. Avoid heavy framework dependencies like Pydantic in pure domain entities unless strictly justified.
- **Protocols vs. Abstract Base Classes (ABCs)**:
  - When to use: Defining interface contracts between Clean Architecture layers.
  - How: Prefer `typing.Protocol` (structural subtyping / duck typing). It allows adapters in outer layers to fulfill inner-layer requirements without explicitly inheriting from domain classes.

## Key Concepts
- **Structural Subtyping**: Typing based on structure (methods and attributes), not explicit inheritance hierarchies.
- **Nominal Subtyping**: Typing based on declared class names and explicit inheritance.
- **Data Transfer Object (DTO)**: Simple typed data containers used to pass structured data across layer boundaries.
- **Runtime Validation**: Validating input schemas when data enters the application (e.g. Pydantic).
- **Static Analysis**: Verifying type correctness before execution using tools like `mypy` or `pyright`.

## Mental Models
- **Pydantic as Border Control, Dataclasses as Citizens**: Pydantic guards the border checkpoints (controllers/gateways) inspecting and verifying passports. Once inside the domain city, lightweight pure Python dataclasses move freely.
- **Protocols as Invisible Handshakes**: An adapter doesn't need to know the name of the base class; as long as its hand has the right shape (methods and signatures), the handshake succeeds.

## Anti-patterns
- **Using Pydantic for Everything**: Inheriting every domain entity from Pydantic `BaseModel`, coupling pure business logic to a third-party validation library.
- **Type Annotations as Mere Documentation**: Writing type hints but never running `mypy` in CI, allowing type drift and broken contracts.
- **Using `Any` as an Escape Hatch**: Sprinkling `Any` across layer boundaries to bypass type checking, destroying static boundary verification.

## Code Examples

```python
from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic, Optional
from pydantic import BaseModel, Field

# 1. Outer Layer: Pydantic for Inbound Request Validation
class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    age: int = Field(..., ge=18)

# 2. Inner Layer: Pure Domain Entity (Standard Dataclass)
@dataclass(frozen=True)
class User:
    id: str
    username: str
    email: str
    age: int

# 3. Inner Layer: Generic Repository Protocol
T = TypeVar("T")

class Repository(Protocol[T]):
    def get(self, entity_id: str) -> Optional[T]:
        ...
    def save(self, entity: T) -> None:
        ...

# 4. In-memory implementation satisfies Protocol WITHOUT inheritance
class InMemoryUserRepository:
    def __init__(self):
        self._storage: dict[str, User] = {}

    def get(self, entity_id: str) -> Optional[User]:
        return self._storage.get(entity_id)

    def save(self, entity: User) -> None:
        self._storage[entity.id] = entity
```
- **What it demonstrates**: Combining Pydantic at the perimeter with pure dataclasses in the core, connected by generic Protocols without inheritance coupling.

## Reference Tables

| Feature | `typing.Protocol` | `abc.ABC` | Pydantic `BaseModel` |
|---|---|---|---|
| **Subtyping Mode** | Structural (Duck typing) | Nominal (Inheritance) | Data parsing / validation |
| **Coupling** | Zero inheritance coupling | Explicit base class coupling | High library coupling |
| **Primary Location** | Ports in Application layer | Shared base classes | Interface Adapters |
| **Validation Timing** | Static (at type-check time) | Runtime (at instantiation) | Runtime (at deserialization) |

## Worked Example
Enforcing boundary integrity using generic use-case input/output types:

```python
from typing import Generic, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")

class UseCase(Protocol, Generic[InputDTO, OutputDTO]):
    def execute(self, request: InputDTO) -> OutputDTO:
        ...

@dataclass(frozen=True)
class RegisterUserInput:
    username: str
    email: str

@dataclass(frozen=True)
class RegisterUserOutput:
    user_id: str
    success: bool

class RegisterUserInteractor:
    def execute(self, request: RegisterUserInput) -> RegisterUserOutput:
        # Execution logic...
        return RegisterUserOutput(user_id="u-123", success=True)
```
Mypy statically proves that `RegisterUserInteractor` strictly adheres to `UseCase[RegisterUserInput, RegisterUserOutput]`.

## Key Takeaways
1. Use Pydantic at application boundaries for input sanitization and deserialization.
2. Keep core domain models as pure dataclasses or standard Python classes.
3. Define ports using `typing.Protocol` to decouple adapters from explicit inheritance.
4. Run `mypy --strict` in CI to guarantee architectural boundary compliance.

## Connects To
- **Ch 15**: Structural subtyping realizes the Interface Segregation Principle.
- **Ch 18**: Request and Response DTOs in use cases.
- **Ch 20**: Pydantic in FastAPI web controllers.
