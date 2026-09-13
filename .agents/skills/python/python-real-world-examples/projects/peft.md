# PEFT

> Repository: [huggingface/peft](https://github.com/huggingface/peft/tree/0e8d0ae8ab94f189f28b845e293d7452d7892d91)
> Checked-out commit: 0e8d0ae8ab94f189f28b845e293d7452d7892d91
> License: Apache-2.0, from LICENSE.
> Domain: Parameter-efficient fine-tuning adapters for PyTorch and Transformers models.
> Python: >=3.10.0, from setup.py.
> Evidence level: A for adapter wrapping, configuration mapping, persistence, and test claims; B for the native boundary.

## 1. Architecture Summary

PEFT turns a base torch.nn.Module into an adapter-aware model without requiring each model family to know every tuning method. A PeftConfig selects a method, get_peft_model selects the task wrapper, and a method-specific BaseTuner injects trainable modules into matching target modules. PeftModel then owns adapter activation, saving, loading, and merging.

The architecture has two registries. Configuration and tuner classes are mapped by PeftType; built-in tuner modules register themselves while the package is imported. The common tuner base centralizes injection and adapter lifecycle, while LoRA, IA3, prompt tuning, and many other methods supply method-specific configuration and replacement logic.

## 2. Python Boundary

Python owns method metadata, configuration serialization, target-module selection, wrapper/tuner composition, adapter state, and Hub/local persistence. PyTorch modules execute the forward/backward graph; optional bitsandbytes, Transformers, quantization, and CUDA extensions provide specialized tensor paths. PEFT is consequently a Python adapter layer over a model runtime, not the owner of the base model’s native kernels.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Evidence and trade-off |
|---|---|---|---|---|---|
| P07 Composition Root and Dependency Injection | [__init__.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/__init__.py) | [test_imports](https://github.com/huggingface/peft/tree/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests) | Architecture Patterns with Python ch13; Clean Architecture with Python ch14 and ch19–20 | B | Package imports establish the built-in method map; it is import-time assembly rather than an application composition root. |
| P08 Factory, Registry, and Plugin Architecture | [peft_types.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/utils/peft_types.py), [mapping.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/mapping.py) | [test_mapping.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_mapping.py), [test_tuners_utils.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_tuners_utils.py) | Software Design for Python Programmers ch34; Architecture Patterns with Python ch13 | B | register_peft_method fills global method-to-config/tuner mappings; tests exercise mapping and tuner behavior, though not every extension path. |
| P09 Strategy, Policy, and Template Method | [tuners_utils.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/tuners/tuners_utils.py), [peft_types.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/utils/peft_types.py) | [test_tuners_utils.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_tuners_utils.py), [test_lora_variants.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_lora_variants.py) | Software Design for Python Programmers ch33; Architecture Patterns with Python ch04 | A | PeftType and BaseTuner select method policy while subclasses implement target-specific replacement. |
| P12 Adapter, Façade, and Provider Router | [mapping_func.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/mapping_func.py), [peft_model.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/peft_model.py) | [test_mapping.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_mapping.py), [test_low_level_api.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_low_level_api.py) | Software Design for Python Programmers ch35; Clean Architecture with Python ch19–20 | A | get_peft_model and inject_adapter_in_model translate a base model into the adapter contract. |
| P15 Composite, Iterator, Visitor, and Pipelines | [peft_model.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/peft_model.py) | [test_mixed.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_mixed.py), [test_helpers.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_helpers.py) | Software Design for Python Programmers ch36 and ch39 | A | A PeftModel can hold multiple named adapters and route activation/serialization across the wrapped module tree. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [config.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/config.py), [tuners_utils.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/tuners/tuners_utils.py) | [test_config.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_config.py), [test_auto.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_auto.py), [test_other.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_other.py) | Clean Architecture with Python ch21 and ch24 | A | Config round trips, model wrapping, adapter switching, and persistence are tested at the public seams. |

P01–P06, P10–P11, P13–P14, and P16 are not claimed. PEFT has lifecycle methods and serialization, but the inspected evidence is about adapter composition rather than domain aggregates, events, workflows, or scheduling.

## 4. Source Walkthrough

### Method registry and factory

[utils/peft_types.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/utils/peft_types.py#L19-L202) defines PeftType and register_peft_method. Registration validates method names and prefixes, then fills configuration, tuner, mixed-model, and prefix mappings. [__init__.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/__init__.py#L15-L157) imports the built-in tuner modules whose registration calls populate those maps.

[mapping_func.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/mapping_func.py#L105-L204) selects a generic or task-specific PeftModel and wraps the base model. [mapping.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/mapping.py#L47-L103) provides the lower-level injection path and rejects method classes that cannot be directly injected.

### Common tuner and adapter policy

[tuners/tuners_utils.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/tuners/tuners_utils.py#L258-L418) supplies BaseTuner state, target-module matching, and lifecycle hooks. Subclasses implement replacement and configuration preparation; the common base injects adapters and supports activation of named adapters. [tuners/lora/config.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/tuners/lora/config.py) is a concrete method policy.

### Persistence and compatibility

[config.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/config.py#L77-L228) serializes method configuration, records the PEFT version, and reconstructs the correct config from a saved type. It drops unexpected fields with a warning for forward compatibility. [peft_model.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/src/peft/peft_model.py) owns save_pretrained/from_pretrained, add_adapter, load_adapter, set_adapter, and merge behavior.

## 5. Theory Versus Practice

### Theoretical ideal

The books describe an adapter as a narrow boundary translating one interface to another, with explicit construction and substitutable strategies. A registry should be deliberate and testable, and persistence should sit behind an infrastructure port.

### Production implementation

PEFT uses one global mapping for many method families, package-import registration, a common BaseTuner, and a PeftModel wrapper that mutates/wraps the base model. Configuration JSON is the compatibility boundary; model-specific target matching and method constraints remain in each tuner.

### Difference and rationale

Import-time global registration keeps the public API small and makes new tuning methods independent of the central factory. The cost is import order/circular-dependency risk and runtime errors when a method is not registered. The wrapper is easier for Transformers users than an explicit adapter object graph, but get_peft_model can mutate the supplied model and repeated wrapping requires warnings. Unknown config fields are dropped with warnings to keep old readers usable; this can conceal a feature mismatch. The low-level injection API rejects prompt/shared-state cases, showing that one universal adapter seam has real limits.

## 6. Testing Strategy

[test_mapping.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_mapping.py) checks wrapping and repeated-use behavior. [test_config.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_config.py) covers config validation and serialization. [test_helpers.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_helpers.py), [test_mixed.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_mixed.py), and tuner-specific files exercise multiple adapter names, activation, save/load, and method variants. [test_auto.py](https://github.com/huggingface/peft/blob/0e8d0ae8ab94f189f28b845e293d7452d7892d91/tests/test_auto.py) covers AutoPeft loading and local/Hub round trips; Hub-marked tests are external-state dependent.

The source and tests are present at the pinned commit. GPU, optional quantization, and Hub cases should be treated as environment-dependent rather than locally executed evidence.

## 7. Lessons

- Copy the common tuner contract when many adapter strategies must target many model families.
- Keep the registry narrow and validate names, prefixes, duplicate registration, and target-module failures.
- Prefer explicit composition for a small application; PEFT’s import-time global map is justified by its ecosystem of independently shipped tuning methods.
- Treat adapter names, active-adapter state, save format, and merge semantics as part of the architecture, not incidental model details.

## 8. Practice Exercise

Wrap a small torch.nn.Module with a LoRA-like adapter, register a second method in a local method map, and support add/set/save/load for named adapters. Test duplicate method registration, missing target modules, repeated wrapping, active-adapter switching, and unknown configuration fields.
