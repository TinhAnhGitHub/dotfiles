# Pattern index

## Find by problem

| Problem signal | Start here |
|---|---|
| Several independent feature axes are creating subclasses | [Composition over inheritance](principles/composition.md), [SOLID boundaries](principles/solid.md), [Adapter](composition/adapter.md), [Decorator](composition/decorator.md) |
| A caller must work with multiple providers or APIs | [Adapter](composition/adapter.md), [Facade](composition/facade.md), [Dependency injection and registry](extensibility/registry-di.md) |
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
| A familiar pattern feels too complex | [Anti-patterns](anti-patterns/singleton-inheritance.md) |

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
