# Singleton and inheritance overuse

## Intent

Recognize when a familiar design pattern is adding coupling, hidden state, or combinatorial
complexity instead of solving a real design pressure.

## Use when

Use this review pattern when code introduces a Singleton, deep inheritance, multiple inheritance,
or a class hierarchy solely to combine unrelated features.

## Why

An explicit Singleton often hides dependencies and makes tests share mutable state; Python modules
already provide one import-level namespace. Deep or multiple inheritance creates fragile method-
resolution and initialization contracts.

## Prefer instead

- Pass dependencies explicitly.
- Use a module-level immutable constant when shared identity is genuinely required.
- Use a Factory or Registry for construction and extension.
- Use composition, delegation, Adapter, Decorator, or Strategy for independent behavior axes.

```python
class Logger:
    def __init__(self, emit, accept) -> None:
        self.emit = emit
        self.accept = accept

    def log(self, message: str) -> None:
        if self.accept(message):
            self.emit(message)
This replaces a `FilteredSocketLogger`-style subclass matrix with two independently replaceable
collaborators.

### Anti-Pattern: Catch-and-swallow and fake defaults

Wrapping operations in nested `try/except` pyramids and returning synthetic defaults (e.g., `return 0`
when a payment charge is missing) silently corrupts downstream databases and ledgers while masking bugs:

```python
# ❌ ANTI-PATTERN: Nested try/except pyramids & returning fake defaults
def get_fee(payment_intent: dict) -> int:
    try:
        charge = stripe.Charge.retrieve(payment_intent["latest_charge"])
        return charge["fee"]
    except Exception:
        return 0  # Silently corrupts accounting ledger!
```

**Remedy (Fail Fast / "Let It Burn"):**
- Use flat guard clauses that crash visibly with explicit domain exceptions (`raise ValueError(...)`).
- Confine broad exception handling to the outermost application boundary (e.g. API gateway middleware)
  for logging and 500 responses.
- In distributed microservices, pair local fail-fast with Circuit Breakers to prevent cascading failures.

Adapted from the [ArjanCodes Fail Fast video](https://www.youtube.com/watch?v=YA0Wq1rcs6U) and
[2024 burn examples](https://github.com/ArjanCodes/examples/tree/main/2024/burn).

### Anti-Pattern: Combinatorial subclass explosion ($M \times N$)

When multiple independent feature axes (e.g. payment type, commission structure, bonus, persistence)
are modeled using inheritance, classes multiply multiplicatively ($M \times N \times K$):

```python
# ❌ ANTI-PATTERN: Subclasses for every feature combination
class HourlyEmployee(Employee): ...
class SalariedEmployee(Employee): ...
class Freelancer(Employee): ...
class HourlyEmployeeWithCommission(HourlyEmployee): ...
class SalariedEmployeeWithCommission(SalariedEmployee): ...
class FreelancerWithCommission(Freelancer): ...
```

**Why this is harmful:**
- **Code Duplication**: Logic (such as commission or bonus calculation) is copy-pasted across sibling subclasses.
- **Strongest Coupling in OOP**: Child classes depend on parent constructor arguments, attribute names,
  and `super()` execution order, causing the fragile base class problem.
- **Remedy**: Favor composition over inheritance. Decompose each variation axis into a collaborator
  (`Contract`, `Commission`) and assemble them dynamically in a single stable entity (`Employee`).
  See [Composition over inheritance](../principles/composition.md) and
  [ArjanCodes 2021 composition vs inheritance](https://github.com/ArjanCodes/2021-composition-vs-inheritance).

### Anti-Pattern: Configuration Subclasses ("Turning Values into Types")

Creating subclasses solely to alter default constants, thresholds, or configuration settings:

```python
# ❌ ANTI-PATTERN: Subclasses just to override data values
@dataclass(frozen=True)
class StandardCheckout:
    tax_rate: Decimal = Decimal("0.21")
    retry_count: int = 3

@dataclass(frozen=True)
class GermanCheckout(StandardCheckout):
    tax_rate: Decimal = Decimal("0.19")

@dataclass(frozen=True)
class ReliableGermanCheckout(GermanCheckout):
    retry_count: int = 10
```

**Why this is harmful:**
- **Combinatorial Explosion**: Every new configuration dimension ($M$ regions $\times N$ retry policies $\times K$ currencies) demands new classes.
- **Pollutes Type System**: Types should enforce distinct behavior and constraints, not combinations of settings.
- **Remedy**: Encapsulate configuration as data using frozen dataclasses (`CheckoutConfig`), pass it to a single `Checkout` class, and use factory functions for named defaults. See [`02_configuration_subclasses_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/02_configuration_subclasses_after.py).

### Anti-Pattern: God Base Class & Stamp Coupling (ISP Violation)

Defining wide, monolithic base classes where specialized subclasses stub out irrelevant methods:

```python
# ❌ ANTI-PATTERN: God base class forcing unimplemented methods
class BaseStoreIntegration:
    def authenticate(self, api_key: str) -> Session: raise NotImplementedError
    def upload_images(self, urls: list[str]) -> None: raise NotImplementedError
    def download_inventory(self, session: Session) -> list[Item]: raise NotImplementedError
    def subscribe_webhooks(self, url: str) -> None: raise NotImplementedError

class WarehouseSupplier(BaseStoreIntegration):
    # Only implements authenticate and download_inventory; others raise NotImplementedError!
```

**Why this is harmful:**
- **Stamp Coupling**: Callers receive an object with 10+ methods when they only need one capability.
- **Runtime Landmines**: Unimplemented methods can be called by unsuspecting clients, causing production crashes.
- **Remedy**: Split into small, consumer-defined structural `Protocol`s (`Authenticated`, `InventorySource`). See [`04_god_base_class_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/04_god_base_class_after.py).

### Anti-Pattern: Pretender Subtypes & Broken Substitutability (LSP Violation)

Creating a subtype that disables or breaks guarantees made by its parent:

```python
# ❌ ANTI-PATTERN: Subtype raises error for valid parent operation
class OrderQueue:
    def enqueue(self, order: Order) -> None: ...

class ReadOnlyOrderQueue(OrderQueue):
    def enqueue(self, order: Order) -> None:
        raise RuntimeError("This order queue is read-only")  # 💥 Breaks LSP!
```

**Why this is harmful:**
- Functions accepting `OrderQueue` type-check cleanly, but crash with `RuntimeError` at runtime when passed `ReadOnlyOrderQueue`.
- **Remedy**: Segregate into separate protocols (`OrderReader`, `OrderWriter`) and distinct concrete implementations (`OrderHistory`, `OrderQueue`). See [`05_substitutability_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/05_substitutability_after.py).

### Anti-Pattern: Premature Template Method Abstraction

Coupling disparate domains into an abstract base class hierarchy because they share superficial syntactic steps:

```python
# ❌ ANTI-PATTERN: Premature base class destroys domain typing
class BaseImporter(ABC):
    def import_records(self) -> list[object]:  # Degraded to object!
        raw = self.load()
        return [self.transform(r) for r in raw if self.is_valid(r)]
    @abstractmethod def load(self) -> list[str]: ...
    @abstractmethod def is_valid(self, record: str) -> bool: ...
    @abstractmethod def transform(self, record: str) -> object: ...
```

**Why this is harmful:**
- Return types degrade to `list[object]`, stripping callers of strong static typing.
- Changes to customer CSV loading risk breaking order API imports because they are coupled to the same base template.
- **Remedy**: Keep them as two focused, independent functions (`import_customers_from_csv`, `import_paid_orders_from_api`). *Duplication is far cheaper than the wrong abstraction* (Sandi Metz). See [`06_premature_abstraction_after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/oop/06_premature_abstraction_after.py).

### Anti-Pattern: The Naive Prototype Trap ("Works on My Machine")

Shipping quick scripts or naive prototypes directly to production environments where real-world operational requirements are ignored:

```python
# ❌ ANTI-PATTERN: Naive prototype mixing transport, global state, and console prints (starting_point.py)
RATES = {("USD", "EUR"): 0.91}  # Module-level mutable state

@app.get("/convert")
def convert(from_currency: str, to_currency: str, amount: float):
    rate = RATES.get((from_currency.upper(), to_currency.upper()))
    if rate is None:
        raise HTTPException(status_code=400, detail="Exchange rate not available")
    print(f"Using rate {rate}")  # Unstructured console debugging
    return {"result": amount * rate}  # Binary float precision drift; no validation or rate limiting
```

**Why this is harmful:**
- **Zero Observability**: `print()` statements cannot be structured, filtered, or ingested by monitoring systems (e.g. Sentry, Datadog).
- **Silent Numerical Drift**: Using binary `float` for currency causes precision loss and accounting mismatches.
- **Transport / Domain Tangling**: Route handlers directly execute calculations and queries, preventing automated unit testing without spinning up HTTP servers.
- **Denial-of-Service Risk**: Without rate limiting (`slowapi`), a single misbehaving client can exhaust backend resources.
- **Brittle Infrastructure**: Hardcoded ports, lack of health probes (`/health`), and unmanaged database lifecycles prevent automated container orchestration (Kubernetes).

**Remedy**: Follow the 11-step production-readiness roadmap:
1. Extract business logic into an injected domain service (`ExchangeRateService`).
2. Use `Decimal` for precision.
3. Validate request bounds (`Query(..., min_length=3, max_length=3, gt=0)`).
4. Inject scoped database sessions with deterministic cleanup (`yield db`).
5. Add rate limiting (`@limiter.limit("5/minute")`).
6. Expose an orchestrator health probe (`/health`).
7. Manage configuration with `pydantic-settings` `BaseSettings` and `.env`.

See [`ArjanCodes 2025 production`](https://github.com/ArjanCodes/examples/tree/main/2025/production) and the [ArjanCodes Production-Ready video](https://www.youtube.com/watch?v=GMBiCMsEsq8).

## When not to use

Do not reject every class hierarchy or shared object automatically. Keep inheritance when there is
a genuine substitutable “is-a” relationship and the base contract is stable. Keep process-wide
identity only when it is a documented invariant with explicit lifecycle and test isolation.

## Trade-offs and tests

Composition adds wiring, while explicit dependencies can make constructors longer. Look for
hidden global state, subclass combinations, `super()` ordering assumptions, constructor argument
collisions, and tests requiring global reset. Confirm behavior before deleting hierarchy code.

## Related patterns

See [composition over inheritance](../principles/composition.md), [Dependency Injection and Registry](../extensibility/registry-di.md),
and [Decorator](../composition/decorator.md).

## Framework examples

### PydanticAI — `Agent` dependencies

PydanticAI `deps_type` and `RunContext` solve the problem of tools reaching for singleton
clients or other hidden process-wide state. Dependency injection fits this review pattern because
the agent receives an explicit service bundle that production and tests can replace independently.

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Services:
    weather: "WeatherClient"

agent = Agent("provider:model", deps_type=Services)

@agent.tool
def weather(ctx: RunContext[Services], city: str) -> str:
    return ctx.deps.weather.lookup(city)
```

Adapted from the [PydanticAI dependencies guide](https://pydantic.dev/docs/ai/core-concepts/dependencies/)
(latest, fetched 2026-08-30; adapted).

## ArjanCodes OOP lessons (adapted)

### Prefer frozen configuration and explicit dependencies to a Singleton

When shared settings are values rather than identity-bearing resources, a frozen dataclass and an
ordinary factory solve the problem without hidden mutable state or global reset logic. This fits
Python because callers can construct independent services for production and tests.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    endpoint: str
    timeout_seconds: float = 5.0

def make_service(config: AppConfig, transport: Transport) -> Service:
    return Service(endpoint=config.endpoint, timeout=config.timeout_seconds,
                   transport=transport)
```

Adapted from [ArjanCodes' configuration-subclasses example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/02_configuration_subclasses_after.py).

### Keep independent behavior as options or callables

When logging, retry, and formatting vary independently, a Singleton or multiple-inheritance class
combines unrelated axes and makes tests order-dependent. Explicit options and strategies solve the
problem by putting variation at the call site.

```python
from collections.abc import Callable

def send(message: str, *, retry: Callable[[Callable[[], None]], None],
         format_message: Callable[[str], str]) -> None:
    retry(lambda: deliver(format_message(message)))
```

Adapted from [ArjanCodes' feature-variation example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/03_feature_variation_after.py).

### Do not build a base class before a change axis exists

When implementations do not yet share meaning, a hierarchy only predicts future requirements and
creates coupling. Keep the local function or concrete class until a second implementation proves
the contract; see [ArjanCodes' premature-abstraction example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/06_premature_abstraction_after.py)
and the accompanying [OOP video](https://www.youtube.com/watch?v=RqcEK7sWesQ).

### Avoid framework coupling in domain logic (the Polluted Hexagon)

Coupling core business decisions to transport frameworks (e.g., FastAPI `HTTPException`) and database drivers (e.g., SQLAlchemy `Connection`, raw SQL) makes domain rules untestable in isolation and unusable outside a live HTTP server.

```python
# ❌ ANTI-PATTERN: Business calculation coupled to HTTP transport & database queries
def reserve_stock(db: Connection, sku: str, quantity: int) -> dict[str, Any]:
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid quantity")  # 💥 Leaks web transport
    row = db.execute(text("SELECT stock FROM inventory WHERE sku = :s"), {"s": sku}).fetchone()
    if not row or row[0] < quantity:
        raise HTTPException(status_code=409, detail="Out of stock")      # 💥 Database + HTTP coupled
    db.execute(text("UPDATE inventory SET stock = stock - :q WHERE sku = :s"), {"q": quantity, "s": sku})
    db.commit()
    return {"status": "ok", "reserved": quantity}
```

**Consequences**:
1. **Zero Reusability**: The logic cannot be called from a background Celery worker, CLI tool, or event subscriber without simulating HTTP exceptions.
2. **Brittle Unit Tests**: Testing requires spin-up of an active database connection or complex mock patches.
3. **Hidden Invariants**: Validation rules are scattered across HTTP response codes instead of typed domain invariants.

**The Clean Remedy**:
Separate pure domain models and domain errors from structural ports and transport adapters:

```python
# ✅ CLEAN REMEDY: Pure use case + pure domain errors + structural port
class DomainError(Exception): """Base domain error."""
class OutOfStock(DomainError): """Insufficient stock for reservation."""
class InvalidQuantity(DomainError): """Requested quantity must be positive."""

class InventoryPort(Protocol):
    def get_stock(self, sku: str) -> int: ...
    def reserve(self, sku: str, quantity: int) -> None: ...

def place_order(req: OrderRequest, inventory: InventoryPort) -> OrderPlaced:
    if req.quantity <= 0:
        raise InvalidQuantity("Quantity must be positive")
    if inventory.get_stock(req.sku) < req.quantity:
        raise OutOfStock(f"Out of stock for {req.sku}")
    inventory.reserve(req.sku, req.quantity)
    return OrderPlaced(sku=req.sku, quantity_reserved=req.quantity)
```

The web handler (FastAPI) becomes an inbound adapter that invokes `place_order` and maps `OutOfStock` to `HTTPException(409)`.
See [ArjanCodes' Ports & Adapters video](https://www.youtube.com/watch?v=FXwBWS4qDAA) and companion code [`examples/2026/ports`](https://github.com/ArjanCodes/examples/tree/main/2026/ports).
