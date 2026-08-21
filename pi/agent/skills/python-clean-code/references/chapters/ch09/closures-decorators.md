# Ch. 9 — Closures and Decorators

Decorators are higher-order functions: they receive a callable and return a callable (or a
callable-like object). Closures provide the private configuration/state that the returned object
needs. The production rule is simple: **make the wrapper transparent unless deliberately changing
the callable’s interface.**

## Distilled patterns

### D1. Decorator factory: configuration → decorator → wrapper

```python
def retry(attempts: int = 3):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == attempts - 1:
                        raise
        return wrapper
    return decorate
```

The outer function captures configuration; the middle function receives the target; the inner
function runs at call time.

### D2. Always preserve metadata for transparent wrappers

Use `@functools.wraps(fn)`. Frameworks inspect `__name__`, `__doc__`, annotations, and sometimes
`__wrapped__`/`__signature__`. If a wrapper intentionally changes the signature, repair it
explicitly and document the new contract.

### D3. A decorator may return a different callable object

Tool decorators often return `Tool`, `Function`, or `StepFunction`, not the original function. That
is correct when the returned object adds schema, hooks, execution policy, or state. Type the change
with overloads; do not pretend the function is unchanged.

### D4. Use attributes as a narrow communication channel between stacked decorators

One decorator can attach a sentinel or metadata attribute; a later decorator can read it. Keep
attribute names private and collision-resistant, and return the function. For more complex state,
use an explicit registry or wrapper object.

### D5. Use `contextmanager` for acquire/restore lifecycle

```python
@contextmanager
def temporary_setting(value):
    old = get_setting()
    set_setting(value)
    try:
        yield
    finally:
        set_setting(old)
```

The `finally` block is the important part: cleanup happens on exceptions and nested scopes restore
their own previous values.

### D6. Cache only pure/stable observations

`cache`/`lru_cache` are excellent for signature inspection, capability probes, and immutable
configuration resolution. They are wrong for mutable registries unless registration invalidates the
cache.

### D7. Prefer a closure for small private state; use a class when state has a public lifecycle

A closure is ideal for `prev_bytes`, a retry count, or a bound configuration. If callers need
`reset`, `close`, metrics, or several operations, a callable object makes the lifecycle visible.

## Verified examples

### 1. AG2 — decorator factories register one function for two agents

- **File:** `autogen/agentchat/conversable_agent.py:3547-3620,3648-3692`
- **Source:** [AG2 v0.8.7](https://github.com/ag2ai/ag2/blob/v0.8.7/autogen/agentchat/conversable_agent.py#L3547-L3620)
- **Context:** `register_for_llm(...)` captures name/description/API style, then returns a decorator
  that converts the target into a `Tool`, registers it, appends it, and returns the tool.
- **Real shape:**
  ```python
  def register_for_llm(..., api_style: Literal["function", "tool"] = "tool"):
      def _decorator(func_or_tool, name=name, description=description) -> Tool:
          tool = self._create_tool_if_needed(func_or_tool, name, description)
          self._register_for_llm(tool, api_style, silent_override=silent_override)
          self._tools.append(tool)
          return tool
      return _decorator
  ```
  Stacking `@user_proxy.register_for_execution()` over
  `@agent2.register_for_llm()` shares the same function definition across roles.
- **Solves:** `EXTENSIBILITY`, `READABILITY`, and `DYNAMIC RUNTIME CONSTRUCTION`.

### 2. LangChain — `@tool` supports bare and configured forms

- **File:** `langchain_core/tools/convert.py:17-89`
- **Source:** [LangChain current source](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/tools/convert.py#L17-L89)
- **Real shape:** multiple overloads describe `@tool`, `@tool(...)`, named Runnables, and direct
  callable conversion; one runtime implementation returns a `BaseTool` or a decorator.
- **Context:** the returned object deliberately differs from the function because it carries an
  inferred schema, description, and execution behavior.
- **Solves:** `EXTENSIBILITY`: a regular function becomes a model-facing tool without duplicating
  schema construction at every call site.

### 3. Agno — `@tool` is a typed function-to-`Function` adapter

- **File:** `agno/tools/decorator.py:1-112`
- **Source:** [Agno current source](https://github.com/agno-agi/agno/blob/main/libs/agno/agno/tools/decorator.py#L56-L112)
- **Real shape:** `@overload` declarations describe bare/configured use; the runtime decorator
  returns a `Function` and accepts `pre_hook`, `post_hook`, and `tool_hooks` callables.
- **Solves:** `EXTENSIBILITY` (hooks are injected), `CORRECTNESS` (tool metadata is explicit), and
  `READABILITY` (one decorator replaces repetitive adapter construction).

### 4. LlamaIndex Workflows — `@step` captures execution policy and attaches metadata

- **File:** `packages/llama-index-workflows/src/workflows/decorators.py:118-214,241-244`
- **Source:** [LlamaIndex Workflows](https://github.com/run-llama/llama-agents/blob/main/packages/llama-index-workflows/src/workflows/decorators.py#L118-L214)
- **Real shape:** `@step` supports bare/configured forms; its closure captures worker count,
  retry policy, workflow, and graph checks, then attaches `_step_config` to the callable.
- **Context:** this decorator changes the function’s role in the workflow graph while preserving its
  invocation contract via `StepFunction`.
- **Solves:** `EXTENSIBILITY` and `READABILITY`: execution policy lives beside the step definition.

### 5. LlamaIndex — sync/async adapters use closures at the execution boundary

- **File:** `llama_index/core/tools/function_tool.py:39-64`
- **Source:** [LlamaIndex current source](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/tools/function_tool.py#L39-L64)
- **Real shape:** `sync_to_async` returns `_async_wrapped_fn`, and `async_to_sync` returns
  `_sync_wrapped_fn`; each closure captures the original function.
- **Solves:** `CORRECTNESS` and `READABILITY`: sync/async conversion is isolated in one reusable
  policy rather than scattered through every tool call.

### 6. MLflow — `@trace` is a typed dual-form decorator

- **File:** `mlflow/tracing/fluent.py:91-120,251-296`
- **Source:** [MLflow master](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/tracing/fluent.py#L91-L120)
- **Real shape:** overloads support bare/configured use; `ParamSpec` preserves the target
  signature; a closure captures span settings and output reducers; wrapping uses `@wraps`.
- **Solves:** `CORRECTNESS`: adding tracing does not make every function appear as
  `(*args, **kwargs) -> Any` to tools and IDEs.

### 7. Hugging Face Hub — validation decorator captures a signature once

- **File:** `huggingface_hub/utils/_validators.py:41-90`
- **Source:** [Hub current source](https://github.com/huggingface/huggingface_hub/blob/ee0a4510f4bc15e26cb722be2efc2bdb01383ca0/src/huggingface_hub/utils/_validators.py#L41-L90)
- **Real shape:** `validate_hf_hub_args` captures `inspect.signature(fn)`, validates selected
  arguments in a closure, and returns an `@wraps(fn)` wrapper.
- **Solves:** `READABILITY` and `CORRECTNESS`: cross-cutting validation is centralized while
  function metadata remains visible.

### 8. vLLM — stacked request decorators preserve framework introspection

- **File:** `vllm/entrypoints/openai/chat_completion/api_router.py:40-53` and
  `vllm/entrypoints/serve/utils/api_utils.py:51-101`
- **Source:** [vLLM router](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/entrypoints/openai/chat_completion/api_router.py#L40-L53)
- **Real shape:** a route decorator is stacked with cancellation and load-aware wrappers, each
  preserving metadata.
- **Context:** decorator order is part of the behavior: route registration must see the final
  callable while cancellation/load accounting wraps execution.
- **Solves:** `EXTENSIBILITY` and `CORRECTNESS`; it also illustrates why `@wraps` is not optional
  in web/agent frameworks.

### 9. vLLM — `run_once` closure plus `ParamSpec`

- **File:** `vllm/utils/func_utils.py:22-48`
- **Source:** [vLLM current source](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/utils/func_utils.py#L22-L48)
- **Real shape:** the decorator keeps `has_run` and a lock in closure state, while
  `Callable[P, None] -> Callable[P, None]` preserves arguments.
- **Solves:** `STATE` (private one-shot state), `CORRECTNESS` (thread-safe one-shot execution), and
  `READABILITY`.

### 10. MLflow — `contextmanager` restores nested trace context

- **File:** `mlflow/tracing/context.py:23-45,103-123`
- **Source:** [MLflow master](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/tracing/context.py#L23-L45)
- **Real shape:** a context manager stores a `ContextVar` token, yields, then resets the token in
  `finally`.
- **Solves:** `CORRECTNESS` for nested/exceptional scopes; manual “set then reset” calls are easy
  to forget.

### 11. `returns` — typed curry and partial application

- **File:** `returns/curry.py:10-59`
- **Source:** [returns current source](https://github.com/dry-python/returns/blob/master/returns/curry.py#L10-L59)
- **Real shape:** a typed `partial` wraps `functools.partial`; `curry` repeatedly returns closures
  until enough arguments are supplied.
- **Solves:** `READABILITY` and `CORRECTNESS` at higher-order functional boundaries. Use this for
  composable policies, not ordinary two-line calls where a named function is clearer.

## Common decorator failures

- **Metadata loss:** wrapper has the wrong `__name__`, docstring, annotations, or signature. Fix
  with `@wraps`; repair `__signature__` only when necessary.
- **Unclear return type:** a function-to-tool decorator returns a different object but is annotated
  as returning the original function. Use overloads and a named wrapper type.
- **Hidden global state:** a decorator mutates a module-level registry without duplicate checks or
  reset behavior. Use a registry object or make registration explicit in tests.
- **Wrong stacking order:** route, tracing, retry, auth, and caching decorators have different
  boundaries. Write a small order test and inspect `__wrapped__`.
- **Caching mutable observations:** cache only stable inputs or invalidate when registry/config
  state changes.
