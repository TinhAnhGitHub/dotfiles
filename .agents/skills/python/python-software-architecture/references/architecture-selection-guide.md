# Architecture and pattern selection guide

Use this guide when the question is “which pattern solves this?” Start with the constraint and the simplest implementation that can meet it. Add a named pattern only when it gives a durable seam, lifecycle rule, or testable ownership boundary.

## Fast decision path

~~~text
Is the pressure a business invariant?
  └─ yes → P01 domain model → P02 aggregate if it spans objects
Does persistence leak into policy?
  └─ yes → P03 repository → P04 UoW if writes must be atomic
Is one user-visible operation coordinating collaborators?
  └─ yes → P05 use case → P06 ports when a dependency must vary
Are construction and ownership scattered?
  └─ yes → P07 composition root/DI
Are implementations selected by a key or extended by third parties?
  └─ yes → P08 registry/factory
Does one workflow need interchangeable algorithms?
  └─ yes → P09 strategy/policy
Are side effects queued, fanned out, or replayed?
  └─ yes → P10 commands/events → P11 projections for separate read needs
Do external APIs disagree?
  └─ yes → P12 adapter/façade/router
Can work pause, retry, compensate, or outlive a process?
  └─ yes → P13 workflow/state → P16 for scheduling/resources
Is behavior cross-cutting at a boundary?
  └─ yes → P14 middleware/decorator
Is data tree-shaped or staged?
  └─ yes → P15 composite/iterator/pipeline
Will legacy code be replaced incrementally or must the rule stay enforced?
  └─ yes → P17 ACL/Strangler/fitness tests
~~~

## Choose the least powerful option

| Pressure | Start with | Escalate when | Avoid when |
|---|---|---|---|
| One changing calculation | A function | It needs state, lifecycle, or a public contract → P09 | The branch is local and stable |
| Two providers | A tuple/dictionary in the composition root | Provider errors/capabilities need translation → P12 | APIs have no shared semantics |
| One database query | A query function | Multiple persistence implementations or aggregate access → P03 | The repository only forwards ORM methods |
| Several writes | One explicit transaction | Multiple repositories share atomicity → P04 | The operation is read-only |
| One lifecycle flag | An enum and guard | Legal transitions, resume, or compensation matter → P13 | The state will never outlive a call |
| A few side effects | Direct calls | Fan-out, retries, or replay matter → P10 | Immediate failure must reach the caller |
| A read view | Query the write model | Shape/scale/freshness diverges → P11 | Eventual consistency is unacceptable |
| Logging/metrics | An explicit helper | A stable boundary needs uniform instrumentation → P14 | It hides business policy or ordering |
| A list of transformations | A straight-line function | Steps are independently selected/tested → P15 | The stages are fixed and tiny |
| External/legacy schema | A thin wrapper | Translation and containment need a contract → P12/P17 | The wrapper hides important semantics |

## Pattern cards

| ID | Ask these questions | Main failure mode |
|---|---|---|
| P01 | What has identity? What invariant belongs with the value? | Anemic records and duplicated validation |
| P02 | What must be consistent in one transaction? Can the boundary stay small? | Giant aggregates and cross-boundary locking |
| P03 | Is this a meaningful collection port or an ORM façade? | Generic repository indirection |
| P04 | Who owns commit, rollback, and session lifetime? | Partial writes or hidden transactions |
| P05 | What is the one use case and its input/output contract? | God services and fat controllers |
| P06 | Which dependency points inward, and who implements the port? | Framework imports in core policy |
| P07 | Who constructs, owns, and closes each resource? | Service locators and hidden globals |
| P08 | When and how is an implementation discovered? | Import-order bugs and incompatible plugins |
| P09 | Which axis varies independently? | Class explosion or configuration spaghetti |
| P10 | Is this intent or a past fact? What are delivery guarantees? | Obscured control flow and duplicate effects |
| P11 | What is the source of truth and acceptable staleness? | Projection drift and double migrations |
| P12 | What is normalized, and which capabilities remain provider-specific? | Lowest-common-denominator APIs |
| P13 | Can a worker restart from a durable checkpoint? | Invalid transitions and lost work |
| P14 | Where is ordering, redaction, and exception behavior defined? | Silent failures and leaky telemetry |
| P15 | Does traversal or stage order change independently? | Over-abstraction and opaque pipelines |
| P16 | Who owns cancellation, backpressure, and native handles? | Leaks, starvation, and unbounded queues |
| P17 | Which contract proves the seam and how will migration be reversed? | Mocks that miss integration failures |

## Routing to applied evidence

Use the canonical pages in [book-pattern-matrix](book-pattern-matrix.md), then read the matching project dossier before making a repository claim.

| Question | Start with | Applied repositories |
|---|---|---|
| “Show me registry examples” | P08 [registry/factory](../patterns/registry-factory.md) | Transformers, pytest, vLLM, Django, smolagents |
| “How do strategies work?” | P09 [strategy/policy](../patterns/strategy-policy.md) | TRL, verl, SGLang, DeepSpeed, Transformers |
| “How do I normalize providers?” | P12 [adapter/router](../patterns/adapter-provider-router.md) | LiteLLM, HTTPX, smolagents, Transformers, TensorRT-LLM |
| “How do I model pause/resume?” | P13 [state/workflow](../patterns/state-workflow.md) | verl, LangGraph, CrewAI, OpenAI Agents, Ray, Home Assistant |
| “How do events fail?” | P10 [events/message bus](../patterns/events-message-bus.md) | Home Assistant, AutoGen, OpenRLHF, CrewAI, MCP Python SDK |
| “How do I test a boundary?” | P17 [testing boundaries](../patterns/testing-boundaries.md) | pytest, HTTPX, FastAPI, Django, Transformers, vLLM, MLflow |
| “What is Python versus CUDA/native?” | P16 [concurrency/lifecycle](../patterns/concurrency-lifecycle.md) | vLLM, SGLang, Megatron-LM, TensorRT-LLM, llama.cpp, MLC-LLM |

## Reading a case study correctly

1. Confirm the pinned commit in source-manifest.json.
2. Read the dossier’s source and test paths.
3. Classify the claim as A (direct), B (strong), or C (inferred).
4. Compare the textbook ideal with the production compromise.
5. Copy the exercise, not the repository’s incidental complexity.

A source path without a test or runtime call site is a research lead, not proof.

