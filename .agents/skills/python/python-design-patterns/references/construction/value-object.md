# Value Object

## Intent

Represent a domain value by its content rather than by identity, and enforce its invariants at
construction. A value object is normally immutable, comparable by value, and safe to pass between
layers.

## Use when

Use a value object when:

- a primitive carries domain meaning, such as an email address, money amount, percentage, or model
  identifier;
- invalid values should fail before entering the core workflow;
- equality should mean equal content rather than the same database row; or
- normalization and derived operations must be consistent everywhere the value is used.

## Why

The value object centralizes validation and removes repeated checks from services. Immutability
prevents a validated value from becoming invalid after it is cached, logged, or shared. A named
type also makes a function signature communicate units and invariants better than `str` or `float`.

## Example

Use a frozen, slotted dataclass for a small trusted-domain value. `Decimal` avoids silently mixing
binary floating-point values into a money calculation:

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("money cannot be negative")
        if len(self.currency) != 3 or not self.currency.isalpha():
            raise ValueError("currency must be a three-letter code")
        object.__setattr__(self, "currency", self.currency.upper())

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)


total = Money(Decimal("10.00"), "usd").add(Money(Decimal("2.50"), "USD"))
assert total == Money(Decimal("12.50"), "USD")
```

The service no longer needs to check currency length or negative amounts at every call site. Keep
conversion from raw JSON, database rows, and user input at an outer boundary; the core can accept
`Money` with confidence.

## When not to use

Use a plain primitive for a genuinely local value with no invariant or domain meaning. Use a
parameter object for a group of options that configures one operation. Use an entity when identity,
lifecycle, or mutation matters. Do not create a wrapper solely to make a type name longer.

## Trade-offs

Value objects add construction and conversion code and can make serialization more explicit. Frozen
objects may require replacing rather than mutating a value. Validation policy must be chosen
carefully: normalization in `__post_init__` is convenient, but a caller may need the original
representation for audit purposes. Prefer one canonical representation and test it.

## Tests

Test valid construction, every invariant boundary, normalization, equality, and immutability.
Test operations involving incompatible units or currencies. Test JSON/API conversion separately so
domain tests do not depend on a framework parser.

## ArjanCodes 2026 examples (adapted)

The [2026 `value/after_price.py` example](https://github.com/ArjanCodes/examples/blob/main/2026/value/after_price.py)
uses validated `Price` and `Percentage` numeric types so discount functions cannot silently accept
negative or out-of-range values. The [`EmailAddress` example](https://github.com/ArjanCodes/examples/blob/main/2026/value/email_address.py)
uses a frozen dataclass and exposes `domain` as derived behavior. These examples show the useful
boundary: make invalid values fail once, then keep the rest of the code simple.

## Framework examples

### PydanticAI — structured output as a validated value (adapted)

PydanticAI can use a Pydantic model as the agent's output type. This makes the model a validated
boundary value rather than passing an untyped dictionary through the application:

```python
from pydantic import BaseModel, AnyHttpUrl
from pydantic_ai import Agent


class Citation(BaseModel):
    title: str
    url: AnyHttpUrl


class Answer(BaseModel):
    text: str
    citations: list[Citation]


research_agent = Agent("openai:gpt-4o", output_type=Answer)
```

The application can now rely on `Answer` and `Citation` invariants after the agent boundary. This
is adapted from PydanticAI's [structured output documentation](https://pydantic.dev/docs/ai/core-concepts/output/);
verify the model name and output configuration against the installed release.
