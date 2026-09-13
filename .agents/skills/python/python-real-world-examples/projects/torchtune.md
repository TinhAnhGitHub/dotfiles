# TorchTune

> Repository: [pytorch/torchtune](https://github.com/pytorch/torchtune/tree/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1)
> Checked-out commit: bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1
> License: BSD 3-Clause, from LICENSE and pyproject.toml.
> Domain: PyTorch-native LLM fine-tuning, quantization, preference/RL recipes, and distributed training.
> Python: >=3.9, from pyproject.toml.
> Evidence level: A for configuration, recipe, registry, checkpoint, and test claims; B for the Python/native boundary.

## 1. Architecture Summary

TorchTune separates reusable model, dataset, optimizer, checkpointer, and training components from executable recipe scripts. A recipe is the application service: it owns setup, the training loop, checkpoint/resume, logging, and cleanup. OmegaConf YAML files provide the composition root and can replace components by dotted Python path.

The main distributed LoRA recipe combines configuration instantiation with PyTorch distributed dimensions, FSDP, activation checkpointing, optional compilation, adapter injection, and checkpoint persistence. A static recipe registry supplies the user-facing inventory for tune list/copy commands; it is an explicit catalog, not a general runtime plugin system.

## 2. Python Boundary

Python owns recipe orchestration, YAML parsing, component construction, validation, checkpoint policy, and process lifecycle. PyTorch’s C++/CUDA kernels and distributed implementations own tensor execution, communication, FSDP, and compilation. The recipe code is therefore a Python control plane over a native-heavy execution plane; the clone does not justify attributing individual kernels to TorchTune.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Evidence and trade-off |
|---|---|---|---|---|---|
| P05 Application Service / Use Case | [lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/lora_finetune_distributed.py) | [test_lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/recipes/test_lora_finetune_distributed.py) | Architecture Patterns with Python ch04; Clean Architecture with Python ch18 | A | The recipe class is a concrete fine-tuning use case with setup, train, save, and cleanup. |
| P07 Composition Root and Dependency Injection | [config/_parse.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/config/_parse.py), [config/_instantiate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/config/_instantiate.py) | [test_parse.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/config/test_parse.py), [test_instantiate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/config/test_instantiate.py) | Architecture Patterns with Python ch13; Clean Architecture with Python ch14 and ch18–20 | A | YAML and CLI overrides build the object graph at the recipe boundary. |
| P08 Factory, Registry, and Plugin Architecture | [_recipe_registry.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/_recipe_registry.py) | [test_import_recipes.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/test_import_recipes.py), [test_configs.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/recipes/test_configs.py) | Software Design for Python Programmers ch34; Architecture Patterns with Python ch13 | A | The static Recipe/Config catalog is direct registry evidence; it should not be described as dynamic discovery. |
| P09 Strategy, Policy, and Template Method | [config/_instantiate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/config/_instantiate.py), [8B_lora.yaml](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/configs/llama3/8B_lora.yaml) | [test_instantiate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/config/test_instantiate.py), [test_validate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/config/test_validate.py) | Software Design for Python Programmers ch33; Architecture Patterns with Python ch04 | A | Optimizer, scheduler, model, dataset, logger, and checkpointer are selected as policies through component paths. |
| P12 Adapter, Façade, and Provider Router | [checkpoint/_checkpoint_client.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/training/checkpointing/_checkpoint_client.py), [checkpoint/_checkpointer.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/training/checkpointing/_checkpointer.py) | [test_checkpointer.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/training/checkpointing/test_checkpointer.py), [test_distributed_checkpointer.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/training/checkpointing/test_distributed_checkpointer.py) | Software Design for Python Programmers ch35; Clean Architecture with Python ch19–20 | A | Checkpointer APIs hide format and distributed-storage details from the recipe. |
| P13 State Machine, Workflow, and Saga | [lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/lora_finetune_distributed.py) | [test_lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/recipes/test_lora_finetune_distributed.py) | Architecture Patterns with Python ch08–11; Clean Architecture with Python ch18 | B | Resume state and checkpoint phases form a workflow, but this is not a general saga with compensating actions. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/lora_finetune_distributed.py) | [test_lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/recipes/test_lora_finetune_distributed.py) | Software Design for Python Programmers ch41; Clean Architecture with Python ch23 | A | Process groups, FSDP meshes, dataloaders, checkpoint clients, and cleanup are explicit lifecycle responsibilities. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [config/_validate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/config/_validate.py) | [test_validate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/config/test_validate.py), [test_configs.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/recipes/test_configs.py) | Clean Architecture with Python ch21 and ch24 | A | The suite validates component syntax and all shipped YAML configurations before expensive training tests. |

P01–P04, P10–P12 beyond checkpoint adaptation, and P14–P15 are not claimed here. In particular, the recipe registry is not evidence of a third-party plugin ecosystem.

## 4. Source Walkthrough

### Configuration composition

[config/_instantiate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/config/_instantiate.py#L18-L166) recursively resolves _component_ dictionaries, nested components, lists, dotted imports, and CLI overrides. [config/_parse.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/config/_parse.py#L20-L99) makes a recipe’s config file mandatory and lets command-line keys override YAML.

[recipes/configs/llama3/8B_lora.yaml](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/configs/llama3/8B_lora.yaml#L20-L127) shows the object graph: model, tokenizer, LoRA modules, checkpointer, dataset, optimizer, scheduler, loss, logger, profiler, and output paths are all configuration-selected components.

### Recipe and registry

[recipes/lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/lora_finetune_distributed.py#L134-L227) constructs process-group and parallelism state. Its setup path instantiates logging, checkpoint, model, tokenizer, optimizer, scheduler, data, and profiler components. The model path builds a LoRA configuration, instantiates on a meta device, applies FSDP/activation policies, and restores adapter/base state ([same recipe](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/lora_finetune_distributed.py#L472-L627)).

[_recipe_registry.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/torchtune/_recipe_registry.py#L10-L21) stores an explicit list of recipe and config metadata used by the CLI. Adding a recipe is consequently a source change plus a registry entry.

### Checkpoint and lifecycle

The recipe constructs a StatefulDistributedSampler and DataLoader, then uses CheckpointClient to save model, optimizer, training progress, and adapter configuration ([recipe](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/recipes/lora_finetune_distributed.py#L659-L734)). The main function parses and logs resolved configuration, instantiates the recipe, runs it, and cleans up distributed resources.

## 5. Theory Versus Practice

### Theoretical ideal

The books recommend a use-case layer that depends on stable ports and an explicit composition root. A repository or adapter should isolate persistence, while strategies should be small replaceable policies.

### Production implementation

TorchTune places the composition root in YAML plus a recipe, and allows YAML to name arbitrary Python components. The recipe is intentionally stateful and knows about FSDP, meta-device construction, checkpoint formats, sampler state, and distributed cleanup. Its registry is static and user-facing.

### Difference and rationale

Import-path configuration is more flexible than a closed dependency graph but shifts errors to runtime and makes static analysis harder. A recipe containing setup and training is less layered than a pure use-case/domain split, yet it keeps research experiments readable and makes distributed invariants visible in one place. drop_last=True protects compiled/flexible shapes at the cost of discarding incomplete batches. Resume is practical checkpoint restoration, not a transactional guarantee or mid-batch saga.

## 6. Testing Strategy

[test_instantiate.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/config/test_instantiate.py#L70-L146) tests simple, nested, invalid, and overridden components. [test_parse.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/torchtune/config/test_parse.py#L20-L77) tests YAML/CLI precedence. [test_configs.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/recipes/test_configs.py#L18-L29) validates all recipe configurations.

[test_lora_finetune_distributed.py](https://github.com/pytorch/torchtune/blob/bd2a0fc7c31430972728494fa01aaeeb0ebf1ba1/tests/recipes/test_lora_finetune_distributed.py) covers distributed LoRA loss and resume behavior, but is marked for two GPUs/integration execution. The source/test evidence is direct; this dossier does not claim those GPU tests were run locally.

## 7. Lessons

- Copy the declarative component graph when experiments need repeatable swapping of model, dataset, optimizer, and checkpoint policies.
- Prefer a typed, closed composition root for a smaller service where arbitrary import paths are unnecessary.
- Keep the explicit recipe lifecycle if distributed invariants are more important than strict domain isolation.
- Do not describe the static recipe inventory as automatic plugin discovery; it improves discoverability but adds a maintenance step.

## 8. Practice Exercise

Add a small custom dataset or optimizer component, select it through a YAML _component_ path, and override one argument from the CLI. Write tests for nested instantiation, invalid paths, CLI precedence, and restoration of a minimal training-progress state.
