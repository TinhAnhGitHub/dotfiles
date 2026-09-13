# SGLang

> Repository: [sgl-project/sglang](https://github.com/sgl-project/sglang/tree/ae1acf822dd357641d885f30c58d2ad547ec9220)
> Default branch: `main`
> Commit: `ae1acf822dd357641d885f30c58d2ad547ec9220`
> License: Apache-2.0
> Domain: LLM/VLM inference, batching, disaggregation, and multi-hardware serving
> Python: >=3.10 (`python/pyproject.toml`)
> Evidence level: A for registry, hook, scheduler-state, and unit-test claims; B for the full serving/native boundary
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/sglang` (read-only pinned checkout)

## 1. Executive Architecture Summary

SGLang’s SRT runtime places a Python `Engine` and scheduler between API clients and highly specialized attention/model kernels. The scheduler owns request queues, token budgets, radix/prefix cache decisions, disaggregation, pause/retract behavior, and lifecycle components. Backend registries and model-override passes adapt model families and hardware without putting every conditional in the public engine.

```text
HTTP/OpenAI-compatible API or EngineBase
                 │
                 ▼
              Engine ── Scheduler ── ScheduleBatch + SchedulePolicy
                 │                         │
                 │                         ├── attention/grammar/model registries
                 │                         └── radix/KV cache + disaggregation
                 ▼
        Python runtime control plane ── Triton/CUDA/Rust/hardware kernels
```

The architecture is a serving runtime rather than a domain application. No authoritative P01–P07 or CQRS-style P10/P11 business boundary was found in the assigned source.

## 2. Layering & Boundary Discipline

| Layer | Responsibility | Evidence |
|---|---|---|
| Public engine/API | Stable generate/flush/shutdown operations and server integration | `python/sglang/srt/entrypoints/EngineBase.py`, `python/sglang/srt/entrypoints/engine.py` |
| Scheduling state | Request objects, batches, queues, policies, cache-aware admission | `python/sglang/srt/managers/schedule_batch.py`, `schedule_policy.py`, `scheduler.py` |
| Adaptation/extension | Attention backend factories, grammar backends, model overrides, plugin hooks | `python/sglang/srt/layers/attention/attention_registry.py`, `python/sglang/srt/constrained/base_grammar_backend.py`, `python/sglang/srt/arg_groups/*`, `python/sglang/srt/plugins/hook_registry.py` |
| Distributed/resource lifecycle | Disaggregation, cache/event publication, pause/retract, weight/profile/idle components | `python/sglang/srt/managers/scheduler.py`, `python/sglang/srt/disaggregation/kv_events.py`, scheduler components |
| Performance/native perimeter | CUDA/Triton kernels, hardware backends, and optional Rust server/tokenizer paths | Imports and runtime branches in SRT |

### Python/native boundary

The Python SRT layer owns request normalization, policy selection, cache bookkeeping, backend construction, process coordination, and API lifecycle. It calls specialized CUDA/Triton and hardware kernels and can host or coordinate Rust-backed serving paths. The backend selected at runtime determines how much work leaves Python; the clean architectural seam is the scheduler/runner contract, not a universal language boundary for every request.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | `python/sglang/srt/layers/attention/attention_registry.py` (`ATTENTION_BACKENDS`, decorator); `python/sglang/srt/arg_groups/model_override_base.py`; `python/sglang/srt/constrained/base_grammar_backend.py` | `test/registered/unit/model_executor/model_runner_components/test_attention_backend_setup.py`, `test/registered/unit/test_split_attention_backend_decisions.py`, `test/registered/unit/test_model_overrides.py` | Software Design ch34; Architecture with Python ch13 | A |
| P09 | Strategy and policy | `python/sglang/srt/managers/schedule_policy.py` (`CacheAwarePolicy`, `CacheAgnosticPolicy`, `SchedulePolicy`); post-process passes in `python/sglang/srt/arg_groups/overrides.py` | Scheduler decision/pause tests and model-override tests | Software Design ch33; Architecture with Python ch04; Clean Architecture ch14 | A |
| P12 | Adapter and provider/backend router | Attention backend creators normalize flashinfer/triton/TensorRT/hardware implementations to a runner contract; grammar backend registration and OpenAI serving boundary provide additional adapters | Attention setup/selection tests and scheduler tests | Software Design ch35; Clean Architecture ch19–20 | A/B |
| P13 | State machine/workflow/lifecycle | `EngineBase`/`Engine` lifecycle, `Scheduler.pause_generation`, request retraction, disaggregation queues, and engine shutdown | `test/registered/unit/managers/test_scheduler_pause_generation.py`, chunked-abort-race and flush-cache tests | Architecture with Python ch08–11; Clean Architecture ch18 | A/B |
| P14 | Decorator, middleware, hooks, and observability | `python/sglang/srt/plugins/hook_registry.py`; post-process hook registry; KV event publisher and scheduler metrics components | `test/registered/unit/plugins/test_hook_registry.py`, `test_load_plugins.py`, `test_model_overrides.py` | Software Design ch37/ch39; Clean Architecture ch23 | A |
| P16 | Scheduling, concurrency, and resource lifecycle | `Scheduler.run_event_loop`, schedule policy, overlap mode, request queues, radix/KV cache, pause/flush, idle/resource components | `test/registered/unit/managers/test_scheduler_*.py` focused tests and manual scheduler tests | Software Design ch41; Clean Architecture ch23 | A |
| P17 | Testing seams and architecture fitness | CPU CI registration, `MagicMock` scheduler construction, hook registry isolation, backend selection tests, and race/failure tests | The unit paths above | Clean Architecture ch21 | A |

No authoritative P01–P07, P10, or P11 evidence was found. SGLang has event publication for KV/disaggregation telemetry, but the inspected code does not justify labeling the serving scheduler a durable message bus or CQRS system.

## 4. Source Walkthrough

### `python/sglang/srt/entrypoints/EngineBase.py` and `engine.py`

`EngineBase` defines the public `generate`, `flush_cache`, and `shutdown` contract. `Engine` implements request submission and owns the scheduler-facing runtime. `shutdown` and `flush_cache` make lifecycle operations visible at the façade rather than leaving cleanup to callers that know internal scheduler state.

### `python/sglang/srt/managers/scheduler.py`

The scheduler initializes model workers, memory pools, attention backends, schedule policy, metrics, disaggregation, request dispatch, and optional overlap/idle components. Its event loop ingests requests, builds batches, runs generation, updates cache/request state, and emits results. `pause_generation` supports in-place and retract semantics; retraction requeues or releases state according to the selected mode. `flush_cache` and `shutdown` are explicit resource boundaries.

### `python/sglang/srt/managers/schedule_batch.py` and `schedule_policy.py`

`Req` and `ScheduleBatch` hold the mutable request/KV state needed by prefill/decode scheduling. `CacheAwarePolicy` includes longest-prefix and weighted/aging policies; `CacheAgnosticPolicy` includes FCFS, longest-output-first, random, and routing-key policies. `SchedulePolicy` validates/adjusts the selected policy and computes ordering with cache and priority information. The strategy is therefore data-aware and performance-coupled, not a generic comparator.

### `python/sglang/srt/layers/attention/attention_registry.py`

`ATTENTION_BACKENDS` maps names to creator functions. Decorated creators lazily import the selected implementation and reject unsupported combinations such as incompatible MLA/speculative modes. The registry’s return value is an attention backend object that the model runner can use through a common interface, while hardware-specific validation remains at the adapter boundary.

### `python/sglang/srt/arg_groups/model_override_base.py` and `overrides.py`

Model overrides are registered by exact architecture or predicate. Post-process functions are collected and run as named passes, with a resolved read-only view and declaration validation. This is a useful example of a registry that carries ordering and conflict semantics instead of merely storing constructors.

### `python/sglang/srt/plugins/hook_registry.py`

`HookRegistry` supports around and replace hooks for Python methods, including class, static, and instance methods. The plugin loader applies hooks after registration. It is a deliberate perimeter mechanism: extension code can instrument or replace a target without changing the target module, while tests exercise the exact descriptor cases.

## 5. Theory Versus Practice

### Theoretical ideal

Software Design ch33/ch34 suggests replaceable strategies and factories with small contracts. Clean Architecture ch14/19–20 puts hardware/provider mechanisms at the outer boundary. Ch18 and Architecture with Python ch08–11 describe explicit workflow state and transition ownership; ch21/ch23 call for testable seams and observability that do not contaminate policy.

### Production implementation

SGLang keeps the scheduler close to its radix cache, token allocator, overlap mode, speculative decoding, disaggregation, and hardware constraints. It uses several registries: attention creators, grammar backends, model overrides, post-process passes, plugin hooks, and event publishers. Validation hooks reject unsupported combinations before the scheduler enters a mode that would be unsafe or inconsistent.

### Difference and rationale

The generic strategy ideal cannot decide whether a request fits without seeing cache residency and device budgets, so SGLang intentionally couples policy to scheduler state. The registry set is broader than a small application’s plugin list because backend combinations grow combinatorially. The cost is process-global state, import-order sensitivity, and many compatibility validators. Pause/retract and disaggregation improve operational control but require precise ownership of queues, KV memory, and in-flight batches.

## 6. Testing Strategy

- `test/registered/unit/test_model_overrides.py` isolates global registries, checks exact/predicate registration order, validates non-dict results, and exercises the resolved-view/pass pipeline.
- `test/registered/unit/plugins/test_hook_registry.py` checks around/replace hooks for class, static, and instance methods.
- `test/registered/unit/plugins/test_load_plugins.py` checks plugin loading; `test/registered/unit/scripted_runtime/test_scheduler_hook.py` covers scheduler hook integration.
- `test/registered/unit/model_executor/model_runner_components/test_attention_backend_setup.py` and `test/registered/unit/test_split_attention_backend_decisions.py` check backend setup/selection boundaries.
- `test/registered/unit/managers/test_scheduler_pause_generation.py` uses a CPU-constructed scheduler with mocked pools and verifies in-place pause, retraction, invalid modes, queue preservation, and state cleanup.
- `test/registered/unit/managers/test_scheduler_chunked_abort_race.py`, `test_scheduler_flush_cache.py`, and related scheduler tests cover race, cache, and lifecycle cases; manual scheduler tests document GPU/integration scenarios.

The source and test files were inspected at the pinned revision. The GPU/manual suites were not run locally; the CPU-oriented unit seams were used as evidence rather than inferred from README text.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Scheduler policy sees cache internals | Maximizes token throughput and prefix-cache reuse | Keep policy/domain rules separate in ordinary applications with no memory-budget coupling |
| Many process-global registries | Makes hardware/model additions incremental | Use instance registries when tests or tenants require isolation; add deterministic registration validation |
| Hook replacement at runtime | Powerful observability and deployment-specific patches | Avoid unrestricted replacement in safety-critical code; prefer typed middleware at a known boundary |
| Explicit mode validation and fallback | Prevents incompatible backend combinations | A growing matrix of validators can become a hidden product contract; document supported combinations |
| Python control plane over native kernels | Rapid iteration while preserving performance | Expect backend-specific operational/debugging complexity and test on each target device |

## 8. Practice Exercise

Create a CPU-only inference scheduler with:

1. A named backend registry containing `torch`, `fake_cuda`, and a backend creator that validates capabilities.
2. FCFS, longest-output-first, and longest-prefix-match strategies.
3. A request state object with `queued`, `running`, `paused`, `finished`, and `aborted` transitions.
4. A hook registry with one around hook for metrics and a replace hook used only in a test.
5. Tests for invalid backend/policy combinations, pause/retract/flush, registration order, and an abort race.

The exercise is complete when the scheduler loop is unchanged while a new backend and policy are added through registries.
