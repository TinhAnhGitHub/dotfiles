# Framework example crosswalk

Concrete, adapted snippets belong in the `## Framework examples` section of the clean-code pattern
page that teaches the relevant implementation pattern. This file only helps route a question to a
family page; it does not replace the embedded example.

| Clean-code concern | Pattern page to open | Frameworks represented there |
|---|---|---|
| Typed dependency and tool boundaries | [`../patterns/typing.md`](../patterns/typing.md) | PydanticAI, DSPy, TRL, Transformers |
| Decorators, callbacks, and hooks | [`../patterns/closures-decorators.md`](../patterns/closures-decorators.md) | MLflow, Hugging Face Hub, Transformers, LiteLLM |
| Provider/client adapters | [`../patterns/oop.md`](../patterns/oop.md) | OpenAI SDK, LiteLLM, Hugging Face Hub, vLLM |
| State, workflows, and lifecycle | [`../patterns/iteration-resources.md`](../patterns/iteration-resources.md) | LangGraph, Google ADK, Agno, OpenAI SDK |
| Worker and async boundaries | [`../patterns/async-concurrency.md`](../patterns/async-concurrency.md) | verl, OpenRLHF, slime, vLLM, OpenAI SDK |
| Dynamic registration and class behavior | [`../patterns/dynamic-classes.md`](../patterns/dynamic-classes.md) | Transformers, qwen-agent, MLflow |

For the complete framework-to-design-pattern crosswalk, see the [design-pattern matrix](../../../python-design-patterns/references/frameworks/index.md).
