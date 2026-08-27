---
name: model-registry
description: >
  MLflow Model Registry and Unity Catalog model lifecycle: log and register immutable model
  versions, signatures, aliases, tags, lineage, search, promotion, rollback, CI/CD, OSS
  backend configuration, and the bridge from UC versions to Azure Databricks custom model
  serving endpoints, traffic splits, logs, and monitoring. Use for MLOps or LLMOps model
  promotion/versioning/deployment questions. Load parent `mlflow` first.
compatibility: MLflow 3.x; Databricks operations require compatible workspace APIs, SDK/CLI, privileges, and region support
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-01"
---

# MLflow Model Registry and Serving Lifecycle

The registry is the governed **artifact approval plane**. A registered model version identifies an
MLflow Model artifact; aliases express mutable lifecycle intent. A serving endpoint is a separate
runtime configuration and must be updated explicitly.

## Mandatory preflight

1. Load parent `mlflow`; identify OSS registry, Databricks workspace registry, Databricks Unity
   Catalog, or OSS Unity Catalog.
2. Inspect MLflow client/server versions and registry URI.
3. Confirm model signature, input example, dependencies/resources, source lineage, and evaluation
   evidence.
4. Define naming/environment boundary and alias policy.
5. Define promotion gate, approver, rollback target, and retention policy.
6. For Databricks, load `databricks`, `databricks-core`, and `databricks-model-serving` before
   endpoint/API work; verify profile, UC grants, endpoint ACLs, quotas, and preview features.
7. Run `python scripts/inspect_model_registry.py` in the target environment.

## Core object model

```text
MLflow Model / LoggedModel artifact
  → Registered Model (stable governed name)
       ├─ Version 1 (artifact identity + lineage; version metadata can be annotated)
       ├─ Version 2
       └─ aliases: candidate, champion, rollback (mutable pointers)
```

For Databricks:

```text
UC model version
  → served entity(entity_name, entity_version, compute)
  → serving endpoint config version
  → traffic routes
  → inference/telemetry tables, logs, metrics, traces
```

Moving a registry alias does **not** update a served entity pinned to `entity_version`.

## Canonical register/promote workflow

```python
import mlflow
from mlflow import MlflowClient
from mlflow.models import infer_signature

MODEL_NAME = "catalog.schema.support_agent"  # Use a flat name for OSS registry.
mlflow.set_registry_uri("databricks-uc")      # Omit/change for the selected environment.

signature = infer_signature(INPUT_EXAMPLE, MODEL.predict(INPUT_EXAMPLE))
info = mlflow.pyfunc.log_model(
    python_model=MODEL,
    name="model",
    input_example=INPUT_EXAMPLE,
    signature=signature,
)
registered = mlflow.register_model(info.model_uri, MODEL_NAME)

client = MlflowClient(registry_uri=mlflow.get_registry_uri())
client.set_model_version_tag(MODEL_NAME, registered.version, "validation_status", "pending")
# Run evaluation/integration/security gates, then:
client.set_model_version_tag(MODEL_NAME, registered.version, "validation_status", "approved")
client.set_registered_model_alias(MODEL_NAME, "champion", registered.version)
```

Prefer `info.model_uri` returned by logging. Avoid reconstructing artifact locations from run paths,
especially in MLflow 3 where model storage semantics changed.

## Reference router

| Need | Read |
|---|---|
| Entities, registration methods, signatures, aliases, tags, loading/search/deletion | [`references/registry-workflow.md`](references/registry-workflow.md) |
| Quality gates, champion/challenger, environment promotion, rollback, webhooks/CI | [`references/promotion-cicd.md`](references/promotion-cicd.md) |
| OSS SQL backend, Databricks UC, permissions, naming and migration | [`references/oss-and-unity-catalog.md`](references/oss-and-unity-catalog.md) |
| Azure Databricks served entities, traffic, zero-downtime update, logs/telemetry | [`references/databricks-serving-bridge.md`](references/databricks-serving-bridge.md) |
| Official MLflow/Microsoft source inventory and status notes | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Every release design should identify the exact source model URI, immutable registered version,
signature, dependencies/resources, evaluation dataset/scorers/run, approval metadata, alias before
and after, endpoint config/served entity/traffic before and after, readiness verification,
observability destination, rollback target, and audit record. Never promote based on “latest” or
aggregate score alone.
