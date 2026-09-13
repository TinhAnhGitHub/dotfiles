# Project Case Study: LMDeploy

> **Repository**: [InternLM/lmdeploy](https://github.com/InternLM/lmdeploy/tree/309d2b503ca846b3be2e9cdafeec9f895f3d315c)  
> **Checked-out commit**: 309d2b503ca846b3be2e9cdafeec9f895f3d315c  
> **License**: Apache-2.0 (LICENSE and source copyright headers)  
> **Domain**: LLM/VLM inference, TurboMind and PyTorch backends, continuous batching, KV-cache/disaggregated serving, local/multiprocess/Ray execution  
> **Python**: setup.py classifiers include Python 3.10 through 3.13; the inspected setup metadata has no narrower python_requires  
> **Architecture style**: User-facing Pipeline façade over auto-detected backend/task adapters, with an async engine loop and selectable Uni/MP/Ray executors  
> **Evidence level**: A/B claims below are tied to source and tests.

## 1. Architecture Summary

LMDeploy presents a small public pipeline API over two substantially different inference implementations: TurboMind and the PyTorch engine. The Pipeline resolves/downloads a model, auto-selects a backend and task, constructs an AsyncEngine, starts an internal event loop, and turns sessions/requests into scheduled engine work. The PyTorch path further separates model/config construction, scheduler/cache management, engine loop, and executor implementation.

~~~text
lmdeploy.pipeline / lmdeploy.api
            |
            +--> archs.autoget_backend_config / get_task
            |       +--> TurboMind AsyncEngine
            |       |       +--> C++/CUDA TurboMind runtime
            |       +--> PyTorch AsyncEngine
            |               +--> Engine + Scheduler + CacheEngine
            |               +--> UniExecutor / MPExecutor / RayExecutor
            |                       +--> Python torch model path
            |                       +--> CUDA kernels / device backend
            |
            v
      sessions, streams, cancellation, sleep/wakeup, close
~~~

The project’s main architectural seam is backend substitution. The user does not need to know whether model support came from TurboMind or PyTorch, while the engine still exposes enough configuration for tensor parallelism, cache policy, device choice, and distributed execution.

## 2. Python Boundary

### Python control and orchestration plane

- lmdeploy/api.py and pipeline.py are the public façade, model-resolution boundary, session API, stream/infer adapter, and top-level close owner.
- lmdeploy/archs.py detects backend/task/model architecture and maps configuration classes.
- lmdeploy/pytorch/configurations/builder.py selects a model-specific configuration builder using subclass registration.
- lmdeploy/pytorch/engine/engine.py builds scheduler/cache/backend/distributed configs, chooses an executor, and owns the engine loop.
- lmdeploy/pytorch/engine/engine_loop.py schedules requests, drains work for sleep, and coordinates executor tasks.
- lmdeploy/pytorch/engine/executor/base.py defines the executor lifecycle and cache sizing contract; MP/Ray executors own process/actor transport.

### Native and performance-critical plane

- TurboMind execution is implemented below the Python serving façade in lmdeploy/turbomind and its native source/build boundary.
- lmdeploy/pytorch/backends/cuda contains CUDA attention, cache, graph-runner, MoE, communication, and sampling implementations.
- PyTorch model execution and distributed collectives remain performance-critical even when selected through Python.
- Shared-memory buffers, process groups, Ray actors, and KV-transfer connectors move large tensors and cache state across worker boundaries.

Python therefore owns policy and lifecycle, not the hot token-generation loop. A backend-selection bug is visible in archs.py; a cache/kernel/device bug is often in the CUDA/TurboMind/native plane.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Trade-off |
| :--- | :--- | :--- | :--- | :--- | :--- |
| P07 Composition Root and Dependency Injection | [pipeline.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pipeline.py#L33-L95), [engine.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/engine.py#L102-L186) | [test_pipeline.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/test_lmdeploy/test_pipeline.py) | Architecture ch13; Clean Architecture ch18-ch20 | B | Pipeline/Engine compose the runtime explicitly, but configuration and backend detection remain global/framework-aware. |
| P08 Factory, Registry, and Plugin Architecture | [builder.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/configurations/builder.py#L9-L60), [selector.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/backends/selector.py#L7-L43) | [test_model.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/test_lmdeploy/test_model.py), [test_model_config.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/pytorch/config/test_model_config.py) | Design ch34; Clean Architecture ch19-ch20 | A | Subclass registration and device-backend selection let new model/device implementations join the system, but import order becomes part of discovery. |
| P09 Strategy, Policy, and Template Method | [archs.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/archs.py#L10-L90), [executor/__init__.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/executor/__init__.py#L32-L140) | [test_executor_base.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/pytorch/engine/test_executor_base.py) | Design ch33; Architecture ch04; Clean Architecture ch18 | A | Backend, device, and distributed-executor policies vary behind a stable engine contract, with explicit fallback when TurboMind is unavailable/unsupported. |
| P12 Adapter, Façade, and Provider Router | [api.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/api.py#L15-L82), [archs.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/archs.py#L31-L90) | [test_pipeline.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/test_lmdeploy/test_pipeline.py), [test_model.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/test_lmdeploy/test_model.py) | Design ch35; Clean Architecture ch19-ch20 | A | One API normalizes local model IDs, TurboMind/PyTorch engines, LLM/VLM tasks, and session/stream behavior. |
| P13 State Machine, Workflow, and Saga | [engine_loop.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/engine_loop.py#L100-L220), [engine_instance.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/engine_instance.py) | [test_engine_instance_cleanup.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/test_lmdeploy/pytorch/engine/test_engine_instance_cleanup.py), [test_ray_mp_engine.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/pytorch/engine/test_ray_mp_engine.py) | Design ch38; Clean Architecture ch18 and ch24 | B | Sessions and streams have explicit cancellation/finish states, but the system is an inference lifecycle, not a durable business saga. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [base.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/executor/base.py#L30-L240), [mp_executor.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/executor/mp_executor.py#L207-L320), [ray_executor.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/executor/ray_executor.py#L213-L350) | [test_engine_sleep.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/pytorch/engine/test_engine_sleep.py), [test_executor_base.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/pytorch/engine/test_executor_base.py) | Design ch41; Clean Architecture ch23 | A | Async loops, cache sizing, sleep/wakeup, process termination, Ray worker cleanup, and distributed groups are explicit lifecycle contracts. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [engine.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/engine.py#L649-L679) | [test_engine_sleep.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/pytorch/engine/test_engine_sleep.py), [test_engine_instance_cleanup.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/test_lmdeploy/pytorch/engine/test_engine_instance_cleanup.py), [test_ray_mp_engine.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/tests/pytorch/engine/test_ray_mp_engine.py) | Clean Architecture ch21 and ch24 | B | Tests replace schedulers/executors, force cancellation, and inject Ray initialization failures; broad GPU correctness remains integration coverage. |

P10 Commands, Events, and Message Bus is **C and excluded**. The engine uses async queues and RPC/transport messages, but the inspected code does not establish a durable event bus or replay/idempotency contract.

## 4. Source Walkthrough

### File 1 — Public façade

[lmdeploy/api.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/api.py#L15-L82) exposes pipeline(model_path, backend_config, chat_template_config, and policy flags). [lmdeploy/pipeline.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pipeline.py#L33-L95) downloads/locates models, calls backend/task discovery, constructs the chosen AsyncEngine, starts an internal event-loop thread, and owns close. This is a façade plus composition root in one perimeter object.

### File 2 — Backend and task routing

[lmdeploy/archs.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/archs.py#L10-L163) detects whether TurboMind supports a model, falls back to PyTorch when it does not, maps configuration types between backends, detects LLM versus VLM, and reads model architecture from Hugging Face config. The fallback is a real production compromise: coverage is favored over a hard failure, but performance and feature parity are not identical.

### File 3 — Model configuration registry

[lmdeploy/pytorch/configurations/builder.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/configurations/builder.py#L9-L74) registers every AutoModelConfigBuilder subclass through __init_subclass__. build iterates registered builders, chooses the first condition matching the Hugging Face config, and falls back to DefaultModelConfigBuilder. This is an extensible factory with an intentionally simple precedence rule.

### File 4 — Engine and lifecycle

[lmdeploy/pytorch/engine/engine.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/engine.py#L102-L227) normalizes engine configuration, checks the environment, builds scheduler/cache/backend/distributed configs, and chooses the distributed executor. Its run path builds an EngineLoop and waits for its tasks; close and sleep/wakeup coordinate scheduler, loop, executor, and cache state.

### File 5 — Executor contracts and implementations

[lmdeploy/pytorch/engine/executor/base.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/executor/base.py#L30-L240) defines model build, graph runner, cache, warmup, sleep/wakeup, forward, and release hooks, as well as cross-rank KV-cache sizing. [mp_executor.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/executor/mp_executor.py#L207-L620) uses spawned processes, shared buffers, signals, and process-group cleanup. [ray_executor.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/engine/executor/ray_executor.py#L213-L555) uses Ray workers, kills/cleans workers on failed initialization, and documents that coordinated multi-rank shutdown is non-trivial.

### File 6 — Hot backend selection

[lmdeploy/pytorch/backends/selector.py](https://github.com/InternLM/lmdeploy/blob/309d2b503ca846b3be2e9cdafeec9f895f3d315c/lmdeploy/pytorch/backends/selector.py#L7-L43) maps the active device context to CUDA, Ascend, MACA, or CAMB OpsBackend classes. The selected backend then dispatches attention/cache/MoE and communication operations under lmdeploy/pytorch/backends/cuda or other native/device-specific packages.

## 5. Theory Versus Practice

### Theoretical ideal

The book mappings suggest a façade over a stable port, a factory for model/backend strategies, explicit session state, and a composition root that injects a scheduler and executor. Infrastructure-specific adapters should remain outside the core use case.

### Production implementation

LMDeploy combines façade, routing, factory, and lifecycle ownership in a small number of framework modules. It uses subclass registration for model configuration, automatic backend fallback, environment checks, global device context, asynchronous request loops, and executor-specific process/Ray transports. Its engine contract contains cache and distributed methods because the same lifecycle must coordinate model memory and worker ranks.

### Difference and rationale

Inference startup needs to choose a viable implementation from model architecture, device, optional native installation, parallelism, and serving mode. A strict dependency rule would force a large amount of configuration translation at the perimeter. LMDeploy keeps that translation close to the engine and accepts framework coupling so users get one pipeline API. The resulting risk is that import order, backend fallback, cache policy, and executor teardown all affect behavior.

## 6. Testing Strategy

The inspected tests emphasize isolated lifecycle contracts:

- tests/test_lmdeploy/test_pipeline.py and test_model.py cover the user façade/model decisions.
- tests/pytorch/engine/test_executor_base.py uses a recording ExecutorBase subclass to assert initialization ordering, empty initialization behavior, cache sizing, configuration rejection, and failed Ray worker cleanup.
- tests/pytorch/engine/test_engine_sleep.py uses fake request managers, schedulers, engine loops, and executors to prove that sleep blocks new input, cancels sessions, drains work, and wakes only after all tags are released.
- tests/test_lmdeploy/pytorch/engine/test_engine_instance_cleanup.py checks that rejected/cancelled streams clear session state and do not emit invalid END_SESSION messages.
- tests/pytorch/engine/test_ray_mp_engine.py forces stream startup cancellation, remote stream dropping, final-output handling, and pre-first-output errors.
- tests/pytorch/kernel and tests/pytorch/paging suites cover the CUDA/cache/native-facing components separately.

The tests show a useful split: pure Python fakes prove ordering and ownership, while device/kernel suites prove numerical and native behavior. The full serving matrix was not executed in this workspace because it requires model weights, GPU libraries, and distributed runtimes.

## 7. Production Compromises and Failure Boundaries

1. **Automatic fallback.** Unsupported or unavailable TurboMind falls back to PyTorch, improving usability but risking surprise performance/feature differences.
2. **Subclass discovery.** AutoModelConfigBuilder registration is concise, but imports determine which builders exist and the first matching condition wins.
3. **Engine lifecycle is broad.** Model build, cache sizing, graph capture, warmup, request scheduling, sleep, wakeup, and release share an executor contract because they must remain coordinated.
4. **MPExecutor uses termination.** The deprecated multiprocess executor can terminate child processes and destroy process groups; this is robust as a last resort but not graceful cancellation.
5. **Ray teardown is difficult.** The source explicitly notes that coordinated shutdown across data-parallel ranks is non-trivial and sometimes relies on external teardown.
6. **Python/native parity.** TurboMind, PyTorch, CUDA, and non-CUDA device backends can expose different limits and cache behavior even through the same Pipeline façade.

## 8. Lessons and When Not to Use It

Copy the auto-detection/fallback façade when your product must support several execution engines without exposing them to users. Copy the fake executor/engine-loop tests when shutdown, cancellation, and sleep/wakeup ordering are more important than testing only final outputs.

Do not add automatic fallback when a silent performance change is unacceptable; make backend selection explicit and fail fast. Do not build a broad executor contract for a single-device application. A direct async queue and one resource owner are simpler until model, device, and distributed variants justify the extra boundary.

## 9. Practice Exercise

Implement a miniature inference Pipeline with:

1. a model-architecture detector;
2. a TurboMind-like backend and PyTorch-like fallback;
3. a subclass-registered model configuration builder;
4. a common AsyncEngine contract;
5. local and multiprocessing executors;
6. session cancellation and sleep/wakeup tags.

Test unsupported-model fallback, duplicate/precedence builder behavior, cancellation before first output, worker initialization failure cleanup, and wakeup only after both weights and cache resources are ready.
