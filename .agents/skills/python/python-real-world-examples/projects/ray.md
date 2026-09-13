# Project Case Study: Ray

> **Repository**: [ray-project/ray](https://github.com/ray-project/ray/tree/44e93d309792bd714ab286044adc5fa6bea99735)  
> **Checked-out commit**: 44e93d309792bd714ab286044adc5fa6bea99735  
> **License**: Apache-2.0 (LICENSE)  
> **Domain**: Distributed task/actor runtime, object store, scheduling, placement, failure recovery, and Python-native execution  
> **Python**: >=3.10; setup.py classifiers include 3.10 through 3.14  
> **Architecture style**: Python façade and client-side control plane over native CoreWorker, Raylet, GCS, and object-store services  
> **Evidence level**: A/B claims below are tied to source and tests. C findings are explicitly not authoritative pattern claims.

## 1. Architecture Summary

Ray makes ordinary Python functions and classes into distributed tasks and actors. The Python API captures a function/class descriptor, options, runtime environment, placement strategy, and serialized arguments. At invocation time it submits the request to a native CoreWorker, which communicates with Raylet/GCS/object-store services and eventually returns ObjectRefs.

~~~text
Python driver
  ray.init / ray.remote / placement_group
          |
          v
RemoteFunction / ActorClass / ObjectRef façade
          |
          v
native CoreWorker
  +--> Raylet scheduler and worker pool
  +--> GCS metadata/actor/placement managers
  +--> object store and spilling workers
          |
          v
Python worker executes user code
~~~

Ray’s useful boundary is not a conventional application “repository.” It is a durable runtime protocol: Python descriptions and object references must remain meaningful across processes, nodes, retries, actor restarts, and graceful shutdown.

## 2. Python Boundary

### Python control and orchestration plane

- python/ray/remote_function.py implements the RemoteFunction descriptor, runtime-environment handling, tracing injection, argument flattening, retry options, placement strategy, and remote invocation.
- python/ray/actor.py discovers actor methods, stores actor metadata, creates ActorHandles, and submits actor tasks.
- python/ray/util/placement_group.py validates resource bundles and constructs placement-group handles and scheduling strategies.
- python/ray/_private/worker.py owns driver/worker initialization, connection state, runtime setup, and shutdown.
- python/ray/_private/serialization.py and related serializers turn Python values/ObjectRefs into the wire representation expected by the runtime.

### Native and performance-critical plane

- src/ray/core_worker/core_worker.cc and core_worker.h implement the native worker-side submission, object, actor, and task operations called by Python.
- src/ray/raylet/node_manager.cc and worker_pool.cc implement node-local scheduling and worker lifecycle.
- src/ray/gcs/gcs_server.cc and placement/actor managers hold cluster metadata and coordination.
- Plasma/object-store and spilling paths own large-object memory movement and disk spill behavior.

The Python layer is intentionally a façade over native RPC/state machines. It should not be judged as if it were a self-contained scheduler; its contracts are the C++ worker APIs, IDs, serialized descriptors, and lifecycle events.

## 3. Pattern Map

| Pattern | Source | Test | Book mapping | Evidence | Trade-off |
| :--- | :--- | :--- | :--- | :--- | :--- |
| P07 Composition Root and Dependency Injection | [worker.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/_private/worker.py#L1439-L1520) | [test_worker_graceful_shutdown.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/tests/test_worker_graceful_shutdown.py#L20-L66) | Architecture ch13; Clean Architecture ch18-ch20 | B | ray.init composes a runtime from process/environment options, but it configures global worker state rather than injecting small services. |
| P08 Factory, Registry, and Plugin Architecture | [remote_function.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/remote_function.py#L41-L183), [actor.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/actor.py#L1553-L1640) | [test_basic.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/tests/test_basic.py) | Design ch34; Clean Architecture ch19-ch20 | B | Remote descriptors and actor metadata register executable definitions with the runtime, but this is runtime export rather than an application plugin registry. |
| P12 Adapter, Façade, and Provider Router | [remote_function.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/remote_function.py#L358-L570), [core_worker.cc](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/src/ray/core_worker/core_worker.cc) | [test_failure.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/tests/test_failure.py#L22-L145) | Design ch35; Clean Architecture ch19-ch20 | A | The Python API translates Python calls into a native task protocol and maps native errors back to Python exceptions. |
| P16 Concurrency, Scheduling, and Resource Lifecycle | [placement_group.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/util/placement_group.py#L26-L230), [worker.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/_private/worker.py#L2067-L2148) | [test_placement_group.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/tests/test_placement_group.py#L29-L227), [test_object_spilling.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/tests/test_object_spilling.py#L748-L803) | Design ch41; Clean Architecture ch23 | A | Resource bundles, fate-sharing, spilling, and shutdown are explicit, but correctness depends on distributed services and native state. |
| P17 Testing Seams, Fitness Tests, ACL, and Strangler Migration | [actor.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/actor.py#L2480-L2590) | [test_worker_graceful_shutdown.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/tests/test_worker_graceful_shutdown.py#L74-L210), [test_failure.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/tests/test_failure.py#L181-L240) | Clean Architecture ch21 and ch24 | A | Tests inject process death, actor death, queueing, and shutdown to protect a native-backed lifecycle contract. |

P13 State Machine, Workflow, and Saga is **C and excluded**. Actors have state and Ray has restart/failover state machines internally, but the public runtime code inspected here is not a general durable application workflow engine.

P10 Commands, Events, and Message Bus is also **C for application architecture**. Ray has internal pub/sub and task events, but ObjectRefs/task submissions are not a durable domain event log with application-level idempotency.

## 4. Source Walkthrough

### File 1 — Remote function façade

[python/ray/remote_function.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/remote_function.py#L41-L183) stores options and the function descriptor. Its _remote method exports the function when necessary, resolves retries/runtime environments/placement, and eventually calls worker.core_worker.submit_task. The function is not sent to the scheduler on every call; Ray maintains export/descriptor state and re-exports when the cluster/job context changes.

### File 2 — Actor metadata and handle

[python/ray/actor.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/actor.py#L1553-L1640) builds ActorClass metadata from the user class. The remote creation path calls native create_actor, while ActorHandle method calls use native submit_actor_task. This is a stateful object façade: method order, concurrency groups, restart policy, and actor identity are runtime concerns rather than ordinary Python object semantics.

### File 3 — Placement and resource ownership

[python/ray/util/placement_group.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/util/placement_group.py#L26-L230) represents a placement group as an ObjectRef-backed handle. It validates PACK/SPREAD/STRICT strategies, supports detached or fate-shared lifetime, asks CoreWorker to create the group, and exposes ready/wait operations. User applications can use this as a composition boundary for a multi-worker topology.

### File 4 — Driver/worker lifecycle

[python/ray/_private/worker.py](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/python/ray/_private/worker.py#L1439-L1520) starts or attaches to a cluster and configures runtime environments. shutdown disconnects the worker, clears local definitions/actors, shuts down the native worker, and optionally waits for child processes. This lifecycle cannot be reduced to closing one Python socket because it includes object-store, node, and worker state.

### File 5 — Native handoff

[src/ray/core_worker/core_worker.cc](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/src/ray/core_worker/core_worker.cc), [src/ray/raylet/node_manager.cc](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/src/ray/raylet/node_manager.cc), and [src/ray/gcs/gcs_server.cc](https://github.com/ray-project/ray/blob/44e93d309792bd714ab286044adc5fa6bea99735/src/ray/gcs/gcs_server.cc) are the native counterparts to the Python façade. They own task submission, node scheduling, and cluster metadata. Python callers should therefore treat native IDs and exceptions as part of the adapter contract.

## 5. Theory Versus Practice

### Theoretical ideal

The book mappings suggest a small application service using injected ports for scheduling, storage, and transport. A command/message bus would provide explicit delivery, and a stateful aggregate would own consistent transitions.

### Production implementation

Ray exposes a global worker singleton, decorators that mutate/wrap user functions/classes, native ObjectRefs, and distributed services. The runtime uses IDs and asynchronous futures rather than a repository/unit-of-work boundary. Resource placement, retries, actor restart, and object spilling are first-class runtime behavior.

### Difference and rationale

The abstraction has to cross process and language boundaries with low overhead. A purely Python dependency-injection design would not replace CoreWorker, Raylet, or GCS; it would only hide them. Ray keeps the public API ergonomic and pushes the consistency/lifecycle protocol into native services. The compromise is global state, serialization constraints, and a larger semantic gap between a local function call and a remote task.

## 6. Testing Strategy

The inspected tests emphasize fault injection and resource lifecycle:

- python/ray/tests/test_failure.py checks unhandled task errors, failed actor initialization, worker death, actor worker death, future-task errors, and actor failover after a node is removed.
- python/ray/tests/test_object_spilling.py::test_recover_from_spill_worker_failure kills a spill worker, reruns a workload that forces large-object spilling, and checks cleanup.
- python/ray/tests/test_placement_group.py checks invalid resources, readiness, PACK topology, actor placement, and placement-group leak cleanup.
- python/ray/tests/test_worker_graceful_shutdown.py distinguishes in-flight work, application errors, and queued work during actor/process shutdown.

These are architecture fitness tests: they protect the promise that an ObjectRef either returns a result/error promptly, a placement group does not leak, and a shutdown drains only the work it promises to drain. They require a Ray cluster fixture and were inspected but not executed in this documentation workspace.

## 7. Production Compromises and Failure Boundaries

1. **Global worker state.** It makes ray.remote concise and fast, but tests and applications must control initialization/shutdown carefully.
2. **Serialization as a hidden boundary.** Closures, arguments, exceptions, and runtime environments must be serializable; a local type can fail only when exported.
3. **Runtime export is not a plugin registry.** Function descriptors can be re-exported when a cluster/job changes, which is necessary for correctness but adds version/job-context behavior.
4. **Resource lifetime is policy-driven.** Detached placement groups survive drivers, while default groups can be fate-shared. This is powerful but easy to misread as ordinary object ownership.
5. **Retries and failover are selective.** Task retry, actor restart, in-flight drain, and queued-task failure have different contracts; there is no single retry rule for every failure.
6. **Native state is authoritative.** Python wrappers cannot independently repair a lost worker/object-store state; the recovery protocol is distributed.

## 8. Lessons and When Not to Use It

Copy the explicit placement/resource handle and the fault-injection test style when building a distributed worker runtime. Copy the façade pattern when callers need a simple Python API over a stable native protocol.

Do not use Ray for a small in-process pipeline where a queue, thread pool, or asyncio TaskGroup is sufficient. Do not mistake actors for transactional aggregates or Ray task events for a durable business event stream. Use a domain event store or workflow engine when side effects must be replayed and audited.

## 9. Practice Exercise

Implement a mini remote runtime with:

1. a Python RemoteFunction descriptor;
2. a worker process that accepts serialized calls;
3. an ObjectRef future;
4. max-retry and actor-restart policies;
5. a placement-group validator;
6. graceful shutdown that drains in-flight calls but fails queued calls.

Write tests that kill a worker, spill a large result to a temporary directory, create an invalid resource bundle, and compare in-flight versus queued shutdown behavior. Keep the public façade independent of the process transport so the adapter boundary remains visible.
