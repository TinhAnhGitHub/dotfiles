# Model Context Protocol Python SDK

> Repository: [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk/tree/9972c21aa42054fb1450c5fc614761ed11847ec6)
> Default branch: `main`
> Commit: `9972c21aa42054fb1450c5fc614761ed11847ec6`
> License: MIT (`LICENSE`)
> Domain: Typed MCP clients/servers, JSON-RPC dispatch, tools/resources/prompts, and stdio/HTTP transports
> Python version: `>=3.10` (`pyproject.toml`)
> Architecture style: Typed protocol kernel with ergonomic registries, middleware, and pluggable async transports
> Evidence level: A for P06, P07, P08, P10, P12, P14, P16, and P17; B for the limited P13 session-state finding

## 1. Executive Architecture Summary

### High-Level Architectural Diagram

The SDK has to let application authors register ordinary Python functions as MCP
tools, resources, or prompts, while clients and servers still speak a strict
JSON-RPC protocol over very different transports. It also has to handle concurrent
requests, notifications, cancellation, authentication, middleware, and cleanup.
The main architecture is:

```text
MCPServer decorators / add_* methods
    -> ToolManager | ResourceManager | PromptManager
    -> low-level Server request-handler table
    -> ServerRunner + JSONRPCDispatcher
    -> stdio | SSE | Streamable HTTP transport

Client Transport protocol -> stream pair
    -> Dispatcher -> ClientSession typed MCP methods

events/subscriptions -> SubscriptionBus -> listen stream / notifications
middleware -> request context -> handler -> result/error envelope
```

Python owns the protocol models, async orchestration, ASGI integration, registries,
and lifecycle. AnyIO, Starlette, Uvicorn, and generated `mcp-types` models are
dependencies at the runtime boundary; this checkout has no repository-owned
C++/CUDA/native execution plane. Optional native packages may accelerate parts of
an installation, but they are not the architecture studied here.

## 2. Layering & Boundary Discipline

### Inward Dependency Rule Audit

The ergonomic `MCPServer` is a composition façade. It turns functions into typed
tool/resource/prompt objects, registers request handlers on the low-level server,
and exposes transport-specific app runners. `ServerRunner` owns protocol validation,
connection state, middleware, and handler invocation. `JSONRPCDispatcher` owns
request correlation, receive order, concurrency, cancellation, and response writes.

On the client side, `Transport` only promises an async context manager yielding
read/write streams. `ClientSession` builds typed requests over a dispatcher. This
keeps MCP method code independent from whether the bytes arrived by subprocess
stdio, SSE, or Streamable HTTP. The boundaries are strong in types, but some
middleware and registration lists remain mutable for practical extension.

## 3. Macro Architectural Patterns in Action

| ID | Problem solved | Code modules and roles | Source / test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P06 | Keep protocol/session logic independent of transport and handler implementations | `Transport`, `Dispatcher`, `Server`, `ClientSession`, `Resource` ABC | [client/_transport.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/client/_transport.py), [shared/dispatcher.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/shared/dispatcher.py), [test_dispatcher.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/shared/test_dispatcher.py) | Clean Architecture ch14, ch16, ch19–20 | A |
| P07 | Assemble managers, handlers, middleware, and lifespan policy in one place | `MCPServer.__init__`, low-level `Server` construction, app factories | [mcpserver/server.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/mcpserver/server.py), [test_lifespan.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/server/test_lifespan.py) | Architecture Patterns ch13; Clean Architecture ch14 | A |
| P08 | Register tools, resources, prompts, templates, and extensions by stable names | `ToolManager`, `ResourceManager`, `PromptManager`, decorators, extensions | [tool_manager.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/mcpserver/tools/tool_manager.py), [test_tool_manager.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/server/mcpserver/test_tool_manager.py) | Software Design ch34; Architecture Patterns ch13 | A |
| P10 | Dispatch concurrent commands and fan out selected events | `JSONRPCDispatcher`, `ServerRunner`, `SubscriptionBus`, `ListenHandler` | [shared/jsonrpc_dispatcher.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/shared/jsonrpc_dispatcher.py), [subscriptions.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/subscriptions.py), [test_subscriptions.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/server/test_subscriptions.py) | Architecture Patterns ch08–11 | A |
| P12 | Present one session API over multiple wire transports | stdio, SSE, Streamable HTTP transports and `ClientSession` | [client/stdio.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/client/stdio.py), [server/streamable_http_manager.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/streamable_http_manager.py), [test_streamable_http.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/interaction/transports/test_streamable_http.py) | Software Design ch35; Clean Architecture ch19–20 | A |
| P13 | Track handshake, negotiated protocol, stateful sessions, and disconnect transitions | `Connection`, `ServerRunner`, `StreamableHTTPSessionManager` | [server/connection.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/connection.py), [server/runner.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/runner.py), [test_streamable_http_manager.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/server/test_streamable_http_manager.py) | Software Design ch38; Clean Architecture ch18 | B / limited |
| P14 | Apply observability, authorization, and request policy around handlers | `Server.middleware`, `ServerRunner._compose_server_middleware`, OTel/auth middleware | [server/context.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/context.py), [server/lowlevel/server.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/lowlevel/server.py), [test_otel.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/server/test_otel.py) | Software Design ch39; Clean Architecture ch23 | A |
| P16 | Bound async connections, subprocesses, HTTP sessions, and lifespan resources | `ClientSession` context, `stdio_client`, server lifespan, session manager | [client/session.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/client/session.py), [server/streamable_http_manager.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/streamable_http_manager.py), [test_lifespan.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/server/test_lifespan.py) | Software Design ch41; Clean Architecture ch23 | A |
| P17 | Verify registration, protocol errors, transport behavior, cancellation, and cleanup | unit, server, interaction, and issue regression tests | [test_jsonrpc_dispatcher.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/shared/test_jsonrpc_dispatcher.py), [test_tool_manager.py](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/tests/server/mcpserver/test_tool_manager.py) | Clean Architecture ch21 | A |

P01–P05, P09, and P11 are not claimed as primary patterns here. P13 is limited
to protocol/session state: the SDK is not a business workflow or Saga engine, and
its subscription event store is not automatically a durable event log.

## 4. Meso Tactical Design Patterns in Action

### P06 — Protocol Ports and Session Boundaries

**Problem.** A client should call typed `list_tools` or `call_tool` without knowing
whether a transport is a subprocess pipe, an HTTP stream, or an in-memory test
pair. A server handler should likewise receive a request context rather than raw
wire framing.

**Code modules and roles.** `mcp/client/_transport.py` defines `Transport` as a
structural protocol: any async context manager that yields read/write streams can
be used. `mcp/shared/dispatcher.py` defines the duplex `Dispatcher` contract for
request correlation and notifications. `ClientSession` adds typed MCP requests;
low-level `Server` and `ServerRunner` add typed handler dispatch. `Resource` is an
abstract base for resource implementations.

**How this expresses P06.** A port is a stable capability, and an adapter is a
translation to an outside mechanism. The protocols are ports; concrete transports,
dispatchers, and resource implementations are adapters. Python's `Protocol` means
an object can satisfy the interface by having the right methods, without needing
to inherit from a base class.

**Minimal standard-library sketch.**

```python
from typing import Protocol

class Transport(Protocol):
    def send(self, message: dict) -> None: ...

class Client:
    def __init__(self, transport: Transport): self.transport = transport
    def ping(self): self.transport.send({"method": "ping"})
```

**Tests and evidence.** `tests/shared/test_dispatcher.py` runs request/notification
behavior against in-memory peer pairs and checks back-channel restrictions,
timeouts, cancellation, and closure. This is A evidence for the port boundary.

**Compromise and simpler alternative.** A protocol plus dispatcher is more complex
than calling one local function. For a single in-process tool, direct calls are
clearer; use this boundary when transport substitution, concurrency, or protocol
compatibility matters.

### P07 — Composition Root in `MCPServer`

**Problem.** A server needs tool/resource/prompt managers, low-level request
handlers, a subscription bus, lifespan policy, middleware, authentication, and
extensions. If every caller wires these independently, server behavior becomes
inconsistent.

**Code modules and roles.** `MCPServer.__init__` creates `ToolManager`,
`ResourceManager`, and `PromptManager`, defaults to `InMemorySubscriptionBus`,
constructs low-level `Server` callbacks, and appends request-state and user
middleware. `_apply_extension` adds extension contributions and method handlers.

**How this expresses P07.** A composition root is the place where parts are wired
together. The constructor is that root for the ergonomic server. Decorators later
register application functions, but they do not reconstruct the transport kernel;
the composition already established the dependency graph.

**Minimal standard-library sketch.**

```python
def build_server(config):
    bus = InMemoryBus()
    tools = ToolManager()
    return Server(tools=tools, bus=bus, auth=config.auth)
```

**Tests and evidence.** `tests/server/test_lifespan.py` checks low-level and
ergonomic server lifespan behavior. Server integration tests exercise registered
handlers through the assembled object. This is A evidence for the construction
boundary.

**Compromise and simpler alternative.** A large constructor has many options and
can become a hidden service locator. For a small server, instantiate one router and
one transport explicitly; use a composition root once multiple policies must be
consistent.

### P08 — Tool, Resource, Prompt, and Extension Registries

**Problem.** MCP clients discover capabilities by stable names and URIs, while
server authors want to expose ordinary functions. The server must reject or warn
about duplicates and convert Python signatures into protocol schemas.

**Code modules and roles.** `ToolManager` stores a name-to-`Tool` dictionary;
`Tool.from_function` builds metadata, JSON schema, context injection, and result
conversion. `ResourceManager` stores concrete URI resources and URI templates.
`PromptManager` stores named prompt objects. `MCPServer.tool`, `.resource`, and
`.prompt` decorators are the authoring API; extension registration adds tools and
resources during construction.

**How this expresses P08.** A registry is a map from an external key to a callable
or object. The managers are registries with domain-specific validation. The
decorator is a convenient registration syntax: it constructs a protocol-aware
object and inserts it into the manager while returning the original function.
Duplicate names return the existing item or log a warning according to policy,
which is a deliberate compatibility choice rather than silent replacement.

**Minimal standard-library sketch.**

```python
tools = {}
def tool(name):
    def decorate(fn):
        if name in tools: raise ValueError("duplicate tool")
        tools[name] = fn
        return fn
    return decorate
```

**Tests and evidence.** `tests/server/mcpserver/test_tool_manager.py` covers
registration, duplicate behavior, schemas, context handling, annotations,
structured output, and removal. Resource-manager tests cover concrete resources,
templates, duplicates, and lookup; prompt-manager tests cover named prompt
registration. This is A evidence.

**Compromise and simpler alternative.** A manager adds indirection to what could
be a module-level function. For a tiny server, a dictionary and direct dispatch
may be enough. Use a manager when schema generation, duplicate policy, resource
templates, or runtime discovery needs one place to live.

### P10 — JSON-RPC Commands, Notifications, and Subscription Bus

**Problem.** Requests need correlated responses; notifications must not block the
receive loop; cancellation and progress must be associated with the right request;
and selected server events should reach multiple listening clients.

**Code modules and roles.** `JSONRPCDispatcher` owns the receive loop, request IDs,
concurrent handler tasks, cancellation, progress, and response writes.
`ServerRunner` turns wire methods into typed handler calls. `SubscriptionBus` is a
typed fan-out seam, and `ListenHandler` subscribes one stream, filters event kinds,
stamps the subscription ID, and sends events over that request's response stream.

**How this expresses P10.** A command is a request with a response; a notification
is fire-and-forget. The dispatcher separates those lifecycles and isolates handler
failures. The subscription bus is an event publisher/subscriber abstraction, but
the default `InMemorySubscriptionBus` is process-local. The source explicitly
describes an external Redis/NATS implementation as a possible seam; no such
external implementation is proven in this checkout.

**Minimal standard-library sketch.**

```python
subscribers = []
def publish(event):
    for subscriber in list(subscribers): subscriber(event)
```

**Tests and evidence.** Dispatcher tests cover out-of-order response correlation,
timeouts, cancellation, concurrent handlers, EOF, and notification isolation.
`tests/server/test_subscriptions.py` covers fan-out, ack ordering, filters, limits,
overflow, close, and listener failure isolation. This is A evidence for the
in-process event/message patterns.

**Compromise and simpler alternative.** In-memory fan-out has no replay or
cross-replica durability. A direct callback is simpler for one consumer; a broker
is needed for durable, multi-process events. Do not infer broker guarantees from
the `SubscriptionBus` protocol alone.

### P12 — Transport Adapters and Provider Router

**Problem.** Stdio, SSE, and Streamable HTTP have different connection, buffering,
session, and server-initiated-message rules. Duplicating MCP method logic per
transport would cause protocol behavior to drift.

**Code modules and roles.** `client/stdio.py` starts a subprocess and bridges its
stdin/stdout into streams. Client Streamable HTTP/SSE modules provide the same
stream shape. On the server, `StreamableHTTPServerTransport` and
`StreamableHTTPSessionManager` translate ASGI requests into server streams;
`MCPServer` delegates actual method handling to the low-level server.

**How this expresses P12.** Each transport is an adapter from a wire mechanism to
the common stream/dispatcher port. The client session and server runner therefore
operate on typed messages, not on sockets or ASGI scopes. Stateless HTTP and
stateful sessions remain explicit policy choices at the adapter boundary.

**Minimal standard-library sketch.**

```python
class Stdio:
    def send(self, message): self.output.write(encode(message) + "\n")

class Http:
    def send(self, message): return self.client.post(self.url, json=message)
```

**Tests and evidence.** `tests/interaction/transports/test_stdio.py` checks a
tool call and one-message-per-line behavior. Streamable HTTP interaction tests
cover JSON responses, stateless requests, request-scoped server messages, and
cancellation. This is A evidence.

**Compromise and simpler alternative.** Supporting three transports multiplies
edge cases. If the deployment is strictly local, stdio is simpler; if it is one
HTTP service, use one HTTP mode and avoid retaining compatibility paths you do not
need.

### P13 — Protocol and Session State (Limited Workflow Finding)

**Problem.** A connection is not valid in one state forever. It must negotiate a
protocol, reject calls before initialization when required, remember capabilities,
and eventually expire or close a stateful HTTP session.

**Code modules and roles.** `Connection` records negotiated protocol and readiness.
`ServerRunner` handles `initialize`, commits negotiation after successful
middleware/handler execution, and gates later methods. `StreamableHTTPSessionManager`
tracks session IDs, credentials, idle timeouts, maximum sessions, and cleanup.

**How this expresses P13.** These modules form a small state machine: the same
message is accepted or rejected according to connection/session state, and
transitions occur on initialize, close, delete, crash, or idle timeout. It is not a
business workflow with compensating actions, so the mapping is B and intentionally
limited to protocol lifecycle.

**Minimal standard-library sketch.**

```python
state = "new"
def handle(method):
    global state
    if method == "initialize": state = "ready"
    elif state != "ready": raise RuntimeError("not initialized")
```

**Tests and evidence.** `tests/server/test_connection.py` checks born-ready and
loop connections, capabilities, and back-channel behavior. Session-manager tests
cover one-shot `run`, cleanup, idle reaping, max sessions, failed opening requests,
and credential ownership. This supports B evidence for the limited state claim.

**Compromise and simpler alternative.** A full workflow library would be excessive
for protocol negotiation. For a simple one-request service, a boolean readiness
flag may suffice; use explicit states when invalid transitions and recovery matter.

### P14 — Middleware, Decorator, and Observability Chain

**Problem.** Authentication, request-state checks, tracing, logging, and policy
decisions should apply consistently to every request without copying them into each
tool handler.

**Code modules and roles.** `Server.middleware` stores middleware callables.
`ServerRunner._compose_server_middleware` wraps the inner handler in reverse order,
so the configured chain controls entry and exit. `OpenTelemetryMiddleware` is
installed by default at the low-level server; auth middleware belongs at the ASGI
transport edge. Extensions can intercept tool calls.

**How this expresses P14.** Middleware is a decorator for an entire request
pipeline: it receives a context and `call_next`, then can observe, reject, rewrite,
or delegate. This is the same idea as a function decorator, applied to a chain of
handlers. The SDK keeps wire/error shaping inside the chain so telemetry can see
failures as well as successes.

**Minimal standard-library sketch.**

```python
def middleware(next_handler):
    def wrapped(request):
        audit(request)
        return next_handler(request)
    return wrapped
```

**Tests and evidence.** OTel tests inspect spans; dispatcher/JSON-RPC tests cover
middleware observation, cancellation, and failure containment. Auth and transport
security tests exercise the outer boundary. This is A evidence.

**Compromise and simpler alternative.** Middleware order can be hard to understand,
and a short-circuiting middleware can bypass later handlers. For a small server,
one explicit wrapper around the use case may be clearer.

### P16 — Async Lifespan and Resource Ownership

**Problem.** Async streams, task groups, subprocesses, HTTP sessions, and background
listeners must close even when a request is cancelled or a peer disappears. A
server that forgets to cancel its tasks leaks work and connections.

**Code modules and roles.** `ClientSession.__aenter__` starts a task group and the
dispatcher; `__aexit__` cancels it, closes notification queues, and settles listen
routes. `stdio_client` uses an async context manager and bounded process shutdown.
`Server.run` enters the server lifespan. The Streamable HTTP manager enters its
lifespan once, owns a task group, enforces one `run()` call, and discards sessions
with shielded transport termination.

**How this expresses P16.** Context managers make ownership visible: entering
starts resources, exiting cancels and closes them. Shielded cleanup prevents an
outer cancellation from interrupting the final release. Idle timeouts and session
limits are operational lifecycle policies, not just configuration values.

**Minimal standard-library sketch.**

```python
from contextlib import contextmanager

@contextmanager
def connection():
    resource = open_resource()
    try: yield resource
    finally: resource.close()
```

**Tests and evidence.** Lifespan tests verify startup/shutdown contexts. Session
manager tests verify cleanup after graceful exit, exceptions, cancellation, idle
timeouts, deleted sessions, and failed opening requests. Stdio and dispatcher tests
cover process/stream closure. This is A evidence.

**Compromise and simpler alternative.** Async task groups and shielded cancellation
are more complex than a synchronous `with` block. For a short-lived local script,
one synchronous context manager is enough; use the full lifecycle approach for
long-lived servers and concurrent transports.

### P17 — Boundary and Failure-Injection Tests

**Problem.** Protocol systems often fail at edges rather than in the happy-path
handler: duplicate registration, malformed parameters, out-of-order responses,
cancelled requests, transport EOF, slow clients, or leaked sessions.

**Code modules and roles.** Unit tests target managers and dispatcher contracts.
Interaction tests connect real client/server layers over stdio and HTTP. Issue
regression tests preserve fixes for concurrency, request IDs, URL decoding, and
transport security. Fixtures also run in-memory dispatchers to avoid subprocesses
when the boundary under test is the protocol kernel.

**How this expresses P17.** These are architecture fitness tests: each one protects
a rule at a seam, such as “a notification handler cannot cancel the whole receive
loop” or “a failed opening request leaves no session.” The tests reveal production
compromises more clearly than the happy path does.

**Minimal standard-library sketch.**

```python
def test_closed_transport_rejects_request():
    transport = FakeTransport(closed=True)
    try: Client(transport).ping()
    except ConnectionError: pass
    else: raise AssertionError("closed transport accepted a request")
```

**Compromise and simpler alternative.** Full interaction matrices cost time and
can be platform-sensitive. A small tool can begin with fake transport contract
tests and one end-to-end test, then add cancellation and failure injection once it
becomes a long-lived service.

## 5. Micro Code Craftsmanship & Idioms

- Pydantic models turn Python function signatures and wire dictionaries into
  validated protocol schemas.
- AnyIO task groups, memory streams, and cancellation scopes make concurrency and
  cleanup explicit rather than relying on garbage collection.
- `Protocol` is used for replaceable seams; abstract classes are used where shared
  implementation or validation is useful.
- Error translation deliberately hides unexpected handler details from clients
  while retaining causes for server-side debugging.

## 6. Pragmatic Compromises & Architectural Trade-offs

### Theoretical ideal

The book-aligned ideal is a narrow protocol port, explicit composition root,
transport adapters, a typed command/event channel, middleware for cross-cutting
concerns, and deterministic resource ownership.

### Production implementation

The SDK combines a low-level protocol kernel with a convenience server, mutable
manager registries, modern and legacy protocol eras, three transport families,
in-memory subscriptions, middleware lists, and extensive cancellation/cleanup
logic.

### Difference and rationale

The extra layers make the SDK usable from both a small script and a long-lived ASGI
service. Compatibility and transport diversity require more state than a textbook
single-port design. The in-memory subscription bus is a safe default but does not
provide distributed durability; the source leaves external fan-out to a custom
implementation. Do not copy every transport or lifecycle option into an application
that needs only one local request path.

## 7. Curated File Tours (Annotated Walkthroughs)

1. [`src/mcp/server/mcpserver/server.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/mcpserver/server.py): ergonomic server composition, decorators, handler wiring, and transport runners.
2. [`src/mcp/server/mcpserver/tools/tool_manager.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/mcpserver/tools/tool_manager.py): tool registry, schema construction boundary, duplicates, and calls.
3. [`src/mcp/server/mcpserver/resources/resource_manager.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/mcpserver/resources/resource_manager.py): concrete URI/template lookup and security policy.
4. [`src/mcp/shared/dispatcher.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/shared/dispatcher.py) and [`src/mcp/shared/jsonrpc_dispatcher.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/shared/jsonrpc_dispatcher.py): request correlation, notifications, cancellation, and lifecycle contracts.
5. [`src/mcp/server/runner.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/runner.py): protocol state, validation, middleware composition, and handler execution.
6. [`src/mcp/server/subscriptions.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/subscriptions.py): typed event bus, listen streams, filters, backpressure, and close behavior.
7. [`src/mcp/client/session.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/client/session.py), [`src/mcp/client/stdio.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/client/stdio.py), and [`src/mcp/server/streamable_http_manager.py`](https://github.com/modelcontextprotocol/python-sdk/blob/9972c21aa42054fb1450c5fc614761ed11847ec6/src/mcp/server/streamable_http_manager.py): typed client transport and server HTTP session lifecycle.

## 8. Test Harness & Verification Strategy

- `tests/server/mcpserver/test_tool_manager.py` and resource/prompt manager tests:
  registration, schema, duplicate, template, and call behavior.
- `tests/shared/test_dispatcher.py` and `tests/shared/test_jsonrpc_dispatcher.py`:
  correlation, concurrency, cancellation, timeouts, EOF, back-channel policy,
  and middleware failure behavior.
- `tests/interaction/transports/test_stdio.py` and
  `tests/interaction/transports/test_streamable_http.py`: real transport round
  trips and transport-specific restrictions.
- `tests/server/test_lifespan.py`, `test_streamable_http_manager.py`,
  `test_connection.py`, and `test_session.py`: lifecycle, state, credentials,
  cleanup, and request routing.
- `tests/server/test_subscriptions.py` and
  `tests/interaction/lowlevel/test_subscriptions.py`: event filters, ack ordering,
  stream loss, graceful close, and concurrent listens.
- `tests/server/test_otel.py` and auth/security suites: cross-cutting boundaries.

The checkout has unusually strong seam coverage. It still cannot prove the behavior
of an external broker or every deployment-specific ASGI configuration not present
in the repository.

## Practice Exercise

Build a small async protocol server with a `ToolManager`, a `Transport` protocol,
an in-memory dispatcher, and a stdio adapter. Add middleware that logs requests,
an event bus with bounded subscriber queues, a state transition from `new` to
`ready`, and context-managed cleanup. Test duplicate tools, malformed calls,
out-of-order responses, cancellation, subscriber overflow, and transport closure.
Then identify which parts of the MCP SDK you would remove for a one-transport
application.

## Research Limitations

Only the pinned checkout and its source/tests were inspected. The subscription
module documents possible Redis/NATS implementations, but none was treated as
present or authoritative here. P13 is intentionally limited to protocol/session
state rather than a claim that the SDK implements business workflows or Sagas.
