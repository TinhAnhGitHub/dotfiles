# Weights & Biases (W&B)

> Repository: [wandb/wandb](https://github.com/wandb/wandb/tree/955991a2e30719bc520b1f36ce14e4686bba930e)
> Default branch: `main`
> Commit: `955991a2e30719bc520b1f36ce14e4686bba930e`
> License: MIT (`LICENSE`)
> Domain: Experiment tracking SDK, integrations, local service transport, and run lifecycle
> Python version: `>=3.10` (`pyproject.toml`)
> Architecture style: Typed Python façade over a separate local Go core, with adapters for messages and integrations
> Evidence level: A for P06, P12, P14, P16, and P17; B for P07 and the limited P10 finding; C for P08 because no central plugin registry was proven

## 1. Executive Architecture Summary

### High-Level Architectural Diagram

W&B has two related problems. The Python API must feel simple to a user who calls
`wandb.init()` and `run.log()`, but recording, synchronization, retries, and
process coordination should not block the training program. It also has to adapt
many third-party libraries for autologging without requiring those libraries to
depend on W&B directly.

```text
wandb.init / Run / integrations
    -> Settings: defaults, files, environment, runtime, kwargs
    -> InterfaceBase / InterfaceShared
    -> InterfaceSock -> ServiceClient -> local wandb-core process
                                 (protobuf over a local socket)
    -> server-side Go core and W&B service

integration PatchAPI
    -> lazy provider import -> temporary method wrapper -> Run logging
```

The Python SDK owns configuration, public run objects, adapters, and lifecycle
coordination. `wandb-core` is a separate Go module under `core/`; the repository
also contains a Rust parquet wrapper under `parquet-rust-wrapper/`. These are
process/library boundaries rather than Python/CUDA boundaries. The source reviewed
here does not claim that the Python SDK owns the performance-critical core.

## 2. Layering & Boundary Discipline

### Inward Dependency Rule Audit

`Run` is the user-facing façade. Settings are normalized before the run is built;
typed interface classes then translate public operations into service messages.
`ServiceClient` owns socket framing and response correlation, while
`service_process.py` owns starting the Go process. This keeps protobuf framing and
process details out of most user code.

The integration layer is deliberately more dynamic. `PatchAPI` imports a provider
only when needed and monkey-patches a target method for the duration of autologging.
That is useful at a large compatibility surface, but it is a runtime boundary and
not a compile-time dependency rule.

## 3. Macro Architectural Patterns in Action

| ID | Problem solved | Code modules and roles | Source / test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P06 | Keep the public SDK independent of the wire/service implementation | `InterfaceBase`, `InterfaceShared`, `InterfaceSock`, `ServiceClient` | [interface.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/interface/interface.py), [test_service_client.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/tests/unit_tests/test_lib/test_service_client.py) | Clean Architecture ch14, ch16, ch19–20 | A |
| P07 | Centralize configuration precedence and SDK assembly | `Settings`, `wandb.setup`, `Run` initialization | [wandb_settings.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/wandb_settings.py), [wandb_run.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/wandb_run.py) | Architecture Patterns ch13; Clean Architecture ch14 | B |
| P08 | Extend provider/integration behavior without hard-coding every library in the core | `PatchAPI` and integration modules; no proven central registry | [auto_logging.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/integration_utils/auto_logging.py) | Software Design ch34; Architecture Patterns ch13 | C / gap |
| P10 | Carry asynchronous records and lightweight callbacks across boundaries | protobuf service requests, `ServiceClient`, `wandb.trigger` | [service_client.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/lib/service/service_client.py), [trigger.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/trigger.py), [test_run_messages.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/tests/unit_tests/test_lib/test_run_messages.py) | Architecture Patterns ch08–11 | B / limited |
| P12 | Translate typed SDK operations to socket/queue service protocols | `InterfaceSock`, legacy `InterfaceQueue`, `ServiceClient` | [interface_sock.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/interface/interface_sock.py), [interface_queue.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/interface/interface_queue.py) | Software Design ch35; Clean Architecture ch19–20 | A |
| P14 | Add autologging around third-party calls | `PatchAPI`, `AutologAPI`, run decorators/guards | [auto_logging.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/integration_utils/auto_logging.py), [wandb_run.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/wandb_run.py) | Software Design ch39; Clean Architecture ch23 | A |
| P16 | Start, connect, flush, and tear down the local service safely | `ServiceProcess`, `ServiceConnection`, `ServiceFinalizer` | [service_process.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/lib/service/service_process.py), [service_connection.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/lib/service/service_connection.py), [test_service_finalizer.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/tests/unit_tests/test_lib/test_service_finalizer.py) | Software Design ch41; Clean Architecture ch23 | A |
| P17 | Test IPC, finalizers, settings, and integration patch seams with fakes | fake socket/server, finalizer tests, settings/system tests, patch tests | [test_service_client.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/tests/unit_tests/test_lib/test_service_client.py), [test_autolog_patch_integration.py](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/tests/unit_tests/test_autolog_patch_integration.py) | Clean Architecture ch21 | A |

P01–P05, P09, P11, and P13 are not claimed as primary patterns here. W&B has run
state and messages, but the inspected paths do not prove a DDD aggregate, CQRS
read model, or business workflow engine.

## 4. Meso Tactical Design Patterns in Action

### P06 — Port and Adapter for the SDK/Service Boundary

**Problem.** A run API should not expose socket framing, protobuf request classes,
or a legacy queue implementation. If those details leak into every logging method,
changing the local service would require changing the public SDK everywhere.

**Code modules and roles.** `InterfaceBase` defines the interface shape, including
asynchronous delivery. `InterfaceShared` supplies common typed publish/deliver
operations. `InterfaceSock` implements the current socket-backed route, while
`InterfaceQueue` retains the older queue-backed route. `ServiceClient` is the
lower-level wire client.

**How this expresses P06.** A port is the capability the application relies on;
an adapter translates that capability to an external mechanism. The interface
classes are the port, and socket/queue implementations are adapters. W&B can keep
`Run` focused on run semantics while the service transport evolves underneath.

**Minimal standard-library sketch.**

```python
class Publisher:
    def publish(self, message: dict) -> None: ...

class Run:
    def __init__(self, publisher: Publisher): self.publisher = publisher
    def log(self, data): self.publisher.publish({"kind": "log", "data": data})
```

**Tests and evidence.** Service-client tests use a fake asyncio server to check
publish, delivery, read errors, EOF, and mailbox closure. The direct port/adapter
source and transport tests support A evidence.

**Compromise and simpler alternative.** An interface plus IPC is unnecessary for a
small script. A direct callback or local list is easier when there is no need to
isolate service work. W&B accepts the extra boundary because logging should be
decoupled from user training and the core can be implemented separately.

### P07 — Centralized Settings and Composition

**Problem.** A configuration value can come from defaults, files, `WANDB_`
environment variables, runtime detection, `wandb.setup()`, `wandb.init()`, or
init keyword arguments. Scattering precedence rules across run methods would make
behavior hard to predict.

**Code modules and roles.** `Settings` is a typed Pydantic model. Its source
documentation and validators represent the precedence chain. `wandb.setup()` and
`Run` initialization then assemble settings, interfaces, hooks, and service
connections from that normalized object.

**How this expresses P07.** A composition root is where dependencies and policies
are wired together. W&B uses its setup/init path as that root, while `Settings`
acts as a configuration object rather than a global bag of unvalidated strings.
The result is dependency injection by construction: run methods receive already
resolved settings and service handles.

**Minimal standard-library sketch.**

```python
def build_settings(defaults, env, kwargs):
    return {**defaults, **env, **kwargs}  # later sources win
```

**Tests and evidence.** `tests/system_tests/test_core/test_wandb_settings.py`
checks settings paths, offline directories, and environment-derived behavior;
run tests check initialization and finish behavior. This is B evidence because
settings and assembly are direct, while the full precedence matrix spans more
than one test file.

**Compromise and simpler alternative.** A typed settings model is more code than
reading `os.environ` at the point of use, but the latter makes precedence and tests
fragile. For a small application, parse environment variables once in `main()` and
pass a plain dataclass.

### P08 — Integration Extension Mechanism (Negative Finding)

**Problem.** Autologging must support optional third-party libraries without
importing all of them at SDK startup. It should also be possible to add integration
logic without rewriting the core run object.

**Code modules and roles.** `PatchAPI` stores a provider name, target symbols, and
an `ArgumentResponseResolver`. `patch` lazily imports the provider, wraps the target
method, and records the original for `unpatch`. `AutologAPI` coordinates enabling,
disabling, run creation, and telemetry.

**How this expresses the pattern.** This is plugin-like extension by convention,
but the inspected revision does not establish a central registry or packaging
entry-point discovery comparable to MLflow or lm-evaluation-harness. Therefore the
P08 classification is C and is not an authoritative registry case study. The
important lesson is to distinguish an extension surface from a proven registry.

**Minimal sketch.**

```python
integrations = {"library": "library.module"}

def enable(name):
    module = __import__(integrations[name])
    return patch_module(module)
```

**Tests and evidence.** `tests/unit_tests/test_autolog_patch_integration.py` gives
direct patch behavior evidence, but there is no inspected test proving a generic
provider registry. Keep this finding labeled C and do not use it to claim that W&B
has a general plugin registry.

**Compromise and simpler alternative.** Explicit integration modules are easier to
debug than a generic plugin registry. If the set of integrations is small and
owned by one team, explicit imports are preferable; lazy patching is useful when
optional packages and compatibility versions dominate.

### P10 — Message Channel and Lightweight Event Hooks

**Problem.** Logging calls need to cross from Python to a background service, and a
run may expose small callbacks without turning every call into a blocking request.

**Code modules and roles.** `ServiceClient.publish` is fire-and-forget, while
`deliver` returns a response handle through mailbox correlation. `InterfaceSock`
wraps typed messages for that channel. `wandb.trigger` holds a simple synchronous
name-to-callback map with `register`, `call`, and `unregister`.

**How this expresses P10.** The service channel is a command/message boundary;
the trigger map is an in-process observer hook. It is not a durable event bus: the
source does not provide broker persistence, replay, or general retry semantics.
This distinction is why the evidence is B/limited rather than a full event-driven
architecture claim.

**Minimal sketch.**

```python
handlers = {}
def register(name, fn): handlers.setdefault(name, []).append(fn)
def publish(name, value):
    for fn in handlers.get(name, []): fn(value)
```

**Tests and evidence.** Run-message tests check fake-interface delivery and the
system-level run-message test checks the integrated path. Service-client tests
verify message correlation and failure handling. Trigger-specific behavioral
coverage was not found in the inspected test set, so retain the limitation.

**Compromise and simpler alternative.** A direct function call is clearer when
there is one consumer. A broker is justified only when durability, replay, or
cross-process fan-out is required; W&B's local service solves process decoupling,
not all of those broker problems.

### P12 — Socket and Queue Adapters

**Problem.** The current service transport and a legacy queue transport have
different primitives, but SDK callers should publish typed operations in the same
way.

**Code modules and roles.** `InterfaceShared` supplies common message methods.
`InterfaceSock` assigns stream IDs, builds protobuf server requests, and maps
responses into mailbox handles through `ServiceClient`. `InterfaceQueue` puts
messages on a queue and checks whether the process is alive; its source comments
identify it as a compatibility path.

**How this expresses P12.** Both adapters translate one conceptual interface into
different transports. The queue implementation is a useful production example:
the clean abstraction remains while a legacy backend is retained for compatibility.

**Minimal standard-library sketch.**

```python
class SocketAdapter:
    def send(self, message): self.socket.send(encode(message))

class QueueAdapter:
    def send(self, message): self.queue.put(message)
```

**Tests and evidence.** Service-client and run-message tests exercise the socket
path and fake interfaces; the adapter modules directly show the queue compatibility
path. This is A evidence for the adapter boundary.

**Compromise and simpler alternative.** Supporting two transports costs code and
test coverage. Remove the legacy adapter in a new application unless migration or
backward compatibility is an explicit requirement.

### P14 — Decorator and Monkey-Patch Instrumentation

**Problem.** An SDK needs to observe third-party calls without asking each library
to add W&B code. Instrumentation must also be reversible and must not change the
provider's result or async behavior.

**Code modules and roles.** `PatchAPI.patch` replaces a provider method with a
wrapper that resolves arguments and logs to the active run. It stores originals for
`unpatch` and handles sync/async targets. `AutologAPI` owns enable/disable and run
creation. `wandb_run.py` uses decorators/guards to reject operations after finish.

**How this expresses P14.** A decorator is a wrapper that adds behavior around an
existing function. Monkey-patching applies that idea to a method owned by another
module. The source makes the cross-cutting concern explicit, while the run remains
the owner of logging state.

**Minimal sketch.**

```python
def instrument(fn, record):
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        record(result)
        return result
    return wrapper
```

**Tests and evidence.** Autolog patch integration tests cover patched provider
behavior. Run tests cover finished-run guards and finish timeout raise/warn paths.
This supports A evidence for the instrumentation/guard boundary.

**Compromise and simpler alternative.** Monkey patches are sensitive to import
order, version changes, and multiple wrappers. Explicit callbacks or an adapter
owned by the application are safer when you control the provider code.

### P16 — Process and Resource Lifecycle

**Problem.** Starting a background service is easy; stopping it reliably when a run
ends, a socket breaks, or Python is cancelled is harder. A leaked core process or
unflushed log stream is a production failure.

**Code modules and roles.** `ServiceProcess` launches the core executable with
bounded waits and platform-specific termination. `ServiceConnection` connects,
registers exit cleanup, and coordinates finalization. `ServiceClient` closes the
mailbox/socket. `ServiceFinalizer` uses a daemon thread and `weakref.finalize` as a
fallback while explicitly warning that garbage collection and interpreter exit are
not reliable ownership mechanisms.

**How this expresses P16.** The process and connection are resources with owners;
context managers and explicit `finalize` establish normal cleanup, while the
finalizer is a last-resort safety net. This is a concrete example of lifecycle
design being part of the architecture, not an afterthought.

**Minimal sketch.**

```python
class Resource:
    def __enter__(self): self.open(); return self
    def __exit__(self, *exc): self.close()
```

**Tests and evidence.** `test_service_finalizer.py` checks weak-reference cleanup
and close behavior; service-client tests cover EOF and broken sockets; run tests
cover finish timeouts. The direct implementation/test pairing makes this A evidence.

**Compromise and simpler alternative.** A subprocess and IPC path add failure modes
and packaging work. A local application should use direct writes until throughput,
isolation, or cross-language core requirements justify the extra process.

### P17 — IPC and Integration Test Seams

**Problem.** Testing the real service process for every SDK unit test would be slow
and brittle, but testing only the Python façade would miss framing, EOF, cleanup,
and patching errors.

**Code modules and roles.** Service-client tests use fake servers and mailboxes.
Finalizer tests isolate weak-reference cleanup. Settings tests check configuration
paths and environment behavior. Integration tests use provider patch targets and
system tests exercise full run messages.

**How this expresses P17.** The suite separates unit tests at the socket/finalizer
seam from system tests at the Python-to-core seam. That is an architecture fitness
strategy: each test protects a contract at a boundary rather than asserting only
internal line coverage.

**Minimal sketch.**

```python
def test_run_uses_fake_transport():
    run = Run(publisher=FakePublisher())
    run.log({"loss": 1})
    assert run.publisher.messages
```

**Compromise and simpler alternative.** A two-level test suite costs maintenance,
but an IPC product needs both levels. A single-process library can usually rely on
fake adapters plus a small number of integration tests.

## 5. Micro Code Craftsmanship & Idioms

- Pydantic `Settings` turns a long precedence chain into validated data before the
  run is assembled.
- Protocols/ABCs describe narrow seams while protobuf provides an explicit wire
  schema between Python and Go.
- `weakref.finalize` is used as a fallback, not presented as a guarantee; explicit
  cleanup remains the reliable path.
- Lazy imports and reversible patches keep optional integrations from becoming
  unconditional dependencies.

## 6. Pragmatic Compromises & Architectural Trade-offs

### Theoretical ideal

The book-aligned ideal is a narrow SDK port, explicit composition, provider
adapters, decorator-based observability, and deterministic resource ownership.

### Production implementation

W&B uses a separate Go core process and a protobuf/socket channel, retains a legacy
queue adapter, centralizes settings in a validated model, and instruments external
libraries through dynamic patches. Finalizers provide best-effort cleanup after
explicit lifecycle handling.

### Difference and rationale

The extra process isolates logging and lets the core evolve in Go, but IPC and
process shutdown are more complex than a direct function call. Dynamic patching
supports a wide integration ecosystem, but it is less stable than compile-time
interfaces. These are sensible compromises for a general SDK; they are poor
defaults for a small application with one provider and no background service.

## 7. Curated File Tours (Annotated Walkthroughs)

1. [`wandb/sdk/wandb_settings.py`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/wandb_settings.py): typed settings, validation, and source precedence.
2. [`wandb/sdk/interface/interface.py`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/interface/interface.py): abstract SDK messaging seam.
3. [`wandb/sdk/interface/interface_sock.py`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/interface/interface_sock.py): typed-to-protobuf/socket adapter.
4. [`wandb/sdk/lib/service/service_client.py`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/lib/service/service_client.py): framing, publish/deliver, mailbox correlation, and broken-socket handling.
5. [`wandb/sdk/lib/service/service_process.py`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/lib/service/service_process.py): core subprocess startup and bounded termination.
6. [`wandb/sdk/lib/service/service_finalizer.py`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/lib/service/service_finalizer.py): fallback cleanup and its lifecycle warning.
7. [`wandb/sdk/integration_utils/auto_logging.py`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/wandb/sdk/integration_utils/auto_logging.py): lazy provider patching and reversible autologging.

The native/process boundary is visible in [`core/go.mod`](https://github.com/wandb/wandb/blob/955991a2e30719bc520b1f36ce14e4686bba930e/core/go.mod) and the `parquet-rust-wrapper/` directory; those components should not be described as Python modules.

## 8. Test Harness & Verification Strategy

- `tests/unit_tests/test_lib/test_service_client.py`: fake-server framing,
  publish/deliver, EOF, and mailbox failure behavior.
- `tests/unit_tests/test_lib/test_service_finalizer.py`: weak-reference cleanup.
- `tests/unit_tests/test_lib/test_run_messages.py` and
  `tests/system_tests/test_core/test_run_messages_full.py`: message-loop and
  integrated run-message behavior.
- `tests/system_tests/test_core/test_wandb_settings.py`: settings and environment
  seams.
- `tests/system_tests/test_core/test_wandb_run.py`: finished-run guards and finish
  timeout behavior.
- `tests/unit_tests/test_autolog_patch_integration.py`: provider patch behavior.

The checkout gives strong coverage for service, run, settings, and patch seams.
Provider-specific integrations and a generic plugin registry are not treated as
proven without direct registry tests.

## Practice Exercise

Implement a `Publisher` protocol with socket and in-memory adapters, a typed
settings object with explicit precedence, and a reversible `instrument` decorator.
Add tests for malformed settings, socket EOF, response correlation, explicit close,
finish-after-close, and a fake provider patch. Then decide whether your application
actually needs a separate process or whether the direct adapter is sufficient.

## Research Limitations

Only the pinned checkout and inspected source/tests were used. The P08 result is
explicitly a gap: W&B's integration mechanism is plugin-like, but this dossier does
not claim a central registry without source and test evidence. Trigger coverage is
also limited because no trigger-specific test file was found in the inspected set.
