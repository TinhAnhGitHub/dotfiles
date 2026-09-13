# Project Case Study: OpenRLHF

> **Repository**: [OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF/tree/0c550f39d215f6c859674d0d6d721e931397f6d5)  
> **Checked-out commit**: 0c550f39d215f6c859674d0d6d721e931397f6d5  
> **License**: Apache-2.0 (LICENSE)  
> **Domain**: Distributed reinforcement learning from human/AI feedback, PPO/GRPO training, rollout serving  
> **Python**: >=3.10 (setup.py); pytest paths and markers are declared in pyproject.toml  
> **Architecture style**: Ray actor-learner/controller-worker topology with a strategy boundary around DeepSpeed and an optional vLLM rollout plane  
> **Evidence level**: A/B claims below are source-plus-test claims. C findings are explicitly excluded from authoritative pattern claims.

## 1. Architecture Summary

OpenRLHF turns a PPO training run into a group of colocated Ray actors. A driver builds placement groups and actor groups, then a remote PPO controller coordinates policy, reference, reward, critic, and rollout workers. The control loop remains Python; tensor execution, distributed collectives, and optimizer kernels are delegated to PyTorch, DeepSpeed, NCCL, and vLLM.

~~~text
CLI train_ppo_ray.py
        |
        v
Ray placement groups and RayActorGroup
        |
        +--> Python PPO controller and experience maker
        |       +--> policy / critic remote actors
        |       +--> reference / reward remote actors
        |       +--> optional vLLM rollout actors
        |
        +--> DeepspeedStrategy --> torch.distributed / NCCL / CUDA
        +--> vLLM engine       --> model execution and KV-cache runtime
~~~

The important architectural decision is not a domain-layer separation in the DDD sense. It is a resource-and-lifecycle separation: the controller owns training progression, Ray owns placement and remote references, and each worker owns one model/runtime lifecycle.

## 2. Python Boundary

### Python control and orchestration plane

- openrlhf/cli/train_ppo_ray.py is the composition root. It parses arguments, initializes Ray, creates placement groups, selects synchronous or asynchronous training, and starts one remote PPO controller.
- openrlhf/trainer/ray/launcher.py turns a logical actor group into Ray actors, assigns rank/environment variables, and batches remote method calls.
- openrlhf/trainer/ppo_trainer.py owns the episode/step loop, checkpoint policy, evaluation, experience production, and coordination between actor groups.
- openrlhf/trainer/ray/ppo_actor.py and vllm_engine.py adapt the model-facing APIs to Ray calls and manage inter-process weight synchronization.

### Native and performance-critical plane

- PyTorch owns tensor graphs and model forward/backward execution.
- DeepSpeed and its distributed backend own optimizer/ZeRO state, process groups, parameter sharding, and collective communication. OpenRLHF exposes this through openrlhf/utils/deepspeed/deepspeed.py.
- vLLM owns high-throughput token generation, scheduling, KV-cache operations, and its native/CUDA kernels.
- OpenRLHF itself does not define the hot CUDA kernels. Its Python boundary is therefore an orchestration boundary over several native-heavy runtimes.

This split matters when debugging: an incorrect Ray rank or placement assignment is a Python control-plane defect; a collective hang, CUDA OOM, or generation throughput problem may be in the DeepSpeed, NCCL, vLLM, or PyTorch plane.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Trade-off |
| :--- | :--- | :--- | :--- | :--- | :--- |
| P07 Composition Root and Dependency Injection | [train_ppo_ray.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/cli/train_ppo_ray.py#L19-L195) | [test_ray_env_vars.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_ray_env_vars.py#L80-L215) | Architecture with Python ch13; Clean Architecture ch18-ch20 | B | Explicit construction makes resource topology visible, but the CLI is tightly coupled to Ray and training roles. |
| P09 Strategy, Policy, and Template Method | [deepspeed.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/utils/deepspeed/deepspeed.py#L37-L108) | [test_deepspeed_save_model.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_deepspeed_save_model.py#L39-L149) | Design for Python Programmers ch33; Architecture ch04; Clean Architecture ch18 | B | The strategy centralizes distributed preparation and optimizer policy, but inherits DeepSpeed configuration complexity. |
| P12 Adapter, Façade, and Provider Router | [vllm_engine.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ray/vllm_engine.py#L33-L327), [ppo_actor.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ray/ppo_actor.py#L494-L662) | [test_samples_generator.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_samples_generator.py#L62-L160) | Design ch35; Clean Architecture ch19-ch20 | B | The rollout adapter stabilizes PPO-facing calls, while weight-sync and Ray references leak into the boundary. |
| P13 State Machine, Workflow, and Saga | [ppo_trainer.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ppo_trainer.py#L148-L300), [ppo_trainer_async.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ppo_trainer_async.py) | [test_ppo_trainer.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_ppo_trainer.py#L22-L118), [test_samples_generator.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_samples_generator.py#L110-L160) | Design ch38; Clean Architecture ch18 and ch24 | B | Sync/async training and checkpoint restore form a workflow, but it is not a durable saga with compensating transactions. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [launcher.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ray/launcher.py#L202-L360), [vllm_engine.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ray/vllm_engine.py#L209-L327) | [test_ray_env_vars.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_ray_env_vars.py#L131-L215), [test_agent.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_agent.py#L17-L140) | Design ch41; Clean Architecture ch23 | B | Fractional GPU placement and asynchronous calls improve utilization, but correctness depends on distributed rank and cleanup conventions. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [ppo_trainer.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ppo_trainer.py#L213-L300) | [test_ppo_trainer.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_ppo_trainer.py#L22-L118), [test_deepspeed_save_model.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/tests/test_deepspeed_save_model.py#L39-L149) | Clean Architecture ch21 and ch24 | A | Tests replace Ray, vLLM, and DeepSpeed modules to isolate coordination and boundary failures. |

P10 Commands, Events, and Message Bus is present only as a **C, non-authoritative observation**: Ray remote calls and callbacks move work between actors, but the inspected code does not establish a durable message bus, event log, or idempotent event-delivery contract.

## 4. Source Walkthrough

### File 1 — CLI composition and topology

[openrlhf/cli/train_ppo_ray.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/cli/train_ppo_ray.py#L19-L195) initializes Ray with selected environment variables, creates placement groups for actor/reference/critic/reward/rollout roles, chooses the synchronous or asynchronous trainer, and invokes fit/save. It is the best file for seeing the whole resource topology. It is also a warning: composition-root code can become a second configuration system when every role has its own GPU and colocation flags.

### File 2 — Actor groups and rank setup

[openrlhf/trainer/ray/launcher.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ray/launcher.py#L17-L360) defines BaseDistributedActor, BaseModelActor, and RayActorGroup. BaseDistributedActor derives distributed environment variables from Ray node and GPU information. RayActorGroup computes the logical world size, creates placement-group bundles, launches remote actors, and slices/batches calls before putting data in Ray’s object store.

### File 3 — Training controller

[openrlhf/trainer/ppo_trainer.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ppo_trainer.py#L148-L410) coordinates experience creation, optional load/offload operations, actor/critic updates, vLLM weight broadcast, checkpointing, and evaluation. The remote PPO controller later in the file makes the controller a resource owner without making it the owner of model tensors.

### File 4 — Rollout and weight synchronization

[openrlhf/trainer/ray/vllm_engine.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ray/vllm_engine.py#L33-L327) wraps vLLM’s asynchronous engine in Ray actors. It creates an async engine per actor, initializes process groups for weight transfer, supports cache sleep/wake, gathers asynchronous generation results, and batches remote calls. [openrlhf/trainer/ray/ppo_actor.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/trainer/ray/ppo_actor.py#L110-L489) shows the opposite direction: DeepSpeed rank zero and vLLM workers share a synchronization group and receive updated weights.

### File 5 — Distributed strategy

[openrlhf/utils/deepspeed/deepspeed.py](https://github.com/OpenRLHF/OpenRLHF/blob/0c550f39d215f6c859674d0d6d721e931397f6d5/openrlhf/utils/deepspeed/deepspeed.py#L37-L293) is an explicit Strategy boundary. It seeds processes, initializes torch.distributed, derives device meshes for data/sequence/tensor parallelism, prepares training/evaluation models, builds dataloaders, and exposes backward/step operations. The abstraction is useful for testing and policy selection, but it is deliberately aware of distributed details rather than a domain-pure interface.

## 5. Theory Versus Practice

### Theoretical ideal

The book mappings suggest a composition root that injects ports, a strategy that hides algorithm variation, commands/events for decoupled coordination, and a workflow state machine with explicit persistence and recovery.

### Production implementation

OpenRLHF uses direct construction and direct Ray method calls. The controller passes concrete RayActorGroup instances into a trainer. Actor groups hold remote references, placement-group assumptions, rank setup, and batching logic. The PPO loop uses synchronous Ray get calls in important paths, while asynchronous generation and the async trainer overlap work. Checkpoints are the recovery boundary; there is no transaction that atomically rolls back a partially completed PPO update across all actors.

### Difference and rationale

The production system optimizes GPU utilization and collective correctness. A generic message bus would add serialization, delivery, and retry semantics to a workload whose real consistency boundary is a distributed optimizer/model update. Keeping the resource topology in the composition root makes fractional GPU colocation and ring/tensor parallel choices inspectable. The compromise is tighter coupling to Ray and a larger failure surface at the boundaries between Ray, DeepSpeed, and vLLM.

## 6. Testing Strategy

The strongest testing seam is dependency replacement rather than a full local cluster:

- tests/test_ppo_trainer.py injects fake Ray and heavy modules, loads the trainer module, and exercises the controller with terminal and empty rollout behavior.
- tests/test_ray_env_vars.py supplies a fake Ray module, captures the runtime_env passed to ray.init, checks defaults and user overrides, and verifies that an already-initialized Ray process is not reinitialized.
- tests/test_agent.py uses an aiohttp test server to exercise asynchronous reward fetching, empty shard handling, multi-turn truncation, and penalty behavior.
- tests/test_deepspeed_save_model.py stubs DeepSpeed and validates that tied embeddings are handled while genuine parameter mismatches still raise.
- tests/test_samples_generator.py checks terminal oversampling buffers, dynamic filtering, and cancellation behavior.

These tests reveal the actual lifecycle contracts: initialization must be idempotent enough to respect an existing Ray session, cancellation must not strand rollout work, and model-save normalization must not hide real shape errors. They do not prove multi-node NCCL correctness; that remains an integration/system concern.

## 7. Production Compromises and Failure Boundaries

1. **Ray is both scheduler and transport.** Object references and remote calls are efficient, but actor groups now know placement, rank, and batching details. A simpler local trainer is preferable for one GPU.
2. **The strategy is not fully opaque.** DeepspeedStrategy exposes mesh, ZeRO, ring attention, dataloader, and checkpoint details because those details determine memory and throughput.
3. **Checkpointing is recovery, not a transaction.** The controller can restore model/trainer state, but a crash between actor, critic, and rollout updates is not modeled as a two-phase commit.
4. **Native hot paths are delegated.** Python abstractions can make orchestration legible without making CUDA operations portable. Portability still depends on the installed PyTorch/DeepSpeed/vLLM stack.
5. **Dynamic imports and runtime flags multiply combinations.** Colocation, async mode, vLLM sleep, tensor/ring parallelism, and agent rollouts require a broad matrix; the unit tests cover seams, not every topology.

## 8. Lessons and When Not to Use It

Copy the explicit controller/worker split when work has several GPU roles, different resource footprints, and a real need to overlap rollout and training. Copy the test seam pattern when importing the full runtime is expensive.

Do not copy this topology for a small synchronous training job, a single-provider inference wrapper, or a service that needs durable business events. In those cases, a local strategy object, a normal queue, or a simple application service is easier to reason about.

## 9. Practice Exercise

Build a small fake PPO controller with three roles: policy, reward, and rollout. Give each role a protocol-like test double, add a synchronous and asynchronous execution mode, and write tests for:

1. a cancelled rollout;
2. a worker that returns an error after another worker has updated;
3. a checkpoint that restores the controller step;
4. duplicate resource registration.

Then replace the local role objects with Ray actors and keep the controller tests unchanged. The goal is to feel which part of P16 is a useful seam and which part is Ray-specific coupling.
