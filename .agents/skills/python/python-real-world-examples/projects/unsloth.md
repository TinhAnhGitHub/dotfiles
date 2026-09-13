# Unsloth

> Repository: [unslothai/unsloth](https://github.com/unslothai/unsloth/tree/7c63bc8c4f18c1d0b0eec5e656ae20797893b500)
> Checked-out commit: 7c63bc8c4f18c1d0b0eec5e656ae20797893b500
> License: Apache-2.0 in the root LICENSE and pyproject.toml. Individual bundled or test files may carry additional notices and should be reviewed when redistributed.
> Domain: Accelerated LLM, vision, diffusion, embedding, and RL fine-tuning, adapter training, model export, and Unsloth Studio.
> Python: >=3.9,<3.15, from pyproject.toml.
> Evidence level: A for registry, loader, trainer patch, export, and test claims; B for the complete Python/native boundary.

## 1. Architecture Summary

Unsloth exposes high-level FastLanguageModel and FastModel APIs that load a model, select precision/device policy, patch supported model families, and prepare training or inference. Model-family modules, a model/quantization registry, PEFT integration, TRL trainer patches, optimizer extensions, and export functions sit behind those public entry points.

The import path is part of the composition root. It gates optional backends, normalizes Transformers compatibility, detects devices, and avoids hard-requiring bitsandbytes on unsupported hosts. A separate Studio application adds a Python backend and Rust/Tauri desktop boundary; this dossier focuses on the core training architecture while recording that additional boundary.

## 2. Python Boundary

Python owns public loaders, model-family dispatch, PEFT/TRL integration, device and precision policy, compatibility patches, optimizer construction, export routing, and disk preflight. PyTorch and optional bitsandbytes/vLLM/llama.cpp/unsloth-zoo components execute compiled tensor or inference work. The repository’s own visible performance layer is largely Python plus Triton kernels under unsloth/kernels; Studio also contains Rust under studio/src-tauri. Because several compiled providers are external and not all kernel implementations are in this clone, the full boundary is B.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Evidence and trade-off |
|---|---|---|---|---|---|
| P05 Application Service / Use Case | [models/loader.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/loader.py), [trainer.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/trainer.py) | [test_fast_language_model_text_only.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_fast_language_model_text_only.py), [test_qlora_train_and_merge.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/qlora/test_unsloth_qlora_train_and_merge.py) | Architecture Patterns with Python ch04; Clean Architecture with Python ch18 | A | Fast loader plus trainer is the application-facing fine-tuning use case. |
| P07 Composition Root and Dependency Injection | [__init__.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/__init__.py), [device_type.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/device_type.py) | [test_import_without_bitsandbytes.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_import_without_bitsandbytes.py), [test_cross_platform_parity.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_cross_platform_parity.py) | Architecture Patterns with Python ch13; Clean Architecture with Python ch14 and ch19–20 | A | Import-time capability detection assembles a backend-specific runtime and fallbacks. |
| P08 Factory, Registry, and Plugin Architecture | [registry/registry.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/registry/registry.py), [registry/__init__.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/registry/__init__.py) | [test_model_registry.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/test_model_registry.py) | Software Design for Python Programmers ch34; Architecture Patterns with Python ch13 | A | ModelMeta registration creates a guarded model/quantization catalog; tests verify registration, aliases, and Hub failure handling. |
| P09 Strategy, Policy, and Template Method | [models/loader.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/loader.py), [trainer.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/trainer.py) | [test_fast_model_config_passthrough.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_fast_model_config_passthrough.py), [test_patch_trl_rl_trainers_defensive.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_patch_trl_rl_trainers_defensive.py) | Software Design for Python Programmers ch33; Architecture Patterns with Python ch04 | B | Precision, task, model-family, packing, and optimizer choices are policies; the broad loader test suite is partly AST-based. |
| P12 Adapter, Façade, and Provider Router | [models/loader.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/loader.py), [models/_utils.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/_utils.py), [save.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/save.py) | [test_fast_language_model_text_only.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_fast_language_model_text_only.py), [test_export_dispatch.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/saving/test_export_dispatch.py) | Software Design for Python Programmers ch35; Clean Architecture with Python ch19–20 | A | Public loading/saving APIs route to model-family, quantization, PEFT, compressed-tensor, GGUF, or torchao providers. |
| P14 Decorator, Middleware, and Observability | [trainer.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/trainer.py), [models/rl.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/rl.py) | [test_patch_trl_rl_trainers_defensive.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_patch_trl_rl_trainers_defensive.py) | Clean Architecture with Python ch23; Software Design for Python Programmers ch39 | A | Unsloth wraps/patches TRL trainer classes and isolates compatibility failures. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [save.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/save.py), [trainer.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/trainer.py) | [test_export_dispatch.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/saving/test_export_dispatch.py), [test_launch_cleanup.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/kaggle/test_launch_cleanup.py) | Software Design for Python Programmers ch41; Clean Architecture with Python ch23 | B | Export dispatch, staging, disk preflight, and launch cleanup make resource ownership explicit, but are platform-heavy. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [models/loader.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/loader.py), [registry/registry.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/registry/registry.py) | [test_import_without_bitsandbytes.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_import_without_bitsandbytes.py), [test_model_registry.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/test_model_registry.py), [test_export_dispatch.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/saving/test_export_dispatch.py) | Clean Architecture with Python ch21 and ch24 | A | AST/source tests and monkeypatched dispatch tests protect optional-dependency and provider seams. |

P01–P04, P10–P11, P13, and P15 are not claimed. Unsloth has RL and export workflows, but this batch did not establish a durable event bus, aggregate boundary, or general state-machine implementation.

## 4. Source Walkthrough

### Import and model composition

[unsloth/__init__.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/__init__.py) performs early environment and backend gating before importing heavy libraries. It handles MLX versus GPU paths, compatibility workarounds, and optional dependency errors. [models/__init__.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/__init__.py) exposes model-family classes and FastLanguageModel/FastModel.

[models/loader.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/models/loader.py#L375-L411) exposes FastLanguageModel.from_pretrained with precision, device-map, gradient-checkpointing, revision, quantization, and inference options. It delegates to FastModel and model-family implementations, handles task/text-only configuration, and falls back when bitsandbytes is unavailable. FastModel also has explicit for_training and for_inference transitions.

### Registry and training policy

[registry/registry.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/registry/registry.py#L34-L195) models family metadata, quantization types, and duplicate-protected registration. [registry/__init__.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/registry/__init__.py#L9-L65) lazily registers model families and supports filtered search.

[trainer.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/trainer.py#L415-L514) adds UnslothTrainingArguments and UnslothTrainer policies such as embedding learning rates and Q-GaLore. [trainer.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/trainer.py#L1055-L1086) discovers compatible TRL Trainer/Config pairs and applies guarded compatibility wrappers.

### Export and resource lifecycle

[save.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/unsloth/save.py) routes merged 16-bit, compressed-tensor, GGUF, LoRA, and torchao exports. Its preflight helpers estimate staging/output disk requirements and can choose a different temporary filesystem. [test_export_dispatch.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/saving/test_export_dispatch.py) verifies routing without requiring the heavy converters.

## 5. Theory Versus Practice

### Theoretical ideal

The books recommend stable ports around infrastructure, explicit composition, and replaceable strategies. Performance-specific code should remain behind a narrow adapter so the use case can be tested without the native runtime.

### Production implementation

Unsloth puts compatibility and capability detection in import-time code, dispatches model families from a broad loader, patches external TRL classes, and keeps a global model registry. It uses fallback behavior for missing bitsandbytes, version-specific Transformers/TRL paths, and multiple export providers.

### Difference and rationale

Import-time patching is pragmatic because the goal is to make existing Transformers/TRL user code faster without changing that code. The cost is global side effects, version coupling, and failure modes that depend on import order. A single loader reduces user friction but accumulates precision, task, device, model-family, and quantization branches. The registry is more disciplined: registration is lazy, duplicate-protected, and separately tested. Export preflight is a production compromise that treats disk space as a runtime resource and may redirect staging rather than pretending serialization is a pure function.

## 6. Testing Strategy

[test_model_registry.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/test_model_registry.py) tests family registration, quantization tags, duplicate/import behavior, and distinguishes a Hub outage from a missing model. [test_fast_language_model_text_only.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_fast_language_model_text_only.py) and [test_fast_model_config_passthrough.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_fast_model_config_passthrough.py) protect loader delegation and task/config boundaries. [test_import_without_bitsandbytes.py](https://github.com/unslothai/unsloth/blob/7c63bc8c4f18c1d0b0eec5e656ae20797893b500/tests/python/test_import_without_bitsandbytes.py) uses AST/import-chain checks for optional dependency safety. The defensive TRL patch tests and export-dispatch tests use monkeypatching and fake providers to isolate expensive or unavailable backends.

The QLoRA, Kaggle, GPU, Hub, and Studio suites are valuable integration evidence but require external models, accelerators, or platform tooling. They were inspected at the pinned revision, not treated as locally executed results.

## 7. Lessons

- Copy the façade plus capability-gated fallback when a performance library must preserve a familiar upstream API.
- Keep compatibility patches narrow, idempotent, and defensively tested; global monkey patches are expensive to debug.
- Make model/quantization registries lazy and duplicate-protected, and distinguish provider outages from invalid metadata.
- For a small project, use explicit model factories and a normal Trainer; Unsloth’s import and export machinery is justified by hardware/version breadth.

## 8. Practice Exercise

Implement a small model loader with a model-family registry, a CPU fallback when an optional accelerator package is absent, and explicit for_training/for_inference transitions. Add a fake export provider router with disk preflight, then test duplicate registration, missing capability, provider failure, idempotent patching, and output-path selection.
