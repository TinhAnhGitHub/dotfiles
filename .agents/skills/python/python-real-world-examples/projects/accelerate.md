# Accelerate

> Repository: [huggingface/accelerate](https://github.com/huggingface/accelerate/tree/f13f7c13b64c10b6eb7e2d73171ea1b94c748701)
> Checked-out commit: f13f7c13b64c10b6eb7e2d73171ea1b94c748701
> License: Apache-2.0, from LICENSE.
> Domain: A unified control-plane API for PyTorch distributed training, mixed precision, device placement, checkpointing, DeepSpeed, FSDP, Megatron-LM, TPU, and parallelism.
> Python: >=3.10.0, from setup.py.
> Evidence level: A for facade, backend dispatch, configuration, state, and tests; B for the Python/native boundary.

## 1. Architecture Summary

Accelerate is a façade around heterogeneous execution backends. The user creates an Accelerator, supplies optional backend plugins and kwargs handlers, calls prepare on models/optimizers/dataloaders/schedulers, and uses the same training loop across single-process, multi-GPU, FSDP, DeepSpeed, Megatron, TPU, and mixed-precision environments.

The constructor and shared state form a large composition root. Configuration can come from the accelerate CLI, YAML/JSON files, environment variables, launch arguments, and explicit constructor arguments. prepare then routes each object through the selected distributed policy. Checkpointing is an explicit lifecycle extension through state_dict/load_state_dict contracts.

## 2. Python Boundary

Python owns the stable user API, environment/config parsing, backend selection, device placement, state bookkeeping, launcher assembly, and checkpoint orchestration. PyTorch distributed, CUDA, XLA, DeepSpeed, FSDP, Megatron-LM, and related compiler/kernel layers own most execution and communication. This is an adapter-heavy Python control plane, not a reimplementation of the native training runtime.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Evidence and trade-off |
|---|---|---|---|---|---|
| P05 Application Service / Use Case | [accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/accelerator.py) | [test_accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_accelerator.py) | Architecture Patterns with Python ch04; Clean Architecture with Python ch18 | A | Accelerator is the application-facing use-case façade for preparing and running a training graph. |
| P07 Composition Root and Dependency Injection | [accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/accelerator.py), [config_args.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/commands/config/config_args.py) | [test_dataclasses.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_dataclasses.py), [test_cli.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_cli.py) | Architecture Patterns with Python ch13; Clean Architecture with Python ch14 and ch18–20 | A | Plugin arguments, config objects, and handlers are assembled into Accelerator state. |
| P09 Strategy, Policy, and Template Method | [state.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/state.py), [parallelism_config.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/parallelism_config.py) | [test_accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_accelerator.py), [test_dataclasses.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_dataclasses.py) | Software Design for Python Programmers ch33; Architecture Patterns with Python ch04 | A | DistributedType, parallelism configuration, and kwargs handlers encode backend policy. |
| P12 Adapter, Façade, and Provider Router | [accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/accelerator.py) | [test_accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_accelerator.py), [test_deepspeed.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/deepspeed/test_deepspeed.py), [test_fsdp.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/fsdp/test_fsdp.py) | Software Design for Python Programmers ch35; Clean Architecture with Python ch19–20 | A | prepare dispatches one public operation to backend-specific preparation paths. |
| P14 Decorator, Middleware, and Observability | [hooks.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/hooks.py) | [test_hooks.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_hooks.py) | Clean Architecture with Python ch23; Software Design for Python Programmers ch39 | A | Model/device hooks and tracking integrations wrap execution without changing the user loop. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [state.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/state.py), [accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/accelerator.py) | [test_state_checkpointing.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_state_checkpointing.py), [test_launch.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_launch.py) | Software Design for Python Programmers ch41; Clean Architecture with Python ch23 | A | Process state, launch policy, preparation, and checkpoint lifecycle are first-class APIs. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [utils/dataclasses.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/utils/dataclasses.py) | [test_kwargs_handlers.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_kwargs_handlers.py), [test_configs](https://github.com/huggingface/accelerate/tree/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_configs) | Clean Architecture with Python ch21 and ch24 | A | Backend/config fixtures and checkpoint tests protect compatibility seams. |

P01–P04, P08, P10–P11, P13, and P15 are not claimed for this dossier. Accelerate consumes registries and callbacks from dependencies but its inspected core evidence is primarily façade, policy, adapter, and lifecycle design.

## 4. Source Walkthrough

### Composition and policy

[accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/accelerator.py#L280-L477) accepts DeepSpeed/FSDP/Megatron/parallelism plugins, project configuration, kwargs handlers, and device settings. It validates incompatible combinations and creates shared AcceleratorState.

[state.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/state.py) separates PartialState, AcceleratorState, and GradientState, but these objects intentionally share process-level state. [parallelism_config.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/parallelism_config.py) validates mesh sizes and parallelism strategies before execution.

### Adapter router

[Accelerator.prepare](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/accelerator.py#L1415-L1579) keeps the public call stable while dispatching to DeepSpeed, Megatron, FSDP2, FP8, or standard preparation paths. This is a provider router whose providers are distributed execution backends rather than network services.

[utils/dataclasses.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/utils/dataclasses.py) defines kwargs handlers and backend plugin dataclasses. DeepSpeed auto settings are matched against user arguments and may be filled from the environment, which reduces boilerplate while preserving compatibility checks.

### Configuration and checkpoint lifecycle

[commands/config/config_args.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/commands/config/config_args.py#L29-L173) loads YAML/JSON, serializes enum/dataclass values, applies defaults, and rejects unknown keys. [commands/launch.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/commands/launch.py) maps config to the selected launcher. Accelerator.register_for_checkpointing requires custom objects to expose state_dict/load_state_dict ([accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/src/accelerate/accelerator.py#L4115-L4149)).

## 5. Theory Versus Practice

### Theoretical ideal

The books recommend an explicit composition root, stable ports, and small adapters around infrastructure. A strategy should vary independently of the application use case, and lifecycle ownership should be visible.

### Production implementation

Accelerate presents one large Accelerator façade with many constructor options and a process-global state model. It keeps compatibility with old config fields, environment variables, launcher modes, and backend-specific plugins. Its adapter layer is implemented with conditional dispatch inside the façade rather than a family of fully independent provider objects.

### Difference and rationale

The large façade makes ordinary user loops portable and keeps backend knowledge out of user code. The compromise is constructor complexity, backend conditionals, and hidden assumptions about one process-level Accelerator state. Multiple configuration sources are useful for CLI ergonomics and backward compatibility, but there is no single immutable source of truth. The checkpoint contract is intentionally narrow: custom objects must reconstruct their state in the same script/environment, not through a portable event log.

## 6. Testing Strategy

[test_kwargs_handlers.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_kwargs_handlers.py) tests handler serialization and default-difference behavior. [test_accelerator.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_accelerator.py) covers preparation and public façade behavior. [test_state_checkpointing.py](https://github.com/huggingface/accelerate/blob/f13f7c13b64c10b6eb7e2d73171ea1b94c748701/tests/test_state_checkpointing.py) saves and reloads model/training state and RNG-related progress. Backend-specific suites under deepspeed, fsdp, and tp exercise the adapter contracts; config fixtures cover old and invalid schemas.

The source and test paths are present at the pinned commit. TPU/GPU/distributed cases are environment-dependent and were not treated as locally executed evidence.

## 7. Lessons

- Copy the stable prepare/context/checkpoint façade when the application must support several distributed providers.
- Use a smaller explicit backend interface if the project has one execution mode; a universal façade is otherwise premature.
- Keep backend policy in typed config objects and test invalid combinations at the boundary.
- Document process-global state and checkpoint portability limits; convenience can otherwise look like dependency injection while remaining implicit.

## 8. Practice Exercise

Write a tiny Accelerator-like façade with a CPU provider and a fake distributed provider. Add a kwargs handler that serializes only non-default values, implement prepare and register_for_checkpointing, and test backend selection, invalid combinations, and save/load round trips.
