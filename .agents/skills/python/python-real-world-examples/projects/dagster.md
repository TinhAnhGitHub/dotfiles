# Dagster

> Repository: [dagster-io/dagster@249fbed](https://github.com/dagster-io/dagster/tree/249fbedf4d81541bf83b8e2727ae2fb6332a243d)
> Default branch: `master`
> Commit: `249fbedf4d81541bf83b8e2727ae2fb6332a243d`
> License: [Apache-2.0](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/LICENSE)
> Domain: Data orchestration, asset/job definitions, execution plans, resources, and retries
> Python/native boundary: The reviewed Dagster core is Python. External storage, process/container launchers, databases, and user code are drivers; native execution is not required for the core orchestration model.
> Evidence level: A for definitions/repository composition, executor strategies, execution-plan state, retry policy, instance persistence, and tests
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/dagster` (read-only pinned checkout)

## 1. Executive Architecture Summary

Dagster separates declarative definitions from execution. `Definitions` collects assets, jobs, schedules, sensors, resources, executors, and loggers, then wraps them in a repository definition. The execution API resolves a job into an `ExecutionPlan`; an executor consumes that plan and emits a stream of typed `DagsterEvent` values.

The active execution object is an explicit state machine. It tracks pending, executable, in-flight, success, failure, skipped, abandoned, and retry states, while executor implementations choose in-process or multiprocess orchestration. `DagsterInstance` owns durable run/event/storage integrations, so the execution engine can report events without hard-coding one persistence mechanism.

```text
User definitions
      │
      ▼
Definitions ── RepositoryDefinition ── JobDefinition / resources / executor
      │                                      │
      ▼                                      ▼
create_execution_plan ────────────────> Executor
                                              │
                                              ▼
                                  ActiveExecution state machine
                                              │
                                              ▼
                                  DagsterEvent / DagsterInstance
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Definition/composition | `dagster/_core/definitions/definitions_class.py`, `repository_definition/`, decorators | Collect and validate user assets/jobs/resources/executors |
| Plan compiler | `dagster/_core/execution/api.py`, `execution/plan/plan.py` | Resolve configuration and dependencies into executable steps |
| Execution state | `dagster/_core/execution/plan/active.py`, `execution/plan/execute_plan.py` | Track step readiness, outputs, failures, retries, and event emission |
| Execution strategies | `dagster/_core/definitions/executor_definition.py`, `_core/executor/` | Construct in-process or multiprocess executors and orchestrate steps |
| Persistence/drivers | `dagster/_core/instance/instance.py`, storage/launcher modules | Store runs/events and launch external processes or services |

Dagster’s definition objects are framework-level models rather than pure business entities. The architecture is still disciplined about construction, plan compilation, execution strategy, resource ownership, and persistence seams.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | [`dagster/_core/definitions/definitions_class.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster/_core/definitions/definitions_class.py) composes definitions and exposes a repository; [`repository_definition/repository_definition.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster/_core/definitions/repository_definition/repository_definition.py) resolves jobs/resources | [`python_modules/dagster/dagster_tests/definitions_tests/test_definitions_class.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/definitions_tests/test_definitions_class.py), [`python_modules/dagster/dagster_tests/definitions_tests/test_definitions.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/definitions_tests/test_definitions.py) | Software Design ch34; Clean Architecture ch20 | A |
| P09 | Strategy, policy, and template method | [`dagster/_core/definitions/executor_definition.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster/_core/definitions/executor_definition.py) defines executor factories/configuration; `_core/executor/base.py` supplies a common execute/retry contract; in-process and multiprocess implementations vary the orchestration strategy | [`python_modules/dagster/dagster_tests/execution_tests/engine_tests/test_jobs.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/execution_tests/engine_tests/test_jobs.py), [`python_modules/dagster/dagster_tests/execution_tests/engine_tests/test_multiprocessing.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/execution_tests/engine_tests/test_multiprocessing.py) | Software Design ch33; Clean Architecture ch15 | A |
| P13 | State machine, workflow, and saga | [`dagster/_core/execution/plan/active.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster/_core/execution/plan/active.py) tracks pending/in-flight/terminal/retry state and enforces completion on context exit; `execution/plan/execute_plan.py` emits failure/retry events | [`python_modules/dagster/dagster_tests/execution_tests/execution_plan_tests/test_execution_plan.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/execution_tests/execution_plan_tests/test_execution_plan.py), [`python_modules/dagster/dagster_tests/execution_tests/misc_execution_tests/test_retries.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/execution_tests/misc_execution_tests/test_retries.py) | Clean Architecture ch18/ch24; Software Design ch38 | A |
| P16 | Concurrency, scheduling, and resource lifecycle | [`dagster/_core/execution/plan/plan.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster/_core/execution/plan/plan.py) builds topologically ordered steps; in-process/multiprocess executors implement concurrency; [`dagster/_core/instance/instance.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster/_core/instance/instance.py) registers storages and launchers with instance ownership | [`python_modules/dagster/dagster_tests/execution_tests/execution_plan_tests/test_execution_plan.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/execution_tests/execution_plan_tests/test_execution_plan.py), [`python_modules/dagster/dagster_tests/execution_tests/misc_execution_tests/test_instance_concurrency_context.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/execution_tests/misc_execution_tests/test_instance_concurrency_context.py), [`python_modules/dagster/dagster_tests/core_tests/instance_tests/test_instance.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/core_tests/instance_tests/test_instance.py) | Software Design ch41; Clean Architecture ch23 | A |
| P17 | Testing seams, fitness tests, and migration boundaries | `Definitions.validate_loadable` delegates to repository validation; `DagsterInstance.ephemeral` and `instance_for_test` create isolated execution/storage boundaries for tests | [`python_modules/dagster/dagster_tests/definitions_tests/test_definitions_class.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/definitions_tests/test_definitions_class.py), [`python_modules/dagster/dagster_tests/core_tests/instance_tests/test_instance.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/core_tests/instance_tests/test_instance.py), [`python_modules/dagster/dagster_tests/execution_tests/misc_execution_tests/test_execute_in_process.py`](https://github.com/dagster-io/dagster/blob/249fbedf4d81541bf83b8e2727ae2fb6332a243d/python_modules/dagster/dagster_tests/execution_tests/misc_execution_tests/test_execute_in_process.py) | Clean Architecture ch21/ch24–25; Software Design ch26–27 | A |

## 4. Source Walkthrough

### `Definitions` and repository resolution

`Definitions` accepts assets, jobs, schedules, sensors, resources, an executor, loggers, and metadata. `get_repository_def` wraps these inputs in a cached `RepositoryDefinition`; `validate_loadable` checks name/key conflicts, resolvability, resource requirements, and partition mappings. The wrapper gives tools a stable loadable composition root.

### Plan and executor seams

`create_execution_plan` builds a topological step graph from a `JobDefinition`. `ExecutorDefinition` stores config, requirements, and a creation function; its decorators produce named executor definitions. `Executor` then exposes `execute` and retry policy, with in-process and multiprocess implementations supplying different orchestration strategies.

### Active execution and instance

`ActiveExecution` maintains pending, executable, in-flight, terminal, and retry buckets and acts as a context manager that rejects incomplete/unknown execution on exit. `execute_plan.py` converts step errors into retry or failure events. `DagsterInstance` registers run/event/storage/launcher components and provides ephemeral/local test instances.

## 5. Theory Versus Practice

Dagster makes the architecture pattern unusually explicit: definitions are composed first, a plan is compiled, an executor interprets the plan, and events flow to an instance. The framework still couples definitions, config resolution, execution state, and event semantics because they must agree on step identity and resumability.

Retries are represented as events and retry state rather than hidden recursive calls. That supports reexecution and observability, but it means every executor and storage boundary must preserve enough metadata to resume safely. A small workflow can use an enum/table and one transaction; Dagster’s machinery is justified by dynamic graphs, distributed execution, and operational introspection.

## 6. Testing Strategy

- Definitions tests validate composition, asset/job resolution, and loadability.
- Execution-plan tests assert topological order, active state transitions, skips, failures, and retries.
- Engine tests exercise in-process and multiprocess executor behavior.
- Retry tests assert retry events, limits, reexecution, and success after a failed attempt.
- Instance tests exercise ephemeral/local storage and persisted run boundaries.

The source and tests were inspected at the pinned revision. Full daemon, database, and multiprocess suites were not executed in this pass.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| One `Definitions` object gathers many definition types | Tools get one loadable composition root and validation entry point | Avoid a single global container when independent bounded contexts need separate ownership |
| Plan compilation precedes execution | Enables scheduling, subsets, reexecution, and validation before side effects | Adds an intermediate model and serialization cost for tiny workflows |
| Executors emit event streams instead of returning only results | Observability, retries, cancellation, and UI integration become first-class | Event schemas and storage become compatibility contracts |
| Instance registers many storage/launcher resources | Deployments can swap persistence and process drivers | Keep lifetimes explicit; do not make a general service depend on ambient global instance state |

## 8. Practice Exercise

Use [the workflow-state exercise](../../python-software-architecture/exercises/workflow-state.md) and [the event-driven-training exercise](../../python-software-architecture/exercises/event-driven-training.md): define a small job graph, compile it into executable steps, run in-process or multiprocess-style strategies, emit retry/failure events, and validate complete/unknown state on context exit. Add an ephemeral fake instance for tests.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `dagster-io/dagster`, `master` |
| Pinned revision | `249fbedf4d81541bf83b8e2727ae2fb6332a243d` |
| License | Apache-2.0, verified from repository `LICENSE` |
| Python/native boundary | Python definitions, plan, execution, and instance core; external storage/process/user-code drivers |
| Canonical pattern IDs | P08 (A), P09 (A), P13 (A), P16 (A), P17 (A) |
| Source evidence | Definitions/repository, executor definition/base, plan/active state, retry/event execution, instance |
| Test evidence | Definitions, plan state, retry, engine, concurrency, and instance tests |
| Book mapping | Clean Architecture ch15, ch18, ch20–21, ch23–25; Software Design ch33–34, ch38, and ch41 |
| Production compromise | Plan/event/instance machinery is intentionally broad to support distributed execution, reexecution, and observability |
| Practice exercise | `exercises/workflow-state.md`, `exercises/event-driven-training.md` |
