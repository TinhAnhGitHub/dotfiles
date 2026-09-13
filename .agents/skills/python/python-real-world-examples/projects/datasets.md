# Hugging Face Datasets

> Repository: [huggingface/datasets](https://github.com/huggingface/datasets/tree/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06)
> Default branch: `main`
> Commit: `d336dcb84cdd6647a685cf4c9e0e8c26cc105b06`
> License: Apache-2.0 (`LICENSE`)
> Domain: Dataset discovery, download, Arrow-backed transformation, and streaming
> Python version: `>=3.10.0` (`setup.py`)
> Architecture style: Factory/registry dispatch around a builder pipeline, with filesystem/Hub/format adapters
> Evidence level: A for the mapped patterns; B for the `DatasetBuilder` interface; no README-only claims are used

## 1. Executive Architecture Summary

### High-Level Architectural Diagram

The central problem is to give callers one dataset API while accepting many origins
(local files, packaged formats, the Hub, cached modules), storage systems, file
formats, and execution modes (materialized or streaming). The repository separates
selection from execution:

```text
load_dataset / dataset_module_factory
    -> module factory: local | packaged | Hub | cached
    -> DatasetBuilder: cache, lock, download_and_prepare
    -> DownloadManager / filesystem adapters
    -> Apache Arrow / PyArrow table representation
    -> Dataset or IterableDataset
    -> Python / NumPy / Pandas / Torch / TF / JAX format adapters
```

Python owns discovery, configuration, caching, iteration, and public orchestration.
PyArrow/Apache Arrow and optional array frameworks provide the native table and
conversion work. This checkout does not contain a repository-owned C++/CUDA hot
path in the areas studied; the native boundary is dependency-facing.

## 2. Layering & Boundary Discipline

### Inward Dependency Rule Audit

`datasets.load` is the composition-facing boundary. It selects a module factory
and returns a builder/module abstraction rather than making callers understand
Hub URLs, file extensions, or cache layout. `DatasetBuilder` owns preparation and
its output contract. `DownloadManager` and streaming extensions sit at the edge
where local/remote filesystem behavior is translated. Formatting is another edge:
the internal Arrow/Python representation is projected into optional user-facing
frameworks.

This is not strict Clean Architecture. Discovery and cache policy are intentionally
centralized in `load.py`, and streaming uses runtime patching of imported modules.
Those choices make the library practical across many data sources but mean that
the boundary is partly dynamic rather than enforced only by imports or types.

## 3. Macro Architectural Patterns in Action

| ID | Problem solved | Code modules and roles | Source / test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P06 | Keep dataset construction behind a stable builder contract | `DatasetBuilder` and concrete builders in `src/datasets/builder.py` | [builder.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/builder.py), [test_builder.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/tests/test_builder.py) | Clean Architecture ch14, ch16; Architecture Patterns ch13 | B |
| P08 | Select packaged, local, Hub, or cached implementations without changing the public loader | `_DatasetModuleFactory` family, `_PACKAGED_DATASETS_MODULES`, formatter registry | [load.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/load.py), [formatting/__init__.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/formatting/__init__.py), [test_load.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/tests/test_load.py) | Software Design ch34; Architecture Patterns ch13 | A |
| P12 | Normalize local, remote, cached, and framework-specific I/O | `DownloadManager`, filesystem handling, formatter registrations | [download_manager.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/download/download_manager.py), [test_download_manager.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/tests/test_download_manager.py) | Software Design ch35; Clean Architecture ch19–20 | A |
| P15 | Compose lazy, shardable, resumable data transformations | `_BaseExamplesIterable` and `IterableDataset` wrappers | [iterable_dataset.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/iterable_dataset.py), [test_iterable_dataset.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/tests/test_iterable_dataset.py) | Software Design ch36; Clean Architecture ch18 | A |
| P16 | Avoid duplicate preparation and manage cache/resource lifecycle | Builder cache directories, lock files, download/extract lifecycle | [builder.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/builder.py), [test_builder.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/tests/test_builder.py) | Software Design ch41; Architecture Patterns ch06 | A |
| P17 | Test dynamic source selection, concurrency, streaming, and format seams | Factory fixtures, multiprocessing preparation tests, iterable state tests | [test_load.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/tests/test_load.py), [test_iterable_dataset.py](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/tests/test_iterable_dataset.py) | Clean Architecture ch21 | A |

P01–P05, P07, P09–P11, P13–P14 are not claimed as authoritative in this dossier:
the repository has configuration and service-like code, but the inspected source
and tests do not establish those book patterns as its primary architecture.

## 4. Meso Tactical Design Patterns in Action

### P08 — Factory, Registry, and Plugin Architecture

**Problem.** A caller may provide a Hub identifier, a local data directory, a
packaged file format, or a cached module. Hard-coding one branch in every public
API would make adding a source format a breaking change.

**Code modules and roles.** `dataset_module_factory` in `src/datasets/load.py`
coordinates `_DatasetModuleFactory` implementations. `LocalDatasetModuleFactory`
infers a builder from local files and metadata; `PackagedDatasetModuleFactory`
selects generic CSV/JSON/Parquet-style loaders; `CachedDatasetModuleFactory`
recovers an already materialized module. `import_main_class` discovers a concrete
`DatasetBuilder` subclass. Separately, `src/datasets/formatting/__init__.py`
keeps `_FORMAT_TYPES` and registers formatters for Python, Arrow, NumPy, Pandas,
and optional frameworks.

**How this expresses P08.** The factory is the selection policy; the dictionaries
are registries; the builder class is the product. The public loader depends on the
factory result, not on each concrete source. Registration is mostly explicit in
the package, while user/module discovery is dynamic import and metadata-driven.

**Minimal standard-library sketch.**

```python
builders = {"csv": CsvBuilder, "json": JsonBuilder}

def choose(kind: str):
    try:
        return builders[kind]()
    except KeyError as exc:
        raise ValueError(f"unsupported dataset kind: {kind}") from exc
```

**Tests and evidence.** `tests/test_load.py` exercises local, packaged, Hub, and
cached module factories, including metadata configurations. Formatter behavior is
also covered by the packaged-module tests. This is A evidence because both the
selection implementation and targeted tests are present.

**Compromise and simpler alternative.** Dynamic discovery supports community
formats but increases import-time behavior, cache invalidation, and error surface.
For a small application, a single `dict[str, Callable]` constructed in the
composition root is easier to reason about. Use this registry shape when new
formats or remote modules are a real extension requirement.

### P12 — Adapter and Provider Router

**Problem.** Downloading and extracting data should not require each builder to
know whether a path is local, cached, remote, archived, or backed by a particular
filesystem implementation. Likewise, a caller wants `with_format("torch")`-style
behavior without coupling the dataset core to every optional framework.

**Code modules and roles.** `DownloadManager` wraps download, extraction, archive
iteration, checksum, and cache operations. `dataset_module_factory` translates
source metadata into a module object. The formatter registry turns the internal
dataset into framework-specific views. `streaming.py` extends module/builder
behavior so file and reader operations can work against streamable filesystems.

**How this expresses P12.** These objects translate an external vocabulary (URLs,
archives, filesystem paths, NumPy/Pandas/Torch calls) into the core builder/Arrow
vocabulary. The adapter is deliberately broad: it is a normalization façade over
several provider-specific operations, not merely a one-method interface wrapper.

**Minimal sketch.**

```python
class Storage:
    def read(self, name: str) -> bytes: ...

class DatasetLoader:
    def __init__(self, storage: Storage):
        self.storage = storage

    def rows(self, name: str):
        return decode_rows(self.storage.read(name))
```

**Tests and evidence.** `tests/test_download_manager.py`, streaming download
tests, filesystem tests, and packaged-module tests exercise the boundary. The
source and tests support A evidence.

**Compromise and simpler alternative.** One manager centralizes policy and makes
remote behavior consistent, but it can become a large façade with many optional
features. If a program has one storage backend, inject a small `read_bytes`
function instead of reproducing the full manager.

### P15 — Iterator, Composite, and Data Pipelines

**Problem.** Streaming datasets cannot load all rows into memory, must support
sharding and worker reshaping, and often need to resume after a checkpoint. A
single eager list pipeline would lose those properties.

**Code modules and roles.** `_BaseExamplesIterable` defines the iterable/state
contract. `ExamplesIterable`, `ArrowExamplesIterable`, and wrapper iterables
implement concrete sources and transformations. `IterableDataset` composes those
objects behind map/filter/shard/batch-style operations. State dictionaries capture
position and shard information for resumption.

**How this expresses P15.** Each wrapper is an iterator node whose output becomes
the input of another node: that is a composite pipeline. The consumer sees the
iterator protocol while the source controls laziness and state. The pattern is
valuable here because the operation graph remains cheap until iteration.

**Minimal sketch.**

```python
class Map:
    def __init__(self, source, fn): self.source, self.fn = source, fn
    def __iter__(self):
        for item in self.source:
            yield self.fn(item)
```

**Tests and evidence.** `tests/test_iterable_dataset.py` checks map/filter/shard
behavior and explicitly verifies `state_dict`/`load_state_dict` resumption for
ordinary and Arrow iterables. That makes the pipeline claim A evidence.

**Compromise and simpler alternative.** Stateful lazy wrappers complicate
debugging and exact replay. For a bounded dataset, a list comprehension or an
eager dataframe is simpler and often faster. Use the iterable graph for large,
remote, or resumable data rather than by default.

### P16 — Concurrency, Scheduling, and Resource Lifecycle

**Problem.** Multiple processes may prepare the same dataset concurrently. Without
a shared cache key and lock, they duplicate downloads or observe half-written
Arrow output.

**Code modules and roles.** `DatasetBuilder` computes cache/output locations and
uses lock files around preparation. `DownloadManager` controls cached downloads,
extraction, and archive handles. `download_and_prepare` is the lifecycle boundary
that creates the prepared artifact.

**How this expresses P16.** The lock is a cross-process coordination primitive and
the builder is the resource owner. The architecture does not turn preparation
into a general scheduler; it protects a narrowly scoped critical section.

**Minimal sketch.**

```python
with file_lock(cache_key):
    if not artifact_exists(cache_key):
        build_artifact(cache_key)
```

**Tests and evidence.** `BuilderTest.test_concurrent_download_and_prepare` uses
multiple processes and checks the resulting artifact; builder tests also inspect
prepared Arrow output and dataset metadata. This is A evidence.

**Compromise and simpler alternative.** File locks work on a shared filesystem
but do not replace a distributed job scheduler or object-store transaction. For a
single process, a normal in-memory lock or no lock is less operationally costly.

### P17 — Testing Seams and Architecture Fitness

**Problem.** Dynamic import, optional dependencies, remote source selection, and
streaming state can fail only at runtime. Unit tests need to exercise these seams
without requiring every external service.

**Code modules and roles.** Factory tests construct temporary/local modules and
exercise cached/packaged branches. Builder tests validate output contracts and
concurrent preparation. Iterable tests use deterministic sources and checkpoints.
Packaged-module tests inject malformed and format-specific data.

**How this expresses P17.** The test suite treats factory choice, cache output,
resume state, and format conversion as architectural contracts. It is more than
line coverage: each test pins a boundary that could otherwise be hidden behind a
convenient `load_dataset` call.

**Minimal sketch.**

```python
def test_loader_uses_fake_storage():
    loader = DatasetLoader(FakeStorage({"x": b"..."}))
    assert list(loader.rows("x")) == expected_rows
```

**Compromise and simpler alternative.** The repository needs a broad matrix of
fixtures because its extension surface is broad. A smaller application can start
with one contract test per adapter and a few end-to-end tests, then add failure
injection when concurrency or remote inputs become important.

## 5. Micro Code Craftsmanship & Idioms

- Type hints and abstract builder methods describe the core contract, while
  metadata dictionaries preserve compatibility with many dataset shapes.
- Lazy imports keep optional framework dependencies out of the base path.
- Cache keys, lock files, and dataset metadata make preparation repeatable rather
  than relying on process-local state.
- Runtime streaming patches are powerful but should be isolated and documented;
  they are harder to inspect than an explicit adapter object.

## 6. Pragmatic Compromises & Architectural Trade-offs

### Theoretical ideal

The book-aligned ideal would put a stable port around source loading, inject one
implementation at the composition root, keep transformation nodes independent of
storage, and make concurrency/resource ownership explicit.

### Production implementation

Datasets uses a central, metadata-aware factory; global-ish format registrations;
dynamic module imports; filesystem/cache locks; and runtime patching for streaming.
Arrow is the practical shared representation, while optional framework adapters
are loaded only when needed.

### Difference and rationale

The library optimizes for ecosystem breadth and zero-friction loading. Explicitly
injecting every provider would make the public API cumbersome; dynamic factories
let a new file format or Hub module participate without changing every caller.
The cost is import complexity, deferred failures, and cache semantics. Do not use
this architecture for a small fixed ETL script unless those extension and scale
requirements exist.

## 7. Curated File Tours (Annotated Walkthroughs)

1. [`src/datasets/load.py`](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/load.py): factory dispatch, local/packaged/Hub/cached module creation, and dynamic builder discovery.
2. [`src/datasets/builder.py`](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/builder.py): cache paths, locks, builder contract, and preparation lifecycle.
3. [`src/datasets/download/download_manager.py`](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/download/download_manager.py): download/extract/archive/cache façade.
4. [`src/datasets/streaming.py`](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/streaming.py): streaming adaptation through patched filesystem and reader operations.
5. [`src/datasets/iterable_dataset.py`](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/iterable_dataset.py): lazy iterable nodes and resumable state.
6. [`src/datasets/formatting/__init__.py`](https://github.com/huggingface/datasets/blob/d336dcb84cdd6647a685cf4c9e0e8c26cc105b06/src/datasets/formatting/__init__.py): formatter registry and optional framework boundary.

## 8. Test Harness & Verification Strategy

- `tests/test_load.py`: local, packaged, Hub, cached, and metadata/config factory
  cases.
- `tests/test_builder.py`: prepared Arrow output, metadata, streaming, and
  multiprocessing concurrency.
- `tests/test_iterable_dataset.py`: pipeline behavior, sharding, and checkpoint
  resume.
- `tests/test_download_manager.py` and streaming/filesystem tests: download and
  filesystem seams.
- `tests/packaged_modules/`: malformed input and format-specific adapter behavior.

These tests validate the important architecture boundaries without claiming that
every optional provider or remote service is covered.

## Practice Exercise

Build a small standard-library registry with `CsvBuilder` and `JsonBuilder`, a
`Storage` protocol, and a `DatasetPipeline` iterator. Add tests for duplicate
registration, missing providers, a fake storage backend, lazy map/filter, and
resuming from a serialized item index. Then compare your explicit composition root
with Datasets' dynamic factory and list which production requirements would justify
each additional layer.

## Research Limitations

The dossier is based only on the pinned checkout and its repository tests. It does
not treat README architecture statements as proof, and it does not claim that
uninspected optional integrations implement the same patterns.
