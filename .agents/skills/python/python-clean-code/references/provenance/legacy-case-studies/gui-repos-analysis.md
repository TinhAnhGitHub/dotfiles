# GUI Repositories — Ch. 7–10 Functional-Pattern Review

This review covers the GUI-agent repositories under
`/home/tinhanhnguyen/Desktop/project/reference/`. It focuses on Python source and distinguishes
existing good usage from places where a functional pattern would reduce duplication or unsafe
dispatch. It does **not** recommend refactoring every class: stateful agents, device drivers, and
distributed workers often need classes.

## Cross-repository findings

The most common problem is string/enum dispatch spread through large `if/elif` functions. The
strongest fixes are:

1. **Dispatch table:** `name -> callable` for independent branches.
2. **Strategy function:** pass the varying operation into shared orchestration.
3. **Registry decorator:** make plugin/tool/model extension additive.
4. **Decorator factory:** centralize retries, authorization, or instrumentation.
5. **Protocol + Callable:** type behavior without forcing inheritance.
6. **Setup-time binding:** resolve the strategy once; do not add a lookup to a hot loop.

The strongest positive examples are CogAgent’s `META_OPERATION`, ClawGUI’s inferencer registry,
SCALE-CUA’s `EventBus`, TuriX-CUA’s action registry, and deer-flow-agent’s `ParamSpec` auth
decorators. The strongest refactor targets are InfiGUI-G1’s benchmark normalizer, SCALE-CUA’s
duplicated agent loops, and agent-s/ClawGUI’s duplicated handlers.

---

## agent-s

### Existing usage

- `gui_agents/s3/agents/worker.py:312` — `functools.partial` binds an agent and observation into
  a format-checker callback.
- `gui_agents/s3/utils/formatters.py:16-55` — lambdas are injected as validation hooks.
- `gui_agents/s3/agents/grounding.py:25-27,346+` — `@agent_action` marks action methods; a
  decorator-backed action boundary is present, although the metadata is underused.
- `gui_agents/s2/core/knowledge.py:192,229` — similarity results are ranked with a first-class
  key/sort operation.

### Opportunities

- `gui_agents/s3/core/engine.py:19-445` — nine provider classes repeat API-key lookup, client
  construction, and completion calls. **Problem:** a new provider copies 40–60 lines.
  **Fix:** one provider-compatible engine plus a `make_engine(env_key, build_client, ...)` closure or
  partials for provider-specific configuration. Keep genuinely different request protocols as
  separate strategies.
- `gui_agents/s3/core/mllm.py:22-102` — a long engine-type `if/elif` chain. **Fix:** an engine
  registry plus small parameter-normalization callables.
- `gui_agents/s3/agents/code_agent.py:38-43` — bash/python dispatch by string. **Fix:**
  `{"bash": run_bash, "python": run_python}` with an explicit unknown-type error.
- `gui_agents/s3/agents/grounding.py:25` and `worker.py:224` — the marker decorator does not
  build a registry; generated code is executed with `eval`. **Problem:** unsafe and unverifiable
  dispatch. **Fix:** registry decorator + `ast.parse`/validated action nodes; never `eval` model
  output.

---

## ClawGUI

### Existing usage

- `clawgui-eval/inference/__init__.py:18-56` — model-name → inferencer registry/factory.
- `clawgui-agent/phone_agent/actions/handler.py:90-108` — action-name → bound-handler dispatch.
- `handler.py:36-43` — injected `Callable[[str], bool]` confirmation/takeover callbacks.
- `clawgui-eval/judge/base_judge.py:103-163` — template method with abstract evaluation hooks.
- `clawgui-rl/.../env_manager.py:1155-1202` — projection strategies selected with `partial`.

### Opportunities

- `phone_agent/actions/handler.py:24` plus the model-specific handlers — five near-identical
  handler classes repeat tap/type/swipe/wait execution. **Problem:** a typing change needs five
  edits. **Fix:** shared device primitives + one action dispatch table; model handlers only parse
  responses and map action names.
- `phone_agent/model/adapters.py:843-879` — model detection is a regex `if/elif` chain. **Fix:**
  ordered `(compiled_pattern, ModelType)` rules and `next(...)` with a default.
- `phone_agent/device_factory.py:33-46,128-139` — the same `DeviceType` mapping is duplicated
  for modules and connections. **Fix:** two lazy factory maps derived from one device spec.
- `phone_agent/agent.py:107-128,424-435,669-675` — model-specific behavior is scattered in
  repeated chains despite an adapter registry. **Fix:** `adapter.build_messages(...)` and
  `adapter.handle_response(...)` strategy methods.

---

## CogAgent

### Existing usage

- `app/register.py:145-163` — `META_OPERATION` maps operation names to callables.
- `app/register.py:19-37` — `META_PARAMETER` is data-driven operation metadata.
- `app/client.py:483` — `partial` binds Gradio workflow context.
- `app/vllm_openai_server.py:33` — `@asynccontextmanager` manages FastAPI lifespan.

### Opportunities

- `app/register.py:63-130` — many one-line functions differ only by the PyAutoGUI function or
  scroll sign. **Fix:** `box_action(pyautogui_fn)` and parameterized scroll strategies.
- `app/register.py:19-37,145-163` — parameter metadata and operation callable are parallel maps.
  **Problem:** names can drift. **Fix:** one `OPS = {name: (callable, parameters)}` specification,
  then derive validation and dispatch maps.
- `app/register.py:40-49` and `app/client.py:91-112` — duplicated `identify_os`. **Fix:** one
  shared function; `lru_cache` is appropriate if the process OS is immutable.

---

## dart-gui

### Existing usage

- `validation/model_service.py:744-761` — `@asynccontextmanager` plus `min(..., key=...)` picks
  and releases the least-loaded endpoint.
- `validation/task_loader.py:136,142` — `max(..., key=...)` and `iter(lambda: read(...), b"")`.
- `validation/trajectory_runner.py:445` — `partial` bridges `env.step` to an executor.
- Vendored `verl/.../registry.py:20-30` demonstrates decorator registration.

### Opportunities

- `validation/ui_tars_utils.py:305-465` — a 160-line action-type parser constructs code through
  a large branch chain, duplicated in `mm_agents/ui_tars.py`. **Fix:** action-type → code-generator
  functions, each independently testable.
- `validation/ui_tars_utils.py:312-354` — arrow-key normalization is duplicated and one branch
  references `hotkey` before assignment. **Fix:** a single `KEYMAP` dictionary.
- `validation/ui_tars_utils.py:395-411` — `eval(start_box)`/`eval(end_box)` parses model output.
  **Problem:** code execution risk. **Fix:** `ast.literal_eval` plus a typed `_parse_box` helper.
- `validation/model_service_pool_bak.py` duplicates active pool logic. **Fix:** remove stale backup
  code; a functional abstraction cannot compensate for two sources of truth.

---

## deepseek-harness

This is primarily TypeScript, but its Python SDK contains useful small examples.

### Existing usage

- `python/sdk/src/deepseek_harness/client.py:20-21` — bounded `TypeVar` and a `Callable` filter
  alias.
- `python/sdk/src/deepseek_harness/api.py:142-152` — `collect(notification)` closes over event
  lists and callbacks.
- `client.py:474-491` — predicate factory returns a closure capturing `session_id`.
- `api.py:122,136` and `client.py:143-144` — callback and predicate hooks are injected through
  the request path.

### Opportunities

- `client.py:186-190,206-210,531-535` — three near-identical queue pop-or-raise methods.
  **Fix:** `_pop_or_raise(queue)` plus tiny bound callables or methods.
- `api.py:205-242` — two reverse-event scans differ only by event type and extractor. **Fix:**
  `_last_event(events, type_)` plus extractor strategies.

---

## deer-flow-agent

### Existing usage

- `backend/app/gateway/authz.py:361-453` — `ParamSpec`/`TypeVar`, `@wraps`, and a permission
  decorator factory.
- `backend/app/channels/dedupe_store.py:30-40` — `Protocol` defines a memory/Postgres strategy.
- `backend/app/channels/run_policy.py:113-118` — import-time policy registry.
- `backend/app/channels/message_bus.py:338-346` — outbound observer callbacks.
- `backend/packages/harness/deerflow/tools/sync.py:38-92` — async-to-sync wrapper factory and
  partial-aware unwrapping.

### Opportunities

- `backend/packages/harness/deerflow/client.py:451-486` — message serialization uses a growing
  `isinstance` chain. **Fix:** ordered `(MessageType, serializer)` pairs.
- `backend/app/gateway/github/registry.py:67-72` — manual cache + lock keyed by a store signature.
  **Fix:** `@functools.cache` on `_build_registry(signature)` if the signature fully captures
  invalidation.
- `backend/app/gateway/authz.py:383-394,452-463` — auth wrappers duplicate request-stub
  injection. **Fix:** shared decorator-composition helper with `@wraps`.
- `backend/app/channels/dedupe_store.py:247-276` — backend selection chain. **Fix:** backend →
  factory table, with `auto` as an explicit resolver.

---

## InfiGUI-G1

### Existing usage

- `eval/prompts.py:229-241` — prompt processor registry/factory.
- `recipe/infigui-g1/reward_fn.py:335-388` — reward-handler dispatch table.
- `eval/prompts.py:88-226` — injected prompt strategy object.
- `eval/data.py:455-481` — recursive aggregation over hierarchical metrics.

### Opportunities

- `eval/data.py:61-295` — `standardize_sample` has five benchmark branches, each repeating bbox,
  image, instruction, and group assembly. **Fix:** benchmark → normalizer functions or a shared
  field-spec factory using `partial`.
- `eval/data.py:31-56` — JSON/JSONL/directory loader chain. **Fix:** extension/type → loader table.
- `eval/models/qwen2vl.py:74-89` — role formatting chain. **Fix:** role → canonical tag mapping;
  keep image injection as a separate strategy.

---

## MAI-UI

### Existing usage

- `src/base.py:22-102` — ABC lifecycle plus list-comprehension projections.
- `src/mai_naivigation_agent.py:251-264` — prompt strategy selected by tool availability.
- `evaluation/grounding/extract_metrics.py:143,223` — `max`/`sorted` with `key=`.

### Opportunities

- `src/mai_naivigation_agent.py:130-176` — coordinate normalization is repeated for three keys
  and again in history serialization. **Fix:** `_normalize_coord(value)` plus a loop over coordinate
  keys; reuse `mem2response` from `history_responses`.
- `src/mai_grounding_agent.py:234-258` and `mai_naivigation_agent.py:530-560` — identical retry
  loops. **Fix:** a `retry(times)` decorator factory or a shared thunk helper with `@wraps`.
- `evaluation/grounding/eval_server.py` and `models/MAI_UI.py` duplicate parsing utilities. **Fix:**
  one shared module; functional reuse is preferable to another class hierarchy.

---

## midscene

No Python files were found. The repository is TypeScript-only; it is out of scope for a Python
ch. 7–10 skill. Its TypeScript registries/hooks may still inspire a separate TypeScript skill.

## OpenGUI

No Python files were found. The client is Kotlin/Android and the server is TypeScript. There is no
Python code to review.

## UI-TARS-desktop

No Python files were found. The repository is a TypeScript/JavaScript monorepo. It is a useful
negative example for scope control, not a Python pattern source.

---

## Open-AgentRL

### Existing usage

- `reward/osworld_rl_reward.py:107-117` — local closure passed as a sort key.
- `autotool/phase2/utils/data_utils.py:86,106,110,114,172` — `cached_property` memoizes derived
  values.
- `scripts/converter_hf_to_mcore.py:402` — `@contextmanager` lifecycle boundary.

### Opportunities

- `reward/osworld_rl_reward.py:35-71` — response normalization has a growing type-shape chain.
  **Fix:** `singledispatch` for `str`/`dict`/other response types, with one fallback.
- `reward/osworld_rl_reward.py:428-488` — two standardization functions copy the same grouping and
  normalization logic. **Fix:** one higher-order function taking `key_fn`, with `partial` for each
  grouping policy.
- `reward/alfworld_reward.py:51-56` and `alfworld_rl_reward.py:121-128` — duplicate mean/max
  branches. **Fix:** shared aggregation table, avoiding a parameter named `type`.
- `reward/math_utils.py:181-202,421-427` — mode strings select math behavior in multiple functions.
  **Fix:** central mode → checker registry.

## SCALE-CUA

### Existing usage

- `scalecua_rl/eval/src/agentrl/eval/event/bus.py:11-77` — `EventBus` stores callable listeners;
  `wait_for` creates a one-shot closure.
- `.../event/types.py:61-78` — `Annotated` discriminated event union, `Literal` event types,
  `TypeVar`, and `Callable` listener aliases.
- `.../session/metric.py:8-31` — `Metric.__call__` is a callable strategy.
- `.../trainer/components/task_manager.py:209-229` — `partial` binds task functions.
- `.../trainer/agentic/loops.py:1326-1354` — chat-agent loop registry.

### Opportunities

- `worker/environment/_base.py:30-104` — six sync methods repeat the same coroutine-threadsafe
  wrapper. **Fix:** a typed `sync_wrapper(async_method)` decorator factory with `@wraps`.
- `worker/environment/state/__init__.py:7-37` — driver/backend chain. **Fix:** driver → state
  provider factory table with lazy imports.
- `eval/client/_create.py:20-36` — provider branch selects client/options pairs. **Fix:** provider
  → `(client_cls, options_cls)` table.
- `trainer/agentic/loops.py:318-1331` — five agent loops repeat a 200-line skeleton. **Fix:**
  one parameterized core loop with `start_fn`, `gen_fn`, `obs_fn`, `end_fn`, and mode-specific hooks.
  This is the clearest ch. 10 template-method-via-functions opportunity in the scan.

---

## ShowUI

### Existing usage

- `train.py:512,524,569` — `partial` parameterizes collate functions.
- `app.py:243-281` — Gradio callbacks are first-class lambdas.
- `main/utils_aitw.py:352-356` — action → numeric ID dispatch table.
- Qwen processor classes expose a callable `__call__` interface.

### Opportunities

- `main/utils_aitw.py:289-300,365-384` — scroll geometry is encoded in repeated branches.
  **Fix:** one action → `(touch, lift)` geometry table shared by both functions.
- `data/dset_aitw.py:43-55` and sibling datasets — interleaving layout branches are copied many
  times. **Fix:** layout → formatter callables in a shared module.
- `main/evaluator.py:14-19` and five sibling files — precision branches are duplicated. **Fix:**
  one `precision → tensor-cast` table and helper.
- `main/eval_aitw.py:195-223` — per-action metric updates use linear branches. **Fix:** action →
  metric-updater registry.

## TongUI-agent

### Existing usage

- `synapse/envs/miniwob/action.py:15-342` — command objects implement `__call__`.
- `tongui/utils/agent_function_call.py:6,146` — tool registry decorator.
- `synapse/envs/mind2web/env_utils.py:17,128` — `sorted(key=...)` projections.
- `run_screenspot_vllm.py:176,187,252` — aggregation closures with `defaultdict`.

### Opportunities

- `synapse/agents/miniwob.py:405-430` — brittle `type(action) == ...` chain. **Fix:**
  `singledispatch` or a polymorphic `record()` strategy; this also fixes subclass handling.
- `synapse/envs/miniwob/action.py:34-342` — seven command classes repeat protocol methods and
  contain an equality bug. **Fix:** frozen dataclass/base protocol for shared serialization and
  equality, while keeping `__call__` commands.
- `tongui/utils/agent_function_call.py:92-117,230-247` — string action branches duplicate the
  declared enum. **Fix:** one action → bound handler table.
- Four evaluation scripts duplicate load/predict/metric aggregation. **Fix:** one `evaluate(...,
  predict_fn, prompt_builder)` function with strategy parameters.

## TuriX-CUA

### Existing usage

- `src/utils/__init__.py:12-41` — `@wraps` + `ParamSpec`/`TypeVar` decorator factories.
- `src/controller/registry/service.py:38-80` — action registry decorator.
- `src/controller/registry/views.py:65-72` — action-name dispatch map.
- `src/mac/element.py:247` — `cached_property`.

### Opportunities

- `src/controller/service.py:303-375` — four actions repeat try/except → `ActionResult` plumbing.
  **Fix:** an async higher-order `guarded(label, fn, ...)` helper or decorator.
- `src/controller/registry/service.py:56-67` — manually copies `__signature__`, `__name__`, and
  annotations for a sync→async wrapper. **Fix:** `@wraps`; manual copying currently omits metadata.
- `src/agent/service.py:383-392` — tool-calling method branch by library name. **Fix:** library →
  tool-method table.
- `src/agent/service.py:118-181` — provider `isinstance` chain. **Fix:** ordered type → strategy
  table, preserving provider precedence and fallback.

## Practical priority order

1. Remove unsafe `eval` of model output (agent-s, dart-gui).
2. Extract duplicated normalization/serialization helpers (MAI-UI, ShowUI, InfiGUI-G1).
3. Replace large string dispatch chains at setup/request boundaries (ClawGUI, SCALE-CUA,
   TongUI-agent, Open-AgentRL).
4. Add typed decorator factories where wrappers are duplicated (deer-flow-agent, TuriX-CUA).
5. Leave tensor kernels, device drivers, and stateful distributed loops imperative unless a measured
   setup-boundary refactor is available.
