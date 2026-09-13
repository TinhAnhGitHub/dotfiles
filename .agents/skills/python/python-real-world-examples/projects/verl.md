# verl

> Repository: [verl-project/verl](https://github.com/verl-project/verl/tree/10db40d0da4d59150bb389960b77585f81a89b8d)
> Default branch: `main`
> Commit: `10db40d0da4d59150bb389960b77585f81a89b8d`
> License: Apache-2.0
> Domain: Distributed reinforcement-learning training for language models
> Python: 3.10–3.12 (`pyproject.toml`)
> Evidence level: A for dispatch/resource/rollout registries with focused tests; B for trainer composition and lifecycle claims
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/verl` (read-only pinned checkout)

## 1. Executive Architecture Summary

verl separates the RL driver from the workers that perform actor, rollout, critic, reference-policy, and reward-model work. The driver maps semantic roles to worker classes, asks a `ResourcePoolManager` for Ray placement, and invokes worker-group methods. Decorators attach dispatch metadata to worker methods so the same driver call can be expanded across ranks. Rollout engines such as vLLM and SGLang are loaded behind adapters and replica modes.

```text
OmegaConf/config
       │
       ▼
RayPPOTrainer ── Role + role_worker_mapping ── ResourcePoolManager
       │                                            │
       └── WorkerGroup RPC ── Ray placement groups ── actor/critic/ref/rollout workers
                                                        │
                                                        └── PyTorch/FSDP/Megatron/vLLM/SGLang
```

This is a distributed control-plane architecture. Its primary consistency boundary is a worker/resource topology, not a transactional domain aggregate. No authoritative P01–P04 repository/unit-of-work implementation was found in the assigned source.

## 2. Layering & Boundary Discipline

| Layer | Responsibility | Evidence |
|---|---|---|
| Driver/application orchestration | PPO lifecycle, checkpointing, logging, validation, role topology | `verl/trainer/ppo/ray_trainer.py` |
| Worker invocation protocol | Dispatch mode, execute mode, future materialization, liveness | `verl/single_controller/base/decorator.py`, `verl/single_controller/base/worker_group.py` |
| Resource topology | Ray placement groups, GPU/CPU bundles, colocation and splitting | `verl/single_controller/ray/base.py` |
| Algorithm policy | Policy-loss selection and role requirements | `verl/trainer/ppo/core_algos.py`, `verl/trainer/ppo/utils.py` |
| Rollout/adapters | Engine-specific loading and hybrid/colocated/standalone lifecycle | `verl/workers/rollout/base.py`, `verl/workers/rollout/replica.py` |
| Performance plane | PyTorch/FSDP/Megatron and external serving engines | Worker and rollout imports |

### Python/native boundary

Python owns configuration, driver orchestration, role mapping, Ray RPC metadata, resource placement, checkpoint coordination, and the worker-facing interfaces. Tensor computation and model execution are delegated to PyTorch/FSDP/Megatron; generation may be delegated to vLLM, SGLang, or TensorRT-LLM. The repository’s clean abstractions therefore sit above several native/performance implementations. A worker class is an orchestration seam, not evidence that the computation itself is Python-only.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | `verl/single_controller/base/decorator.py` (`DISPATCH_MODE_FN_REGISTRY`, `register_dispatch_mode`); `verl/trainer/ppo/core_algos.py` (`POLICY_LOSS_REGISTRY`); `verl/workers/rollout/base.py` and `verl/workers/rollout/replica.py` | `tests/single_controller/base/test_decorator.py`; `tests/workers/rollout/test_pd_disaggregation.py` | Software Design ch34; Architecture with Python ch13 | A for dispatch/replica registries; B for policy-loss registry (no focused registry test found) |
| P09 | Strategy and policy | `Dispatch` modes, `Role` topology decisions in `verl/trainer/ppo/utils.py`, and named policy-loss functions in `core_algos.py` | Dispatch registration tests and resource/topology tests exercise selected policies | Software Design ch33; Architecture with Python ch04; Clean Architecture ch14 | A/B |
| P12 | Adapter and provider router | Lazy rollout class resolution in `verl/workers/rollout/base.py`; `RolloutReplicaRegistry` and backend-specific loaders in `verl/workers/rollout/replica.py` | `tests/workers/rollout/test_pd_disaggregation.py`, `test_vllm_pd_disaggregation_on_cpu.py`, and rollout abort/determinism tests | Software Design ch35; Clean Architecture ch19–20 | A |
| P13 | State machine/workflow/lifecycle | `RolloutMode` (`HYBRID`, `COLOCATED`, `STANDALONE`), `RolloutReplica.init_*`, wake/sleep/release and abort paths | PD disaggregation and vLLM abort tests cover mode selection and failure/lifecycle behavior | Architecture with Python ch08–11; Clean Architecture ch18 | A/B |
| P16 | Scheduling, concurrency, and resource lifecycle | `ResourcePool`, `RayResourcePool`, `ResourcePoolManager`, placement-group creation, pool splitting, and worker liveness checking | `tests/single_controller/test_split_resource_pool.py`, `test_high_level_scheduling_api.py`, and colocated/fused worker tests | Software Design ch41; Clean Architecture ch23 | A |
| P17 | Testing seams and architecture fitness | Deferred `ClassWithInitArgs`, fake worker classes, registry reset fixtures, CPU rollout imports, and pool-level tests | `tests/single_controller/base/test_decorator.py`, `tests/single_controller/test_split_resource_pool.py`, and rollout tests | Clean Architecture ch21 | A |

No authoritative P01–P07 or P10–P11 evidence was found in this batch. The policy-loss registry has a focused-source gap: no direct registry test was located, so it remains B rather than A.

## 4. Source Walkthrough

### `verl/single_controller/base/decorator.py`

`Dispatch` and `Execute` describe how a logical method call maps to ranks and how it runs. `DISPATCH_MODE_FN_REGISTRY` stores the implementation of each mode. `register_dispatch_mode` extends the mode set and rejects duplicate names; `update_dispatch_mode` replaces an existing implementation deliberately. The `register` decorator validates the selected modes, optionally materializes futures, and stores dispatch metadata on the wrapped method.

### `verl/single_controller/base/worker_group.py`

`WorkerGroup._bind_worker_method` reads the decorator metadata from a worker class, resolves the dispatch function, and creates a group-level callable. `ClassWithInitArgs` defers construction so the same worker specification can be launched in the selected Ray processes. A liveness-check thread and an “all workers alive” barrier make worker startup a lifecycle concern of the group rather than of each algorithm method.

### `verl/single_controller/ray/base.py`

`RayResourcePool` converts a resource description into Ray placement groups and orders bundles by node. `ResourcePoolManager` maps logical pool names to concrete pools and checks availability before launching work. `split_resource_pool` creates views for separate roles while reusing placement groups where possible. This gives the trainer an explicit topology language—separate, colocated, or split—at the cost of Ray-specific coordination.

### `verl/trainer/ppo/ray_trainer.py`

`RayPPOTrainer` accepts a role-to-worker mapping and a `ResourcePoolManager`. `init_workers` turns role requirements into `RayClassWithInitArgs` entries, creates worker groups, and binds role-specific services. `fit` stays on the driver: it loads checkpoints, asks workers to update weights or generate data, tracks progress, validates, and saves state. The application service is therefore a coordinator of remote capabilities rather than the owner of model tensors.

### `verl/trainer/ppo/core_algos.py` and `verl/trainer/ppo/utils.py`

The loss registry turns names into policy-loss callables through a decorator. Utility functions derive the required roles from the algorithm/configuration and create datasets/samplers, including a stateful sampler for recoverable shuffling. This is Strategy expressed as functions and topology decisions rather than subclassing the entire trainer.

### `verl/workers/rollout/base.py` and `verl/workers/rollout/replica.py`

`BaseRollout` defines the engine-facing contract. `_ROLLOUT_REGISTRY` maps `(engine, mode)` pairs to lazily imported adapter classes. `RolloutReplica` then separates process topology from engine identity: hybrid uses the trainer process, colocated uses another process in the same pool, and standalone owns another resource pool. The registry chooses vLLM/SGLang/TensorRT-LLM loaders and selects PD-disaggregation classes when supported.

## 5. Theory Versus Practice

### Theoretical ideal

Architecture Patterns with Python ch04/ch13 and Clean Architecture ch14/18 favor a use-case/service layer that depends on inward-facing ports, with bootstrapping assembled at the edge. Software Design ch33/ch34 presents strategies and factories as small, replaceable units. A workflow can model transitions explicitly and test each boundary in isolation.

### Production implementation

verl uses a driver plus remote worker groups. Registries are process-local and frequently class/module-level because every Ray worker needs to import the same registration code. Resource pools are concrete Ray placement groups, and the trainer’s configuration decides which roles exist. Rollout lifecycle includes weight transfer, KV-cache sleep/wake, abort, profiling, and disaggregation modes.

### Difference and rationale

The ideal port can be backend-neutral; production verl must express GPU counts, tensor/data/pipeline parallelism, node locality, and Ray actor behavior. Sharing placement groups improves utilization and enables hybrid engines, but reduces isolation and makes failure/recovery state more complex. Lazy backend imports keep optional engines from becoming mandatory dependencies, but missing or incompatible engines fail at runtime. Class-level registries simplify worker bootstrap, yet import order and process boundaries mean a registration made in the driver is not automatically a registration in an already-started worker.

## 6. Testing Strategy

- `tests/single_controller/base/test_decorator.py` resets global registries and verifies adding a dispatch mode, updating one, and rejecting invalid duplicates.
- `tests/single_controller/test_split_resource_pool.py` checks split sizes, cross-node behavior, and repeated splitting.
- `tests/single_controller/test_high_level_scheduling_api.py` launches fake Ray actors and checks placement/device behavior.
- `tests/single_controller/test_colocated_workers.py`, `test_colocated_workers_fused.py`, and `test_fused_workers_on_cpu.py` exercise topology variants.
- `tests/workers/rollout/test_pd_disaggregation.py` verifies backend names, plain versus PD replica class selection, and unsupported TensorRT-LLM combinations.
- `tests/workers/rollout/rollout_vllm/test_vllm_abort.py` and `test_vllm_generation_determinism.py` cover concrete rollout behavior.

The files were inspected at the pinned revision. Ray/GPU integration tests were not run locally; the unit tests still provide direct evidence for the registry and resource boundaries.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Multiple process-global registries | Independent algorithms, dispatch modes, losses, and engines can be added without editing the trainer | Avoid globals when extensions must be tenant-scoped or hot-reloaded safely |
| Ray placement groups as the resource abstraction | Makes GPU topology and colocation explicit | Do not introduce Ray solely for a small single-process workload |
| Hybrid/colocated/standalone rollout modes | Lets deployments trade latency, memory, and isolation | Each mode multiplies synchronization, weight-transfer, and failure states |
| Lazy fully qualified imports | Optional vLLM/SGLang/TensorRT-LLM support | Add startup validation if runtime failure would waste a long training job |
| Driver-owned orchestration | Keeps algorithm policy in one place | The driver can become a coordination bottleneck if worker APIs are too chatty |

## 8. Practice Exercise

Add a small `policy_loss` registry to a toy distributed trainer:

1. Implement `register_policy_loss(name)` and `get_policy_loss_fn(name)` with duplicate and missing-name errors.
2. Add two pure loss functions and a fake `WorkerGroup` whose method is decorated with a custom dispatch mode.
3. Add a fake resource-pool manager with `separate`, `colocated`, and `split` plans.
4. Test registry isolation, worker dispatch metadata, invalid pool splits, and a failed rollout that can be aborted and released.

The exercise is complete when adding a new loss or dispatch policy requires no edit to the trainer’s main loop.
