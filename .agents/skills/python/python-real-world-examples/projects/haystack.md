# Haystack

> Repository: [deepset-ai/haystack@9872f76](https://github.com/deepset-ai/haystack/tree/9872f764f16913f6919eddd955c25c78554bc00a)
> Default branch: `main`
> Commit: `9872f764f16913f6919eddd955c25c78554bc00a`
> License: [Apache-2.0](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/LICENSE)
> Domain: Component pipelines for search, retrieval, generation, and document processing
> Python/native boundary: The core component/pipeline/serialization system is Python; external retrievers, stores, model SDKs, and optional native libraries sit behind component adapters.
> Evidence level: A for component registry/sockets, pipeline execution/lifecycle, serialization, and tests
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/haystack` (read-only pinned checkout)

## 1. Executive Architecture Summary

Haystack models application behavior as typed components connected into a pipeline graph. The `@component` decorator validates component signatures, derives input/output sockets, and registers classes for serialization. `Pipeline` then validates connections, executes ready components, supports sync and async variants, and owns warm-up/close lifecycle calls.

This is a Python pipeline/microkernel architecture: components are the extension unit, while the core controls graph composition, serialization, scheduling, and lifecycle. The design keeps heavyweight model/store initialization out of constructors by giving components a `warm_up` hook.

```text
Component classes
   │ @component: sockets + registry + contract checks
   ▼
Pipeline graph ── validate/connect ── run / run_async
   │                              │
   ├── serialization allowlist     └── warm_up / close lifecycle
   ▼
External model, retriever, store, and transport adapters
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Component contract | `haystack/core/component/component.py` | Decorator, protocol, socket metadata, registry, signature validation |
| Graph/composition core | `haystack/core/pipeline/base.py`, `pipeline.py` | Add/connect components, validate graph, execute sync/async paths |
| Serialization boundary | `haystack/core/serialization.py`, `serialization_security.py` | Encode/decode components and enforce import/trust rules |
| Integration components | Packages under `haystack/components/` | Provider, retriever, document-store, and transport mechanisms |
| Application perimeter | User pipeline definitions and runners | Supply components, input data, secrets, and deployment configuration |

The core does not own provider SDK details. It does own enough component metadata and serialization policy to validate and reconstruct a graph, which is the framework’s central invariant.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | [`haystack/core/component/component.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/haystack/core/component/component.py) validates decorated classes and stores their class paths in a registry; [`haystack/core/pipeline/base.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/haystack/core/pipeline/base.py) resolves registered component classes during deserialization | [`test/core/component/test_component.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/component/test_component.py), [`test/core/pipeline/test_pipeline_base.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/pipeline/test_pipeline_base.py) | Software Design ch34; Clean Architecture ch20 | A |
| P09 | Strategy, policy, and template method | [`haystack/core/pipeline/pipeline.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/haystack/core/pipeline/pipeline.py) selects sync/async execution paths and component priorities while preserving the graph contract; component socket validation centralizes the execution policy | [`test/core/pipeline/test_async_pipeline.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/pipeline/test_async_pipeline.py), [`test/core/pipeline/test_validation_pipeline_io.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/pipeline/test_validation_pipeline_io.py), [`test/core/component/test_component_signature_validation.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/component/test_component_signature_validation.py) | Software Design ch33; Clean Architecture ch15 | A |
| P12 | Adapter, façade, and provider boundary | [`haystack/core/serialization.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/haystack/core/serialization.py) translates component objects to/from JSON-compatible dictionaries; `Component` gives external integrations a common `run`/`warm_up` contract | [`test/core/test_serialization.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/test_serialization.py), [`test/core/test_serialization_security.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/test_serialization_security.py), [`test/core/pipeline/test_pipeline.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/pipeline/test_pipeline.py) | Clean Architecture ch19–20; Software Design ch35 | A |
| P15 | Composite, iterator, visitor, and pipelines | [`haystack/core/pipeline/pipeline.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/haystack/core/pipeline/pipeline.py) traverses ready graph components, propagates socket outputs, supports branches/joins, and exposes run generators; lifecycle methods are defined in `pipeline/base.py` | [`test/core/pipeline/test_pipeline.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/pipeline/test_pipeline.py), [`test/core/pipeline/test_pipeline_lifecycle.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/pipeline/test_pipeline_lifecycle.py), [`test/core/pipeline/test_async_pipeline.py`](https://github.com/deepset-ai/haystack/blob/9872f764f16913f6919eddd955c25c78554bc00a/test/core/pipeline/test_async_pipeline.py) | Clean Architecture ch18; Software Design ch36/ch39 | A |

## 4. Source Walkthrough

### `core/component/component.py`

The decorator and metaclass inspect `run` signatures, derive sockets, reject invalid async/sync definitions, and register a class path. Component constructors are expected to stay lightweight; expensive resources belong in `warm_up`. This separates object graph construction from resource acquisition.

### `core/pipeline/base.py` and `pipeline.py`

The base class serializes a graph, checks registry membership while loading, adds components, connects sockets, and provides `warm_up`/`close` plus async counterparts. `Pipeline.run` and `run_async` then execute components according to graph readiness and propagate outputs to downstream sockets.

### Serialization and security

`component_to_dict`/`component_from_dict` and the default serializers form an anti-corruption boundary between a component graph and JSON-like configuration. `serialization_security.py` supplies import/trust checks so reconstruction is not an unconstrained arbitrary import operation.

## 5. Theory Versus Practice

Haystack’s pipeline is close to the textbook composite/iterator idea, but its primary invariant is socket compatibility and graph readiness rather than a domain aggregate. The global component registry is convenient for serialization and package extensions, while the security layer acknowledges that dynamic class loading is an operational risk.

Sync and async APIs are maintained together, and lifecycle is explicit rather than inferred from `run`. This increases framework surface area but avoids silently creating network/model resources while a graph is executing.

## 6. Testing Strategy

- Component tests verify decorator registration, socket metadata, and signature failures.
- Pipeline tests cover add/connect validation, branch/connection behavior, runtime failures, and outputs.
- Lifecycle tests use recorder components to verify sync/async warm-up, run, close, and loop-affinity behavior.
- Serialization tests cover default/custom component encoding, registry lookup, import trust, and error cases.

The evidence pass inspected the core source and tests at the pinned commit; external integration components were not executed.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Process-wide component registry | Easy plugin discovery and serialized graph reconstruction | Prefer explicit dependency injection for a small service or security-sensitive plugin set |
| Dynamic import during deserialization | Supports third-party components without a central switch | Keep an allowlist/trust policy and test unknown/untrusted classes |
| Dual sync/async component contracts | Works with both simple Python functions and async providers | Avoid duplicating APIs unless both execution modes are required |
| Framework owns warm-up and close hooks | Makes heavy resources and cleanup visible | Components still need idempotent lifecycle behavior and failure tests |

## 8. Practice Exercise

Use [the registry-plugin exercise](../../python-software-architecture/exercises/registry-plugin.md): implement two components with validated input/output sockets, register them, serialize/deserialize a pipeline, and test warm-up/close plus an untrusted class rejection. Add one async component only after the sync graph is correct.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `deepset-ai/haystack`, `main` |
| Pinned revision | `9872f764f16913f6919eddd955c25c78554bc00a` |
| License | Apache-2.0, verified from repository `LICENSE` |
| Python/native boundary | Python component/pipeline core; external integrations may use SDKs/native libraries |
| Canonical pattern IDs | P08 (A), P09 (A), P12 (A), P15 (A) |
| Source evidence | Component decorator/registry, pipeline base/runtime, serialization/security |
| Test evidence | Component, signature, pipeline, lifecycle, async, serialization, and security tests |
| Book mapping | Clean Architecture ch15 and ch18–20; Software Design ch33–36 and ch39 |
| Production compromise | Registry and dynamic serialization are retained for ecosystem extensibility, with an explicit security boundary |
| Practice exercise | `exercises/registry-plugin.md` |
