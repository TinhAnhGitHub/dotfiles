# LLaMA-Factory

> Repository: [hiyouga/LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory/tree/100e9a42c6c09f8f7849b70d60f3da445fb2024b)
> Checked-out commit: 100e9a42c6c09f8f7849b70d60f3da445fb2024b
> License: Apache-2.0, from LICENSE and pyproject.toml.
> Domain: Unified CLI/Web fine-tuning and inference for many LLM and multimodal model families, using full, freeze, LoRA/OFT/QLoRA, preference, and RL training.
> Python: >=3.11.0, from pyproject.toml.
> Evidence level: A for parser, registry, adapter, trainer, and test claims; B for backend/native and distributed-launch claims.

## 1. Architecture Summary

LLaMA-Factory is a large application shell around Transformers, PEFT, TRL, Accelerate, and optional vLLM/SGLang, DeepSpeed, FSDP, Megatron, NPU, and Ray paths. The CLI parses one of several dataclass argument groups from YAML, JSON, or command-line arguments, validates cross-field constraints, loads model/data/template components, applies a fine-tuning strategy, and enters a trainer or inference engine.

The repository has two composition branches. The default launcher is the established train/infer stack; the CLI can switch to a v1 launcher with USE_V1. The v1 tree adds typed plugin objects for model, data, kernel, and trainer extensions while the established tree uses explicit registries and dispatch functions.

## 2. Python Boundary

Python owns CLI composition, argument validation, model/tokenizer/data loading, chat templates, adapter selection, trainer construction, logging, and launch orchestration. PyTorch/Transformers/TRL/PEFT/Accelerate execute the training graph; optional DeepSpeed/FSDP/Megatron, vLLM/SGLang, NPU libraries, and fused kernels own backend-specific performance paths. The launcher can spawn torchrun workers, so Python’s configuration and lifecycle boundary is reconstructed in child processes.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Evidence and trade-off |
|---|---|---|---|---|---|
| P05 Application Service / Use Case | [train/tuner.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/train/tuner.py), [launcher.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/launcher.py) | [test_train.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/e2e/test_train.py), [test_sft_trainer.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/train/test_sft_trainer.py) | Architecture Patterns with Python ch04; Clean Architecture with Python ch18 | A | run_exp is the application entry point for parsing, loading, training, evaluation, and export. |
| P07 Composition Root and Dependency Injection | [hparams/parser.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/hparams/parser.py), [cli.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/cli.py) | [test_args_parser.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests_v1/config/test_args_parser.py), [test_train.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/e2e/test_train.py) | Architecture Patterns with Python ch13; Clean Architecture with Python ch14 and ch18–20 | A | Argument groups and environment flags assemble one of several runtime graphs. |
| P08 Factory, Registry, and Plugin Architecture | [data/template.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/data/template.py), [v1/utils/plugin.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/v1/utils/plugin.py), [v1/plugins/model_plugins/peft.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/v1/plugins/model_plugins/peft.py) | [test_template.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/data/test_template.py), [test_peft.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests_v1/plugins/model_plugins/test_peft.py) | Software Design for Python Programmers ch34; Architecture Patterns with Python ch13 | A | Template and v1 plugin decorators register model/data/kernel behaviors; registration is import-time and explicit. |
| P09 Strategy, Policy, and Template Method | [hparams/finetuning_args.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/hparams/finetuning_args.py), [model/adapter.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/model/adapter.py) | [test_lora.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/model/test_lora.py), [test_freeze.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/model/test_freeze.py) | Software Design for Python Programmers ch33; Architecture Patterns with Python ch04 | A | stage and finetuning_type select full, freeze, LoRA/OFT, preference, or RL policies. |
| P12 Adapter, Façade, and Provider Router | [model/adapter.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/model/adapter.py), [chat/base_engine.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/chat/base_engine.py), [chat/vllm_engine.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/chat/vllm_engine.py) | [test_lora.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/model/test_lora.py), [test_sglang.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/e2e/test_sglang.py) | Software Design for Python Programmers ch35; Clean Architecture with Python ch19–20 | A | PEFT adapters and HF/vLLM/SGLang engines normalize different model/runtime APIs behind application-facing calls. |
| P14 Decorator, Middleware, and Observability | [train/callbacks.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/train/callbacks.py), [extras/logging.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/extras/logging.py) | [test_sft_trainer.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/train/test_sft_trainer.py), [test_train.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/e2e/test_train.py) | Clean Architecture with Python ch23; Software Design for Python Programmers ch39 | B | Trainer callbacks and rank-aware logging wrap execution; tests validate assembled training behavior more than each hook in isolation. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [launcher.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/launcher.py), [hparams/training_args.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/hparams/training_args.py) | [test_train.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/e2e/test_train.py), [tests_v1/plugins/trainer_plugins/distributed/test_fsdp2.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests_v1/plugins/trainer_plugins/distributed/test_fsdp2.py) | Software Design for Python Programmers ch41; Clean Architecture with Python ch23 | B | torchrun/Ray/FSDP/Megatron choices are resource policies, but execution depends on external hardware/runtime. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [hparams/parser.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/hparams/parser.py), [v1/plugins/model_plugins/peft.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/v1/plugins/model_plugins/peft.py) | [test_template.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/data/test_template.py), [test_lora.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/model/test_lora.py), [test_peft.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests_v1/plugins/model_plugins/test_peft.py) | Clean Architecture with Python ch21 and ch24 | A | Unit, E2E, and v1 plugin tests protect config, template, adapter, and distributed seams. |

P01–P04, P10–P11, and P13 are not claimed. The repository has callbacks and training stages, but the inspected evidence does not establish a durable event bus or resumable saga model.

## 4. Source Walkthrough

### CLI and configuration

[cli.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/cli.py#L16-L24) selects the default or v1 launcher from USE_V1. [hparams/parser.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/hparams/parser.py#L112-L163) merges YAML/JSON with OmegaConf CLI overrides, parses multiple dataclass groups, rejects unknown arguments, and validates cross-field compatibility. It also checks optional dependencies for Unsloth, vLLM, SGLang, Megatron, and alternative optimizers.

### Launch and training strategy

[launcher.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/launcher.py#L38-L157) chooses API, chat, export, train, Web UI, or environment commands and launches torchrun for multi-device training. [train/tuner.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/train/tuner.py) turns parsed arguments into model/data/trainer execution and can hand off to Ray.

[hparams/finetuning_args.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/hparams/finetuning_args.py) is the policy surface for stages and fine-tuning types. [model/adapter.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/model/adapter.py#L101-L203) loads, merges, resumes, or creates PEFT adapters and chooses target modules and task type.

### Registries and provider adapters

[data/template.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/data/template.py#L614-L800) registers named chat templates and resolves a tokenizer to a template, with validation for missing or incompatible templates. The v1 [plugin base](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/v1/utils/plugin.py) provides decorator registration; [v1/plugins/model_plugins/peft.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/v1/plugins/model_plugins/peft.py#L82-L206) registers LoRA and freeze model strategies.

[chat/base_engine.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/src/llamafactory/chat/base_engine.py) defines the application-facing chat engine, while HF, vLLM, and SGLang implementations adapt provider/runtime differences. The repository thus has a real provider router, not just a README list of supported engines.

## 5. Theory Versus Practice

### Theoretical ideal

The books recommend typed use cases depending on stable ports, with adapters translating framework and provider details. Factories and registries should be explicit, and strategy selection should be independent of the core use case.

### Production implementation

LLaMA-Factory uses large dataclass argument groups, HfArgumentParser/OmegaConf, cross-field validation, import-time template/plugin registration, and a trainer shell that knows many external frameworks. The v1 branch is a parallel architecture rather than a small incremental adapter around every legacy path.

### Difference and rationale

One broad configuration surface is valuable for a zero-code fine-tuning product, but it creates a combinatorial validation problem and runtime dependency checks. Import-time registries make support for new model/template/plugin types cheap, at the cost of import-order and discoverability issues. Adapter merging differs by mode: training resumes one LoRA adapter, while inference may merge multiple adapters; this is an explicit practical constraint rather than a universal adapter abstraction. torchrun and Ray launch choices improve scale, but the Python process cannot fully validate worker hardware until execution.

## 6. Testing Strategy

[test_lora.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/model/test_lora.py) checks target-module selection, old/new adapter behavior, trainability, and inference merging. [test_freeze.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/model/test_freeze.py) covers freeze policy. [test_template.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests/data/test_template.py) checks registration and tokenizer/template rendering. v1 [test_peft.py](https://github.com/hiyouga/LLaMA-Factory/blob/100e9a42c6c09f8f7849b70d60f3da445fb2024b/tests_v1/plugins/model_plugins/test_peft.py) exercises LoRA/freeze plugin behavior and export artifacts.

The E2E and SGLang/FSDP2 suites verify assembled boundaries but use tiny Hub models or accelerator hardware; they are environment-dependent. These paths were inspected at the pinned revision, not treated as locally executed results.

## 7. Lessons

- Copy the staged configuration and validation approach when one tool must expose many training modes without custom Python.
- Prefer a smaller explicit use-case object and closed strategy enum for an application with fewer model families.
- Keep provider engines behind one interface, but make provider-specific error and capability differences visible.
- A compatibility branch such as v1 can enable migration, but it doubles the composition surface until the old path is removed.

## 8. Practice Exercise

Create a miniature fine-tuning CLI with dataclass argument groups for model, data, and strategy. Register two templates and two adapter policies, reject incompatible quantization/adapter combinations, and add tests for YAML overrides, template lookup, LoRA resume versus inference merge, and a missing optional provider.
