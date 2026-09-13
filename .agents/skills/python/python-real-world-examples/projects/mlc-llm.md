# MLC LLM

> Repository: [mlc-ai/mlc-llm@9fa644f](https://github.com/mlc-ai/mlc-llm/tree/9fa644f54b04983adea4d0168f49fc6af4a893ba)
> Default branch: `main`
> Commit: `9fa644f54b04983adea4d0168f49fc6af4a893ba`
> License: [Apache-2.0](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/LICENSE)
> Domain: Compiled LLM serving, OpenAI-compatible APIs, and multi-server routing
> Python/native boundary: Python owns configuration, protocol translation, engine orchestration, and process routing; TVM/TVM-FFI and compiled model libraries own the generation engine and device execution.
> Evidence level: A for Python FFI/router seams and their tests; B for compiled-runtime lifecycle
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/mlc-llm` (read-only pinned checkout)

## 1. Executive Architecture Summary

MLC LLM places a Python control plane over a compiled runtime. `SyncMLCEngine` is a deliberately simple synchronous wrapper for tests and debugging; the default serving path uses `MLCEngineBase` and a threaded TVM engine. A separate router can launch multiple server processes and forward OpenAI-compatible requests to the least-congested endpoint or to a disaggregated prefill/decode topology.

The architecture isolates protocol and lifecycle decisions from the model library. Python validates requests, creates TVM global-function handles, registers callbacks, tracks request state, and owns server processes. The compiled engine performs token generation and device work.

```text
OpenAI-style request
        │
        ▼
JSON FFI / Python engine façade
        │
        ├── sync engine for tests/debugging
        ├── threaded engine + callback streams
        └── Router ── PopenServer processes / HTTP endpoints
                              │
                              ▼
                    TVM FFI / compiled model library
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Protocol/API adapter | `python/mlc_llm/protocol/openai_api_protocol.py`, `json_ffi/` | Typed request/response shape and JSON-compatible transport |
| Engine façade | `python/mlc_llm/serve/sync_engine.py`, `serve/engine_base.py` | Config validation, request submission, streaming callbacks, reset/exit |
| Process/router perimeter | `python/mlc_llm/router/router.py`, `serve/popen_server.py` | Start/terminate servers, choose endpoints, proxy requests |
| Compiled runtime | TVM global functions and model libraries created by `mlc.serve.*` | Scheduling, decoding, device execution, and native resource ownership |

The Python layer does not attempt to reproduce the compiled scheduler. Its seam is a function registry/FFI contract plus explicit request and process lifecycle methods.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P12 | Adapter, façade, and provider/router boundary | [`python/mlc_llm/serve/sync_engine.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/python/mlc_llm/serve/sync_engine.py) resolves `mlc.serve.create_engine` and exposes `generate`; [`python/mlc_llm/protocol/openai_api_protocol.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/python/mlc_llm/protocol/openai_api_protocol.py) defines the external request contract; `router.py` translates and forwards requests | [`tests/python/json_ffi/test_json_ffi_engine_mock.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/tests/python/json_ffi/test_json_ffi_engine_mock.py), [`tests/python/router/test_router.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/tests/python/router/test_router.py) | Clean Architecture ch19–20; Software Design ch35 | A |
| P16 | Concurrency, scheduling, and resource lifecycle | [`python/mlc_llm/serve/engine_base.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/python/mlc_llm/serve/engine_base.py) creates the threaded engine and background loop; [`python/mlc_llm/router/router.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/python/mlc_llm/router/router.py) starts/terminates `PopenServer` instances and tracks endpoint load | [`tests/python/serve/test_serve_async_engine.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/tests/python/serve/test_serve_async_engine.py), [`tests/python/serve/test_serve_sync_engine.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/tests/python/serve/test_serve_sync_engine.py), [`tests/python/serve/test_serve_engine_mock.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/tests/python/serve/test_serve_engine_mock.py) | Software Design ch41; Clean Architecture ch23 | A |

The conversation-template registry is a supporting P08 seam in [`python/mlc_llm/conversation_template/registry.py`](https://github.com/mlc-ai/mlc-llm/blob/9fa644f54b04983adea4d0168f49fc6af4a893ba/python/mlc_llm/conversation_template/registry.py), but the focused matrix records the stronger P12/P16 evidence above.

## 4. Source Walkthrough

### `serve/sync_engine.py`

The constructor validates model/config inputs, resolves a device, obtains TVM global functions for initialization, request addition, stepping, abort, reset, metrics, and callbacks, then initializes the engine and tokenizer. `generate` adds requests and repeatedly calls `step` until every request is complete. This makes the Python-to-FFI contract visible and testable.

### `serve/engine_base.py`

The threaded base creates `mlc.serve.create_threaded_engine`, starts a background loop, routes callback chunks into Python streams, and exposes `exit_background_loop`/`reset`. The lifecycle belongs to the engine façade, even though actual execution is compiled.

### `router/router.py`

The router starts one `PopenServer` per endpoint, tracks request counts, and chooses the least-loaded endpoint for round-robin completion. It decrements the count in cleanup paths and terminates child servers explicitly. Disaggregated prefill/decode adds a second topology, which is why the router is more than a simple HTTP client.

## 5. Theory Versus Practice

The adapter pattern asks for a stable port over an unstable mechanism. MLC LLM achieves this with OpenAI-like protocol types and TVM global functions. The lifecycle is intentionally split between sync and threaded engine implementations because the sync path is easier to reason about while the production path needs background work and streaming.

The compiled runtime and Python façade are not fully independent: engine function names, callback signatures, tokenization, and model configuration must agree. That coupling is a valid foreign-function boundary; it should be documented and tested rather than hidden behind a generic “engine” interface that cannot express capability differences.

## 6. Testing Strategy

- Mock JSON-FFI tests use `mock://echo` to verify normal responses, malformed inputs, and invalid parameters without a compiled model.
- Sync and async engine tests cover request generation, callbacks, and lifecycle behavior.
- Router tests exercise multiple endpoints/topologies and verify forwarding plus termination.
- Full GPU/compiled-model tests remain environment-dependent and were not executed in this pass.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Python depends on named TVM global functions | Keeps the control plane thin and makes compiled kernels replaceable | Add version/capability checks at startup; otherwise FFI drift fails late |
| Separate sync/debug and threaded serving engines | Fast deterministic tests plus high-throughput production serving | Do not maintain two paths for a small application unless their contracts are shared and tested |
| Router owns child processes and endpoint load counters | Enables multi-server and disaggregated deployments | Process cleanup and counter decrements must be exception-safe and observable |
| Target/model compilation shapes deployment | Produces efficient device-specific artifacts | Avoid compiler specialization until the operational cost of rebuilding and compatibility is acceptable |

## 8. Practice Exercise

Use [the provider-adapter exercise](../../python-software-architecture/exercises/provider-adapter.md): define a typed generation port, implement a synchronous fake and an async worker-backed adapter, and add a router that chooses the least-loaded endpoint. Test FFI-style capability errors, cancellation, and idempotent termination.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `mlc-ai/mlc-llm`, `main` |
| Pinned revision | `9fa644f54b04983adea4d0168f49fc6af4a893ba` |
| License | Apache-2.0, verified from repository `LICENSE` |
| Python/native boundary | Python protocol/config/router/engine façade; TVM-FFI and compiled model runtime |
| Canonical pattern IDs | P12 (A), P16 (A) |
| Source evidence | `sync_engine.py`, `engine_base.py`, `router.py`, `popen_server.py`, protocol types |
| Test evidence | Mock JSON-FFI, sync/async serving, and router tests |
| Book mapping | Clean Architecture ch19–20 and ch23; Software Design ch35 and ch41 |
| Production compromise | A deliberately coupled FFI contract and dual sync/threaded implementations support device performance and debuggability |
| Practice exercise | `exercises/provider-adapter.md` |
