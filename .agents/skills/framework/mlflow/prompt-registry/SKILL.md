---
name: mlflow-prompt-registry
description: >
  MLflow Prompt Registry lifecycle and optimization: register and load immutable
  prompt versions, manage aliases and tags, format text/chat/Jinja prompts,
  attach model configuration and structured-output metadata, link prompts to
  traces/runs/LoggedModels, evaluate and optimize prompts, use Prompt Engineering
  UI and LLM Playground, and rewrite prompts for model migration. Use whenever a
  user mentions Prompt Registry, prompt versioning, `prompts:/` URIs, prompt
  aliases, prompt optimization, GEPA, MetaPromptOptimizer, prompt migration,
  prompt lineage, or Gateway-backed prompt testing.
metadata:
  version: "0.2.0"
  docs-reviewed: "2026-08-30"
  parent: mlflow
compatibility: MLflow 3.x; optimization, rewrite, UI, and Playground capabilities are version/AI-Gateway gated
---

# MLflow Prompt Registry

Use the Prompt Registry as the prompt-specific lifecycle layer inside an
LLMOps release. Keep application code, prompt review, and environment
configuration in Git, while using the registry for immutable prompt versions,
human-readable commit messages, aliases, prompt metadata, and prompt-to-run/
trace/model lineage.

## Documentation map

Load the relevant subsection rather than treating the landing page as the whole
API:

| Concern | Official page |
|---|---|
| Concepts, versions, aliases, and caching | [Prompt Registry](https://mlflow.org/docs/latest/genai/prompt-registry/) |
| Create/edit/version | [Create and edit](https://mlflow.org/docs/latest/genai/prompt-registry/create-and-edit-prompts/) |
| Promote with aliases | [Prompt lifecycle aliases](https://mlflow.org/docs/latest/genai/prompt-registry/manage-prompt-lifecycles-with-aliases/) |
| Load/use in applications | [Use prompts in apps](https://mlflow.org/docs/latest/genai/prompt-registry/use-prompts-in-apps/) |
| Link to models | [Log prompts with models](https://mlflow.org/docs/latest/genai/prompt-registry/log-with-model/) |
| Structured output metadata | [Structured output](https://mlflow.org/docs/latest/genai/prompt-registry/structured-output/) |
| Offline evaluation | [Evaluate prompts](https://mlflow.org/docs/latest/genai/prompt-registry/evaluate-prompts/) |
| Optimization | [Optimize prompts](https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/) |
| Model migration | [Rewrite prompts](https://mlflow.org/docs/latest/genai/prompt-registry/rewrite-prompts/) |
| Prompt Engineering UI | [Prompt Engineering UI](https://mlflow.org/docs/latest/genai/prompt-registry/prompt-engineering/) |
| Interactive testing | [LLM Playground](https://mlflow.org/docs/latest/genai/prompt-registry/playground/) |
| Local source ledger | [Prompt Registry source ledger](references/source-ledger.md) |

For Databricks-managed MLflow, also load `databricks` and the current Databricks
MLflow 3 documentation because storage, permissions, managed monitoring, AI
Gateway, and release status can differ from OSS MLflow.

## Register and load

```python
import mlflow

prompt = mlflow.genai.register_prompt(
    name="catalog.schema.support-agent",
    template=[
        {"role": "system", "content": "You are a {{tone}} support agent."},
        {"role": "user", "content": "{{question}}"},
    ],
    commit_message="Add escalation behavior",
    tags={"owner": "support-ai", "risk_tier": "medium"},
    model_config={
        "model_name": "<pinned-provider-model>",
        "temperature": 0.2,
        "max_tokens": 800,
    },
)

by_version = mlflow.genai.load_prompt(
    "prompts:/catalog.schema.support-agent/1"
)
by_alias = mlflow.genai.load_prompt(
    "prompts:/catalog.schema.support-agent@production"
)

messages = by_version.format(tone="professional", question="...")
```

Rules:

- Registering new template content creates a new sequential, immutable prompt
  version. Include a commit message and meaningful tags.
- Load an exact version for reproducible evaluation and release evidence.
- Use an alias for a policy pointer such as `staging`, `production`, or
  `candidate`, but resolve and record the numbered version before deployment.
- Treat the reserved `@latest` alias as convenience, never as approval evidence.
- In Databricks/Unity Catalog, use a fully qualified prompt name where required;
  do not copy a simple OSS prompt name into a governed workspace without checking
  the target backend.

## Aliases, tags, and model configuration

```python
mlflow.genai.set_prompt_alias(
    name="catalog.schema.support-agent",
    alias="production",
    version=12,
)
mlflow.genai.delete_prompt_alias(
    name="catalog.schema.support-agent",
    alias="candidate",
)
```

Use prompt-level tags for stable ownership/domain metadata and prompt-version
tags for release/evaluation metadata. Keep values searchable and low-cardinality.
Do not store secrets or raw private user content in tags.

`model_config` records inference parameters alongside a prompt and may be
updated independently of the immutable template. Use `set_prompt_model_config`
and `delete_prompt_model_config` only with an explicit release/evaluation policy.
If changing model configuration changes behavior, create a new application
release and evaluation record even if the Prompt Registry template version is
unchanged. Record model config digests and provider-specific `extra_params`.

## Prompt formats and contracts

- Text templates use `{{variable}}` placeholders.
- Chat prompts use a list of `{role, content}` messages and can contain the same
  placeholders.
- Jinja control flow is supported where the documented sandboxed behavior is
  appropriate; do not treat user-controlled text as trusted template code.
- Use `prompt.format(**values)` and validate required variables before calling a
  provider.
- `to_single_brace_format()` can help framework interop; test escaping and
  nested-template behavior.
- `response_format` documents intended structured output but is not a substitute
  for runtime schema validation. Validate the actual response with Pydantic or
  an equivalent contract at the application boundary.

## Caching and release semantics

Version URIs are immutable and can use the documented long-lived cache. Alias
loads are mutable and have a short default cache window (currently documented as
60 seconds). Configure per-call `cache_ttl_seconds` or the documented environment
variables when release propagation requires a different tradeoff:

```text
MLFLOW_ALIAS_PROMPT_CACHE_TTL_SECONDS
MLFLOW_VERSION_PROMPT_CACHE_TTL_SECONDS
```

Tag/alias changes invalidate relevant cache entries. For production, either:

1. resolve the alias at release time, record the version, and load the exact
   version; or
2. deliberately use an alias for controlled live switching and document the
   cache TTL, propagation window, and rollback behavior.

Test alias changes, cache invalidation, and concurrent releases. Do not let a
long-lived process silently use an old alias resolution after approval.

## Automatic lineage

Use registry URIs inside instrumented application code. MLflow can link loaded
prompts to the active trace or run, and models-from-code can record prompt
dependencies when the model code calls `load_prompt()`.

For explicit model packaging, pass prompt URIs to the supported LLM/agent
flavor’s `log_model(prompts=[...])` parameter where available. Keep a release
manifest that also records:

```text
prompt URI/version, alias resolution, template digest, model_config digest,
Git SHA, LoggedModel ID, registered model version, endpoint/served entity,
evaluation dataset/scorers, and deployment run ID
```

When a trace reports a regression, resolve the prompt identity first, then
compare the same prompt against the previous model, tool, retrieval, and
generation configuration.

## Evaluate prompts

Use `mlflow.genai.evaluate()` with a versioned dataset and fixed scorers. Keep
prompt candidates, model/provider settings, retrieval resources, sampling, and
judge configuration comparable. Add expectations for correctness, required
facts, citations, tool use, safety, or refusal behavior when a final output
alone is insufficient.

Evaluate exact prompt versions, not an alias whose target may move during the
run. Log dataset and scorer digests with results, compare critical slices, and
promote only after absolute and regression thresholds pass.

## Optimize prompts

The current API is `mlflow.genai.optimize_prompts()`; do not use the removed
singular `optimize_prompt` API. A typical call has:

```python
result = mlflow.genai.optimize_prompts(
    predict_fn=predict_fn,
    train_data=train_data,
    prompt_uris=["prompts:/catalog.schema.support-agent/12"],
    optimizer=GepaPromptOptimizer(
        reflection_model="<provider>:/<pinned-reflection-model>",
        max_metric_calls=100,
    ),
    scorers=[Correctness(model="<provider>:/<pinned-judge-model>")],
)
```

Guidance:

- `predict_fn` must load/format the registered prompt and exercise the same
  meaningful application path that production uses.
- Keep `train_data` representative and do not use the only final holdout for
  optimization.
- GEPA is iterative and data-driven; `MetaPromptOptimizer` can perform a faster
  zero-shot or few-shot pass. Record reflection model/config, optimizer,
  metric-call budget, scorer versions, and data digest.
- Multi-prompt optimization can change several registered prompts together;
  release them as one coherent candidate with a manifest. Custom optimizers can
  extend `BasePromptOptimizer`, and aggregation should make scorer weights explicit.
- Optimized prompts are registered as new versions. Inspect initial/final metrics
  and rerun the independent holdout/regression/safety suite before assigning an
  alias or deploying.
- Prompt optimization requires a sufficiently recent MLflow release; current
  documentation identifies MLflow 3.5.0+ for this API.

## Rewrite prompts for a model migration

The rewrite workflow is experimental and is useful when switching providers or
model families. It can be trace-aware when existing outputs/traces provide the
training signal, so a reference answer is not always required.

1. Capture representative traces and outputs from the current model.
2. Build a versioned dataset from those traces.
3. Switch only the target model in a candidate environment.
4. Optimize/rewrite the prompt against an equivalence or task-specific scorer.
5. Inspect safety, correctness, cost, latency, and critical slices.
6. Register the new prompt version and release it with the new model identity.

Do not treat output equivalence as sufficient for safety or access-control
validation; add explicit policy and tool/retrieval checks.

## Prompt Engineering UI and Playground

The Prompt Engineering UI is an experimental, Gateway-backed workflow for
trying prompts, recording configurations as runs, and producing an MLflow Model.
The LLM Playground provides in-browser prompt/model testing with multi-turn chat,
sampling parameters, tools, structured output, variables, Prompt Registry versions,
and model configuration. These are interactive development surfaces, not approval
or deployment gates; export exact prompt/model/config identities into a tested
release workflow.

## Status and currentness gates

- Prompt Registry templates/versions and aliases are distinct from Git branches
  and MLflow model versions.
- `response_format` is documentation/tracking metadata; validate runtime output.
- Prompt model configuration can be mutable; include it in the application
  release manifest and evaluation evidence.
- Optimization, rewrite, Prompt Engineering UI, and Playground capabilities can
  require newer MLflow or AI Gateway support. Verify the installed version,
  backend, permissions, and current official docs before using them in production.
- Never represent an OSS example as a Databricks-managed feature without
  checking the workspace/cloud release and preview status.

## Related skills

- `evaluation-monitoring` for datasets, scorers, judges, feedback, and
  production traces.
- `version-tracking` for Git/LoggedModel identity and app versions.
- `genai-flavors` for model packaging and prompt dependencies.
- `ai-gateway` for Gateway endpoints used by judges, UI, and Playground.
- `model-registry` for UC versions and promotion.
- `databricks-llmops` for the full Git-to-production workflow.
