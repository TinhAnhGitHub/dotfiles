# Pattern index

## Find by problem

| Problem signal | Start here |
|---|---|
| Several independent feature axes are creating subclasses | [Composition over inheritance](principles/composition.md), [SOLID boundaries](principles/solid.md), [Adapter](composition/adapter.md), [Decorator](composition/decorator.md) |
| A caller must work with multiple providers or APIs | [Adapter](composition/adapter.md), [Facade](composition/facade.md), [Dependency injection and registry](extensibility/registry-di.md) |
| A function has sprawling if/elif chains dispatching on strings or formats | [Registry and dependency injection](extensibility/registry-di.md), [Strategy](behavior/strategy.md) |
| A high-level workflow repeats many related parameters | [Parameter Object](construction/parameter-object.md), [Builder](construction/builder.md) |
| Construction is coupled to concrete implementations | [Factory](construction/factory.md), [Builder](construction/builder.md) |
| One algorithm varies at runtime | [Strategy](behavior/strategy.md), [Adapter](composition/adapter.md) |
| Many independent rules must be ordered, enabled, or disabled | [Policy Pipeline](behavior/policy-pipeline.md), [Specification](behavior/specification.md), [Registry and dependency injection](extensibility/registry-di.md) |
| A tree contains both individual items and groups | [Composite](composition/composite.md) |
| Work must be queued, replayed, or deferred | [Command](behavior/command.md), [Lifecycle and workflow](lifecycle/state-workflow.md) |
| A lifecycle has legal events and invalid transitions | [State Machine](lifecycle/state-machine.md), [Lifecycle and workflow](lifecycle/state-workflow.md) |
| Multiple consumers need notifications | [Observer and publish/subscribe](behavior/observer.md) |
| A system has plugins, tools, callbacks, or model providers | [Registry and dependency injection](extensibility/registry-di.md), [Structural Protocols](extensibility/protocols.md), [AI boundaries](architecture/ai-boundaries.md) |
| A domain must not depend on HTTP, SQL, or SDK details | [SOLID boundaries](principles/solid.md), [Adapter](composition/adapter.md), [AI boundaries](architecture/ai-boundaries.md) |
| Reads and writes have different scaling or consistency needs | [CQRS](architecture/cqrs.md) |
| A value must enforce invariants at construction | [Value Object](construction/value-object.md), [Parameter Object](construction/parameter-object.md) |
| A workflow must pause, resume, retry, or recover | [Lifecycle and workflow](lifecycle/state-workflow.md), [State Machine](lifecycle/state-machine.md) |
| A value is missing, not supplied, or intentionally empty | [Sentinel and lazy resources](python-specific/sentinel-lazy.md) |
| Code suffers from concrete imports, isinstance spaghetti, or choosing between Callable, Protocol, and ABC | [Structural Protocols and Abstraction Spectrum](extensibility/protocols.md), [Composition](principles/composition.md) |
| Nested try/except pyramids, catching all exceptions, or returning fake defaults | [Anti-patterns](anti-patterns/singleton-inheritance.md), [Absence values and Fail Fast](../../python-clean-code/references/patterns/absence-values.md) |
| Subclasses created solely to change constants, thresholds, or configuration settings | [Anti-patterns](anti-patterns/singleton-inheritance.md), [OOP](../../python-clean-code/references/patterns/oop.md) |
| Subtypes disabling parent methods (LSP violation) or wide base classes with unimplemented methods (stamp coupling/ISP) | [Structural Protocols](extensibility/protocols.md), [SOLID boundaries](principles/solid.md), [Anti-patterns](anti-patterns/singleton-inheritance.md) |
| Abstracting before understanding similarity (forcing disparate domains into generic templates) | [Anti-patterns](anti-patterns/singleton-inheritance.md), [Composition](principles/composition.md), [OOP](../../python-clean-code/references/patterns/oop.md) |
| Naive prototype with business logic, queries, global state, and prints in route handlers | [Anti-patterns](anti-patterns/singleton-inheritance.md), [SOLID boundaries](principles/solid.md), [Dependency injection](extensibility/registry-di.md) |
| Floating-point numerical drift in monetary, exchange rate, or accounting calculations | [Typed boundaries](../../python-clean-code/references/patterns/typing.md), [Value Object](construction/value-object.md) |
| Web API lacking rate limiting, health checks, or 12-factor environment configuration | [SOLID boundaries](../../python-clean-code/references/patterns/solid-boundaries.md), [Dependency injection](extensibility/registry-di.md) |
| Domain logic raising HTTP exceptions, executing raw SQL, or returning API wire dicts | [Adapter](composition/adapter.md), [SOLID boundaries](../../python-clean-code/references/patterns/solid-boundaries.md), [Anti-patterns](anti-patterns/singleton-inheritance.md) |
| Sluggish application startup from eager I/O, repeated disk/API reloads, or generator caching bugs | [Sentinel and lazy resources](python-specific/sentinel-lazy.md), [Iteration and resources](../../python-clean-code/references/patterns/iteration-resources.md) |
| Stale dynamic API responses or auth tokens caused by unbounded `@cache` without TTL | [Sentinel and lazy resources](python-specific/sentinel-lazy.md) |

## Find by family

- [Principles](principles/composition.md), [SOLID boundaries](principles/solid.md)
- [Composition](composition/adapter.md), [Decorator](composition/decorator.md), [Facade](composition/facade.md), [Composite](composition/composite.md)
- [Construction](construction/factory.md), [Builder](construction/builder.md), [Parameter Object](construction/parameter-object.md), [Value Object](construction/value-object.md)
- [Behavior](behavior/strategy.md), [Policy Pipeline](behavior/policy-pipeline.md), [Command](behavior/command.md), [Observer](behavior/observer.md), [Specification](behavior/specification.md)
- [Extensibility](extensibility/registry-di.md), [Structural Protocols](extensibility/protocols.md)
- [Lifecycle](lifecycle/state-workflow.md), [State Machine](lifecycle/state-machine.md)
- [Architecture and AI systems](architecture/ai-boundaries.md), [CQRS](architecture/cqrs.md)
- [Python-specific patterns](python-specific/sentinel-lazy.md)
- [Anti-patterns](anti-patterns/singleton-inheritance.md)

## Framework crosswalk

Use the [framework matrix](frameworks/index.md) to locate the pattern pages that contain the
embedded examples. The canonical framework names are: verl, Hugging Face Hub, Transformers,
PydanticAI, LangChain, LangGraph, Agno, Google ADK, vLLM, `openai-python`, MLflow, qwen-agent,
OpenRLHF, slime, DSPy, TRL, and LiteLLM.

For the complete ArjanCodes source audit, see
[`provenance/arjancodes-2026-map.md`](provenance/arjancodes-2026-map.md). The map is navigation;
the adapted code examples live on the linked pattern pages.


## Canonical P01–P17 crosswalk

The architecture skill owns the canonical pages and book mappings:
[book-pattern-matrix](../../python-software-architecture/references/book-pattern-matrix.md),
[selection guide](../../python-software-architecture/references/architecture-selection-guide.md),
and [pattern catalog](../../python-software-architecture/patterns.md).

| Topic | Canonical IDs | Applied repositories |
|---|---|---|
| Registry | P08 | Transformers, vLLM, pytest, Django, smolagents |
| Strategy | P09 | TRL, verl, SGLang, DeepSpeed, Transformers |
| Adapter/provider router | P06, P12 | LiteLLM, HTTPX, smolagents, Transformers, TensorRT-LLM |
| Workflow/state | P13, P16 | verl, LangGraph, CrewAI, OpenAI Agents, Ray, Home Assistant |
| Events/message bus | P10, P11 | Home Assistant, AutoGen, OpenRLHF, CrewAI, MCP Python SDK |
| Dependency injection | P06, P07 | PydanticAI, FastAPI, OpenAI Agents |
| Testing boundaries | P17 | pytest, HTTPX, FastAPI, Django, MLflow |

Use the existing family pages for tactical detail, but cite the canonical page and
repository dossier when answering a cross-skill question.
