# llama.cpp

> Repository: [ggml-org/llama.cpp@3057bb6](https://github.com/ggml-org/llama.cpp/tree/3057bb66c86c46d5781e50e85462a760ba7d1feb)
> Default branch: `master`
> Commit: `3057bb66c86c46d5781e50e85462a760ba7d1feb`
> License: [MIT](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/LICENSE)
> Domain: Local LLM inference runtime, model conversion, and HTTP serving
> Python/native boundary: C/C++ owns model loading, inference, sampling, server state, and concurrency; Python in `gguf-py/` owns GGUF metadata reading/writing and conversion tooling. This checkout does not provide a central Python inference binding, so Python architecture claims are limited to the tooling boundary.
> Evidence level: A for the C++ server queue/facade and GGUF Python adapter; B for the full native runtime boundary
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/llama-cpp` (read-only pinned checkout)

## 1. Executive Architecture Summary

llama.cpp is a native-first runtime. The C++ server composes model/context ownership, HTTP routes, request slots, model routing, and a worker queue around the `llama_*` runtime. The repository also contains Python GGUF tooling, but that tooling prepares and validates model files rather than orchestrating inference.

The useful architecture lesson is boundary placement: the server exposes a stable JSON/HTTP façade, while the hot path and resource lifecycle remain in C++. A bounded queue and explicit worker termination keep request scheduling separate from route parsing. Model load/unload and slot state are treated as resources with tests for cancellation and thread safety.

```text
HTTP client / CLI
       │
       ▼
tools/server/server.cpp ── route validation / JSON error boundary
       │
       ├── server queue and slot/model lifecycle
       └── llama context/model/sampler
                         │
                         ▼
                   ggml / CPU / GPU kernels

Python conversion and GGUF metadata tooling ──> GGUF files
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Driver/API façade | `tools/server/server.cpp` | HTTP routes, request parsing, status/error conversion, server composition |
| Runtime coordination | `tools/server/server-context.cpp`, `server-models.cpp`, `server-queue.cpp` | Context ownership, model routing, queueing, cancellation, worker lifecycle |
| Native domain/runtime | `src/llama-model.cpp`, `src/llama-context.cpp`, `src/llama-sampler.cpp` | Model state, inference context, sampling and backend calls |
| Python tooling adapter | `gguf-py/gguf/gguf_reader.py`, `gguf_writer.py` | Read/write validated GGUF metadata and conversion inputs |

There is no claim that the C++ runtime obeys a Python clean-architecture layering rule. The direct native ownership is the point: Python conversion tools and external clients interact through files or HTTP, not through an invented Python domain layer.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P12 | Adapter, façade, and provider/router boundary | [`tools/server/server.cpp`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tools/server/server.cpp) exposes completion/chat/model routes and converts exceptions to JSON HTTP errors; [`gguf-py/gguf/gguf_reader.py`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/gguf-py/gguf/gguf_reader.py) adapts binary metadata into Python values | [`tools/server/tests/unit/test_basic.py`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tools/server/tests/unit/test_basic.py), [`tools/server/tests/unit/test_completion.py`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tools/server/tests/unit/test_completion.py), [`gguf-py/tests/test_gguf_reader_validation.py`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/gguf-py/tests/test_gguf_reader_validation.py) | Clean Architecture ch19–20; Software Design ch35 | A |
| P16 | Concurrency, scheduling, and resource lifecycle | [`tools/server/server-queue.cpp`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tools/server/server-queue.cpp) owns deferred tasks, cancellation, condition variables, worker loop, and termination; `server-models.cpp` owns model load/unload coordination | [`tests/test-thread-safety.cpp`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tests/test-thread-safety.cpp), [`tests/test-model-load-cancel.cpp`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tests/test-model-load-cancel.cpp), [`tools/server/tests/unit/test_router.py`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tools/server/tests/unit/test_router.py), [`tools/server/tests/unit/test_slot_save.py`](https://github.com/ggml-org/llama.cpp/blob/3057bb66c86c46d5781e50e85462a760ba7d1feb/tools/server/tests/unit/test_slot_save.py) | Software Design ch41; Clean Architecture ch23 | A |

P01–P11, P13–P15, and P17 are not labeled authoritative from this focused review. The server has state and events, but that is not enough evidence for a business workflow, message bus, or testing-boundary pattern in Python.

## 4. Source Walkthrough

### `tools/server/server.cpp`

The server constructor initializes common/backend state, chooses router mode, creates the server context, and registers completion, chat, model, and health routes. The exception wrapper turns invalid arguments into client errors and unexpected exceptions into server errors, preserving a stable JSON response shape at the HTTP boundary.

### `tools/server/server-queue.cpp`

`server_queue::post` adds work under a mutex and notifies a worker. Deferred tasks can be canceled, `terminate` signals shutdown, and `worker_loop` drains or waits on the condition variable. This is an explicit ownership boundary for request work; route handlers do not manage worker threads directly.

### `gguf-py/gguf/`

The Python reader/writer is a file-format adapter. Tests focus on metadata and validation, while inference remains in the native runtime. This is a useful example of keeping a Python integration small when the performance-critical system is elsewhere.

## 5. Theory Versus Practice

The façade/adapter pattern suggests a thin outer interface and a stable inner port. llama.cpp keeps the HTTP façade thin, but its internal objects are intentionally native and performance-oriented rather than dependency-inverted Python services. The queue is coupled to server task types because cancellation and slot/model state must be coordinated at low overhead.

That coupling is appropriate for a local runtime with finite memory and device-specific kernels. It is not a template for a web application’s business layer: a Python service should usually keep its policy objects independent from thread primitives and use a smaller queue abstraction.

## 6. Testing Strategy

- Python server unit tests cover route behavior, completion, chat completion, MCP, model routing, and slot persistence.
- C++ tests cover thread safety, canceling model load, and save/load state.
- GGUF Python tests cover metadata and malformed-reader validation without starting inference.
- The full model/backend matrix was not executed; GPU and long-running server tests remain environment-dependent.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Native server owns nearly all runtime state | Predictable latency and direct control of memory/device resources | Do not hide native ownership behind a misleading Python abstraction |
| Route, queue, slot, and model state are closely coordinated | Enables streaming, cancellation, multi-model routing, and low overhead | Separate these concerns in ordinary applications where throughput is not the dominant constraint |
| Python is limited to conversion/metadata tooling | Keeps the hot path out of Python | Add a narrow binding only when its lifetime and error contract can be tested independently |
| JSON errors are produced at the native HTTP boundary | Clients receive consistent status and payloads | Preserve error categories and avoid leaking native stack details |

## 8. Practice Exercise

Use [the provider-adapter exercise](../../python-software-architecture/exercises/provider-adapter.md) to build a Python façade over two fake inference backends. Add a bounded worker queue, cancellation token, normalized JSON errors, and an explicit close method. Keep the backend implementation behind the adapter so the exercise demonstrates the boundary without pretending to reproduce llama.cpp’s native hot path.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `ggml-org/llama.cpp`, `master` |
| Pinned revision | `3057bb66c86c46d5781e50e85462a760ba7d1feb` |
| License | MIT, verified from repository `LICENSE` |
| Python/native boundary | C/C++ server and inference runtime; Python GGUF conversion/metadata tooling |
| Canonical pattern IDs | P12 (A), P16 (A) |
| Source evidence | `server.cpp`, `server-queue.cpp`, `server-models.cpp`, `gguf_reader.py` |
| Test evidence | Server unit tests, thread-safety/model-cancel C++ tests, and GGUF validation tests |
| Book mapping | Clean Architecture ch19–20 and ch23; Software Design ch35 and ch41 |
| Production compromise | Native coupling is intentional for latency and resource control; the Python surface is deliberately narrow |
| Practice exercise | `exercises/provider-adapter.md` |
