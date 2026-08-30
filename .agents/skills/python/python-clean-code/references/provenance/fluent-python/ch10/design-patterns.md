# Ch. 10 — Design Patterns with First-Class Functions

The central refactoring move is not “replace every class.” It is **move variation into a value**:
a function, callable object, registry entry, hook, or small strategy record. Keep a class when it
owns substantial state, invariants, or a lifecycle. Use functions when the variation is behavior.

## Distilled patterns

### S1. Strategy = a function when the strategy has one operation

```python
def score_default(item): ...
def score_strict(item): ...

def evaluate(items, score):
    return [score(item) for item in items]
```

Use a callable object if the strategy needs state or extra operations. Do not create an ABC and one
subclass per one-line algorithm.

### S2. Dispatch table = data-driven selection

```python
HANDLERS: dict[str, Callable[[Request], Response]] = {
    "json": parse_json,
    "csv": parse_csv,
}
return HANDLERS[content_type](request)
```

Use an ordered predicate table when dispatch depends on `isinstance` or overlapping conditions.
Keep a helpful error for unknown keys.

### S3. Registry decorator = additive extension

```python
REGISTRY: dict[str, Callable[..., object]] = {}

def register(name: str):
    def decorate(factory):
        if name in REGISTRY:
            raise ValueError(f"duplicate registration: {name}")
        REGISTRY[name] = factory
        return factory
    return decorate
```

Use this for plugins, tools, model architectures, reward functions, and templates. If import order
or duplicate resolution is business logic, prefer explicit registration.

### S4. Command = callable stored as data

An operation can be queued, retried, passed to an executor, or selected by name without a command
subclass:

```python
commands = {"refresh": refresh_cache, "shutdown": shutdown}
executor.submit(commands[action])
```

Use `partial` to bind command context. Use a callable object when the command needs state and
diagnostics.

### S5. Observer/hooks = a collection of callbacks

```python
listeners: list[Callable[[Event], None]] = []

def subscribe(listener):
    listeners.append(listener)

def publish(event):
    for listener in tuple(listeners):
        listener(event)
```

Define error, ordering, removal, and concurrency semantics. A bare list is not enough if those
semantics matter.

### S6. Compose strategies instead of branching through a pipeline

```python
pipeline = [normalize, validate, enrich]
for step in pipeline:
    value = step(value)
```

Named functions make the pipeline testable. Use a class only when the pipeline needs persistent
mutable state, cancellation, or lifecycle management.

### S7. Resolve once at setup for hot paths

```python
self.step_fn = self.step if use_queue else self.step_without_queue
...
self.step_fn(batch)
```

The functional design is not “lookup on every call”; it is “select a callable once, then invoke it
cheaply.”

## Verified examples

### 1. AG2 — function-call dispatch through a map

- **Files:** `autogen/agentchat/conversable_agent.py:3117,3492-3507`
- **Source:** [AG2 v0.8.7](https://github.com/ag2ai/ag2/blob/v0.8.7/autogen/agentchat/conversable_agent.py#L3117)
- **Context:** an LLM tool-call name must resolve to a registered function/tool.
- **Pattern:** AG2 maintains a function map and `execute_function` looks up the callable before
  executing it, rather than keeping a large function-name `if/elif` chain.
- **Solves:** `EXTENSIBILITY` and `READABILITY`: adding a tool changes registration, not executor
  control flow.

### 2. AG2 — reply hooks implement an observer/template boundary

- **File:** `autogen/agentchat/conversable_agent.py:538-650`
- **Source:** [AG2 v0.8.7](https://github.com/ag2ai/ag2/blob/v0.8.7/autogen/agentchat/conversable_agent.py#L538)
- **Context:** agents register reply functions with trigger conditions, position, and optional
  configuration; the reply loop invokes matching hooks.
- **Pattern:** a hook registry stores callbacks and the core loop asks the hooks whether they can
  produce a reply.
- **Solves:** `EXTENSIBILITY` and `SEPARATION OF CONCERNS`: new reply policies do not modify the
  conversation loop.

### 3. Transformers — callable processors compose a strategy pipeline

- **File:** `src/transformers/generation/logits_process.py:49-98`
- **Source:** [Transformers pinned source](https://github.com/huggingface/transformers/blob/0c92811846095910816a87aca50050d10c545270/src/transformers/generation/logits_process.py#L49-L98)
- **Real shape:**
  ```python
  class LogitsProcessorList(list):
      def __call__(self, input_ids, scores, **kwargs):
          for processor in self:
              scores = processor(input_ids, scores, **kwargs)
          return scores
  ```
- **Context:** each processor is a stateful callable strategy; the list composes them.
- **Solves:** `EXTENSIBILITY` without sacrificing stateful processors or forcing a huge generation
  loop to know every sampling policy.

### 4. Hugging Face Transformers — activation registry with construction policy

- **File:** `src/transformers/activations.py:224-228,324-357`
- **Source:** [Transformers pinned source](https://github.com/huggingface/transformers/blob/0c92811846095910816a87aca50050d10c545270/src/transformers/activations.py#L224-L228)
- **Pattern:** `ACT2CLS` stores class values or `(class, kwargs)` specifications; `ClassInstantier`
  turns lookup into construction.
- **Solves:** `EXTENSIBILITY` and `DYNAMIC RUNTIME CONSTRUCTION`: model configuration selects an
  activation without a branch per activation.

### 5. vLLM — model and backend registries with lazy loading

- **Files:** `vllm/model_executor/models/registry.py:753-758,1057-1069`,
  `vllm/v1/attention/backends/registry.py:132-173,243-295`
- **Source:** [vLLM model registry](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/model_executor/models/registry.py#L753-L758)
- **Pattern:** architecture names map to lazy module/class loaders; attention backends accept
  decorator/direct overrides.
- **Solves:** `EXTENSIBILITY` and `STARTUP COST`: optional architectures/backends are imported only
  when selected.

### 6. vLLM — setup-time strategy selection and parameterized observers

- **File:** `vllm/v1/engine/core.py:234-235,1467-1470,1925-1945`
- **Source:** [vLLM engine core](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/v1/engine/core.py#L234-L235)
- **Real shape:**
  ```python
  self.step_fn = self.step if self.batch_queue is None else self.step_with_batch_queue
  self._idle_state_callbacks.append(partial(engine_idle_callback, future=future))
  ```
- **Solves:** `PERFORMANCE` (no repeated mode selection), `EXTENSIBILITY` (callbacks), and
  `DYNAMIC RUNTIME CONSTRUCTION` (future context is bound once).

### 7. verl — policy losses are registered functions

- **File:** `verl/trainer/ppo/core_algos.py:37-64,70-85,113-150`
- **Source:** [verl pinned source](https://github.com/verl-project/verl/blob/6cbca9ce7208100d11b4d1b06eccf098cc9e76aa/verl/trainer/ppo/core_algos.py#L37-L64)
- **Pattern:** `POLICY_LOSS_REGISTRY` stores functions under names; `@register_policy_loss` makes
  adding a loss additive.
- **Solves:** `EXTENSIBILITY` and `TESTABILITY`: a loss is a direct function that can be unit
  tested independently from trainer orchestration.

### 8. verl — rollout backend/mode is a lazy strategy table

- **File:** `verl/workers/rollout/base.py:88-109`
- **Source:** [verl pinned source](https://github.com/verl-project/verl/blob/6cbca9ce7208100d11b4d1b06eccf098cc9e76aa/verl/workers/rollout/base.py#L88-L109)
- **Pattern:** `("vllm", "async")` and similar keys resolve to qualified class paths, imported
  only at lookup time.
- **Solves:** `EXTENSIBILITY` and `OPTIONAL DEPENDENCY ISOLATION`: the main process need not import
  every rollout backend.

### 9. ms-swift — model/template registries separate selection from implementation

- **Files:** `swift/template/register.py:13-20,31-52,187-191`,
  `swift/model/register.py:31-42`
- **Source:** [ms-swift template registry](https://github.com/modelscope/ms-swift/blob/a54a4ae5c8680451ba4ddc91ad4577a38c74d560/swift/template/register.py#L13-L20)
- **Pattern:** metadata maps model/template names to classes, loaders, and architecture details;
  selection returns the registered class.
- **Solves:** `EXTENSIBILITY` and `READABILITY`: model-specific behavior is declarative and
  co-located with registration.

### 10. MLflow — URI schemes and tools resolve through registries

- **Files:** `mlflow/genai/scorers/registry.py:239-302`,
  `mlflow/genai/judges/tools/registry.py:21-75`
- **Source:** [MLflow scorer registry](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/genai/scorers/registry.py#L239-L302)
- **Pattern:** a scheme/name maps to a builder or callable tool object; optional tracing decorates
  the selected tool invocation.
- **Solves:** `EXTENSIBILITY` and `SEPARATION OF CONCERNS`: storage/tool selection is separate from
  invocation and instrumentation.

### 11. LlamaIndex — `FunctionTool` is the command object for sync/async tools

- **File:** `llama_index/core/tools/function_tool.py:71-94,174-190`
- **Source:** [LlamaIndex current source](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/tools/function_tool.py#L71-L94)
- **Pattern:** a function tool object stores sync/async functions, metadata, and optional callback
  strategies. It remains callable through the tool interface but can expose schema and output
  handling.
- **Solves:** `STATE` and `EXTENSIBILITY`: a plain function is enough for the operation; the object
  adds tool-specific metadata and lifecycle only where needed.

## Refactoring opportunities found in real repositories

These are deliberately conservative: they target selection/setup boundaries, not tensor or
distributed hot loops.

- **MLflow MIME dispatch** — `pyfunc/scoring_server/__init__.py:276-375` uses a growing CSV/JSON/
  Parquet branch. Extract a local content-type → parser table, preserving exact errors and lazy
  dependencies. This is a textbook S2 dispatch-table refactor.

- **vLLM platform selection** — `model_executor/custom_op.py:196-207` has a platform chain. An
  ordered predicate → bound-method table can clarify precedence, but selection must still happen
  once during initialization. Do not table-lookup in `forward`.

- **ms-swift inference backend selection** — `swift/pipelines/infer/infer.py:52-94` branches over
  Transformers/vLLM/SGLang/LMDeploy. Extract typed backend builders returning `(client_cls, kwargs)`;
  preserve backend-specific seed/distributed mutations and explicit unsupported errors.

- **verl KL-controller selection** — `trainer/ppo/core_algos.py:193-212` has fixed/adaptive
  branches. A factory table is worthwhile only if policies will grow; for two stable choices the
  current branches may be more readable.

- **AG2 reply behavior** — if a new reply policy is currently added by editing the conversation
  loop, move it into the existing trigger/position hook registry instead. The registry already
  defines the right S5 observer boundary.

## Pattern selection decision

1. One algorithm, no state → plain function.
2. One algorithm plus persistent state → callable object.
3. Name selects one of several implementations → dispatch table or registry.
4. External code adds implementations → registry decorator/entry point.
5. Several independent reactions → observer hooks.
6. Same pipeline with variable steps → list of callables.
7. Selection happens once, invocation is hot → bind the selected callable during setup.
