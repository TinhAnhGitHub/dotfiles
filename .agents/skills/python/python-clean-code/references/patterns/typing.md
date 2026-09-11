# Typed functional and class boundaries

## Use when

Use precise typing when a function, callback, plugin, decorator, class, or serialized record is a
public boundary whose valid shape should be checked by tools or at runtime.

## Decision rules

- `Callable` for single-operation functions, strategies, and hooks; bind configuration via closures or `functools.partial`.
- `Protocol` for consumer-defined structural contracts, duck typing, and test doubles without import coupling.
- `ABC` for nominal inheritance when implementations must share default state/helpers or require runtime instantiation enforcement.
- `ParamSpec` and `Concatenate` for decorators that preserve parameters.
- `TypeVar` and `Self` for subtype-preserving APIs.
- `Literal` for closed names; `Annotated` for metadata consumed by a framework.
- `TypedDict` for wire-shaped dictionaries; Pydantic models when runtime validation is required.
- `Decimal` over `float` for currencies, prices, and accounting values where floating-point rounding drift corrupts calculations.
- `overload` when input shape changes the return type.

## Example

Instead of importing concrete classes and inspecting them with `isinstance`:

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

# The consumer defines the structural contract it requires
class Loader(Protocol[T]):
    def load(self, key: str) -> T: ...

def fetch(loader: Loader[T], key: str) -> T:
    # No isinstance checks or concrete loader imports needed
    return loader.load(key)
```

This prevents "spaghetti code" by keeping the worker function decoupled from all concrete
implementations: any object conforming to `load(key)` can be passed directly.

## When not to use

Do not add complex generic machinery when the function is private and obvious. Do not treat static
annotations as runtime validation; add an explicit validator at an untrusted boundary.

## Framework examples

### PydanticAI — typed dependencies and output

```python
agent = Agent[AppDeps, Answer](
    "provider:model",
    deps_type=AppDeps,
    output_type=Answer,
)

@agent.tool
def lookup(ctx: RunContext[AppDeps], key: str) -> str:
    return ctx.deps.store[key]
```

`Agent[DepsT, OutputT]` makes injected runtime services and structured results visible to type
checkers and tests. See PydanticAI [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/).

### LangGraph — typed state and reducers

```python
class State(TypedDict):
    messages: Annotated[list[str], add]

graph = StateGraph(State)
```

Typed state documents the graph’s wire contract, while the reducer describes how parallel updates
combine. See the [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).

### DSPy — a typed task signature

```python
class Summarize(dspy.Signature):
    text: str = dspy.InputField()
    summary: str = dspy.OutputField()

predict = dspy.Predict(Summarize)
```

`Signature`, `InputField`, and `OutputField` separate the task contract from prompting strategy,
so modules can be swapped or optimized without changing callers. See [DSPy signatures](https://dspy.ai/api/signatures/).

### LangChain — structured response strategy

```python
agent = create_agent(
    model="provider:model",
    response_format=ToolStrategy(Review),
)
```

The typed `Review` schema keeps provider-specific structured-output handling behind a stable return
contract. See [LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output).

## Trade-offs

Precise types expose contracts and improve tooling, but complex generics can obscure simple code and
increase maintenance when the boundary changes. Keep annotations proportional to the public risk,
and pair them with runtime validation at untrusted boundaries.

## Why

Precise annotations make callable, plugin, and serialized-data contracts visible to tools and test
doubles. Structural types and generic parameters reduce coupling without requiring a shared base class.

## Tests

Run static checking for the public boundary and test runtime validation separately. Include a fake
implementation, invalid wire data, overload variants, and decorator metadata where those contracts apply.

## ArjanCodes 2026 examples (adapted)

### Keep API data separate from persistence data

An API schema is a typed boundary, not a promise that the database model is also the wire format.
Use request and response models and convert deliberately.

```python
from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str


def to_response(user: UserRecord) -> UserResponse:
    return UserResponse(id=user.id, name=user.name)
```

This prevents storage-only fields from leaking into responses and lets each boundary evolve on its
own axis. Adapted from the [2026 `apidata` examples](https://github.com/ArjanCodes/examples/tree/main/2026/apidata).

### Allow bounded flexibility at integration edges

When integrations bring provider-specific fields, keep stable fields typed and put only the
extension point behind a deliberately open type.

```python
from typing import Any
from pydantic import BaseModel, Field


class Shipment(BaseModel):
    tracking_id: str
    custom_data: dict[str, Any] = Field(default_factory=dict)
```

`custom_data` is useful at the edge, but it should not replace types for fields the application
understands. Adapted from the [2026 `flexible` examples](https://github.com/ArjanCodes/examples/tree/main/2026/flexible)
and [API integrations video](https://www.youtube.com/watch?v=rZpwFN_n2-g).

### Type ports by behavior

Protocols make an application depend on the operations it uses rather than a concrete adapter.

```python
from typing import Protocol


class UserReader(Protocol):
    def find(self, user_id: int) -> UserRecord | None: ...


def load_user(reader: UserReader, user_id: int) -> UserRecord:
    user = reader.find(user_id)
    if user is None:
        raise LookupError(user_id)
    return user
```

Both a SQL repository and a test fake can satisfy the port without inheriting from a shared base
class. See the [2026 `ports/domain/ports.py`](https://github.com/ArjanCodes/examples/blob/main/2026/ports/domain/ports.py).

### Give domain values a precise type

If a value has validation or unit semantics, a small immutable type is safer than a bare string.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise ValueError("invalid email address")
```

The type moves the invariant to construction and makes the contract visible to tools and callers.
Adapted from the [2026 `value/email_address.py`](https://github.com/ArjanCodes/examples/blob/main/2026/value/email_address.py).

### Choose `Decimal` over `float` for monetary and accounting calculations

Binary floating-point types (`float`) cannot accurately represent fractions like $0.1$ or $0.7$, accumulating precision drift that corrupts currency conversions and financial ledgers. Always model monetary amounts, exchange rates, and tax figures with `decimal.Decimal`:

```python
# ❌ DANGEROUS: Floats accumulate precision drift in monetary calculations
def convert_naive(amount: float, rate: float) -> float:
    return amount * rate  # 100.0 * 0.91 can produce 90.99999999999999

# ✅ SAFE: Decimal ensures exact arithmetic and bounded API validation
from decimal import Decimal
from fastapi import Query

def convert_production(
    amount: Decimal = Query(..., gt=Decimal("0")),
    rate: Decimal = Query(..., gt=Decimal("0")),
) -> Decimal:
    return amount * rate  # Exactly Decimal('91.000')
```

Adapted from the [ArjanCodes Production-Ready video](https://www.youtube.com/watch?v=GMBiCMsEsq8) and
[`ArjanCodes 2025 production`](https://github.com/ArjanCodes/examples/tree/main/2025/production).

## zedr clean-code-python diagnostics (adapted)

The [zedr clean-code-python table of contents](https://github.com/zedr/clean-code-python#table-of-contents)
treats names as part of a type contract: use the same vocabulary for the same entity and avoid
mental mapping. Typed parameter objects make that vocabulary executable at a boundary.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class MenuRequest:
    title: str
    body: str
    button_text: str
    cancellable: bool = False


def create_menu(request: MenuRequest) -> None:
    render_menu(request.title, request.body, request.button_text)
```

The object is useful because these fields change together; a typed object is not a reason to bundle
unrelated values or pass it into a helper that needs only one field.
