# Hugging Face Evaluate

> Repository: [huggingface/evaluate](https://github.com/huggingface/evaluate/tree/a7dd338386a4fae9a1767e05eb9ef9479513d9e8)
> Default branch: `main`
> Commit: `a7dd338386a4fae9a1767e05eb9ef9479513d9e8`
> License: Apache-2.0 (`LICENSE`)
> Domain: Reusable evaluation modules, metrics, comparisons, measurements, and task evaluators
> Python version: `>=3.8.0` (`setup.py`)
> Architecture style: Dynamic-module factory plus Arrow-backed, process-coordinated evaluation pipeline
> Evidence level: A for P06, P08, P12, P15, P16, and P17; no README-only claims are used

## 1. Executive Architecture Summary

### High-Level Architectural Diagram

The problem is to let a metric or evaluator be authored locally, downloaded from
the Hub, or reused from a cache while presenting one `load`/`compute` API. The
second problem is safe aggregation when several processes contribute examples.
Evaluate solves these with a dynamic-module boundary and an Arrow file lifecycle:

```text
evaluate.load / evaluation_module_factory
    -> local | Hub | cached module factory
    -> hashed importable module in the HF dynamic-module cache
    -> EvaluationModule (metric/comparison/measurement)
    -> ArrowWriter + per-process cache files and rendezvous locks
    -> process 0 finalizes and computes the result

evaluator(task)
    -> task-specific Evaluator
    -> model/pipeline adapter + EvaluationModule
```

Python owns module discovery, validation, orchestration, and distributed file
coordination. Arrow/PyArrow and optional ML frameworks provide the data and model
operations; this checkout has no repository-owned C++/CUDA hot path in the
inspected architecture.

## 2. Layering & Boundary Discipline

### Inward Dependency Rule Audit

`evaluation_module_factory` and `EvaluationModule` form the stable application
surface. Local scripts, Hub revisions, and cached hashes are translated into an
importable module before metric code is invoked. `EvaluationModule` owns input
validation, example writing, process coordination, and the `_compute` extension
point. The evaluator package adds a task/model pipeline without making each metric
know how a model pipeline is constructed.

The boundary is intentionally dynamic: Python code is copied into a cache and
imported at runtime. This improves extension and reproducibility, but it is not the
same isolation as a separate worker or a sandboxed plugin process.

## 3. Macro Architectural Patterns in Action

| ID | Problem solved | Code modules and roles | Source / test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P06 | Give metrics a stable extension contract independent of storage/aggregation | `EvaluationModule` and its `_compute` hook | [module.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/module.py), [test_metric.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_metric.py) | Clean Architecture ch14, ch16; Architecture Patterns ch13 | A |
| P08 | Resolve local, Hub, and cached metric implementations through one loader | `LocalEvaluationModuleFactory`, `HubEvaluationModuleFactory`, `CachedEvaluationModuleFactory` | [loading.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/loading.py), [test_load.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_load.py) | Software Design ch34; Architecture Patterns ch13 | A |
| P12 | Normalize script acquisition and evaluator/model interfaces | dynamic-module cache, `Evaluator`, and pipeline-facing APIs | [evaluator/base.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/evaluator/base.py), [loading.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/loading.py) | Software Design ch35; Clean Architecture ch19–20 | A |
| P15 | Compose task-specific prediction processing with a metric | `Evaluator`, task dispatch, model/pipeline processing | [evaluator/__init__.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/evaluator/__init__.py), [evaluator/base.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/evaluator/base.py), [test_evaluator.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_evaluator.py) | Software Design ch36; Clean Architecture ch18 | A |
| P16 | Coordinate multi-process writes, finalization, and cleanup | cache files, `FileFreeLock`, rendezvous, `_finalize` | [module.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/module.py), [test_metric.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_metric.py) | Software Design ch41; Architecture Patterns ch06 | A |
| P17 | Test dynamic loading, fake pipelines, and distributed metric seams | module-factory tests, dummy metrics, multiprocessing helpers | [test_load.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_load.py), [test_metric.py](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_metric.py) | Clean Architecture ch21 | A |

P01–P05, P07, P09–P11, P13–P14 are not asserted as primary patterns here. In
particular, the Arrow files coordinate an evaluation lifecycle but are not a
general Unit of Work or durable message bus.

## 4. Meso Tactical Design Patterns in Action

### P06 — Port and Extension Contract

**Problem.** A metric author should implement the metric calculation without
rewriting argument validation, Arrow writing, process rendezvous, or cleanup.
Callers should be able to use any metric through the same `compute` and
`add_batch` surface.

**Code modules and roles.** `EvaluationModule` in `src/evaluate/module.py` owns
the public lifecycle. Its constructor validates process parameters and creates
the experiment/cache state. `add_batch` writes normalized examples; subclasses
implement `_compute`. `tests/test_metric.py` defines `DummyMetric` as a concrete
implementation of that contract.

**How this expresses P06.** `EvaluationModule` is the port and `_compute` is the
domain-specific plug-in point. The base class keeps cross-cutting concerns outside
the metric algorithm. It is a template-like abstract class rather than a pure
structural `Protocol`, but the architectural role is the same: depend on the
stable capability, not a particular metric.

**Minimal standard-library sketch.**

```python
from abc import ABC, abstractmethod

class Metric(ABC):
    def compute(self, rows):
        return self._compute(list(rows))

    @abstractmethod
    def _compute(self, rows): ...
```

**Tests and evidence.** `tests/test_metric.py` covers direct compute, batches,
in-memory settings, and multiprocessing helpers. The base/extension relationship
and its tests make this A evidence.

**Compromise and simpler alternative.** The base class is more machinery than a
pure function. For a local one-off metric, `def score(predictions, references)` is
clearer. Use this contract when metrics need shared storage, distributed
aggregation, or a reusable ecosystem.

### P08 — Dynamic Module Factory and Registry-Like Discovery

**Problem.** Community metrics need a stable loader even though their code may be
local, hosted on the Hub, or already cached. Loading every script eagerly would
also make startup and optional dependencies expensive.

**Code modules and roles.** `init_dynamic_modules` establishes the HF module cache.
`import_main_class` finds the concrete `EvaluationModule`. The local, Hub, and
cached factory classes copy scripts/imports/resources into a hash-addressed module
namespace, invalidate import caches, and return an `ImportableModule`.

**How this expresses P08.** The factory selects a provider and the hashed module
directory acts as a persistent registry/discovery result. The public
`evaluation_module_factory` does not care whether the implementation came from a
local path or a Hub revision. Unlike an in-process class dictionary, the registry
also records code identity through the hash/cache path.

**Minimal sketch.**

```python
modules = {"accuracy": "metrics.accuracy:Accuracy"}

def load(name):
    module_name, symbol = modules[name].split(":")
    return getattr(__import__(module_name, fromlist=[symbol]), symbol)()
```

**Tests and evidence.** `tests/test_load.py` tests local, Hub, external/internal
imports, cached factories, offline fallback, and hash-related behavior. This is A
evidence because the factory branches and their tests are both directly inspected.

**Compromise and simpler alternative.** Runtime import of downloaded Python is an
extensibility and supply-chain boundary. Hashing and revisions help reproducibility
but do not make untrusted code safe. For a controlled service, package metrics in
the application and use an explicit constructor map; choose dynamic loading only
when user/community modules are required.

### P12 — Adapter and Evaluator Provider Boundary

**Problem.** A task evaluator needs a model/pipeline, prediction post-processing,
and a metric, but each task has different input and output conventions. The metric
should not know whether predictions came from a Transformers pipeline, a dummy
test object, or another provider.

**Code modules and roles.** `Evaluator` in `src/evaluate/evaluator/base.py` is the
task-facing adapter. Its `predictions_processor` contract turns model output into
metric inputs. `SUPPORTED_EVALUATOR_TASKS` and `evaluator(task)` route a task name
to the matching evaluator class. `loading.py` adapts source scripts into a module
that the metric API can consume.

**How this expresses P12.** The evaluator translates provider-specific model output
into the canonical `(predictions, references)` vocabulary. It is both an adapter
and a small façade: callers get one `compute` path while task-specific differences
remain at the edge.

**Minimal sketch.**

```python
class Evaluator:
    def __init__(self, model, metric): self.model, self.metric = model, metric
    def run(self, inputs):
        predictions = [self.model(x) for x in inputs]
        return self.metric.compute(predictions=predictions)
```

**Tests and evidence.** `tests/test_evaluator.py` uses dummy pipeline classes and
checks task dispatch/device behavior. The source-level routing and test doubles
support A evidence.

**Compromise and simpler alternative.** A task registry can grow into a matrix of
special cases. If one model and one metric are stable, call them directly and
keep only a small conversion function.

### P15 — Evaluation Pipeline and Composable Processing

**Problem.** Evaluation is a sequence: obtain examples, run a model, convert
predictions, feed a metric, and report results. Baking all steps into each metric
duplicates task logic.

**Code modules and roles.** The evaluator package provides task selection and a
base evaluator; concrete evaluators specialize prediction processing. The module
layer supplies the final metric operation. This is a pipeline/composite at the
application level rather than an iterator-heavy data structure.

**How this expresses P15.** Each stage has one responsibility and hands a
well-defined value to the next stage. A task evaluator composes a model adapter
with a metric port. The abstraction is useful when many tasks share stages but
need different conversion policies.

**Minimal sketch.**

```python
def pipeline(items, *steps):
    for step in steps:
        items = step(items)
    return items
```

**Tests and evidence.** `tests/test_evaluator.py` exercises the evaluator seam with
fakes; `tests/test_metric.py` validates the terminal metric contract. The claim is
A for this pipeline boundary.

**Compromise and simpler alternative.** A configurable pipeline adds indirection
and makes stack traces less obvious. For one evaluation task, a straight-line
function may be the best design.

### P16 — Process Coordination and Resource Lifecycle

**Problem.** Several workers need to contribute examples without corrupting one
another's files, and only one process should aggregate and delete the intermediate
artifacts.

**Code modules and roles.** `FileFreeLock` detects lock availability. The module
creates per-process Arrow cache files, gathers all files under a rendezvous lock,
and `_finalize` controls writer closure and cleanup. `compute` makes process 0 the
result-producing owner; other processes return after contributing.

**How this expresses P16.** The cache files are scoped resources and the locks are
the coordination boundary. This is a deliberately narrow lifecycle protocol, not
a general distributed scheduler.

**Minimal sketch.**

```python
def compute_distributed(workers):
    files = [worker.write_private_file() for worker in workers]
    with rendezvous_lock(files):
        return aggregate(files)
```

**Tests and evidence.** `tests/test_metric.py` exercises multiprocessing and
distributed settings; module tests cover in-memory constraints. This is A evidence
for the documented lifecycle, with the usual shared-filesystem limitation.

**Compromise and simpler alternative.** Files and locks avoid requiring a broker,
but assume a working shared filesystem and coordinated processes. A single-process
metric should use an in-memory list; a multi-host production system may need an
object store or job framework with explicit retry semantics.

### P17 — Testing Dynamic Boundaries

**Problem.** A metric framework can appear correct on the happy path while failing
when a script is missing, offline cache selection is needed, a pipeline returns an
unexpected shape, or a worker cannot join.

**Code modules and roles.** `tests/test_load.py` constructs factory scenarios and
temporary modules. `tests/test_metric.py` supplies a dummy metric and worker
helpers. `tests/test_evaluator.py` uses fake pipelines and checks dispatch.

**How this expresses P17.** Tests are organized around seams: source selection,
module import, metric extension, process coordination, and model conversion. The
fakes make those boundaries testable without real Hub downloads or model weights.

**Minimal sketch.**

```python
def test_evaluator_uses_fake_model():
    assert Evaluator(lambda x: x + 1, FakeMetric()).run([1]) == {"score": 2}
```

**Compromise and simpler alternative.** The repository needs many fixtures because
the extension surface is dynamic. A small application can begin with one contract
test per evaluator and one integration test for the selected metric, then add
offline/failure tests as the boundary expands.

## 5. Micro Code Craftsmanship & Idioms

- Hash-addressed dynamic modules make a source revision part of the runtime identity.
- Pydantic validation and Arrow writers keep the wire/storage shape explicit at the
  base-class boundary.
- Optional imports preserve a lightweight core while deferring dependency failures.
- Lock acquisition and cleanup are visible in the lifecycle instead of being left
  to garbage collection.

## 6. Pragmatic Compromises & Architectural Trade-offs

### Theoretical ideal

The book-aligned ideal is an injected metric port, an explicit composition root,
provider adapters at the edge, and a transaction-like lifecycle around shared
evaluation data.

### Production implementation

Evaluate uses dynamic Python module loading, a global-ish HF cache namespace,
process-specific Arrow files, file locks, process-0 aggregation, and task-specific
evaluator dispatch.

### Difference and rationale

The design optimizes for a community catalog and reproducible reuse rather than
strict compile-time dependency control. Deferred imports and cache hashes lower
startup cost and allow offline reuse, while shared files avoid introducing a
message broker. The costs are supply-chain risk, filesystem assumptions, and
deferred runtime failures. Do not copy the dynamic module factory for untrusted
plugins or for a small fixed metric library.

## 7. Curated File Tours (Annotated Walkthroughs)

1. [`src/evaluate/loading.py`](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/loading.py): dynamic cache initialization, local/Hub/cached factories, and importable module creation.
2. [`src/evaluate/module.py`](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/module.py): metric contract, Arrow writers, locks, rendezvous, finalization, and `compute`.
3. [`src/evaluate/evaluator/base.py`](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/evaluator/base.py): evaluator/processor adapter.
4. [`src/evaluate/evaluator/__init__.py`](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/src/evaluate/evaluator/__init__.py): task-to-evaluator dispatch.
5. [`tests/test_load.py`](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_load.py): source and cache factory verification.
6. [`tests/test_metric.py`](https://github.com/huggingface/evaluate/blob/a7dd338386a4fae9a1767e05eb9ef9479513d9e8/tests/test_metric.py): dummy metric, compute, and multiprocessing boundary.

## 8. Test Harness & Verification Strategy

- `tests/test_load.py`: local/Hub/cached factory behavior, imports, and offline fallback.
- `tests/test_metric.py`: concrete metric behavior, batches, cache files, and
  distributed workers.
- `tests/test_evaluator.py`: fake pipelines, evaluator dispatch, and device paths.
- `tests/test_evaluation_suite.py`: higher-level suite composition where applicable.

The suite proves the selected seams at the pinned revision; it does not prove that
every community metric script or every Hub failure mode behaves identically.

## Practice Exercise

Implement a standard-library `Metric` base class, a hash-addressed local module
loader, and a task evaluator that adapts a fake model into metric inputs. Add tests
for duplicate cache identities, missing modules, invalid arguments, a fake
multi-process contribution directory, process-0 aggregation, and evaluator output
conversion. Compare your explicit loader with Evaluate's dynamic factory and write
down which trust and scale assumptions you would reject in production.

## Research Limitations

Only the pinned checkout and its source/tests were inspected. README descriptions,
uninspected Hub modules, and optional framework integrations are not treated as
authoritative evidence.
