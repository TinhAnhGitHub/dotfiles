# Library Repositories — Functional Patterns in Hugging Face, MLflow, vLLM, verl, and ms-swift

This reference collects verified examples from current `main` branches. It is not a style
scorecard: high-performance libraries deliberately keep imperative code in hot loops. The useful
question is **where is behavior selected, configured, registered, or wrapped?** Those boundaries
are where chapters 7–10 patterns usually improve extensibility and correctness.

## Distilled lessons

| Symptom | Functional pattern | Typical payoff |
|---|---|---|
| A name selects a model, backend, task, or reward | `dict[str, Callable]` / registry | Add one implementation without editing a central `if/elif` chain |
| A framework calls a function later | `partial`, a closure, or a typed callable alias | Bind configuration without globals or hidden state |
| A function needs cross-cutting behavior | Decorator factory + `ParamSpec` + `@wraps` | Preserve signatures and make policy reusable |
| A pipeline step must carry state | Callable object with `__call__` | Keep state and invocation syntax together |
| A plugin must extend a closed core | Registry decorator + duplicate validation | Explicit, discoverable extension point |
| A selection is repeated in a hot path | Resolve the strategy once at setup | Avoid per-token/per-request reflection or dispatch |

**Boundary rule:** use functional indirection for initialization, plugin wiring, request routing,
and configuration. Do not replace tensor kernels, schedulers, or stateful distributed workers with
generic dispatch inside their hot loops merely to make them look functional.

---

## Hugging Face Transformers and Hub

**Source basis:**

- Transformers `main` at commit
  [`0c92811846095910816a87aca50050d10c545270`](https://github.com/huggingface/transformers/commit/0c92811846095910816a87aca50050d10c545270).
- Hub `main` at commit
  [`ee0a4510f4bc15e26cb722be2efc2bdb01383ca0`](https://github.com/huggingface/huggingface_hub/commit/ee0a4510f4bc15e26cb722be2efc2bdb01383ca0).

### Usage

- **Transformers — callable strategy pipeline (ch. 7/10).**
  `src/transformers/generation/logits_process.py:49-98`
  ([source](https://github.com/huggingface/transformers/blob/0c92811846095910816a87aca50050d10c545270/src/transformers/generation/logits_process.py#L49-L98))
  defines a `LogitsProcessor.__call__` contract and a `LogitsProcessorList.__call__` that
  composes processors:
  ```python
  class LogitsProcessorList(list):
      def __call__(self, input_ids, scores, **kwargs):
          for processor in self:
              scores = processor(input_ids, scores, **kwargs)
          return scores
  ```
  Stateful processors become interchangeable strategies, while the list owns orchestration.

- **Transformers — parameterized class registry (ch. 7/10).**
  `src/transformers/activations.py:224-228,324-357`
  ([source](https://github.com/huggingface/transformers/blob/0c92811846095910816a87aca50050d10c545270/src/transformers/activations.py#L224-L228))
  stores either a class or `(class, kwargs)` in `ACT2CLS`; `ClassInstantier.__getitem__` turns a
  lookup into construction:
  ```python
  class ClassInstantier(OrderedDict):
      def __getitem__(self, key):
          content = super().__getitem__(key)
          cls, kwargs = content if isinstance(content, tuple) else (content, {})
          return cls(**kwargs)
  ```
  This separates the activation vocabulary from construction policy.

- **Transformers — lazy auto-model mapping (ch. 7/10).**
  `src/transformers/models/auto/auto_factory.py:575-616,665-680`
  ([source](https://github.com/huggingface/transformers/blob/0c92811846095910816a87aca50050d10c545270/src/transformers/models/auto/auto_factory.py#L575-L616))
  maps config classes to model classes and imports the target module only when looked up. This is
  a dispatch table plus lazy factory: extensibility without importing every architecture.

- **Transformers — structural protocols (ch. 8).**
  `src/transformers/_typing.py:21-39,134-165`
  ([source](https://github.com/huggingface/transformers/blob/0c92811846095910816a87aca50050d10c545270/src/transformers/_typing.py#L21-L39))
  uses `Protocol` for logger/model shapes consumed by generic code:
  ```python
  class TransformersLogger(Protocol):
      name: str
      level: int
      def warning_once(self, msg: object, *args: object, **kwargs: object) -> None: ...
  ```
  Implementations need the behavior, not nominal inheritance.

- **Hub — typed domain plus deterministic ordering (ch. 7/8).**
  `src/huggingface_hub/utils/_cache_manager.py:21-34,545-582`
  ([source](https://github.com/huggingface/huggingface_hub/blob/ee0a4510f4bc15e26cb722be2efc2bdb01383ca0/src/huggingface_hub/utils/_cache_manager.py#L21-L34))
  combines `REPO_TYPE_T = Literal["model", "dataset", "space"]` with `sorted(..., key=lambda
  ...)`, making the accepted vocabulary and deterministic projection explicit.

- **Hub — validation decorator with preserved metadata (ch. 9).**
  `src/huggingface_hub/utils/_validators.py:41-90`
  ([source](https://github.com/huggingface/huggingface_hub/blob/ee0a4510f4bc15e26cb722be2efc2bdb01383ca0/src/huggingface_hub/utils/_validators.py#L41-L90))
  captures `inspect.signature(fn)`, validates selected arguments in a closure, and returns an
  `@wraps(fn)` wrapper. This is the right shape for a cross-cutting validation policy.

- **Hub — webhook registry and upload observer closure (ch. 7/9/10).**
  `_webhooks_server.py:104-178` stores callbacks by route and later attaches them to FastAPI;
  `_upload_pipeline.py:193-214` returns a callback that captures `prev` and updates byte
  accounting. These demonstrate registry-backed extension and isolated per-operation closure
  state.

### Opportunities

- `huggingface_hub/inference/_providers/__init__.py:96-211,241-263` eagerly stores helper
  instances in `PROVIDERS`. If helpers become stateful, use a parallel
  `PROVIDER_FACTORIES` table with `partial(HFInferenceTask, "text-generation")` and construct on
  lookup. Keep the current eager form while helpers are cheap and intentionally reusable.

- `huggingface_hub/_webhooks_server.py:142-156` registers a decorated function but the inner
  decorator does not return it. Add `return func` so `@server.add_webhook()` preserves the normal
  decorator contract and the decorated name remains callable. This is a correctness fix, not a
  stylistic rewrite.

- `transformers/generation/logits_process.py:86-98` inspects each processor signature during
  invocation. A setup-time processor plan could cache the extra parameter names, but only if list
  mutation is controlled. Generation is performance-sensitive; do not add a generic lookup per
  generated token.

---

## MLflow

**Source basis:** MLflow `master` at commit
[`cd13d3cdc9d14a5524295fcd934ac00d3465a116`](https://github.com/mlflow/mlflow/commit/cd13d3cdc9d14a5524295fcd934ac00d3465a116).

### Usage

- **Typed tracing decorator factory (ch. 8/9/10).**
  `mlflow/tracing/fluent.py:91-120,251-296,299-377,434-452`
  ([source](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/tracing/fluent.py#L91-L120))
  uses `ParamSpec`, `TypeVar`, overloads, closures, and `@wraps` so both `@trace` and
  `@trace(...)` preserve the user function’s callable shape. `output_reducer: Callable[...]` is a
  strategy passed into the wrapper rather than hard-coded.

- **Scoped tracing context (ch. 9).**
  `mlflow/tracing/context.py:23-45,103-123`
  ([source](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/tracing/context.py#L23-L45))
  uses `@contextmanager` and `ContextVar` tokens to merge nested metadata and restore the prior
  context in `finally`. This is a good example where a context manager is safer than a mutable
  global or manual reset API.

- **Programmatic decorator composition (ch. 7/9/10).**
  `mlflow/pyfunc/model.py:972-1002`
  ([source](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/pyfunc/model.py#L972-L1002))
  discovers callable `predict`/`predict_stream` methods, applies tracing, then validation
  wrappers. The reducer is a first-class callable; the model class is transformed without asking
  every user to hand-stack decorators.

- **Cached signature validation (ch. 8/9).**
  `mlflow/pyfunc/utils/data_validation.py:32-81,145-147`
  ([source](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/pyfunc/utils/data_validation.py#L32-L81))
  combines `NamedTuple` metadata, `@wraps`, `@lru_cache`, and layered warning decorators. Cache
  expensive type-hint inspection by function identity when the function and its annotations are
  stable.

- **MCP metadata registry decorator (ch. 7/9/10).**
  `mlflow/mcp/decorator.py:24-53` and `mcp/server.py:92-181`
  ([source](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/mcp/decorator.py#L24-L53))
  uses a typed decorator factory:
  ```python
  F = TypeVar("F", bound=Callable)

  def mlflow_mcp(tool_name: str) -> Callable[[F], F]:
      def decorator(fn: F) -> F:
          setattr(fn, MCP_METADATA_ATTR, {"tool_name": tool_name})
          return fn
      return decorator
  ```
  Metadata is attached without replacing the callable; the server later filters and exposes the
  selected commands.

- **Scorer as strategy and configured partial (ch. 7/8/9/10).**
  `mlflow/genai/scorers/base.py:48-50,1265-1297`
  ([source](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/genai/scorers/base.py#L1265-L1297))
  types aggregation as `Literal[...] | Callable[...]`, supports bare/configured decorator forms,
  and uses `functools.partial` to bind scorer metadata. A user function becomes a uniform callable
  scorer object.

- **Store/context/tool registries (ch. 7/10).**
  `genai/scorers/registry.py:239-302`, `tracking/context/registry.py:19-98`, and
  `genai/judges/tools/registry.py:21-75` all separate a key from a builder/provider/tool
  callable. The judge registry selects a tool by name and optionally wraps its `.invoke` method
  with tracing.

- **Compatibility decorators (ch. 8/9).**
  `mlflow/utils/annotations.py:213-287`
  ([source](https://github.com/mlflow/mlflow/blob/cd13d3cdc9d14a5524295fcd934ac00d3465a116/mlflow/utils/annotations.py#L213-L287))
  uses `ParamSpec`, `TypeVar`, decorator factories, `@wraps`, and explicit `__signature__` repair.
  Public compatibility layers are a strong reason to preserve metadata rather than writing a
  generic untyped wrapper.

### Opportunities

- `mlflow/tracing/provider.py:794-904` has a hard-coded `isinstance` chain for span destinations
  and even notes a future entry-point registry. A private destination-key → processor-builder
  registry would make new exporters additive. Preserve precedence, lazy imports, and failure
  isolation.

- `mlflow/pyfunc/scoring_server/__init__.py:276-375` has a MIME `if/elif` chain. Extract local
  parser callables keyed by content type, then select the output formatter as a strategy. Keep
  exact 415 responses and unified-LLM handling unchanged.

- `mlflow/mcp/server.py:201-246` repeats six category-selection branches. A category → command
  source table plus one comprehension would centralize collection while preserving insertion
  order and duplicate behavior.

- `mlflow/utils/autologging_utils/events.py:7-16` has an exception-swallowing decorator that
  accepts only `*args`, omits `@wraps`, and discards returns. A `ParamSpec` wrapper with
  `*args: P.args, **kwargs: P.kwargs` and `@wraps` improves custom hook compatibility while
  preserving the intentional “instrumentation failure never escapes” policy.

---

## vLLM

**Source basis:** vLLM `main` at commit
[`ae256289956945c750d5b3cd13848dc734501a6d`](https://github.com/vllm-project/vllm/commit/ae256289956945c750d5b3cd13848dc734501a6d).

### Usage

- **Custom-op registration decorator (ch. 7/10).**
  `vllm/model_executor/custom_op.py:313-327`
  ([source](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/model_executor/custom_op.py#L313-L327))
  stores a class in `op_registry` and returns the class, so a decorated definition remains usable
  while becoming discoverable by name. `register_oot` provides an out-of-tree override path.

- **Backend method selected once (ch. 7/10).**
  `vllm/model_executor/custom_op.py:174-207` selects `forward_hip`, `forward_cpu`, or another
  bound method based on the platform, then calls the selected strategy later. This is the correct
  shape for a performance boundary: dispatch at initialization, not on every tensor operation.

- **Model registry plus cached lazy loading (ch. 7/9/10).**
  `vllm/model_executor/models/registry.py:753-758,1057-1069`
  ([source](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/model_executor/models/registry.py#L753-L758))
  maps architecture names to module/class strategies and caches class resolution with
  `@lru_cache`.

- **Protocol-based endpoint plugins (ch. 8/10).**
  `vllm/plugins/endpoint_plugins/interface.py:43-70,91-123`
  ([source](https://github.com/vllm-project/vllm/blob/ae256289956945c750d5b3cd13848dc734501a6d/vllm/plugins/endpoint_plugins/interface.py#L43-L70))
  defines an `@runtime_checkable Protocol` with `attach_router` and lifecycle methods. Plugin
  implementations can satisfy the contract structurally.

- **Plugin entry points as callable registries (ch. 7/10).**
  `vllm/plugins/__init__.py:36-90` loads entry points into name → callable mappings, executes
  general plugin callables, and delays endpoint plugin construction. This is a clean separation
  between discovery, invocation, and factory construction.

- **Composed endpoint decorators (ch. 9/10).**
  `vllm/entrypoints/openai/chat_completion/api_router.py:40-53` stacks routing,
  cancellation, and load-aware decorators. The wrappers preserve FastAPI-visible metadata with
  `wraps`.

- **Engine-selected strategy, observer callback, and partial (ch. 7/10).**
  `vllm/v1/engine/core.py:234-235,1467-1470,1925-1945` stores either `self.step` or
  `self.step_with_batch_queue`, appends idle callbacks, and uses `partial` to bind each callback’s
  future. Configuration is resolved once; the loop invokes already-bound callables.

- **Typed decorator and run-once closure (ch. 8/9).**
  `vllm/config/utils.py:36-80,201-223` uses overloads, `TypeVar`, and `Protocol` for a dual-form
  `@config` decorator. `vllm/utils/func_utils.py:22-48` uses `ParamSpec` and a closure with a
  lock to implement `run_once`; signature support checks are cached.

- **Literal scheduler policy and key function (ch. 7/8/10).**
  `vllm/config/scheduler.py:21-22,170-191` defines `SchedulerPolicy = Literal["fcfs", "priority"]`,
  permits a user-supplied scheduler class, and uses `max(..., key=lambda ...)` in the scheduler.

### Opportunities

- `vllm/model_executor/custom_op.py:196-207` still has a platform `if/elif` chain. A
  selection-time ordered `(predicate, bound_method)` table can make supported platforms explicit,
  but the selected callable must still be cached; do not perform table iteration in `forward`.

- `vllm/entrypoints/serve/utils/api_utils.py:51-103` uses untyped `*args, **kwargs` in wrappers.
  Add `ParamSpec`/`TypeVar` callable aliases while retaining `@wraps` and the special
  `raw_request` convention. Model cancellation’s possible `None` result accurately.

- `vllm/config/compilation.py:599-604,938-953` annotates pass specs as strings while accepting
  callable objects at runtime. Normalize `str | Callable[..., Any]` through one resolver before
  building `InductorPass` objects; preserve string serialization and lazy import behavior.

- `vllm/plugins/__init__.py:36-70` could distinguish the zero-argument general-plugin command
  protocol from endpoint factories with two `Protocol` aliases. Keep current allowlisting and
  exception isolation because entry points are untrusted third-party code.

---

## verl

**Source basis:** core `verl-project/verl` at commit
[`6cbca9ce7208100d11b4d1b06eccf098cc9e76aa`](https://github.com/verl-project/verl/commit/6cbca9ce7208100d11b4d1b06eccf098cc9e76aa).
The recipe submodule is `verl-project/verl-recipe` at commit
[`e7f889574b8301cc0f0fc1d57c6d67f31ffeb689`](https://github.com/verl-project/verl-recipe/commit/e7f889574b8301cc0f0fc1d57c6d67f31ffeb689).

### Usage

- **Reward-manager registry decorator (ch. 7/9/10).**
  `verl/workers/reward_manager/registry.py:21-38`
  ([source](https://github.com/verl-project/verl/blob/6cbca9ce7208100d11b4d1b06eccf098cc9e76aa/verl/workers/reward_manager/registry.py#L21-L38))
  maps a name to a reward-manager class and returns the class from the decorator. Configuration
  chooses the class without central imports.

- **Callable reward manager with injected scoring function (ch. 7/10).**
  `verl/workers/reward_manager/naive.py:64-66,84-90,129-136` stores
  `self.compute_score = compute_score or default_compute_score` and makes the manager itself
  callable. State and orchestration live in the manager; scoring remains replaceable behavior.

- **Policy-loss function registry (ch. 7/8/10).**
  `verl/trainer/ppo/core_algos.py:37-64,70-85,113-150,1285-1286`
  ([source](https://github.com/verl-project/verl/blob/6cbca9ce7208100d11b4d1b06eccf098cc9e76aa/verl/trainer/ppo/core_algos.py#L37-L64))
  defines `PolicyLossFn`, a `POLICY_LOSS_REGISTRY`, and `@register_policy_loss` functions. New
  algorithms are additive and type-described.

- **Dispatch/collect policy as data (ch. 7/9/10).**
  `verl/single_controller/base/decorator.py:300-335,398-439` stores `partial`-bound dispatch and
  collect functions in a mode registry; sync and async wrappers use `@wraps`. The policy is data
  passed to distributed execution rather than hidden in a branch.

- **Deferred data movement callbacks (ch. 7).**
  `verl/protocol.py:1174-1207` stores `collect_fn`, `dispatch_fn`, and futures together; chunking
  specializes dispatch with `partial`. This is a command/callback object for deferred work.

- **Lazy rollout backend registry (ch. 7/10).**
  `verl/workers/rollout/base.py:88-109` maps `(backend, mode)` to qualified class paths and imports
  only the selected implementation. `workers/rollout/replica.py:302-317,377-380` uses loader
  callables for the same optional-backend problem.

- **Platform plugin registry (ch. 7/10).**
  `verl/plugin/platform/platform_manager.py:29-75,83-104` registers platform classes by name and
  discovers a matching implementation instead of hard-coding every accelerator.

- **Sync/async reward function adaptation (ch. 7/9).**
  `verl/trainer/ppo/reward.py:32-42,50-86,140-151` detects coroutine functions and returns
  partially applied sync/async callables. Sandbox configuration is also bound into the final
  scorer with `partial`.

- **Context-managed timeout and cached capability probes (ch. 9).**
  `verl/workers/reward_manager/naive.py:28-61` uses `@contextmanager` with a closure over timeout
  seconds; `verl/utils/import_utils.py:27-73` uses `@cache`/`@lru_cache` for stable capability
  checks.

### Opportunities

- `recipe/prime/main_prime.py:74-91,131-141` has worker-strategy and reward-manager `if/elif`
  chains. Use lazy worker factories plus the existing reward-manager registry; keep explicit
  validation and backend-specific assertions in each factory.

- `workers/rollout/replica.py:383-404` has a second PD-disaggregation backend branch beside the
  normal rollout registry. Add a small `PD_LOADERS` table, retaining the existing backend-load
  side effects and error message.

- `trainer/ppo/core_algos.py:193-212` selects fixed/adaptive KL controllers with two branches.
  A `KL_FACTORIES` table is reasonable only if policies will grow; for two stable choices the
  current code may remain clearer.

- `trainer/ppo/ray_trainer.py:218-265` handles GAE/GRPO specially even though other advantage
  estimators use a registry. Register adapters with a common context object and route all
  estimators through one lookup, preserving estimator-specific preprocessing.

- `workers/reward_manager/naive.py:90-165` and `reward_manager/dapo.py:58-154` repeat much of the
  item-scoring pipeline. Extract a shared pipeline accepting `score_fn`, `reward_shaper`, and an
  extra-info sink; use Naive’s identity shaper and DAPO’s penalty shaper as strategies. Preserve
  reward timing and exception semantics.

---

## ms-swift

**Source basis:** `modelscope/ms-swift` `main` at commit
[`a54a4ae5c8680451ba4ddc91ad4577a38c74d560`](https://github.com/modelscope/ms-swift/commit/a54a4ae5c8680451ba4ddc91ad4577a38c74d560).

### Usage

- **CLI route mapping (ch. 7/10).**
  `swift/cli/main.py:14-27,86-100` maps command names (`pt`, `sft`, etc.) to importable modules,
  replacing a central command branch with data-driven routing.

- **Checkpoint ordering strategy (ch. 7).**
  `swift/trainers/mixin.py:469-471` chooses `os.path.getmtime` or a local key closure and passes
  the selected callable to `sorted`. The same algorithm accepts either ordering policy.

- **Typed parser factory (ch. 8).**
  `swift/utils/utils.py:177-192` takes `class_type: Type[_T]` and returns a parsed `_T`, keeping
  the relationship between the dataclass class supplied and the result.

- **Annotated protocol fields and closed vocabularies (ch. 8).**
  `swift/infer_engine/protocol.py:13-41,230,411-423` uses `Annotated` for Pydantic serializer/
  validator metadata and `Literal` for roles and finish reasons.

- **Template/model registries (ch. 7/10).**
  `swift/template/register.py:13-20,31-52,187-191` and `swift/model/register.py:31-42` keep model
  and template metadata in mappings. Selection and instantiation are separated from implementations.

- **Callable dataset preprocessors and loaders (ch. 7/10).**
  `swift/dataset/dataset_meta.py:13,19,173-202` types preprocessing as a `Callable` and stores a
  callable object in metadata. Dataset loading and preprocessing are replaceable strategies.

- **Patch context factory (ch. 7/9).**
  `swift/model/register.py:55-70` uses `@contextmanager` and `partial(patch_automodel, **context_kwargs)`
  to create a zero-argument patching context that restores the original function after loading.

- **Retry and Ray decorator factories (ch. 9).**
  `swift/utils/utils.py:439-456` and `swift/ray_utils/base.py:91-118,141-191` configure policies
  once, return `@wraps` wrappers, and preserve callable metadata.

- **Composable loss strategies (ch. 9/10).**
  `swift/loss_scale/mapping.py:7-58` resolves named loss strategies and composes them in sequence;
  `ConcatLossScale` is a concrete strategy-composition example.

- **Callback and reward registries (ch. 7/10).**
  `swift/callbacks/mapping.py:9-16` maps callback names to constructors; reward classes in
  `swift/rewards/orm.py:16-31,460-468` are callable objects stored in a registry and extended by
  imported plugins.

### Opportunities

- `swift/pipelines/infer/infer.py:52-94` selects Transformers/vLLM/SGLang/LMDeploy through a
  growing conditional. Use typed backend-builder callables returning `(client_cls, kwargs)`;
  retain explicit unsupported-backend errors and vLLM seed side effects.

- `swift/dataset/preprocessor/core.py:686-705` selects a preprocessor by ordered feature checks.
  Represent the rules as ordered `(predicate, factory)` callables. Preserve ordering because input
  schemas overlap.

- `examples/train/grpo/plugin/deepeyes/deepeyes_plugin.py:202-218` maps data sources to score
  methods with branches. A source → scorer dispatch table makes adding a reward source additive;
  use named functions rather than lambdas if signatures differ.

- `swift/rewards/orm.py:460-468` and plugin files mutate `orms` directly. A typed
  `@register_orm(name)` decorator with duplicate detection would improve discoverability and
  diagnostics, while preserving a compatibility path for direct dictionary assignment.

---

## Cross-library review checklist

1. **Find the selection boundary.** If a backend/model/task name is resolved once, use a registry or
   factory. If it is resolved per token or tensor, first ask whether the lookup can move to setup.
2. **Type the callable boundary.** Start with `Callable`; use `Protocol` when behavior has several
   named methods; use `ParamSpec` when a decorator must preserve arbitrary arguments.
3. **Preserve decorator metadata.** Use `@wraps`, and repair `__signature__` only when the framework
   introspects it and `wraps` is insufficient.
4. **Keep registries explicit.** Reject duplicates where silently replacing a plugin would be hard
   to debug; preserve import order when it is semantically meaningful.
5. **Do not functionalize hot kernels.** Transformers generation, vLLM attention, and verl
   distributed execution use imperative/stateful code for good reasons. Refactor setup, plugins,
   wrappers, and duplicated selection logic first.
