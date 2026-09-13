# Axolotl

> Repository: [axolotl-ai-cloud/axolotl](https://github.com/axolotl-ai-cloud/axolotl/tree/169df0bd5bb35968fe5f6e3d23fc465c51faf116)
> Checked-out commit: 169df0bd5bb35968fe5f6e3d23fc465c51faf116
> License: Apache-2.0 in LICENSE and CITATION.cff. Some integration headers use different community-license wording, so vendored or optional components should be checked separately.
> Domain: Configurable LLM and multimodal fine-tuning, including SFT, preference/RL training, LoRA/QLoRA, FSDP, DeepSpeed, and Ray execution.
> Python: >=3.10, from pyproject.toml.
> Evidence level: A for configuration, plugin, builder, adapter, and test claims; B for the Python/native boundary because the performance kernels are delegated to dependencies and optional extensions.

## 1. Architecture Summary

Axolotl is a configuration-driven training application. A YAML or JSON file is merged with CLI overrides, converted into a large typed configuration, validated, normalized, and passed through model/data loaders and trainer builders. The builders select a trainer, collator, optimizer, scheduler, and callbacks from model type, training mode, adapter settings, and registered integrations.

The composition root is deliberately integration-aware. The CLI prepares the PluginManager before validation, while train workers may repeat registration and validation after the configuration has been serialized for Ray. This supports a broad matrix of Transformers, TRL, PEFT, DeepSpeed, FSDP, and optional accelerator integrations without requiring every feature in the core trainer.

## 2. Python Boundary

Python owns configuration, validation, model/tokenizer setup, dataset selection, builder composition, lifecycle hooks, and distributed launch coordination. PyTorch, Transformers, TRL, PEFT, DeepSpeed, FSDP, and Ray own most tensor, optimizer, distributed, and execution behavior. The repository also has an integrations/kernels area, but this clone does not establish every native implementation behind those integrations; the boundary is therefore B rather than a claim that Axolotl itself owns a particular CUDA implementation.

The important architectural seam is the trainer boundary: Python chooses and wires the execution objects, then upstream/native libraries run the hot path.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Evidence and trade-off |
|---|---|---|---|---|---|
| P05 Application Service / Use Case | [cli/train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/cli/train.py), [train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/train.py) | [test_cli_train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/cli/test_cli_train.py), [test_builders.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/core/test_builders.py) | Architecture Patterns with Python ch04; Clean Architecture with Python ch18 | A | The CLI use case coordinates model, data, builder, train, and post-train hooks. |
| P07 Composition Root and Dependency Injection | [cli/config.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/cli/config.py), [cli/train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/cli/train.py) | [test_validation.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/patched/test_validation.py), [test_cli_plugins.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/cli/test_cli_plugins.py) | Architecture Patterns with Python ch13; Clean Architecture with Python ch14 and ch18–20 | A | Config is the dependency assembly mechanism, although it is not a small immutable object graph. |
| P08 Factory, Registry, and Plugin Architecture | [integrations/base.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/integrations/base.py) | [test_adapter_plugin_registry.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/integrations/test_adapter_plugin_registry.py), [test_cli_plugins.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/cli/test_cli_plugins.py) | Software Design for Python Programmers ch34; Architecture Patterns with Python ch13 | A | Dotted plugin loading and PluginManager registration are exercised by fake-plugin tests. |
| P09 Strategy, Policy, and Template Method | [core/builders/causal.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/core/builders/causal.py) | [test_builders.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/core/test_builders.py), [test_builders_rl.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/core/test_builders_rl.py) | Software Design for Python Programmers ch33; Architecture Patterns with Python ch04 | A | Trainer, collator, optimizer, and scheduler selection are policy dispatch points. |
| P12 Adapter, Façade, and Provider Router | [loaders/adapter.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/loaders/adapter.py) | [test_adapter_plugin_registry.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/integrations/test_adapter_plugin_registry.py), [test_cli_integrations.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/e2e/patched/test_cli_integrations.py) | Software Design for Python Programmers ch35; Clean Architecture with Python ch19–20 | A | PEFT and plugin capabilities are normalized into one adapter-loading path. |
| P14 Decorator, Middleware, and Observability | [integrations/base.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/integrations/base.py), [train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/train.py) | [test_cli_integrations.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/e2e/patched/test_cli_integrations.py) | Clean Architecture with Python ch23; Software Design for Python Programmers ch39 | B | Callback hooks and post-train hooks are direct lifecycle middleware; tests are broader integration coverage. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [cli/train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/cli/train.py), [train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/train.py) | [test_cli_train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/cli/test_cli_train.py), [test_validation.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/patched/test_validation.py) | Software Design for Python Programmers ch41; Clean Architecture with Python ch23 | B | Ray worker composition and ExitStack-managed training contexts trade isolation for repeated setup. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [integrations/base.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/integrations/base.py) | [test_adapter_plugin_registry.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/integrations/test_adapter_plugin_registry.py), [test_validation.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/patched/test_validation.py) | Clean Architecture with Python ch21 and ch24 | A | Fake plugins and negative configuration tests protect extension boundaries. |

P01–P04, P10–P11, and P13 are not claimed for this concise dossier. Events exist in integration lifecycles, but the inspected code did not justify treating Axolotl as a durable message-bus or saga implementation.

## 4. Source Walkthrough

### Configuration and composition

[cli/config.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/cli/config.py#L207-L350) loads local or remote configuration, applies flat and nested CLI overrides, prepares configured plugins, validates the typed configuration, and cleans up validation side effects. This is the main application composition root.

[cli/train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/cli/train.py#L37-L202) chooses plugin-provided data first, launches ordinary training, and re-registers plugins inside Ray workers after serializing the configuration. Re-validation in workers is an important distributed-system detail.

### Extension and selection

[integrations/base.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/integrations/base.py#L45-L113) defines BasePlugin lifecycle capabilities. Its PluginManager is a singleton with ordered plugin storage, dotted import loading, and first-result dispatch for trainers, collators, optimizers, schedulers, and callbacks ([same file](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/integrations/base.py#L318-L631)).

[core/builders/causal.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/core/builders/causal.py#L70-L193) selects a plugin trainer, model/mode-specific trainer, custom class, or default AxolotlTrainer. The same builder selects TRL arguments, collators, and multimodal processing.

### Adapter and lifecycle boundary

[loaders/adapter.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/loaders/adapter.py#L140-L202) translates typed LoRA configuration and plugin-supplied keyword extensions into PEFT LoraConfig. [train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/train.py#L194-L240) wraps training in managed contexts and invokes plugin post-train hooks; distributed adapter-only save paths handle FSDP/EP state-dict constraints ([train.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/src/axolotl/train.py#L307-L337)).

## 5. Theory Versus Practice

### Theoretical ideal

The books describe a small use-case layer depending on stable ports, an explicit composition root, and replaceable strategies. Configuration should select dependencies without leaking infrastructure into domain logic; adapters translate external APIs at the boundary.

### Production implementation

Axolotl uses Pydantic-backed configuration, upstream Trainer argument shapes, a singleton PluginManager, dotted import strings, and a builder that knows many model and training modes. Plugins contribute to multiple lifecycle points. Ray workers receive a serializable configuration and rebuild integration state locally.

### Difference and rationale

The singleton and first-plugin-wins policy are less explicit than a pure dependency graph, but they make third-party integrations easy to add without changing core builders. The cost is global mutable state, ordering sensitivity, runtime import errors, and less precise conflict diagnostics. Re-validating in Ray workers costs setup time but prevents the driver from assuming GPU capabilities that only workers can observe. Adapter-specific FSDP/EP save code is a practical workaround for distributed state-dict behavior rather than a clean storage port.

## 6. Testing Strategy

The strongest seam tests use a fake BasePlugin. [test_adapter_plugin_registry.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/integrations/test_adapter_plugin_registry.py#L8-L73) verifies plugin-provided PEFT kwargs, adapter capability lookup, and errors for unknown adapters. [test_validation.py](https://github.com/axolotl-ai-cloud/axolotl/blob/169df0bd5bb35968fe5f6e3d23fc465c51faf116/tests/patched/test_validation.py#L37-L216) exercises minimal defaults, dataset requirements, QLoRA/DeepSpeed combinations, and invalid configurations. Builder and CLI tests cover strategy selection; end-to-end integration tests cover the assembled boundary.

The inspected tests establish source and test evidence at this commit. GPU, distributed, and external-model cases should be treated as environment-dependent; this dossier does not claim they were executed locally.

## 7. Lessons

- Copy the typed config plus builder/plugin seam when many model families and optional training backends must share one CLI.
- Do not copy the singleton or first-plugin-wins rule into a safety-critical composition root without deterministic conflict reporting.
- Treat plugin lifecycle order, import strings, distributed re-validation, and adapter checkpoint formats as part of the public architecture.
- The simpler alternative for a small project is one explicit trainer factory and a few typed options; Axolotl’s machinery is justified only once integration variety dominates.

## 8. Practice Exercise

Build a small YAML-to-dataclass training composition root with a Plugin protocol. Add a LoRA adapter plugin that contributes configuration and a collator, reject duplicate plugin names, and test missing-plugin and conflicting-strategy errors. Then add a worker function that receives only a serialized configuration and repeats validation before construction.
