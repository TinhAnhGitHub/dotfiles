# Ch. 8 — Type Hints for Functional Boundaries

Type hints are most valuable where a function crosses a boundary: a decorator, registry,
callback, plugin, tool, or strategy. They should describe the relationship between the caller and
the callable—not merely decorate every local variable.

## Distilled patterns

### T1. Use `Literal` for a closed vocabulary

Use it when a string is a protocol value, registry key, mode, or status with a deliberately finite
set of choices.

```python
ResponseFormat = Literal["content", "content_and_artifact"]

def render(value: object, format: ResponseFormat = "content") -> str: ...
```

`Literal` gives static tooling a finite domain and makes runtime validation/documentation easier.
Do not use it for an open-ended plugin name.

### T2. Use `Annotated` for metadata consumed by a framework

Use it when the base type remains useful to type checkers but a runtime framework needs extra
information: a tool description, reducer, serializer, injected parameter, or validator.

```python
def search(query: Annotated[str, "The user query"]) -> list[str]: ...
```

The metadata must have a clear consumer. An annotation that no framework reads is just hidden
documentation.

### T3. Use `Callable` aliases at strategy and hook boundaries

Name a callable shape when it appears in more than one signature or represents a domain concept.

```python
ScoreFn = Callable[[str, str], float]
Reducer = Callable[[list[object]], object]
```

Use `Protocol` instead when the dependency needs several methods or attributes.

### T4. Use `TypeVar` to preserve relationships

Use a bound `TypeVar` when the output preserves the input subtype, or when a decorator returns the
same callable type.

```python
F = TypeVar("F", bound=Callable[..., object])

def mark(fn: F) -> F:
    fn.is_registered = True
    return fn
```

Use constraints for a closed set of alternatives; use a bound for “any subtype of this contract.”

### T5. Use `ParamSpec` for transparent decorators

`Callable[..., R]` loses the parameter list. `ParamSpec` keeps arbitrary positional and keyword
arguments connected through a wrapper.

```python
P = ParamSpec("P")
R = TypeVar("R")

def traced(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)
    return wrapper
```

### T6. Use `Protocol` for structural plugin contracts

If a plugin only needs `attach_router()` and `init_state()`, do not force it to inherit a base
class solely for typing. A protocol lets independent implementations satisfy the contract.

### T7. Use overloads for dual-form APIs

For APIs supporting both `@decorator` and `@decorator(...)`, overload the public forms and keep one
runtime implementation. The overloads document what callers get; the implementation handles the
runtime union.

### T8. Use typed immutable records for configuration/cache keys

`NamedTuple` is useful for a small immutable record used as a cache key. A generic `TypeVar` or
`Self` is useful when a method returns the same model/class type. Do not introduce a tuple merely to
avoid a small dataclass with named behavior.

## Verified examples

### 1. AG2 — `Literal` separates configuration modes

- **File:** `autogen/agentchat/conversable_agent.py:157-168,3552`
- **Source:** [AG2 v0.8.7](https://github.com/ag2ai/ag2/blob/v0.8.7/autogen/agentchat/conversable_agent.py#L3552)
- **Context:** an agent accepts a finite human-input mode and a finite tool API style.
- **Real shape:**
  ```python
  human_input_mode: Literal["ALWAYS", "NEVER", "TERMINATE"] = "TERMINATE"
  api_style: Literal["function", "tool"] = "tool"
  ```
- **Solves:** `CORRECTNESS` (typos become statically visible), `READABILITY` (the accepted protocol
  is visible at the boundary).

### 2. AG2 — `Annotated` turns a parameter annotation into tool metadata

- **File:** `autogen/agentchat/conversable_agent.py:3552-3590`
- **Source:** [AG2 v0.8.7](https://github.com/ag2ai/ag2/blob/v0.8.7/autogen/agentchat/conversable_agent.py#L3574)
- **Context:** the tool schema is generated from a Python function signature.
- **Real shape:**
  ```python
  def my_function(
      a: Annotated[str, "description of a parameter"] = "a",
      b: int = 0,
      c: float = 3.14,
  ) -> str: ...
  ```
- **Solves:** `READABILITY` and `EXTENSIBILITY`: the function remains callable Python while the
  agent framework can extract descriptions for the model-facing schema.

### 3. AG2 — bounded `TypeVar` preserves decorated callable identity

- **File:** `autogen/agentchat/conversable_agent.py:84`
- **Source:** [AG2 v0.8.7](https://github.com/ag2ai/ag2/blob/v0.8.7/autogen/agentchat/conversable_agent.py#L84)
- **Real shape:**
  ```python
  F = TypeVar("F", bound=Callable[..., Any])
  ```
  The same pattern is used by registration helpers that accept a function and return the original
  function or a tool-compatible wrapper.
- **Solves:** `CORRECTNESS`: type checkers retain “this is still a callable” instead of collapsing
  the result to `Callable[..., Any]`.

### 4. LangChain — `Annotated` is inspected, not merely documented

- **File:** `langchain_core/tools/base.py:93-123,1492-1499`
- **Source:** [LangChain current source](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/tools/base.py#L93-L123)
- **Context:** tool schema generation extracts a string or Pydantic `FieldInfo` from annotation
  metadata.
- **Real shape:**
  ```python
  def _is_annotated_type(typ: type[Any]) -> bool:
      return get_origin(typ) in {typing.Annotated, typing_extensions.Annotated}

  annotated_args = get_args(arg_type)
  for annotation in annotated_args[1:]:
      if isinstance(annotation, str):
          return annotation
  ```
- **Solves:** `EXTENSIBILITY`: a tool author can place model-facing parameter descriptions beside
  the type, and schema generation consumes them consistently.

### 5. LangChain — `Literal`, `Callable`, and `Self` describe tool APIs

- **File:** `langchain_core/tools/base.py:483,528-547,637-647`
- **Source:** [LangChain current source](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/tools/base.py#L483-L547)
- **Real shapes:**
  ```python
  response_format: Literal["content", "content_and_artifact"] = "content"
  handle_tool_error: bool | str | Callable[[ToolException], str] | None

  def model_copy(...) -> Self: ...
  ```
- **Solves:** `CORRECTNESS`: closed response modes are distinct from user-supplied error
  strategies; `Self` communicates that copying a tool returns the concrete tool type.

### 6. Agno — overloads model all three `@tool` call forms

- **File:** `agno/tools/decorator.py:8-10,56-88`
- **Source:** [Agno current source](https://github.com/agno-agi/agno/blob/main/libs/agno/agno/tools/decorator.py#L56-L88)
- **Context:** `tool` supports `@tool`, `@tool()`, and `@tool(name=...)` while returning a
  `Function` wrapper.
- **Real shape:**
  ```python
  F = TypeVar("F", bound=Callable[..., Any])

  @overload
  def tool() -> Callable[[F], Function]: ...

  @overload
  def tool(func: F) -> Function: ...
  ```
- **Solves:** `READABILITY` and `CORRECTNESS`: IDEs show the right decorator form without forcing
  the runtime implementation into several duplicated functions.

### 7. LlamaIndex — explicit sync/async callable aliases

- **File:** `llama_index/core/tools/function_tool.py:39-64`
- **Source:** [LlamaIndex current source](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/tools/function_tool.py#L39-L64)
- **Real shape:**
  ```python
  AsyncCallable = Callable[..., Awaitable[Any]]

  def sync_to_async(fn: Callable[..., Any]) -> AsyncCallable: ...
  def async_to_sync(func_async: AsyncCallable) -> Callable: ...
  ```
- **Solves:** `READABILITY` and `CORRECTNESS`: the sync/async adaptation boundary is named and
  tools can accept either execution form without pretending they have identical semantics.

### 8. LlamaIndex Workflows — `ParamSpec` + `Protocol` for `@step`

- **File:** `packages/llama-index-workflows/src/workflows/decorators.py:102-141`
- **Source:** [LlamaIndex Workflows](https://github.com/run-llama/llama-agents/blob/main/packages/llama-index-workflows/src/workflows/decorators.py#L102-L141)
- **Real shape:**
  ```python
  P = ParamSpec("P")
  R_co = TypeVar("R_co", covariant=True)

  class StepFunction(Protocol, Generic[P, R_co]):
      _step_config: StepConfig
      def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

  @overload
  def step(func: Callable[P, R]) -> StepFunction[P, R]: ...
  ```
- **Context:** the decorator attaches `_step_config`, but the resulting object still behaves like
  the original callable.
- **Solves:** `CORRECTNESS` (arguments/returns stay related), `EXTENSIBILITY` (workflow metadata is
  added without requiring a nominal wrapper base class).

### 9. MLflow — typed tracing preserves arbitrary user signatures

- **File:** `mlflow/tracing/fluent.py:91-120,251-296`
- **Source:** [MLflow master](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/tracing/fluent.py#L91-L120)
- **Real shape:**
  ```python
  _P = ParamSpec("_P")
  _R = TypeVar("_R")

  @overload
  def trace(func: Callable[_P, _R], ...) -> Callable[_P, _R]: ...
  ```
- **Solves:** `CORRECTNESS`: tracing does not erase the decorated function’s parameter contract;
  `READABILITY`: bare and configured decorator forms are explicit.

### 10. vLLM — overloads and protocols for configuration decorators

- **File:** `vllm/config/utils.py:36-80,201-223`
- **Source:** [vLLM main](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/config/utils.py#L36-L80)
- **Real shape:**
  ```python
  ConfigT = TypeVar("ConfigT", bound=DataclassInstance)

  @overload
  def config(cls: type[ConfigT]) -> type[ConfigT]: ...
  ```
  The same module uses `SupportsHash(Protocol)` for cached configuration hashing.
- **Solves:** `CORRECTNESS`: a class decorator returns the same concrete config type while a
  protocol describes the minimum hashing behavior.

### 11. ms-swift — Pydantic metadata in inference protocols

- **File:** `swift/infer_engine/protocol.py:13-41,230,411-423`
- **Source:** [ms-swift main](https://github.com/modelscope/ms-swift/blob/a54a4ae5c8680451ba4ddc91ad4577a38c74d560/swift/infer_engine/protocol.py#L13-L41)
- **Real shape:**
  ```python
  NumpyArray = Annotated[Any, PlainSerializer(...), AfterValidator(...)]
  role: Literal["system", "user", "assistant"]
  finish_reason: Literal["stop", "length", None]
  ```
- **Solves:** `CORRECTNESS`: serialization/validation metadata travels with the type, while
  `Literal` constrains the inference protocol vocabulary.

### 12. verl — algorithm registries use typed function aliases

- **File:** `verl/trainer/ppo/core_algos.py:37-64,70-85,113-150`
- **Source:** [verl pinned source](https://github.com/verl-project/verl/blob/6cbca9ce7208100d11b4d1b06eccf098cc9e76aa/verl/trainer/ppo/core_algos.py#L37-L64)
- **Real shape:** `PolicyLossFn = Callable[...]` describes a policy-loss function and
  `POLICY_LOSS_REGISTRY: dict[str, PolicyLossFn]` stores implementations selected by name.
- **Solves:** `EXTENSIBILITY`: adding a loss is a function plus registration, not a central branch;
  `CORRECTNESS`: registry entries share a callable contract.

### 13. `returns` — higher-order `bind` preserves container type parameters

- **File:** `returns/pointfree/bind.py:7-25`
- **Source:** [returns current source](https://github.com/dry-python/returns/blob/master/returns/pointfree/bind.py#L7-L25)
- **Real shape:** multiple `TypeVar`s and a bounded `_BindableKind` transform
  `Callable[[A], Container[B]]` into `Container[A] -> Container[B]`.
- **Solves:** `CORRECTNESS`: higher-order composition keeps the input/output container and value
  types connected instead of degrading to `Any`.

## Review checklist

1. Is this value a closed protocol (`Literal`) or an open extension key (`str` + registry)?
2. Does metadata have a runtime consumer (`Annotated`), or should it be a docstring/field?
3. Does a decorator preserve the original signature? If yes, use `ParamSpec` and `@wraps`.
4. Does a dependency require one call or a multi-method contract? Choose `Callable` or `Protocol`.
5. Does the output preserve the input subtype? Use a bound/covariant `TypeVar` or `Self`.
6. Do bare and configured decorator forms need distinct static return types? Add overloads.
7. Are annotations used at runtime? Resolve them deliberately (`get_type_hints(...,
   include_extras=True)`) and test postponed/string annotations.
