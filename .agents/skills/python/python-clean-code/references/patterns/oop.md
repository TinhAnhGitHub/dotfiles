# Object-oriented Python

## Use when

Use a class when identity, invariants, lifecycle, state, or a cohesive protocol must be owned by
one object. Use composition and delegation when behavior varies along independent dimensions.

## Why

Well-shaped objects localize invariants and expose Python's native protocols. Composition avoids
subclass explosion and keeps components independently testable.

## Prefer

- Frozen dataclasses or explicit value objects for immutable domain values.
- `Protocol` and delegation for consumer-defined interfaces.
- Properties only for stable derived or validated attributes.
- Special methods when the object should participate naturally in Python syntax.
- Inheritance for a genuine substitutable “is-a” relationship with a stable extension contract.

## Avoid

Deep hierarchies, mixins that require undocumented initialization order, and classes that only
wrap one function without state. For Adapter, Decorator, Facade, and Strategy choices, consult
`python-design-patterns`.

## Tests

Test invariants, equality/hash consistency, protocol behavior, delegation, lifecycle cleanup, and
composition of independently tested objects.

## Framework examples

### MLflow — a portable model object

```python
class SentimentModel(mlflow.pyfunc.PythonModel):
    def predict(self, context, model_input):
        return classify(model_input)
```

`PythonModel` gives different model implementations one lifecycle and prediction protocol; an
extension class fits because MLflow owns serving while the subclass owns model behavior. See the
[MLflow PyFunc API](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html).

### Agno — composition of agents into a team

```python
researcher = Agent(name="researcher", tools=[search])
writer = Agent(name="writer")
team = Team(members=[researcher, writer])
```

`Team` composes independently testable agents and delegates work without forcing a deep inheritance
hierarchy. See [Agno teams](https://docs.agno.com/teams/overview).

### Google ADK — workflow objects

```python
pipeline = SequentialAgent(
    name="summarize",
    sub_agents=[fetch_agent, summarize_agent],
)
```

`SequentialAgent` makes ordering and ownership explicit; a workflow object fits because it owns the
execution lifecycle of its child agents. See [Google ADK workflow agents](https://adk.dev/agents/workflow-agents/).

### qwen-agent — subclassable agent behavior

```python
class SearchAgent(Agent):
    def _run(self, messages, **kwargs):
        yield from super()._run(messages, **kwargs)
```

The subclass keeps the framework’s agent protocol while specializing one cohesive behavior, which
is appropriate when the extension is genuinely substitutable. See the qwen-agent [agent guide](https://github.com/QwenLM/Qwen-Agent/blob/main/qwen-agent-docs/website/content/en/guide/core_moduls/agent.md).

## When not to use

Do not create a class for a stateless one-use function or a simple record that a value object or
dictionary expresses clearly. Avoid inheritance when composition can vary the behavior directly.

## Trade-offs

Classes localize state and invariants, but add lifecycle, indirection, and mocking surface. Inheritance
can reduce duplication while coupling subclasses to base-class initialization and implementation.

## ArjanCodes OOP lessons (adapted)

The [ArjanCodes OOP video](https://www.youtube.com/watch?v=RqcEK7sWesQ) and its [six 2026 examples](https://github.com/ArjanCodes/examples/tree/main/2026/oop) reinforce a practical test for choosing classes: use them to protect invariants or combine state with meaningful behavior. Prefer plain functions when there is no meaningful state or identity to own.

### Reuse behavior through composition

Implementation reuse does not create an “is-a” relationship. Compose the dependencies a class uses,
and describe those dependencies with narrow `Protocol`s so production adapters and test doubles can
vary independently.

```python
class DailySalesReport:
    def __init__(self, database: OrderDatabase, logger: Logger) -> None:
        self.database = database
        self.logger = logger

    def generate(self) -> None:
        self.logger.log(f"Daily sales: {sum(self.database.fetch_paid_order_totals())} EUR")
```

Adapted from [`01_code_reuse_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/01_code_reuse_after.py). This fits when reporting, storage, and logging change on separate axes; inheritance would couple unrelated implementations.

### Keep values as data, not subclass combinations

Configuration is usually a value with validation and identity-by-content, not a family of behavior
subclasses. A frozen dataclass plus a factory gives callers safe, named combinations without a class
for every region, retry policy, or feature setting.

```python
@dataclass(frozen=True)
class CheckoutConfig:
    tax_rate: Decimal
    retry_count: int

def create_german_reliable_config() -> CheckoutConfig:
    return CheckoutConfig(tax_rate=Decimal("0.19"), retry_count=10)
```

Adapted from [`02_configuration_subclasses_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/02_configuration_subclasses_after.py). Use this when the variation is data; the checkout class can then focus on behavior and invariants.

### Combine independent features as options or functions

Features that can be mixed independently should not become a subclass matrix. Represent them as
options, strategies, or functions and keep the domain operation small.

```python
@dataclass(frozen=True)
class SyncOptions:
    validate_products: bool = False
    max_attempts: int = 1

result = sync_catalog(api, products, SyncOptions(validate_products=True, max_attempts=3))
```

Adapted from [`03_feature_variation_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/03_feature_variation_after.py). This fits when each option can vary without changing the meaning of the others.

### Narrow the contract before adding a base class

A god base class creates stamp coupling: every implementation inherits requirements it may not need.
Split it into capability protocols, such as authentication and inventory access, so consumers depend
only on the operations they use. The supplier example is in [`04_god_base_class_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/04_god_base_class_after.py).

Preserve substitutability by separating read and write contracts. A read-only object should satisfy
an `OrderReader`, while a mutable queue satisfies `OrderWriter`; making the read-only subtype pretend
to support writes would violate the parent contract. See [`05_substitutability_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/05_substitutability_after.py).

Finally, do not abstract before the shared meaning and change axis are understood. If importing
customers and importing paid orders merely look similar but evolve differently, keep two small,
domain-specific functions until a real common contract emerges. See [`06_premature_abstraction_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/06_premature_abstraction_after.py).

## More 2026 class-boundary examples

The [2026 `coupling` examples](https://github.com/ArjanCodes/examples/tree/main/2026/coupling)
show why a class should receive collaborators instead of reaching into a global service locator.

```python
class BookingService:
    def __init__(self, flights: FlightPort, payments: PaymentPort) -> None:
        self.flights = flights
        self.payments = payments

    def book(self, booking: Booking) -> Confirmation:
        hold = self.flights.hold(booking.flight_id)
        return self.payments.charge(hold, booking.amount)
```

Split a god object by the questions callers ask. A report generator should not also own payment,
inventory, and notification APIs; the [2026 `god` examples](https://github.com/ArjanCodes/examples/tree/main/2026/god)
use narrow collaborators and contracts for that pressure.

```python
class InventoryReader(Protocol):
    def stock_for(self, sku: str) -> int: ...


class StockReport:
    def __init__(self, inventory: InventoryReader) -> None:
        self.inventory = inventory

    def available(self, sku: str) -> bool:
        return self.inventory.stock_for(sku) > 0
```

Use a dataclass when the class is primarily a value with a small invariant, not because every
object needs a method-heavy abstraction. The [2026 `dataclass` example](https://github.com/ArjanCodes/examples/tree/main/2026/dataclass)
and [value examples](https://github.com/ArjanCodes/examples/tree/main/2026/value) are good fits:

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0 or len(self.currency) != 3:
            raise ValueError("invalid money value")
```

If two implementations differ only in their type-specific operation, a narrow Protocol is usually
enough; see the [2026 `type` examples](https://github.com/ArjanCodes/examples/tree/main/2026/type).
Properties are appropriate for stable derived values, not hidden I/O or surprising mutation:

```python
@dataclass
class Cart:
    lines: list[Money]

    @property
    def total(self) -> Money:
        return Money(sum((line.amount for line in self.lines), Decimal("0")), "EUR")
```

The [2026 `props` examples](https://github.com/ArjanCodes/examples/tree/main/2026/props) explore
the same boundary. Keep the property cheap and deterministic; make expensive work a method.
