# vLLM

> Repository: [vllm-project/vllm](https://github.com/vllm-project/vllm/tree/22f6e4eccb674b534f62810c66838317169b6b98)
> Default branch: `main`
> Commit: `22f6e4eccb674b534f62810c66838317169b6b98`
> License: Apache-2.0
> Domain: High-throughput LLM inference and serving
> Python: 3.10–3.14 (`pyproject.toml`)
> Evidence level: A for scheduler/registry/resource tests; B for the end-to-end Python/native boundary
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/vllm` (read-only pinned checkout)

## 1. Executive Architecture Summary

vLLM’s V1 serving path is a producer/consumer-style engine. The public `LLM` API accepts requests; `LLMEngine` normalizes inputs and outputs; `EngineCore` owns scheduling, model execution, KV-cache state, and lifecycle commands. The scheduler selects work for each forward pass while the model executor and native kernels perform the expensive computation.

```text
Client/API
    │
    ▼
LLM ── LLMEngine ── EngineCore client/process ── SchedulerInterface
                                      │                 │
                                      │                 ├── KV connector factory
                                      │                 └── scheduling policy/preemption
                                      ▼
                                model executor ── PyTorch/CUDA/Triton/native kernels
```

The architecture deliberately keeps an extensible Python control plane around a performance-critical execution plane. It does not present a traditional domain model or transactional repository; P01–P07 are not authoritative patterns for this repository.

## 2. Layering & Boundary Discipline

| Layer | Responsibility | Evidence |
|---|---|---|
| Public serving façade | `LLM`, request validation, sampling API | `vllm/entrypoints/llm.py` |
| Engine/application layer | Input/output processing, request fan-out, stats, abort/sleep/wake | `vllm/v1/engine/llm_engine.py` |
| Engine core | Scheduling, model-executor calls, KV/grammar connectors, IPC/process lifecycle | `vllm/v1/engine/core.py` |
| Policy and adapters | Scheduler interface, scheduling policy, KV connector factory, attention backend registry | `vllm/v1/core/sched/*`, `vllm/distributed/kv_transfer/kv_connector/factory.py`, `vllm/v1/attention/backends/registry.py` |
| Performance/native perimeter | Model executor, CUDA/Triton/C++/Rust components and device-specific kernels | `vllm/model_executor/`, `csrc/`, `rust/` and calls from `EngineCore` |

### Python/native boundary

Python owns request lifecycle, batching decisions, scheduler policy, backend selection, process/IPC coordination, and cleanup. `EngineCore` calls the model executor with a scheduled batch; model execution and KV/attention kernels may run through PyTorch, Triton, CUDA/C++, or Rust-backed components. The exact hot path depends on model, platform, and backend, so “Python scheduler versus native execution” is the useful boundary—not a claim that every execution layer is C++.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | `vllm/distributed/kv_transfer/kv_connector/factory.py` (`KVConnectorFactory`); `vllm/v1/attention/backends/registry.py`; configurable scheduler class in `vllm/config/scheduler.py` | `tests/v1/kv_connector/unit/test_multi_connector.py`, `test_scheduler_kv_connector_override.py`, `tests/test_attention_backend_registry.py`, `tests/plugins_tests/test_scheduler_plugins.py` | Software Design ch34; Architecture with Python ch13 | A |
| P09 | Strategy and policy | `vllm/v1/core/sched/interface.py`, `vllm/v1/core/sched/scheduler.py` (`Scheduler`, `SchedulingPolicy`), `SchedulerConfig.policy` and `scheduler_cls` | `tests/v1/core/test_scheduler.py`, `tests/v1/core/test_async_scheduler.py`, and scheduler plugin tests | Software Design ch33; Architecture with Python ch04; Clean Architecture ch14 | A |
| P12 | Adapter, façade, and provider router | `KVConnectorFactory` separates scheduler/worker connector roles; attention registry turns backend names/class paths into a common backend contract; `LLMEngine` adapts API requests to engine-core messages | Connector override/multi-connector tests and attention registry tests | Software Design ch35; Clean Architecture ch19–20 | A |
| P13 | State machine/workflow/lifecycle | Engine core pause modes, abort queues, request states, sleep/wake, and process shutdown | `tests/v1/core/test_scheduler.py`, `tests/basic_correctness/test_mem.py`, engine-core/multiprocess cleanup tests | Architecture with Python ch08–11; Clean Architecture ch18 | B |
| P14 | Middleware/observability and event publication | Engine/scheduler event publishers, stats, output processing, and lifecycle hooks in `vllm/v1/engine/core.py` and `scheduler.py` | Scheduler/KV connector lifecycle tests plus engine cleanup fixtures | Clean Architecture ch23; Software Design ch37/ch39 by analogy | B |
| P16 | Scheduling, concurrency, and resource lifecycle | `EngineCore.step`, `step_with_batch_queue`, `Scheduler.schedule`, pause/preemption, multiprocess engine wrappers, shutdown | `tests/v1/core/test_scheduler.py`, `tests/v1/core/test_async_scheduler.py`, memory sleep tests, multiprocess executor tests | Software Design ch41; Clean Architecture ch23 | A |
| P17 | Testing seams and architecture fitness | CPU scheduler construction, fake requests/cache blocks, plugin scheduler class, connector overrides, explicit shutdown fixtures | The test files above | Clean Architecture ch21 | A |

No authoritative P01–P07 or durable business P10/P11 evidence was found. vLLM has events and projections for serving telemetry, but that is not sufficient to label it a CQRS/message-bus application.

## 4. Source Walkthrough

### `vllm/entrypoints/llm.py`

`LLM` is the caller-facing façade. Its constructor converts arguments into `EngineArgs` and creates an `LLMEngine`; `generate` submits prompts and sampling parameters; `sleep` and `wake_up` delegate resource lifecycle commands. Application code does not directly construct a scheduler or allocate KV blocks.

### `vllm/v1/engine/llm_engine.py`

`LLMEngine` creates the renderer/input/output processors and an `EngineCoreClient`. `add_request` creates output state and forwards a normalized request to the engine core, including fan-out for multiple completions. `step` receives core outputs, applies output processing, aborts stop-string requests, and records stats. This is a clear anti-corruption/adapter boundary between API semantics and scheduler messages.

### `vllm/v1/engine/core.py`

`EngineCore` constructs the model executor, KV/structured-output managers, scheduler class, and connector aggregators. Each `step` asks the scheduler for a batch, executes the model asynchronously, samples/processes the result, and feeds it back into scheduler state. `step_with_batch_queue` overlaps scheduling with outstanding batch execution. `EngineCoreProc` wraps the core in a background process with queues and handshakes; shutdown explicitly tears down structured-output backends, executors, scheduler/connectors, distributed state, and memory.

### `vllm/v1/core/sched/interface.py` and `vllm/v1/core/sched/scheduler.py`

`SchedulerInterface` defines the lifecycle contract: add/finish requests, schedule, update from output, reset cache, pause, stats, and shutdown. `Scheduler` implements token-budget admission, chunked prefill, prefix caching, speculative/encoder budgets, and preemption. Under KV pressure it can preempt a lower-priority or later request, returning a `SchedulerOutput` that the engine uses to continue the protocol.

### `vllm/distributed/kv_transfer/kv_connector/factory.py`

`KVConnectorFactory.register_connector` stores lazy loaders for optional connector implementations and rejects duplicate names. `create_connector` validates the configuration and creates the role-specific scheduler or worker connector. The file’s explicit separation of those roles prevents a backend adapter from quietly crossing process/layer ownership boundaries.

### `vllm/v1/attention/backends/registry.py`

Attention backend enum values are class paths, with a `CUSTOM` slot and an override map. `register_backend` supports decorator or direct registration, and `get_class` resolves the selected class. This keeps platform/model selection configurable while the runner consumes one backend interface.

## 5. Theory Versus Practice

### Theoretical ideal

Software Design ch33/ch34 recommends small strategy/factory objects. Clean Architecture ch19–20 places external mechanisms behind adapters, while ch23 and ch21 ask for observable, testable boundaries. A workflow abstraction would make request transitions explicit and keep resource cleanup in one lifecycle owner.

### Production implementation

vLLM’s scheduler is not a simple strategy object: it is a token-budget and KV-memory algorithm coupled to request state, prefix caching, speculative decoding, and preemption. Factories use strings and lazy imports because connectors and attention kernels are optional. The engine uses processes, queues, futures, distributed barriers, and sleep modes to overlap work and fit large models into finite GPU memory.

### Difference and rationale

The production scheduler intentionally violates “keep policies independent of mechanisms” at selected hot boundaries because scheduling decisions must see KV allocation and executor output. The interface still preserves a replacement seam for plugins and tests. Background processes and IPC improve isolation and throughput but make serialization, startup handshakes, error propagation, and shutdown correctness part of the architecture. Sleep/wake saves memory between workloads, but it introduces cache state and synchronization modes that a small synchronous service should avoid.

## 6. Testing Strategy

- `tests/v1/core/test_scheduler.py` uses CPU-sized fake schedulers/cache blocks to verify request admission, output updates, cache behavior, priorities, and preemption.
- `tests/v1/core/test_async_scheduler.py` covers in-flight and KV-pressure preemption in the asynchronous path.
- `tests/test_attention_backend_registry.py` registers custom classes and checks class-path resolution and non-aliasing of the custom slot.
- `tests/plugins_tests/test_scheduler_plugins.py` verifies a plugin scheduler can be selected.
- `tests/v1/kv_connector/unit/test_multi_connector.py`, `test_scheduler_kv_connector_override.py`, and `test_config.py` cover connector factory/config seams.
- `tests/basic_correctness/test_mem.py` exercises sleep/wake memory behavior; engine/conftest cleanup code makes shutdown explicit.

The source and test files were inspected at the pinned revision. GPU, multiprocess, and full performance tests were not executed in this research pass.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Scheduler tightly coupled to KV-cache state | Enables high utilization, chunked prefill, prefix caching, and preemption | Do not imitate this coupling for ordinary business queues; keep policy independent there |
| String-keyed lazy factories | Optional backends do not impose all dependencies at import time | Add startup resolution/compatibility checks when delayed errors are unacceptable |
| Background engine process and IPC | Isolates the serving core and permits concurrent request handling | Avoid it for low-throughput services where a direct call is easier to operate |
| Explicit abort/pause/sleep modes | Necessary for overload, memory pressure, and shared GPU deployments | Each mode must have a tested cleanup contract; otherwise leaks and stuck requests are likely |
| Native acceleration beneath Python | Preserves a readable control plane without putting hot loops in Python | Do not infer that a clean Python abstraction eliminates device-specific tuning |

## 8. Practice Exercise

Implement a toy token-budget scheduler with the same seam:

1. Define `SchedulerInterface.schedule()` and `update_from_output()`.
2. Add `fcfs` and `priority` policies behind a `SchedulingPolicy` strategy.
3. Represent a finite KV-block pool and preempt the lowest-priority request when the pool is full.
4. Add a lazy connector factory with one fake connector and a duplicate-registration error.
5. Write CPU-only tests for admission, preemption, pause/resume, connector override, and idempotent shutdown.

The exercise is complete when the scheduler can be replaced by a plugin without changing the engine loop.
