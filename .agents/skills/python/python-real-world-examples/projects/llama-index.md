# LlamaIndex

> Repository: [run-llama/llama_index@7169bcd](https://github.com/run-llama/llama_index/tree/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5)
> Default branch: `main`
> Commit: `7169bcd0dca2e16aecc8e0247f34e50079d9c0d5`
> License: [MIT](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/LICENSE)
> Domain: LLM application framework, indexing, storage, ingestion, and provider integrations
> Python/native boundary: The reviewed `llama-index-core` is Python; external LLM/vector/database integrations are adapters and may bring their own SDKs or native runtimes. Core indexing and pipeline orchestration remain Python.
> Evidence level: A for index registry/loading, storage/LLM adapters, and ingestion pipeline tests
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/llama-index` (read-only pinned checkout)

## 1. Executive Architecture Summary

LlamaIndex core is a Python modular framework that composes documents, indices, storage contexts, LLM interfaces, and ingestion transformations. It uses explicit registries and serialization to reconstruct index objects from persisted storage, while `StorageContext` groups the stores that must move together.

The framework is intentionally integration-heavy: LLMs, vector stores, embeddings, and document stores vary widely. Core abstractions such as `CustomLLM`, `StorageContext`, and `IngestionPipeline` provide stable seams, while integrations live in separate packages. The result is a pipeline/plugin architecture rather than a conventional domain-driven application.

```text
Documents / user query
          │
          ▼
IngestionPipeline ── transformations ── embeddings / vector store
          │
          ▼
Index registry + loading ── StorageContext ── persisted stores
          │
          ▼
Query/index façade ── BaseLLM / provider integrations
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Core protocols and models | `llama-index-core/llama_index/core/base/`, `schema/` | Documents, nodes, LLM and component contracts |
| Composition/registry | `core/indices/registry.py`, `indices/loading.py` | Map persisted type information to index classes and reconstruct objects |
| Storage adapter | `core/storage/storage_context.py` and store modules | Group document/index/vector/property-graph stores and persistence |
| Pipeline/application orchestration | `core/ingestion/pipeline.py` | Transform, deduplicate, cache, upsert, and optionally parallelize documents |
| External adapters | Separate `llama-index-*` packages and LLM/vector integrations | Provider SDKs and backend-specific behavior |

Core code often passes framework models directly across boundaries. This is a deliberate productivity trade-off for a broad integration framework, not evidence of a pure domain/application split.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | [`llama-index-core/llama_index/core/indices/registry.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/llama_index/core/indices/registry.py) maps `IndexStructType` to classes; [`indices/loading.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/llama_index/core/indices/loading.py) selects and constructs the registered class | [`llama-index-core/tests/indices/test_loading.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/tests/indices/test_loading.py), [`llama-index-core/tests/indices/test_loading_graph.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/tests/indices/test_loading_graph.py) | Software Design ch34; Clean Architecture ch20 | A |
| P12 | Adapter, façade, and provider router | [`llama-index-core/llama_index/core/storage/storage_context.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/llama_index/core/storage/storage_context.py) groups interchangeable stores; [`llama-index-core/llama_index/core/llms/custom.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/llama_index/core/llms/custom.py) adapts `complete`/`stream_complete` into chat behavior | [`llama-index-core/tests/storage/test_storage_context.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/tests/storage/test_storage_context.py), [`llama-index-core/tests/llms/test_custom.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/tests/llms/test_custom.py) | Clean Architecture ch19–20; Software Design ch35 | A |
| P15 | Composite, iterator, visitor, and pipelines | [`llama-index-core/llama_index/core/ingestion/pipeline.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/llama_index/core/ingestion/pipeline.py) applies ordered transformations, cache/docstore deduplication, vector upserts, and optional parallel execution | [`llama-index-core/tests/ingestion/test_pipeline.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/tests/ingestion/test_pipeline.py), [`llama-index-core/tests/ingestion/test_cache.py`](https://github.com/run-llama/llama_index/blob/7169bcd0dca2e16aecc8e0247f34e50079d9c0d5/llama-index-core/tests/ingestion/test_cache.py) | Clean Architecture ch18; Software Design ch36/ch39 | A |

## 4. Source Walkthrough

### Index registry and loading

`INDEX_STRUCT_TYPE_TO_INDEX_CLASS` is the explicit registry. `load_indices_from_storage` reads index structures, resolves the type, obtains the class, and constructs the index with the supplied storage context. `load_index_from_storage` rejects zero or multiple matches, keeping ambiguity at the boundary.

### `StorageContext`

`from_defaults` selects in-memory or persisted stores and `persist` writes the document, index, graph, and vector-store components as a group. This is a façade over multiple persistence adapters; callers do not need to coordinate each store manually.

### `CustomLLM` and `IngestionPipeline`

`CustomLLM` turns a small completion implementation into the framework’s LLM contract, including chat and streaming conversion. `IngestionPipeline.run` prepares inputs, applies transformations, consults cache/docstore state, and upserts results. It is an observable sequence of stages, but it is not presented as a transactional workflow.

## 5. Theory Versus Practice

The book patterns recommend stable ports, explicit factories, and composable pipelines. LlamaIndex follows those ideas at integration seams but uses framework-specific Pydantic models and a broad package ecosystem as the common language. This reduces adapter boilerplate and makes new integrations accessible, but it increases the amount of behavior a custom component must understand.

The index registry is intentionally simple and global for core index types. A smaller application should prefer a local registry or direct constructor unless persistence/versioned reconstruction is a real requirement.

## 6. Testing Strategy

- Index-loading tests exercise successful reconstruction, missing stores, and graph/index loading behavior.
- Storage-context tests round-trip store configuration and serialized state.
- Custom LLM tests use a small test subclass to check complete/chat/stream conversion.
- Ingestion tests cover transformations, caching, deduplication, and pipeline execution without requiring every external provider.

The source and tests were inspected at the pinned revision; external vector stores and provider integrations were not run.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Framework models cross core boundaries | Fast integration development and consistent serialization | Map to smaller DTOs when a business domain must remain independent of framework churn |
| Registry-driven persisted loading | Reconstructs many index types from storage | Version and migration behavior must be explicit before persisting class/type names |
| One `StorageContext` façade spans many stores | Callers get one persistence handle and coordinated defaults | Avoid a mega-context when only one repository is needed |
| Optional parallel ingestion | Better throughput for large documents | Ordering, cache keys, and side-effect semantics require tests before enabling multiprocessing |

## 8. Practice Exercise

Use [the registry-plugin exercise](../../python-software-architecture/exercises/registry-plugin.md): define two index implementations, register them by a persisted type, load them through a storage context, and add a transformation pipeline with a fake cache. Test unknown types and ambiguous loads as boundary errors.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `run-llama/llama_index`, `main` |
| Pinned revision | `7169bcd0dca2e16aecc8e0247f34e50079d9c0d5` |
| License | MIT, verified from repository `LICENSE` |
| Python/native boundary | Python core and orchestration; external integration SDK/native runtimes at the perimeter |
| Canonical pattern IDs | P08 (A), P12 (A), P15 (A) |
| Source evidence | Index registry/loading, `StorageContext`, `CustomLLM`, and `IngestionPipeline` |
| Test evidence | Index loading, storage, custom LLM, ingestion, and cache tests |
| Book mapping | Clean Architecture ch18–20; Software Design ch34–36 and ch39 |
| Production compromise | A framework-wide common model and registry are accepted to support a large integration ecosystem |
| Practice exercise | `exercises/registry-plugin.md` |
