# LoggedModel lifecycle and lineage

## Mental model

`LoggedModel` is the MLflow 3 metadata hub for a model or GenAI application version. For an
agent, it can represent source/configuration state even when the underlying provider model and
runtime are hosted elsewhere. It is experiment-scoped and can link parameters, tags, artifacts,
prompts, traces, and evaluation evidence.

Do not collapse these objects:

- A **run** records an execution or experiment.
- A **trace** records one application request and its spans.
- A **LoggedModel** identifies the application/model version responsible for executions.
- A **Registered Model Version** is an immutable governed deployable in Model Registry.

## Explicit lifecycle

Use an explicit `PENDING → READY|FAILED` lifecycle for build pipelines that create a version in
multiple steps:

```python
import mlflow

logged = mlflow.initialize_logged_model(
    name="support-agent-build-2026-08-01",
    model_type="agent",
)
try:
    mlflow.log_model_params(
        {
            "source_commit": "abc123def456",
            "prompt_uri": "prompts:/support-system/7",
            "provider_model": "<PINNED_MODEL_ID>",
        },
        model_id=logged.model_id,
    )
    # Package artifacts and run validation here.
    mlflow.finalize_logged_model(logged.model_id, "READY")
except Exception:
    mlflow.finalize_logged_model(logged.model_id, "FAILED")
    raise
```

Use `mlflow.create_external_model(...)` when MLflow should track an application/model identity
whose executable artifact remains outside MLflow. Feature-detect its exact signature in the
installed release rather than copying a newer example into an older client.

## Active model context

Set the active model **before** traced execution. Traces produced inside that scope are linked to
the version:

```python
import mlflow

with mlflow.set_active_model(name="support-agent-abc123def456"):
    answer = traced_agent("Where is my order?")
```

Avoid process-global ambiguity in concurrent services. Prefer scoped context managers and test
that context propagation works across async/task boundaries used by the app.

## What to capture

Record behavior-changing data, not only a marketing version string:

| Category | Examples |
|---|---|
| Source | repository URL, commit SHA, branch, dirty flag/diff digest, build ID |
| Prompt | immutable prompt version URI, resolved alias, template hash |
| Foundation model | provider, exact model/deployment ID, API version |
| Generation | temperature, top-p, max output tokens, seed where supported |
| Retrieval | embedding model, index/version, chunker, top-k, filters |
| Tools | MCP server/version, tool schema digest, endpoint identity |
| Runtime | Python, MLflow and framework versions, lockfile/container digest |
| Policy | guardrail/routing versions, feature flags, tenant configuration |

Never log secrets, bearer tokens, raw credentials, or unredacted sensitive configuration.

## Retrieval and search

Common inspection functions include:

```python
latest = mlflow.last_logged_model()
same_name = mlflow.search_logged_models(
    experiment_ids=["<EXPERIMENT_ID>"],
    filter_string="name = 'support-agent-abc123def456'"
)
loaded = mlflow.get_logged_model(model_id=latest.model_id)
```

Confirm filter syntax and return shape against the installed API. Search results can identify
candidate versions, but the comparison decision should use trace/evaluation evidence rather than
recency alone.

## Failure modes

- **Orphan traces:** active model was set after instrumented calls began.
- **False reproducibility:** branch name or alias was captured without resolved immutable version.
- **Dirty build loss:** uncommitted changes produced the result but only commit SHA was logged.
- **Version explosion:** every request creates a new app version instead of reusing a source/config
  identity.
- **Secret leakage:** environment dumps or headers were logged as parameters/tags.
- **Conflated lifecycle:** a READY LoggedModel was mistaken for production approval or deployment.
