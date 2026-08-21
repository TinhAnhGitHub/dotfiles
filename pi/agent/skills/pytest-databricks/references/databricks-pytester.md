# databricks-labs-pytester Complete Fixture Reference

> Source: https://github.com/databrickslabs/pytester
> Package: `databricks-labs-pytester` on PyPI
> Latest version: v0.7.4 (83+ fixtures across 13 source modules)
> All `make_*` fixtures are **factory functions** — they return callables, not resources directly.
> All fixtures are **function-scoped** by default (except `ws` and `acc` which are session-scoped).
> Cleanup is automatic via the `factory()` generator pattern with watchdog tagging.

## Table of Contents

- [Installation](#installation)
- [Logging Setup](#logging-setup)
- [Debug Environment Pattern](#debug-environment-pattern)
- [Environment Fixtures](#environment-fixtures)
- [Baseline Fixtures](#baseline-fixtures)
- [SQL Fixtures](#sql-fixtures)
- [Spark Connect Fixture](#spark-connect-fixture)
- [Watchdog Fixtures](#watchdog-fixtures)
- [Catalog Fixtures](#catalog-fixtures)
- [IAM Fixtures](#iam-fixtures)
- [Compute Fixtures](#compute-fixtures)
- [Workspace Fixtures](#workspace-fixtures)
- [Secrets Fixtures](#secrets-fixtures)
- [ML Fixtures](#ml-fixtures)
- [Permissions Fixtures](#permissions-fixtures)
- [Unit Testing with unwrap.py](#unit-testing-with-unwrappy)
- [The factory() Pattern](#the-factory-pattern)
- [Environment Variables Summary](#environment-variables-summary)
- [Serverless Configuration](#serverless-configuration)

---

## Installation

```toml
[project]
name = "your-project"
dependencies = ["databricks-sdk~=0.30"]

[dependency-groups]
test = [
    "databricks-labs-pytester~=0.7.4",
    "pytest-cov~=7.0.0",
    "pytest-mock~=3.15.1",
    "pytest-timeout~=2.4.0",
    "pytest-xdist~=3.8.0",
]
```

The plugin auto-registers via pytest entry points (`pytest11` entry point group) — no
`conftest.py` changes needed to load it. All 83+ fixtures are automatically available.

---

## Logging Setup

```python
# conftest.py
import logging
from databricks.labs.blueprint.logger import install_logger

install_logger()
logging.getLogger('databricks.labs.pytester').setLevel(logging.DEBUG)
```

This enables clickable workspace links in test output showing created/deleted resources.

---

## Debug Environment Pattern

Create `~/.databricks/debug-env.json`:

```json
{
   "ws": {
     "CLOUD_ENV": "azure",
     "DATABRICKS_HOST": "....azuredatabricks.net",
     "DATABRICKS_CLUSTER_ID": "0708-200540-...",
     "DATABRICKS_WAREHOUSE_ID": "33aef...",
     "DATABRICKS_ACCOUNT_ID": "...."
   },
   "acc": {
     "CLOUD_ENV": "aws",
     "DATABRICKS_HOST": "accounts.cloud.databricks.net",
     "DATABRICKS_CLIENT_ID": "....",
     "DATABRICKS_CLIENT_SECRET": "...."
   }
}
```

In `conftest.py`:

```python
@pytest.fixture
def debug_env_name():
    return "ws"
```

---

## Environment Fixtures

### `is_in_debug`
- Returns `True` if running from IDE debugger (PyCharm, IntelliJ, VSCode)
- Scope: function

### `debug_env_name`
- Specifies which key to use from `~/.databricks/debug-env.json`
- Default: `".env"` (loads `.env` file from parent directories)
- Override in `conftest.py`:
```python
@pytest.fixture
def debug_env_name():
    return "ws"
```

### `debug_env`
- Loads environment variables for local debugging
- Returns: `MutableMapping[str, str]` (the `os.environ`)
- In CI/CD: returns `os.environ` directly

### `env_or_skip`
- Returns a callable that gets env var or skips test if missing
- In debug mode: fails instead of skipping
```python
def test_something(env_or_skip):
    token = env_or_skip("SOME_EXTERNAL_SERVICE_TOKEN")
    assert token is not None
```

---

## Baseline Fixtures

### `make_random`
- Generates random alphanumeric strings
- Returns: `Callable[[int], str]` (default length 16)
```python
def test_random(make_random):
    r1 = make_random()      # 16 chars
    r2 = make_random(k=8)   # 8 chars
```

### `product_info`
- Returns `(name, version)` tuple for SDK user-agent tracking
- Default: `(None, None)`

### `ws`
- Creates a `WorkspaceClient` authenticated to the target workspace
- Scope: **session** (shared across all tests)
```python
def test_workspace_operations(ws):
    clusters = ws.clusters.list_clusters()
    assert len(clusters) >= 0
```

### `acc`
- Creates an `AccountClient` for account-level operations
- Scope: **session**
- Required: `DATABRICKS_ACCOUNT_ID` (skips if missing)
```python
def test_listing_workspaces(acc):
    workspaces = acc.workspaces.list()
    assert len(workspaces) >= 1
```

### `log_workspace_link`
- Returns callable that logs a clickable workspace link
```python
log_workspace_link('my-thing', 'explore/data/catalog/schema/table')
```

### `log_account_link`
- Returns callable that logs a clickable account console link

---

## SQL Fixtures

### `sql_backend`
- Creates a `StatementExecutionBackend` for SQL via Databricks SQL Warehouses
- Required: `DATABRICKS_WAREHOUSE_ID`
```python
def test_sql(sql_backend):
    sql_backend.execute("CREATE TABLE foo (id INT)")
    rows = sql_backend.fetch("SELECT * FROM foo")
```

### `sql_exec`
- Partial of `sql_backend.execute` — execute SQL without results

### `sql_fetch_all`
- Partial of `sql_backend.fetch` — fetch all rows
```python
def test_fetch(sql_fetch_all):
    rows = sql_fetch_all("SELECT 1")
    assert rows[0][0] == 1
```

---

## Spark Connect Fixture

### `spark`
- Returns a Databricks Connect `SparkSession`
- Required: `databricks-connect` package (skips if not installed)
- Serverless: set `DATABRICKS_SERVERLESS_COMPUTE_ID=auto`
- Cluster: uses `DATABRICKS_CLUSTER_ID` or `ws.config.cluster_id`
```python
def test_databricks_connect(spark):
    rows = spark.sql("SELECT 1").collect()
    assert rows[0][0] == 1
```

---

## Watchdog Fixtures

### `watchdog_remove_after`
- Returns UTC timestamp string `YYYYMMDDHH` (now + 1 hour, rounded up)
- Used as tag value: `{"RemoveAfter": watchdog_remove_after}`
- Enables cleanup jobs to identify and remove stale test resources

### `watchdog_purge_suffix`
- Returns `ra{hex_timestamp}` (e.g., `"ra1e8a3a1"`)
- Appended to resource names for easy identification of test resources

---

## Catalog Fixtures

### `make_catalog`
- Creates a Unity Catalog catalog, auto-deletes after test
- Returns: `CatalogInfo`
```python
def test_catalog(make_catalog):
    catalog = make_catalog()
    assert catalog.name.startswith("dummy_c")
```

### `make_schema`
- Creates a schema in a catalog
- Returns: `SchemaInfo`
- Default catalog: `"hive_metastore"`
```python
def test_schema(make_catalog, make_schema):
    catalog = make_catalog()
    schema = make_schema(catalog_name=catalog.name)
```

### `make_table`
- Creates a table or view with extensive options
- Returns: `TableInfo`
- KWARGS: `catalog_name`, `schema_name`, `name`, `ctas`, `non_delta`, `external`, `view`, `columns`, `tbl_properties`
```python
def test_table(make_catalog, make_schema, make_table):
    catalog = make_catalog()
    schema = make_schema(catalog_name=catalog.name)
    table = make_table(catalog_name=catalog.name, schema_name=schema.name)
```

### `make_volume`
- Creates a Unity Catalog volume
- Returns: `VolumeInfo`
```python
def test_volume(make_catalog, make_schema, make_volume, make_random):
    catalog = make_catalog()
    schema = make_schema(catalog_name=catalog.name)
    volume = make_volume(catalog_name=catalog.name, schema_name=schema.name,
                         name=f"vol_{make_random(8).lower()}")
```

### `make_udf`
- Creates a SQL or Hive UDF
- Returns: `FunctionInfo`
```python
def test_udf(make_schema, make_udf):
    schema = make_schema()
    make_udf(schema_name=schema.name)
    make_udf(schema_name=schema.name, hive_udf=True)
```

### `make_storage_credential`
- Creates a storage credential (AWS IAM or Azure SPN)
```python
def test_storage_credential(env_or_skip, make_storage_credential, make_random):
    cred_name = f"dummy-{make_random(8).lower()}"
    make_storage_credential(credential_name=cred_name,
                           aws_iam_role_arn=env_or_skip("TEST_UBER_ROLE_ID"))
```

---

## IAM Fixtures

### `make_user`
- Creates a workspace user, auto-deletes after test
- Returns: `User`
- Naming: `dummy-{random8}-{purge_suffix}@example.com`
```python
def test_new_user(make_user, ws):
    new_user = make_user()
    home_dir = ws.workspace.get_status(f"/Users/{new_user.user_name}")
    assert home_dir.object_type == ObjectType.DIRECTORY
```

### `make_group`
- Creates a workspace group with optional members/roles/entitlements
- Returns: `Group`
- Retries up to 90s for eventual consistency
```python
def test_new_group(make_group, make_user, ws):
    user = make_user()
    group = make_group(members=[user.id])
    loaded = ws.groups.get(group.id)
    assert group.display_name == loaded.display_name
```

### `make_acc_group`
- Creates an account-level group (same API as `make_group` but uses `acc`)

### `make_run_as`
- Creates an ephemeral service principal, returns `RunAs` object
- Properties: `ws`, `sql_backend`, `sql_exec`, `sql_fetch_all`, `display_name`, `application_id`
- Override `ws` at file level to run all tests as lower-privilege SPN:
```python
from pytest import fixture

@fixture
def ws(make_run_as):
    run_as = make_run_as(account_groups=['account.group.used.for.all.tests.in.this.file'])
    return run_as.ws

def test_creating_notebook(make_notebook):
    notebook = make_notebook()
    assert notebook.exists()
```
- Limitation: Does not work with Databricks Metadata Service auth on Azure

---

## Compute Fixtures

### `make_cluster`
- Creates a cluster, waits for it to start, auto-deletes
- Returns: `Wait[ClusterDetails]`
- KWARGS: `single_node`, `cluster_name`, `spark_version`, `autotermination_minutes`
- Auto-tags with `RemoveAfter`
```python
def test_cluster(make_cluster):
    cluster = make_cluster(single_node=True)
    assert cluster.cluster_id is not None
```

### `make_cluster_policy`
- Creates a cluster policy
- Returns: `CreatePolicyResponse`

### `make_instance_pool`
- Creates an instance pool
- Returns: `CreateInstancePoolResponse`
- Auto-selects node type with local disk + 16GB memory

### `make_job`
- Creates a Databricks job with extensive configuration
- Returns: `Job`
- KWARGS: `name`, `path`, `content`, `task_type`, `tasks`, `environments`, `spark_conf`, `libraries`, `tags`
```python
def test_job(make_job):
    job = make_job()
    assert job.job_id is not None
```

### `make_pipeline`
- Creates a Delta Live Tables pipeline
- Returns: `CreatePipelineResponse`
```python
def test_pipeline(make_pipeline):
    pipeline = make_pipeline()
    assert pipeline.pipeline_id is not None
```

### `make_warehouse`
- Creates a SQL warehouse
- Returns: `Wait[GetWarehouseResponse]`
- KWARGS: `warehouse_name`, `warehouse_type` (default PRO), `cluster_size` (default 2X-Small)

---

## Workspace Fixtures

### `make_notebook`
- Creates a Databricks notebook, auto-deletes
- Returns: `WorkspacePath` (os.PathLike with `.read_text()`, `.parent`, `.iterdir()`)
- KWARGS: `path`, `content` (default `"print(1)"`), `language`, `format`, `overwrite`
```python
def test_notebook(make_notebook):
    notebook = make_notebook()
    assert "print(1)" in notebook.read_text()
```

### `make_workspace_file`
- Creates a workspace file (like notebook but stored as file)
- Returns: `WorkspacePath`
```python
def test_workspace_file(make_workspace_file):
    f = make_workspace_file()
    assert f.is_file()
    assert "print(1)" in f.read_text()
```

### `make_directory`
- Creates a workspace folder
- Returns: `WorkspacePath`
```python
def test_directory(make_directory, make_notebook):
    folder = make_directory()
    notebook = make_notebook(path=folder / 'foo.py')
    assert ['foo.py'] == [_.name for _ in folder.iterdir()]
```

### `make_repo`
- Creates a Databricks Repo (git folder)
- Returns: `RepoInfo`
- Default URL: `"https://github.com/shreyas-goenka/empty-repo.git"`

---

## Secrets Fixtures

### `make_secret_scope`
- Creates a secret scope, auto-deletes
- Returns: `str` (scope name)
```python
def test_secret_scope(make_secret_scope):
    scope = make_secret_scope()
    assert scope.startswith("dummy-")
```

### `make_secret_scope_acl`
- Creates a secret scope ACL entry
- Returns: `tuple[str, str]` — `(scope_name, principal_name)`
```python
def test_secret_acl(make_user, make_secret_scope, make_secret_scope_acl):
    scope = make_secret_scope()
    user = make_user()
    result = make_secret_scope_acl(scope=scope, principal=user.display_name,
                                   permission=AclPermission.READ)
```

---

## ML Fixtures

### `make_experiment`
- Creates an MLflow experiment
- Returns: `CreateExperimentResponse`

### `make_model`
- Creates a registered model in Model Registry
- Returns: `ModelDatabricks`
- Auto-tags with `RemoveAfter`

### `make_serving_endpoint`
- Creates a model serving endpoint
- Returns: `Wait[ServingEndpointDetailed]`
- Default model: `"system.ai.llama_v3_2_1b_instruct"`

### `make_feature_table`
- Creates a feature store table via REST API
- Returns: `dict`

---

## Permissions Fixtures

All follow the same pattern — accept `object_id`, `permission_level`, `group_name`/`user_name`:

| Fixture | Resource |
|---------|----------|
| `make_cluster_permissions` | Clusters |
| `make_cluster_policy_permissions` | Cluster policies |
| `make_instance_pool_permissions` | Instance pools |
| `make_job_permissions` | Jobs |
| `make_pipeline_permissions` | DLT pipelines |
| `make_notebook_permissions` | Notebooks |
| `make_directory_permissions` | Workspace directories |
| `make_workspace_file_permissions` | Workspace files |
| `make_repo_permissions` | Repos |
| `make_warehouse_permissions` | SQL warehouses |
| `make_experiment_permissions` | MLflow experiments |
| `make_registered_model_permissions` | Registered models |
| `make_serving_endpoint_permissions` | Serving endpoints |
| `make_feature_table_permissions` | Feature tables |
| `make_query_permissions` | Redash queries |
| `make_dashboard_permissions` | Redash dashboards |
| `make_alert_permissions` | Redash alerts |
| `make_lakeview_dashboard_permissions` | Lakeview dashboards |

```python
from databricks.sdk.service.iam import PermissionLevel

def test_permissions(make_group, make_model, make_registered_model_permissions):
    group = make_group()
    model = make_model()
    make_registered_model_permissions(
        object_id=model.id,
        permission_level=PermissionLevel.CAN_MANAGE,
        group_name=group.display_name,
    )
```

---

## Unit Testing with unwrap.py

For fast unit tests without connecting to a real workspace:

```python
from databricks.labs.pytester.fixtures.unwrap import CallContext, call_stateful

# CallContext provides mock implementations of all fixtures
ctx = CallContext()
ctx['sql_backend']  # -> MockBackend()
ctx['ws']           # -> autospec'd WorkspaceClient
ctx['make_random']  # -> always returns 'RANDOM'
ctx['env_or_skip']  # -> returns the env var name

# call_stateful calls a fixture function with mock dependencies
from databricks.labs.pytester.fixtures.catalog import make_table
ctx, result = call_stateful(make_table, catalog_name="hive_metastore")
```

---

## The factory() Pattern

All `make_*` fixtures use this core pattern:

```python
from databricks.labs.pytester.fixtures.baseline import factory

def make_my_resource(ws, make_random):
    def create(**kwargs):
        name = f"my-{make_random(8)}"
        ws.some_api.create(name, **kwargs)
        return name

    def cleanup(name):
        ws.some_api.delete(name)

    yield from factory("my resource", create, cleanup)
```

Behavior:
1. Returns a callable that calls `create()` and stores the result
2. On teardown, iterates through all created items in reverse and calls `cleanup()`
3. Catches `DatabricksError` during cleanup (logs and continues)

---

## Environment Variables Summary

| Variable | Used by | Required? |
|----------|---------|-----------|
| `DATABRICKS_HOST` | `ws`, `acc` | Yes |
| `DATABRICKS_ACCOUNT_ID` | `acc` | Yes (skips if missing) |
| `DATABRICKS_WAREHOUSE_ID` | `sql_backend` | Yes (skips if missing) |
| `DATABRICKS_CLUSTER_ID` | `spark` | Yes (unless serverless) |
| `DATABRICKS_SERVERLESS_COMPUTE_ID` | `spark` | Optional (`"auto"` for serverless) |
| `DATABRICKS_TOKEN` | `ws`, `acc` | Auth (one of many methods) |
| `DATABRICKS_CLIENT_ID` | `ws`, `acc` | OAuth M2M |
| `DATABRICKS_CLIENT_SECRET` | `ws`, `acc` | OAuth M2M |
| `CLOUD_ENV` | Integration tests | `"aws"` or `"azure"` |

---

## Serverless Configuration

```bash
# Enable serverless for the spark fixture
export DATABRICKS_SERVERLESS_COMPUTE_ID=auto
```

When `auto`, Databricks Connect ignores `cluster_id` and uses serverless compute.