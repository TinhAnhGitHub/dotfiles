# Text Generation Inference

> Repository: [huggingface/text-generation-inference@b4adbf2](https://github.com/huggingface/text-generation-inference/tree/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed)
> Default branch: `main`
> Commit: `b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed`
> License: [Apache-2.0](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/LICENSE)
> Domain: Production LLM serving, batching, streaming, and client APIs
> Python/native boundary: Rust owns the HTTP router, request validation, concurrency admission, backend trait, and response streaming; Python owns model loading and model-specific execution; CUDA/C++/custom kernels sit below the Python model backend.
> Evidence level: A for Rust router/concurrency and Python client contracts; B for the launcher-to-model-server boundary
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/text-generation-inference` (read-only pinned checkout)

## 1. Executive Architecture Summary

Text Generation Inference separates a Rust serving router from a Python model server. The router owns the public HTTP/OpenAI-compatible contract, validation, concurrency limits, health, backend selection, and streaming response protocol. The Python server owns model loading, weights, cache handling, and model-family execution. A Rust launcher composes the processes and starts the router/model-server pair.

This split keeps request scheduling and API behavior independent from the rapidly varying model implementations. The `Backend` trait is the router’s inward port; a backend schedules generation streams while the router holds a semaphore permit for the stream lifetime. Errors become typed HTTP responses and metrics at the server boundary.

```text
Python / OpenAI client
          │
          ▼
Rust router: HTTP + validation + semaphore + stream protocol
          │
          ▼
        Backend trait
          │
          ▼
Python text-generation-server model backend
          │
          ▼
PyTorch / CUDA / custom kernels
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Client adapter | `clients/python/text_generation/client.py`, `errors.py` | Build typed requests, parse JSON/SSE, map status to exceptions |
| Rust API/application layer | `router/src/server.rs`, `router/src/lib.rs` | Route requests, validate chat/generation inputs, map failures to responses |
| Scheduling port | `router/src/infer/mod.rs` | `Backend` trait, semaphore admission, stream lifecycle, health state |
| Python model backend | `server/text_generation_server/models/`, `server.py`, `cache.py` | Load models, run forward passes, manage cache and model-specific adapters |
| Process composition | `launcher/src/main.rs` | Resolve model/server configuration and spawn the router/model processes |

The language boundary is intentional. Python is not the owner of the public scheduling state in this revision, and Rust is not the owner of model-family implementation details.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P12 | Adapter, façade, and provider router | [`router/src/infer/mod.rs`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/router/src/infer/mod.rs) defines the `Backend` port and generation façade; [`router/src/server.rs`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/router/src/server.rs) adapts HTTP DTOs to generation calls; [`clients/python/text_generation/client.py`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/clients/python/text_generation/client.py) adapts JSON/SSE back to Python objects | [`clients/python/tests/test_client.py`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/clients/python/tests/test_client.py), [`clients/python/tests/test_errors.py`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/clients/python/tests/test_errors.py), [`integration-tests/models/test_bloom_560m.py`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/integration-tests/models/test_bloom_560m.py) | Clean Architecture ch19–20; Software Design ch35 | A |
| P16 | Concurrency, scheduling, and resource lifecycle | [`router/src/infer/mod.rs`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/router/src/infer/mod.rs) uses an `Arc<Semaphore>` and retains the permit while a stream is alive; [`launcher/src/main.rs`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/launcher/src/main.rs) composes child processes; Python cache/model files own backend resources | [`clients/python/tests/test_client.py`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/clients/python/tests/test_client.py), [`integration-tests/conftest.py`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/integration-tests/conftest.py), [`integration-tests/models/test_flash_gpt2.py`](https://github.com/huggingface/text-generation-inference/blob/b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed/integration-tests/models/test_flash_gpt2.py) | Software Design ch41; Clean Architecture ch23 | A |

No authoritative Python P08/P09/P13/P14 claim is made in this focused entry. The router’s Rust trait and semaphore are the relevant evidence; Python model classes are not presented as a plugin registry without a matching source/test study.

## 4. Source Walkthrough

### `router/src/infer/mod.rs`

`Infer` stores an `Arc<dyn Backend>`, chat-template state, a semaphore, and health flags. `generate_stream` rejects overload when permits are unavailable, validates the request, schedules through the backend, updates health on stream errors, and handles length continuation. `generate` drains the stream and reports incomplete generation distinctly from a successful response.

### `router/src/server.rs` and `router/src/lib.rs`

The server maps `/generate`, streaming, chat, and compatibility routes into the `Infer` façade. `ChatRequest::try_into_generate` is the protocol conversion seam. Error mapping preserves client-visible status categories while keeping backend details inside the Rust service.

### Python server and launcher

`server/text_generation_server/models/model.py` and `server.py` define the model-side execution contract; `cache.py` manages model/cache resources. `launcher/src/main.rs` resolves deployment options and starts `text-generation-server` and `text-generation-router`, making process ownership explicit.

## 5. Theory Versus Practice

The classic adapter/port model would put the use-case policy in a language-neutral application layer. TGI instead gives the router the public contract and keeps model implementations behind a Rust trait plus an inter-process boundary. This is a stronger operational split than a collection of Python classes, because it isolates model memory and failure modes from API scheduling.

The semaphore is deliberately held for the full generation stream, not only request admission. That couples concurrency accounting to stream lifetime, but it prevents a slow client or backend stream from escaping the configured capacity. A simpler service can use an async semaphore around one request call, provided streaming cleanup is still explicit.

## 6. Testing Strategy

- Python client tests exercise sync/async generation, chat, streaming, validation, and not-found/error responses.
- Error tests verify status-to-exception translation independently of a live model.
- Integration fixtures launch processes and wait for health before model-specific generation tests.
- Bloom and GPT-2 integration tests cover real server/model behavior; GPU and model downloads were not run in this research pass.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Rust router plus Python model server | Stable high-throughput API path with flexible model implementations | Adds deployment/process complexity; avoid for a small single-model service |
| Trait and process boundaries instead of one in-process interface | Failure isolation and independent release/performance tuning | Contract drift requires integration tests and versioned launch behavior |
| Concurrency permit spans streaming | Accurate capacity/backpressure accounting | A slow client can hold capacity; configure timeouts and cancellation for interactive workloads |
| Model/cache state stays close to backend code | Efficient GPU memory and model-specific optimization | Do not expose internal cache ownership directly through a generic application API |

## 8. Practice Exercise

Use [the provider-adapter exercise](../../python-software-architecture/exercises/provider-adapter.md): define a Python generation port, add a fake in-process backend and a subprocess/HTTP adapter, hold a semaphore permit for streaming lifetime, and translate backend errors into typed client exceptions. Test overload and cancellation before adding a real model.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `huggingface/text-generation-inference`, `main` |
| Pinned revision | `b4adbf2f6e2e721280bd0ea5f91d70f7d033f5ed` |
| License | Apache-2.0, verified from repository `LICENSE` |
| Python/native boundary | Rust router; Python model server; PyTorch/CUDA/custom-kernel execution below it |
| Canonical pattern IDs | P12 (A), P16 (A) |
| Source evidence | `infer/mod.rs`, `server.rs`, Python client/model server, launcher |
| Test evidence | Python client/error tests and process-backed model integration tests |
| Book mapping | Clean Architecture ch19–20 and ch23; Software Design ch35 and ch41 |
| Production compromise | A multi-process, multi-language split is accepted to isolate scheduling from model execution and support throughput |
| Practice exercise | `exercises/provider-adapter.md` |
