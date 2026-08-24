# OSS Model Registry and Unity Catalog

## OSS Model Registry

Use a database-backed MLflow server for registry features. FileStore is not the production model
registry design and is in maintenance/deprecation direction. Example:

```bash
mlflow server \
  --backend-store-uri postgresql://USER:PASSWORD@HOST:5432/mlflow \
  --host 0.0.0.0 \
  --port 5000
```

Keep credentials out of shell history/config. Use TLS, secret injection, backups, migration tests,
RBAC/auth, and supported database pooling. Run the documented `mlflow db upgrade` process against
a backup during controlled maintenance when upgrading schema.

The registry URI defaults to tracking URI in common OSS setups:

```python
mlflow.set_tracking_uri("https://mlflow.example.com")
mlflow.set_registry_uri("https://mlflow.example.com")
```

Pin client/server versions together; newer clients can expose APIs an older server cannot support.

## Databricks Unity Catalog

```python
import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
client = MlflowClient(registry_uri="databricks-uc")
MODEL_NAME = "catalog.schema.support_agent"
```

UC registered models use three-level names and require a model signature. Advantages include
fine-grained governance, cross-workspace access subject to bindings/permissions, discoverability,
and lineage.

Typical privileges include `USE CATALOG`, `USE SCHEMA`, and model privileges appropriate to
create/read/execute/manage operations. Exact privilege names and ownership behavior vary by
operation and platform release; load Databricks platform/core skills and inspect current docs/API.

## Workspace registry versus UC

The workspace registry is legacy for new governed Databricks designs. Set
`mlflow.set_registry_uri("databricks-uc")` explicitly before registration to avoid writing to the
wrong registry. Plan migration rather than silently duplicating names.

`copy_model_version()` can support migration/promotion. UC requires signatures; any migration
bypass intended for legacy unsigned models is a temporary compatibility path and yields reduced
serving/governance quality. Prefer re-log/re-register with a valid signature.

## OSS Unity Catalog

MLflow docs also describe an OSS Unity Catalog registry URI such as:

```python
mlflow.set_registry_uri("uc:http://localhost:8080")
```

Do not assume Databricks-only serving, workspace auth, or platform features are present merely
because the registry is Unity Catalog-compatible.

## Governance design

Separate duties where risk requires it:

- training identity logs candidate artifacts;
- validation identity reads and evaluates candidates;
- promotion identity moves approved aliases/copies versions;
- deployment identity updates endpoints;
- runtime identity only reads/executes the deployed dependencies;
- auditors read lineage, tags, events, and release manifests.

UC aliases and tags are control metadata, not substitutes for catalog/schema/model permissions.
