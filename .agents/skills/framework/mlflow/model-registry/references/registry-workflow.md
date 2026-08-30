# Model Registry workflow

## Entities

| Entity | Purpose |
|---|---|
| MLflow Model / LoggedModel | packaged artifact and source execution lineage |
| Registered Model | stable named container for governed versions |
| Model Version | numbered registration of a specific model artifact |
| Alias | mutable name that resolves to one model version |
| Tags/descriptions | searchable workflow and documentation metadata |

Treat model artifact identity/version as immutable. Tags, descriptions, and aliases are mutable
control metadata and require audit discipline.

## Registration methods

### During logging

```python
info = mlflow.sklearn.log_model(
    sk_model=model,
    name="model",
    input_example=X_sample,
    signature=signature,
    registered_model_name="forecast-model",
)
```

This creates the registered model if absent and a new version under the name.

### Register the tested logged artifact

```python
info = mlflow.sklearn.log_model(
    sk_model=model,
    name="model",
    input_example=X_sample,
    signature=signature,
)
version = mlflow.register_model(
    model_uri=info.model_uri,
    name="forecast-model",
)
```

This two-step shape is often clearer when evaluation must occur before or around registration.

### Low-level client

```python
from mlflow import MlflowClient

client = MlflowClient()
client.create_registered_model("forecast-model")
version = client.create_model_version(
    name="forecast-model",
    source=info.model_uri,
    run_id=run.info.run_id,
    tags={"validation_status": "pending"},
    description="Candidate trained from approved feature snapshot.",
)
```

Handle already-exists races and asynchronous creation status. Use low-level operations when
control/metadata timing matters; otherwise prefer fluent registration.

## Signatures and examples

Signatures document and validate inputs, outputs, and optional inference parameters. Unity Catalog
requires them. Infer from representative data:

```python
from mlflow.models import infer_signature

signature = infer_signature(X_sample, model.predict(X_sample))
```

For agents, use `ResponsesAgent`'s standard schema or explicit Pydantic/type contract. Test nested,
optional, malformed, and streaming inputs—not just a toy example.

## Aliases

```python
client.set_registered_model_alias("forecast-model", "candidate", version.version)
candidate = client.get_model_version_by_alias("forecast-model", "candidate")
loaded = mlflow.pyfunc.load_model("models:/forecast-model@candidate")
```

Aliases such as `candidate`, `champion`, and `rollback` express intent. Prefer them to legacy
lifecycle stages in new designs. Avoid `latest` for release decisions because recency is not
quality or approval.

## Tags and descriptions

```python
client.set_registered_model_tag("forecast-model", "owner", "forecast-platform")
client.set_model_version_tag("forecast-model", version.version, "test_status", "passed")
client.update_model_version(
    name="forecast-model",
    version=version.version,
    description="Approved on eval dataset support-golden v18; see release R-2026-08-01.",
)
```

Recommended version metadata: source commit/build, dataset identity, feature/prompt/tool versions,
evaluation run and scorer versions, security scan, approver, release ticket, environment, and
deprecation deadline. Do not store secrets or sensitive payloads in tags/descriptions.

## Load and search

```python
by_version = mlflow.pyfunc.load_model("models:/forecast-model/7")
by_alias = mlflow.pyfunc.load_model("models:/forecast-model@champion")

versions = client.search_model_versions("name='forecast-model'")
models = client.search_registered_models()
```

Resolve an alias to a numbered version at release start, record it, and keep using that version for
the transaction. A later alias move should not change an in-progress validation silently.

## Deletion

Deletion is destructive. Remove endpoint references and aliases, satisfy retention/audit policy,
confirm no batch jobs consume the version, then delete versions. Delete the registered model only
when every version can be removed. Prefer deprecation/denial over immediate deletion during
consumer migration.
