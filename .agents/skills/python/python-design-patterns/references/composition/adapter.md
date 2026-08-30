# Adapter

## Intent

Present an existing provider through the smaller interface the client already understands.

## Use when

Use an Adapter when two components have compatible responsibilities but incompatible method names,
argument shapes, return types, sync/async behavior, or error types. It is especially useful at
vendor, model-provider, storage, and legacy-system boundaries.

## Why

The client depends on a stable local contract while the provider can change independently. The
adapter also gives tests a seam for a fake provider.

## Example

```python
from typing import Protocol

class ChatModel(Protocol):
    def complete(self, prompt: str) -> str: ...

class ProviderClient:
    def generate(self, *, input: str) -> dict[str, str]: ...

class ProviderAdapter:
    def __init__(self, client: ProviderClient) -> None:
        self.client = client

    def complete(self, prompt: str) -> str:
        return self.client.generate(input=prompt)["text"]
```

This solves provider-specific request and response shapes without spreading them through callers.

## When not to use

Do not add an adapter when the dependency is already small and stable, or when the translation is
so large that it is actually a domain service or Facade.

## Trade-offs and tests

Adapters can hide latency, retries, streaming, or loss of provider features. Test translation,
timeouts, error mapping, streaming semantics, and whether cancellation reaches the provider.

## Framework evidence

The same boundary appears in LiteLLM's provider-normalized API, MLflow PyFunc model interfaces,
and the OpenAI-compatible interfaces used by vLLM and OpenRLHF. Start with the [framework matrix](../frameworks/index.md)
and verify the exact release before copying an API shape.

## Framework examples

### LiteLLM — provider-normalized `completion` (adapted)

```python
from litellm import completion

class ChatAdapter:
    def __init__(self, model: str) -> None:
        self.model = model

    def complete(self, prompt: str) -> str:
        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
```

This solves application code having to learn each provider's request and response shape. The
adapter fits because `ChatAdapter.complete()` is the local contract while LiteLLM translates it
to a selected provider. See the official [LiteLLM documentation](https://docs.litellm.ai/).

### MLflow — `PythonModel.predict` (adapted)

```python
import mlflow

class AnswerModel(mlflow.pyfunc.PythonModel):
    def predict(self, context, model_input):
        return [answer(prompt) for prompt in model_input["prompt"]]
```

This solves serving different Python model implementations through one `predict` boundary. It
fits Adapter because MLflow PyFunc translates a model-specific callable into the interface used
by generic loading and serving code. See the official [MLflow PyFunc API
documentation](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html).


## ArjanCodes 2026 examples (adapted)

### Provider adapter at a persistence boundary

The 2026 ports example keeps the domain dependent on a small `InventoryPort` while an SQLAlchemy
connection remains an infrastructure detail. The adapter translates the port into SQL queries and
converts database rows into domain-level values; callers do not know whether inventory is backed by
SQLAlchemy, an API, or a test fake.

```python
from dataclasses import dataclass
from typing import Protocol

class InventoryPort(Protocol):
    def get_stock(self, sku: str) -> int: ...
    def reserve(self, sku: str, qty: int) -> int: ...

@dataclass
class SqlAlchemyInventoryAdapter:
    conn: Connection

    def get_stock(self, sku: str) -> int:
        row = self.conn.execute(
            text("SELECT stock FROM inventory WHERE sku = :sku"), {"sku": sku}
        ).fetchone()
        if row is None:
            raise LookupError(sku)
        return int(row.stock)

    def reserve(self, sku: str, qty: int) -> int:
        self.conn.execute(
            text("UPDATE inventory SET stock = stock - :qty WHERE sku = :sku"),
            {"sku": sku, "qty": qty},
        )
        self.conn.commit()
        return self.get_stock(sku)
```

This is the provider-adapter pressure: the use case owns the port, while the concrete database
provider owns translation, transactions, and row handling. Adapted from
[`domain/ports.py`](https://github.com/ArjanCodes/examples/blob/main/2026/ports/domain/ports.py)
and [`adapters/sqlalchemy_inventory.py`](https://github.com/ArjanCodes/examples/blob/main/2026/ports/adapters/sqlalchemy_inventory.py).
