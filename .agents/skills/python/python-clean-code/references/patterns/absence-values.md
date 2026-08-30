# Absence values and strict edges

## Use when

Use `None`, a private sentinel, a Null Object, or a strict validated type when 'missing' has
meaning at a boundary and callers otherwise repeat defensive checks.

## Why

Modeling absence once keeps uncertainty at the edge. The core workflow can then accept a value with
a stronger invariant, while a Null Object makes an optional capability safe and explicit.

## When not to use

Do not replace a meaningful failure with a silent Null Object. Keep `None` when absence is the
actual domain result, use a private sentinel when 'argument omitted' differs from 'argument is None',
and do not add a class for one local check.

## Trade-offs

Strict edge validation moves errors earlier and reduces branching, but it adds conversion code.
A sentinel preserves three states but is easy to confuse with `None`. A Null Object removes
conditionals while potentially hiding that an operation did nothing; name and test that behavior.

## Tests

Test missing, explicit `None`, valid, and invalid inputs separately. For sentinels, assert identity
with `is`. For Null Objects, assert that the no-op contract is safe and observable where needed.

## Python code

The [ArjanCodes 2026 `none` example](https://github.com/ArjanCodes/examples/blob/main/2026/none/after.py)
turns nullable drone telemetry into a strict `ReadyDrone` before route assignment:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Telemetry:
    location: tuple[float, float] | None
    battery: int | None


@dataclass(frozen=True)
class ReadyDrone:
    location: tuple[float, float]
    battery: int


def prepare(telemetry: Telemetry) -> ReadyDrone:
    if telemetry.location is None:
        raise ValueError("GPS location is required")
    if telemetry.battery is None:
        raise ValueError("battery reading is required")
    return ReadyDrone(telemetry.location, telemetry.battery)
```

The strict type is created once; downstream code does not check nullable fields again. For an
optional collaborator, the same source uses a Null Object with a narrow Protocol:

```python
class Diagnostics(Protocol):
    def record(self, message: str) -> None: ...


class NullDiagnostics:
    def record(self, message: str) -> None:
        pass
```

Use a private sentinel when omission and explicit `None` differ:

```python
_MISSING = object()


def read_limit(value: int | None | object = _MISSING) -> int:
    if value is _MISSING:
        return 100
    if value is None:
        raise ValueError("limit cannot be None")
    return int(value)
```

The [zedr clean-code-python table of contents](https://github.com/zedr/clean-code-python#table-of-contents)
supports this edge-focused approach: use defaults where they express the contract, avoid hidden
side effects, and keep the main operation at one abstraction level.

## Framework examples

### Pydantic strict boundary

Pydantic validates external absence and produces a value the application can trust:

```python
from pydantic import BaseModel, ConfigDict


class CreateJob(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    queue: str = "default"
```

Unknown fields and malformed input are rejected at the API boundary; the service does not need to
carry an untyped dictionary. See the [Pydantic models documentation](https://docs.pydantic.dev/latest/concepts/models/).
