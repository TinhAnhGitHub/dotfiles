# Policy pipeline

## Intent

Compose an ordered set of small rules or transformations around a stable operation. A policy
should answer one question or own one responsibility; the pipeline owns ordering and composition.

## Use when

Use a policy pipeline when authorization, validation, audit, routing, filtering, or enrichment
rules vary independently, must be tested separately, or are selected by configuration. Prefer a
callable policy when it only needs its arguments; use a policy object when it owns dependencies or
state.

## Why

One-rule/one-responsibility policies keep the orchestration from becoming a growing conditional.
Python's callable protocol is usually enough: policies can be composed in a list, registered by a
name, and selected by settings without a class hierarchy. Returning a new value (rather than
mutating shared input) makes order and failure behavior easier to reason about.

## Example

```python
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class User:
    name: str
    is_active: bool
    roles: frozenset[str]

@dataclass(frozen=True)
class Request:
    action: str
    required_role: str | None = None
    requires_audit: bool = False
    audit_log: tuple[str, ...] = ()
    access_granted: bool = False

Policy = Callable[[User, Request], Request]
POLICY_REGISTRY: dict[str, Policy] = {}

def register(name: str):
    def decorator(policy: Policy) -> Policy:
        if name in POLICY_REGISTRY:
            raise ValueError(f"duplicate policy: {name}")
        POLICY_REGISTRY[name] = policy
        return policy
    return decorator

@register("active_user")
def active_user(user: User, request: Request) -> Request:
    if not user.is_active:
        raise PermissionError("inactive users cannot make requests")
    return request

@register("role_required")
def role_required(user: User, request: Request) -> Request:
    if request.required_role and request.required_role not in user.roles:
        raise PermissionError(f"missing role: {request.required_role}")
    return request

@register("grant_access")
def grant_access(user: User, request: Request) -> Request:
    return replace(request, access_granted=True)

@dataclass(frozen=True)
class Settings:
    enabled_policies: tuple[str, ...] = ("active_user", "role_required", "grant_access")

def configured_policies(settings: Settings) -> tuple[Policy, ...]:
    try:
        return tuple(POLICY_REGISTRY[name] for name in settings.enabled_policies)
    except KeyError as exc:
        raise ValueError(f"unknown policy: {exc.args[0]!r}") from exc

def apply_policies(user: User, request: Request,
                   policies: Sequence[Policy]) -> Request:
    current = request
    for policy in policies:
        current = policy(user, current)
    return current
```

The registry and `Settings` make policy selection explicit; the loop is the composition. Add an
audit policy as another callable, rather than making every policy know about auditing. This is an
adaptation of the [ArjanCodes policy examples](https://github.com/ArjanCodes/examples/tree/main/2026/policy)
and the [policy video](https://www.youtube.com/watch?v=wYeDGkdMi3g) (2026 source, fetched
2026-08-30; adapted).

## When not to use

Keep one local conditional or a direct function call when the rule set is fixed, short, and not
independently tested. Do not hide important ordering, side effects, or authorization decisions in
an opaque registry. If policies need unrelated protocols, lifecycle, or complex shared state, a
workflow or explicit service boundary may be clearer.

## Trade-offs and tests

The pipeline introduces ordering, named configuration, import/registration coupling, and a choice
between fail-fast exceptions and accumulated violations. Define whether each policy may transform
the request, whether it must be pure, and which policy owns side effects.

Test each policy against the same callable contract, then test the composition separately:

- empty policies return the original request;
- order is observable and intentional;
- a rejected request stops later policies;
- duplicate and unknown registry names fail clearly;
- settings select exactly the requested policies;
- transformations do not mutate earlier inputs when immutability is promised.

## Framework examples

### LangChain — composable middleware policies

LangChain's middleware hooks solve the problem of adding guardrails, logging, retries, or context
checks without changing the agent loop. A decorated `wrap_model_call` function is a callable policy;
the `middleware` list is its configured composition. Keep each middleware focused and document its
execution order.

```python
from collections.abc import Callable
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

@wrap_model_call
def require_tenant(request: ModelRequest,
                   handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    if not request.state.get("tenant_id"):
        raise PermissionError("tenant is required")
    return handler(request)

agent = create_agent(
    model="provider:model",
    tools=[],
    middleware=[require_tenant],
)
```

Adapted from [LangChain custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom)
(1.x documentation, fetched 2026-08-30; adapted).
