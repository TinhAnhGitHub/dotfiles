# Production framework patterns for Chapters 11–15

**Evidence policy:** The links below point to official documentation or official source
repositories. Framework internals change; verify the exact version before copying an internal
implementation. A framework example demonstrates a useful shape, not a requirement to adopt
the framework's entire architecture.

## Cross-framework matrix

| Framework | Ch. 11–12 object/data model | Ch. 13 interface | Ch. 14 inheritance | Ch. 15 typing / streams | Lifecycle companion |
|---|---|---|---|---|---|
| MLflow | `Model`, `PyFuncModel`, properties/repr/equality | `PythonModel` ABC | subclass hook/wrapping | overloads, generators | `ActiveRun`, `ActiveModel` context managers |
| vLLM | dataclass/msgspec output objects | `TokenizerLike` Protocol, `EngineClient` ABC | quantization ABCs, mixins | overloads, generic outputs, async generators | explicit `shutdown()` is preferred over an async CM |
| HF Transformers | `ModelOutput`, `BatchEncoding` mapping/sequence objects | collection ABCs | `PreTrainedModel` and Hub mixins | `TypedDict`, overloads | `ContextManagers`, autocast helpers |
| HF Hub | model mixin objects | dataclass capability Protocol | `ModelHubMixin` / PyTorch mixin | generator APIs | `AsyncInferenceClient`, temp-dir/lock CMs |
| LangChain | Pydantic serializable objects, callable tools | `Runnable` ABC, callable Protocols | callback mixins | overloads, `TypedDict`, streaming | callback context managers, async iterator CMs |
| LlamaIndex | Pydantic components and response objects | runtime Protocols + ABCs | prompt/instrumentation mixins | generic ABCs, `Annotated`, generator responses | trace/event context managers |
| LangGraph | typed graph/state objects | serializer Protocol | `MessageGraph(StateGraph)` / template methods | `TypedDict` + `Annotated` reducers, iterators | explicit compile/invoke lifecycle |
| AutoGen/AG2 | typed agent/result objects | plugin/base contracts | `PluginTarget`, event model | overloads, generics | `AgentRun` async context manager |

## MLflow

### Patterns

- `mlflow.start_run()` returns a context-managed run. Cleanup updates success/failure state in
  `__exit__` without suppressing the exception.
- `ActiveModel` provides a similar scoped lifecycle for logged models.
- `PythonModel` is an ABC-style extension point: users implement `predict`, while MLflow owns
  the wrapper and validation path.
- `Model`/`PyFuncModel` are rich domain objects with controlled representation, properties, and
  prediction methods rather than dictionary-shaped state everywhere.
- Streaming/pagination paths use generators; overloaded result APIs refine return types.

### Best practice to copy

Make ownership explicit with a context manager, keep user extension points narrow, and let the
framework own lifecycle/validation around the user implementation.

### Evidence

- <https://github.com/mlflow/mlflow/blob/master/mlflow/tracking/fluent.py>
- <https://github.com/mlflow/mlflow/blob/master/mlflow/pyfunc/model.py>
- <https://mlflow.org/docs/latest/ml/tracking/tracking-api>

## vLLM

### Patterns

- `TokenizerLike(Protocol)` expresses structural tokenizer capabilities, including overloaded
  token conversion behavior.
- `EngineClient(ABC)` expresses an engine lifecycle/operation boundary with abstract generation,
  encoding, health, abort, and shutdown operations.
- Quantization base classes use ABCs where implementations share framework behavior and must
  satisfy required hooks.
- Sampling/output objects use dataclass/msgspec-style value objects, validation hooks, cached
  properties, cloning, and generic output types.
- `AsyncLLM.generate` exposes an async generator for streaming. This keeps streaming semantics
  separate from the output value object.

### Best practice to copy

Use a Protocol for lightweight adapters and an ABC for a lifecycle-heavy engine. Keep streaming
as an iterator/async-iterator contract; do not overload the result object with hidden stream
state.

### Evidence

- <https://github.com/vllm-project/vllm/blob/main/vllm/tokenizers/protocol.py>
- <https://github.com/vllm-project/vllm/blob/main/vllm/engine/protocol.py>
- <https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/layers/quantization/base_config.py>
- <https://github.com/vllm-project/vllm/blob/main/vllm/v1/engine/async_llm.py>
- <https://docs.vllm.ai/en/stable/examples/deployment/async_llm_streaming/>

## Hugging Face Transformers and Hub

### Patterns

- `ModelOutput` and `BatchEncoding` implement deliberate mapping/sequence hybrids. They support
  string lookup, positional/slice lookup, serialization, and controlled mutation instead of
  accidentally inheriting every dictionary operation.
- `PreTrainedModel` composes multiple focused mixins, including Hub, module utilities, adapter,
  and distributed behavior.
- `ModelHubMixin` supplies a template-method contract: common save/load/push behavior surrounds
  narrow `_save_pretrained`/`_from_pretrained` hooks.
- Hub listing APIs return generators for paginated data rather than materializing everything.
- `AsyncInferenceClient` and temporary-file/lock helpers demonstrate sync and async lifecycle
  protocols.

### Best practice to copy

For a hybrid object, explicitly define the supported operations and reject unsupported mutation.
For reusable cross-cutting behavior, prefer a focused mixin or composition over one huge base
class. For remote listings, expose lazy iterators and document pagination/failure behavior.

### Evidence

- <https://github.com/huggingface/transformers/blob/main/src/transformers/utils/generic.py>
- <https://github.com/huggingface/transformers/blob/main/src/transformers/tokenization_utils_base.py>
- <https://github.com/huggingface/transformers/blob/main/src/transformers/modeling_utils.py>
- <https://huggingface.co/docs/transformers/main_classes/output>
- <https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/hub_mixin.py>
- <https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/inference/_generated/_async_client.py>
- <https://huggingface.co/docs/huggingface_hub/package_reference/mixins>

## LangChain

### Patterns

- `Runnable` is an ABC-like generic execution contract with sync/async, batch, and stream
  operations.
- `Runnable.__or__`/`__ror__` turn `a | b` into a composable `RunnableSequence`; this is a
  carefully constrained operator DSL, not arbitrary operator overloading.
- `RouterRunnable` uses a mapping of keys to runnables, avoiding growing `if/elif` dispatch.
- `@tool` derives schema and metadata from a function signature/docstring, keeping the callable
  and its public tool contract together.
- `RunnableGenerator` and `astream`/event APIs expose lazy and async streaming.
- Callback usage helpers use context-managed scoped state; runtime context keeps request-scoped
  dependencies separate from graph state.

### Best practice to copy

Only overload an operator when the result is an obvious domain composition and both operands
have a stable contract. Keep the underlying method (`pipe`, `invoke`, `stream`) available for
readability and introspection. Treat tool schemas as derived metadata, not a second hand-written
source of truth.

### Evidence

- <https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/runnables/base.py>
- <https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/runnables/router.py>
- <https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/tools/convert.py>
- <https://docs.langchain.com/oss/python/langchain/voice-agent>
- <https://docs.langchain.com/oss/python/langchain/context-engineering>
- <https://reference.langchain.com/python/langchain-core/runnables/base/Runnable/pipe>

## LlamaIndex

### Patterns

- Runtime-checkable Protocols such as `VectorStore` and `Tokenizer` provide duck-typed adapter
  contracts; ABCs such as vector-store/synthesizer bases provide shared behavior and required
  hooks.
- `PromptMixin` is a template-method mixin: public prompt traversal/update methods delegate to
  narrow protected hooks.
- Instrumentation mixins use subclass registration/wrapping to add spans consistently.
- `FunctionTool` is a callable object carrying the wrapped function, schema, metadata, defaults,
  and context requirements in one place.
- `StreamingResponse`/agent response objects expose generator and async-generator token flows.
- `CallbackManager.as_trace`/`event` use context-managed scope and ensure end/error events are
  emitted even when the enclosed operation fails.

### Best practice to copy

Use a Protocol and an ABC side by side when a role has both external adapters and framework-owned
implementations. Keep metadata next to the callable it describes. Use a context manager around
observability state so instrumentation cannot leak across requests.

### Evidence

- <https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/schema.py>
- <https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/vector_stores/types.py>
- <https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/prompts/mixin.py>
- <https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/tools/function_tool.py>
- <https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/callbacks/base.py>
- <https://developers.llamaindex.ai/python/framework/module_guides/deploying/query_engine/streaming/>

## LangGraph

### Patterns

- `SerializerProtocol` is a runtime-checkable Protocol; serializer implementations can satisfy
  it without inheriting from the framework.
- `StateGraph` uses generic state/input/output/context parameters and `TypedDict` state schemas.
  `Annotated` fields carry reducer semantics with the state type.
- `MessagesState` and `add_messages` demonstrate a typed state update protocol rather than a
  mutable global message list.
- `BaseCheckpointSaver` uses a template-method interface with sync and async iterator methods;
  it does not force every implementation into a heavyweight ABC.
- Compiled graphs expose invoke/stream/async variants instead of making the graph object itself
  pretend to be a sequence.

### Best practice to copy

Make state shape and state-update semantics explicit in the type. Pair sync and async methods
only when both are meaningful, and expose streaming as iterators. A simple
`NotImplementedError` template interface can be clearer than an ABC when no shared code or
registration semantics are needed.

### Evidence

- <https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/langgraph/checkpoint/serde/base.py>
- <https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/langgraph/checkpoint/base/__init__.py>
- <https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/graph/message.py>
- <https://docs.langchain.com/oss/python/langgraph/persistence>
- <https://reference.langchain.com/python/langgraph/checkpoint/base/BaseCheckpointSaver>

## AutoGen / AG2

### Patterns

The current AG2 lineage is the most useful evidence for async lifecycle design:

- `AgentRun` is an async context manager. Entering creates a turn scope; exiting cancels or
  closes owned tasks/subscriptions through an `AsyncExitStack`.
- The turn scope is an async-generator/context-manager combination, keeping resources alive
  across the yielded run and guaranteeing cleanup.
- Agent APIs use overloads and generics to refine result types when a response schema is supplied.
- Event `Field` descriptors overload comparisons to construct conditions; event classes compose
  conditions with class-level operators such as `|` and `~`.
- Function registration and execution use decorator factories plus name-to-callable dispatch
  maps, keeping schema and execution registration explicit.

### Best practice to copy

For an async operation that owns tasks, subscriptions, or human-in-the-loop state, make the
operation an async context manager and define cancellation/cleanup semantics in one place. For
operator DSLs, return immutable condition objects and test precedence, invalid operands, and
short-circuit behavior.

### Evidence

- <https://github.com/ag2ai/ag2/blob/main/ag2/agent.py>
- <https://github.com/ag2ai/ag2/blob/main/ag2/events/base.py>
- <https://github.com/ag2ai/ag2/blob/main/docs/adr/0008-agent-run-turn-is-scoped-to-its-context-manager.md>
- <https://docs.ag2.ai/>

## Cross-framework rules worth adopting

1. **Keep the contract close to the boundary.** Protocols, ABCs, `TypedDict`, and overloads
   should describe what consumers actually use.
2. **Keep metadata with the callable/object.** Avoid parallel registries that can drift from
   the implementation.
3. **Make async lifecycle explicit.** If an object owns tasks or network resources, implement
   `__aenter__`/`__aexit__` or provide a documented `aclose`; always use `try/finally`.
4. **Stream lazily.** Use `Iterator`/`AsyncIterator` when results can be large, incremental, or
   cancellable.
5. **Make extension additive.** Prefer registration, dispatch maps, Protocol adapters, and
   focused mixins over editing a central conditional or subclassing a giant base.
6. **Do not confuse static and runtime typing.** `Protocol`, `TypedDict`, overloads, and `cast`
   do not validate untrusted data at runtime.
7. **Test protocol semantics.** Check cleanup on exceptions/cancellation, unknown dispatch keys,
   invalid operands, empty streams, and schema/runtime agreement.
