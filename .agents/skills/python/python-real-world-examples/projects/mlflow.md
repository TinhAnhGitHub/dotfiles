# MLflow

> Repository: [mlflow/mlflow](https://github.com/mlflow/mlflow/tree/d669c6db5950710cab075de650f5e6a9b6362204)
> Default branch: `master`
> Commit: `d669c6db5950710cab075de650f5e6a9b6362204`
> License: Apache-2.0 (`LICENSE.txt`)
> Domain: Experiment tracking, model/deployment integrations, GenAI tracing, and ML lifecycle tooling
> Python version: `>=3.10` (`pyproject.toml`)
> Architecture style: Façade APIs over scheme-selected stores and entry-point-discovered providers
> Evidence level: A for P06, P07, P08, P12, P14, and P17; B for P16; no README-only claims are used

## 1. Executive Architecture Summary

### High-Level Architectural Diagram

MLflow has to preserve one user-facing tracking API while supporting local files,
SQL databases, REST servers, Databricks endpoints, and separately installed
deployment or gateway providers. It also has to observe user code without making
instrumentation failures break a training run. Its Python control plane is shaped
around registries and adapters:

```text
mlflow.start_run / MlflowClient / @mlflow.trace
    -> tracking URI and client façade
    -> TrackingStoreRegistry: URI scheme -> store builder
    -> FileStore | SQLAlchemyStore | RestStore | Databricks/UC store
    -> backend persistence or HTTP service

gateway/deployments
    -> ProviderRegistry + Python entry points
    -> provider adapter -> external LLM/deployment API

autologging/tracing decorators
    -> safe wrapper -> run/trace context -> async logging/export
```

Python owns the public API, provider selection, context management, and request
translation. The persistence and service boundaries are external files, databases,
HTTP APIs, OpenTelemetry, and optional Java/Scala/Spark integrations. The inspected
Python paths do not contain a repository-owned C++/CUDA hot path, so this case
study is about the control plane rather than numerical kernels.

## 2. Layering & Boundary Discipline

### Inward Dependency Rule Audit

`MlflowClient` and the fluent API are façades: they offer a small front door while
delegating to a tracking client and a selected store. `AbstractStore` defines the
backend capability boundary. URI parsing and entry-point lookup belong at the
outside of that boundary, where external configuration is converted into a store
object or provider object.

The dependency rule is practical rather than pure. Global registries are populated
at import time, environment variables influence tracking URI selection, and some
client/store classes retain compatibility methods across many backend versions.
That makes old deployments easier to support but means the composition boundary
is partly global and mutable.

## 3. Macro Architectural Patterns in Action

| ID | Problem solved | Code modules and roles | Source / test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P06 | Keep tracking operations independent of the storage backend | `AbstractStore`, `MlflowClient`, concrete store classes | [abstract_store.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/store/tracking/abstract_store.py), [test_utils.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/tests/tracking/_tracking_service/test_utils.py) | Clean Architecture ch14, ch16, ch19–20 | A |
| P07 | Wire built-ins and extensions into a usable application at startup | `_register_tracking_stores`, entry-point registration, client construction | [utils.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracking/_tracking_service/utils.py), [registry.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracking/registry.py) | Architecture Patterns ch13; Clean Architecture ch14 | A |
| P08 | Add providers/stores without editing the core dispatcher | `ProviderRegistry`, tracking-store registry, Python entry points | [provider_registry.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/gateway/provider_registry.py), [plugins.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/utils/plugins.py), [test_provider_registry.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/tests/gateway/test_provider_registry.py) | Software Design ch34; Architecture Patterns ch13 | A |
| P12 | Translate a stable MLflow API to heterogeneous stores and providers | URI scheme builders, `StoreRegistry`, gateway/deployment providers | [tracking/registry.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracking/_tracking_service/registry.py), [provider_registry.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/gateway/provider_registry.py) | Software Design ch35; Clean Architecture ch19–20 | A |
| P14 | Add tracing and autologging around user code | `mlflow.trace`, autologging safety decorators/context managers | [fluent.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracing/fluent.py), [safety.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/utils/autologging_utils/safety.py) | Software Design ch39; Clean Architecture ch23 | A |
| P16 | Manage asynchronous logging and trace/run cleanup | async logging queue in store layer, run/trace context managers, flush behavior | [abstract_store.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/store/tracking/abstract_store.py), [fluent.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracing/fluent.py) | Software Design ch41; Clean Architecture ch23 | B |
| P17 | Verify registries, plugins, tracing, and failure isolation | entry-point fixtures, provider tests, tracing/autologging tests | [test_utils.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/tests/tracking/_tracking_service/test_utils.py), [test_fluent.py](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/tests/tracing/test_fluent.py) | Clean Architecture ch21 | A |

P01–P05, P09–P11, and P13 are not asserted as primary patterns in this dossier.
MLflow has workflows and event-like telemetry, but the inspected code does not
establish a DDD aggregate, CQRS read model, or durable message bus as the focus of
these examples.

## 4. Meso Tactical Design Patterns in Action

### P06 — Ports and Adapters at the Tracking Store Boundary

**Problem.** A call such as “create a run” should not change when the tracking URI
points to a local directory, a SQL database, or a REST server. If business-facing
client code imported each backend directly, every new backend would spread
conditionals through the SDK.

**Code modules and roles.** `AbstractStore` in `mlflow/store/tracking/abstract_store.py`
defines the backend operations and shared capabilities. Concrete stores implement
those operations for files, SQLAlchemy, HTTP, and Databricks-style services.
`MlflowClient` and the tracking service utilities call the abstract store after
selection, so the client is not responsible for SQL or HTTP details.

**How this expresses P06.** A port is simply a stable interface owned by the
application; an adapter is the implementation that speaks to an outside system.
`AbstractStore` is the port, and each concrete store is an adapter. The interface
is large because MLflow must preserve a broad compatibility surface, but the
dependency direction is still clear: tracking operations depend on capabilities,
not on one persistence technology.

**Minimal standard-library sketch.**

```python
from typing import Protocol

class RunStore(Protocol):
    def create_run(self, name: str) -> str: ...

class Client:
    def __init__(self, store: RunStore): self.store = store
    def start(self, name: str) -> str: return self.store.create_run(name)
```

**Tests and evidence.** Tracking utility tests resolve file, SQL, REST, Databricks,
custom, and entry-point stores, while test plugins provide fake implementations.
This is A evidence because the port, adapters, and resolution tests are directly
present.

**Compromise and simpler alternative.** A large abstract store can become a
compatibility burden and may expose operations a backend cannot implement equally
well. For a service with one database, a repository module with direct SQL is often
clearer. Use a port when multiple backends or a separately deployed tracking
server are real requirements.

### P07 — Composition Root and Dependency Injection

**Problem.** The SDK must start with all built-in schemes and providers wired, while
still allowing an installed plugin to add a new scheme. The place where these
objects are assembled is a composition root: the “wiring code” that connects
interfaces to implementations.

**Code modules and roles.** `set_tracking_uri` manages the process-wide selection
input. `_register_tracking_stores` in `tracking/_tracking_service/utils.py` creates
the global registry and registers built-in schemes, then asks the registry to
discover entry points. `MlflowClient` obtains the selected store lazily, keeping
construction out of most call sites.

**How this expresses P07.** Dependency injection means passing a dependency in or
having one controlled factory create it, instead of constructing it in every method.
MLflow combines both forms: the registry injects a store based on a URI, while
tests can register a custom store or plugin. Startup registration is centralized,
so the rest of the client can depend on the registry contract.

**Minimal sketch.**

```python
def build_app(config):
    store = SqlStore(config.database_url) if config.sql else FileStore(config.path)
    return Client(store)
```

**Tests and evidence.** `tests/tracking/_tracking_service/test_utils.py` covers
custom schemes, direct registry registration, entry-point plugins, broken plugins,
and unknown schemes. This directly verifies the composition seam (A evidence).

**Compromise and simpler alternative.** Import-time global registration is easy for
a library user but can make tests order-dependent and makes configuration timing
surprising. An application with one deployment can build its client once in
`main()` and pass it explicitly, avoiding a global registry.

### P08 — Provider and Plugin Registries

**Problem.** Gateway and deployment integrations evolve independently. Requiring a
core pull request for every provider would make the central package a bottleneck;
letting arbitrary names silently overwrite providers would make behavior unsafe.

**Code modules and roles.** `ProviderRegistry` stores provider names and classes,
rejects duplicate registration, checks the allowed-provider policy, and exposes
lookup. `_register_default_providers` adds built-ins. `_register_plugin_providers`
uses `get_entry_points("mlflow.gateway.providers")` to load installed extensions.
The tracking registry applies a similar scheme-to-builder idea for stores.

**How this expresses P08.** A registry is a map from a stable key to a constructor
or implementation. An entry point is package metadata that tells Python where an
external plugin can be loaded. MLflow separates discovery from use: the plugin is
found during registration, while the selected provider is looked up when a request
needs it. Duplicate checks and allowlists are production safeguards around the
pattern.

**Minimal sketch.**

```python
providers = {}

def register(name, provider):
    if name in providers: raise ValueError("duplicate provider")
    providers[name] = provider

def get(name): return providers[name]
```

**Tests and evidence.** `tests/gateway/test_provider_registry.py` checks defaults,
keys, missing providers, and allowlist policy. Tracking tests exercise entry-point
registration and broken-plugin behavior. This is A evidence.

**Compromise and simpler alternative.** Entry-point discovery adds import-time
work, packaging/version compatibility concerns, and failures that may surface
only when a provider is selected. An explicit dictionary in the composition root
is simpler for a closed set of providers. Use plugins when independent packages
must extend the system.

### P12 — URI Router and Provider Adapters

**Problem.** `file:`, `sqlite:`, `http:`, Databricks, gateway, and deployment
providers have different protocols, authentication, and failure modes. Callers
still need one client surface and one error vocabulary.

**Code modules and roles.** `TrackingStoreRegistry.get_store` resolves a URI into a
normalized scheme and calls a cached builder. The utility module registers file,
SQLAlchemy, REST, and Databricks builders. Gateway provider lookup maps a provider
name to a class that translates MLflow requests into that provider’s API.

**How this expresses P12.** The router decides which adapter is appropriate; the
adapter translates calls and responses. This is more than a façade because the
provider implementation owns protocol-specific details, while the router is the
stable selection point.

**Minimal sketch.**

```python
routes = {"file": FileStore, "sqlite": SqlStore, "http": RestStore}

def store_for(uri):
    scheme = uri.split(":", 1)[0]
    return routes[scheme](uri)
```

**Tests and evidence.** Store-resolution tests cover standard schemes, custom
schemes, unknown schemes, entry points, and a broken plugin. Provider tests cover
the policy boundary. The direct source/test pairing supports A evidence.

**Compromise and simpler alternative.** URI routing is convenient but hides which
network, credentials, and retry behavior a call will use. If an application owns
one backend, pass a typed store directly and avoid scheme parsing.

### P14 — Decorator, Middleware, and Observability Wrapper

**Problem.** MLflow wants tracing and autologging around arbitrary user functions,
including third-party training code, without requiring users to insert logging at
every line. At the same time, a telemetry bug should not normally abort training.

**Code modules and roles.** `mlflow.tracing.fluent` implements `@mlflow.trace`
using context and span creation, including sync/async/error paths. The autologging
safety module wraps patched functions, manages runs, catches broad instrumentation
failures in non-testing modes, and restores behavior when appropriate.

**How this expresses P14.** A decorator is a function that wraps another function
and adds behavior before or after it. Here the wrapper records inputs, outputs, and
errors, or establishes a managed run. The wrapped function remains the domain
operation; tracing is an orthogonal concern.

**Minimal sketch.**

```python
def traced(fn):
    def wrapper(*args, **kwargs):
        print("start", fn.__name__)
        try: return fn(*args, **kwargs)
        finally: print("finish", fn.__name__)
    return wrapper
```

**Tests and evidence.** `tests/tracing/test_fluent.py` verifies nested sync/async
traces, outputs, errors, streaming, and flush behavior. Autologging unit and
behavior tests exercise safety wrappers. This is A evidence.

**Compromise and simpler alternative.** Wrapping third-party APIs can be brittle
when signatures or call order change, and suppressing telemetry exceptions can
hide observability gaps. A small service can use explicit logging in its use case;
use decorators when cross-cutting instrumentation must be consistently applied.

### P16 — Asynchronous Logging and Resource Lifecycle

**Problem.** Logging every metric synchronously would slow user workloads, but
background work creates a lifecycle question: when are events flushed, and what
happens if a run or process exits?

**Code modules and roles.** The tracking store abstraction initializes asynchronous
logging support where configured. Fluent tracing uses context managers and flush
paths to close spans and restore context. Client/run code delegates lifecycle to
these layers rather than asking every model integration to manage queues.

**How this expresses P16.** The queue is a scheduled resource and the run/trace
context is its ownership boundary. The architecture trades immediate durability
for lower foreground latency and must therefore expose shutdown/flush behavior.

**Minimal sketch.**

```python
with TraceSession() as trace:
    trace.record("step")
# __exit__ flushes and closes the resource
```

**Tests and evidence.** Tracing tests explicitly cover async behavior and flush;
tracking store tests cover store construction and backend behavior. The lifecycle
claim is B because the abstraction and targeted tracing tests are direct, while
deployment-specific queue behavior is broader than this dossier.

**Compromise and simpler alternative.** Background logging can lose the last
events on an abrupt process kill and can make tests timing-sensitive. For a small
tool, synchronous writes with an explicit `close()` are easier to reason about.

### P17 — Plugin and Observability Test Seams

**Problem.** Registries and decorators fail at boundaries: a plugin may be broken,
a URI may be unknown, a provider may be disallowed, or a traced function may raise.
Tests need to isolate those conditions without contacting every real service.

**Code modules and roles.** `tests/resources/mlflow-test-plugin/` contains fake
store/deployment/evaluator plugins. Tracking tests replace or register entry
points. Tracing tests use small functions and inspect spans/errors; autologging
tests exercise the safety policy.

**How this expresses P17.** These are architecture fitness tests: they protect a
rule at a boundary, such as “duplicate providers are rejected” or “instrumentation
does not change the user exception.” They make extension behavior a contract rather
than an undocumented convention.

**Minimal sketch.**

```python
def test_unknown_scheme_is_clear():
    with pytest.raises(KeyError): store_for("other://run")
```

**Compromise and simpler alternative.** Plugin matrices can be expensive to keep
current. A smaller application can begin with one fake adapter, one unknown-input
test, and one end-to-end backend test, then add contract tests for every external
provider that matters.

## 5. Micro Code Craftsmanship & Idioms

- URI schemes, provider names, and entry-point groups are stable strings; the
  registry validates them at the boundary rather than scattering string checks.
- Lazy client/store construction reduces startup work and lets tests substitute a
  backend before it is used.
- Context managers and `contextvars` make run/trace ownership explicit across
  nested and asynchronous calls.
- Autologging deliberately contains instrumentation failures so an optional feature
  remains optional to the user’s primary workload.

## 6. Pragmatic Compromises & Architectural Trade-offs

### Theoretical ideal

The book-aligned ideal is an explicit composition root, narrow ports, provider
adapters at the edge, decorators for cross-cutting concerns, and lifecycle objects
whose ownership is obvious.

### Production implementation

MLflow combines those ideas with process-wide tracking URI state, import-time
registries, packaging entry points, a broad compatibility-oriented store ABC,
autologging monkey patches, and asynchronous telemetry.

### Difference and rationale

The choices favor a library that can be dropped into many existing training
programs and deployed against many old/new backends. Global defaults and discovery
reduce setup for users; safety wrappers preserve training when observability is
imperfect. The costs are hidden state, deferred plugin failures, version-sensitive
interfaces, and eventual-consistency/flush concerns. Do not copy the full registry
and autologging machinery into a single-backend application.

## 7. Curated File Tours (Annotated Walkthroughs)

1. [`mlflow/tracking/_tracking_service/utils.py`](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracking/_tracking_service/utils.py): tracking URI state, built-in store registration, entry points, and store lookup.
2. [`mlflow/tracking/_tracking_service/registry.py`](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracking/_tracking_service/registry.py): scheme-to-builder registry and cached store construction.
3. [`mlflow/gateway/provider_registry.py`](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/gateway/provider_registry.py): default providers, plugin entry points, duplicate checks, and allowlists.
4. [`mlflow/store/tracking/abstract_store.py`](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/store/tracking/abstract_store.py): backend port and asynchronous logging hooks.
5. [`mlflow/tracing/fluent.py`](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/tracing/fluent.py): tracing decorator/context implementation.
6. [`mlflow/utils/autologging_utils/safety.py`](https://github.com/mlflow/mlflow/blob/d669c6db5950710cab075de650f5e6a9b6362204/mlflow/utils/autologging_utils/safety.py): safe wrapping and managed-run behavior.

## 8. Test Harness & Verification Strategy

- `tests/gateway/test_provider_registry.py`: provider keys, lookup, and policy.
- `tests/tracking/_tracking_service/test_utils.py`: built-ins, custom stores,
  entry-point plugins, broken plugins, and unknown schemes.
- `tests/resources/mlflow-test-plugin/`: concrete fake plugin implementations used
  to exercise extension seams.
- `tests/tracing/test_fluent.py`: nested, async, streaming, output, error, and
  flush behavior.
- `tests/autologging/test_autologging_safety_unit.py` and related behavior tests:
  instrumentation containment and restoration.

The tests validate source-level extension boundaries at the pinned revision; they
do not prove every external vendor provider or deployment target.

## Practice Exercise

Create a small `RunStore` protocol with file and in-memory adapters, a URI registry,
and a plugin registration function. Add a `@traced` decorator that records success
and failure without changing the wrapped function’s exception. Test duplicate and
unknown providers, a fake entry point, adapter-specific error translation, and an
explicit flush on context exit. Then decide which MLflow compromises you would
keep for a service with one backend.

## Research Limitations

This dossier uses only the pinned checkout and inspected source/tests. It does not
claim that every MLflow flavor, deployment plugin, or language integration follows
the same architecture, and it treats telemetry as distinct from a durable event
bus unless a source path proves otherwise.
