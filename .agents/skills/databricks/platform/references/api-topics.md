# Databricks Workspace API Topics — Complete Reference

All 80+ workspace API topics mapped to SDK services, CLI commands, and REST API URLs.
REST API base: `https://<workspace-url>/api/2.0/` (workspace) or `https://<workspace-url>/api/2.1/` (Unity Catalog)

---

## AI / ML

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.serving_endpoints` | `serving-endpoints` | `/api/2.0/serving-endpoints` | `create_and_wait`, `get`, `list`, `update_config_and_wait`, `put_ai_gateway`, `query`, `get_permissions`, `set_permissions`, `build_logs`, `logs`, `export_metrics`, `patch` (tags), `delete` |
| `w.experiments` | `experiments` | `/api/2.0/mlflow/experiments` | `create`, `get`, `list`, `search`, `update`, `delete`, `restore`, `set_experiment_tag` |
| `w.experiments` (runs) | `experiments` | `/api/2.0/mlflow/runs` | `create`, `get`, `search`, `update`, `delete`, `restore`, `log_metric`, `log_param`, `log_batch`, `log_model`, `log_inputs`, `log_outputs`, `set_tag`, `get_history`, `list_artifacts` |
| `w.experiments` (logged models) | `experiments` | `/api/2.0/mlflow/logged-models` | `create`, `get`, `search`, `delete`, `finalize`, `log_params` |
| `w.registered_models` | `registered-models` | `/api/2.1/unity-catalog/registered-models` | `create`, `get`, `list`, `update`, `delete`, `set_alias`, `delete_alias`, `get_permissions`, `set_permissions` |
| `w.model_versions` | `model-versions` | `/api/2.1/unity-catalog/model-versions` | `create`, `get`, `list`, `update`, `delete`, `get_permissions`, `set_permissions` |
| `w.model_aliases` | `model-aliases` | `/api/2.1/unity-catalog/registered-models/{name}/aliases` | `get`, `set`, `delete` |
| `w.model_registry` | `model-registry` | `/api/2.0/mlflow/registered-models` | `create`, `get`, `list`, `search`, `update`, `delete`, `rename`, `create-transition-request`, `approve-transition-request`, `reject-transition-request`, `create-webhook`, `list-webhooks`, `update-webhook`, `delete-webhook`, `test-webhook` |
| `w.model_version_artifacts` | `model-registry` | `/api/2.0/mlflow/model-versions` | `get-download-uri`, `list-artifacts` |
| `w.external_models` | `serving-endpoints` | `/api/2.0/endpoint-external-models` | `get-credential`, `list-providers` |
| `w.feature_tables` | `feature-tables` | `/api/2.0/feature-store/feature-tables` | `create`, `get`, `list`, `search`, `update`, `delete`, `recover`, `pause`, `resume`, `describe`, `get-code-diff`, `get-features`, `get-usage`, `log-features`, `search-upserts` |
| `w.feature_online_stores` | `feature-online-stores` | `/api/2.0/feature-store/feature-online-stores` | `create`, `get`, `list`, `delete` |
| `w.feature_store` | `feature-store` | `/api/2.0/feature-store` | `search` |
| `w.online_stores` | N/A | `/api/2.0/online-stores` | `create`, `get`, `list`, `delete` |
| `w.vector_search_endpoints` | `vector-search-endpoints` | `/api/2.0/vector-search/endpoints` | `create_endpoint`, `get_endpoint`, `list_endpoints`, `delete_endpoint`, `update_endpoint_budget_policy`, `retrieve_user_visible_metrics` |
| `w.vector_search_indexes` | `vector-search-indexes` | `/api/2.0/vector-search/indexes` | `create_index`, `get_index`, `list_indexes`, `query_index`, `scan_index`, `sync_index`, `upsert_data_vector_index`, `delete_data_vector_index`, `delete_index` |
| `w.clean_rooms` | `clean-rooms` | `/api/2.0/clean-rooms` | `create`, `get`, `update`, `delete` |
| `w.clean_room_assets` | `clean-room-assets` | `/api/2.0/clean-rooms/{id}/assets` | `create`, `get`, `list` |
| `w.clean_room_auto_approval_rules` | `clean-room-auto-approval-rules` | `/api/2.0/clean-rooms/{id}/auto-approval-rules` | `create`, `list` |
| `w.clean_room_task_runs` | `clean-room-task-runs` | `/api/2.0/clean-rooms/{id}/task-runs` | `get`, `list` |
| `w.ai_query_beta` | N/A | `/api/2.0/ai-query` | SQL `ai_query()` function |

---

## Unity Catalog

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.catalogs` | `catalogs` | `/api/2.1/unity-catalog/catalogs` | `create`, `get`, `list`, `update`, `delete`, `get_permissions`, `set_permissions` |
| `w.schemas` | `schemas` | `/api/2.1/unity-catalog/schemas` | `create`, `get`, `list`, `update`, `delete`, `get_permissions`, `set_permissions` |
| `w.tables` | `tables` | `/api/2.1/unity-catalog/tables` | `create`, `get`, `list`, `update`, `delete`, `get_permissions`, `set_permissions` |
| `w.table_constraints` | `table-constraints` | `/api/2.1/unity-catalog/table-constraints` | `create`, `delete` |
| `w.table_summaries` | `table-summaries` | `/api/2.1/unity-catalog/tables/summaries` | `get` |
| `w.volumes` | `volumes` | `/api/2.1/unity-catalog/volumes` | `create`, `get`, `list`, `update`, `delete` |
| `w.connections` | `connections` | `/api/2.1/unity-catalog/connections` | `create`, `get`, `list`, `update`, `delete` |
| `w.external_locations` | `external-locations` | `/api/2.1/unity-catalog/external-locations` | `create`, `get`, `list`, `update`, `delete`, `list-credentials` |
| `w.metastores` | `metastores` | `/api/2.1/unity-catalog/metastores` | `create`, `get`, `list`, `update`, `assign`, `unassign`, `get-summary` |
| `w.storage_credentials` | `storage-credentials` | `/api/2.1/unity-catalog/storage-credentials` | `create`, `get`, `list`, `update`, `delete`, `validate`, `get-access-bindings`, `update-access-bindings` |
| `w.metastore_assignments` | N/A | `/api/2.1/unity-catalog/workspace-assignments` | `get`, `list`, `batch-get`, `batch-update`, `update`, `delete` |
| `w.quality_monitors` | `quality-monitors` | `/api/2.1/unity-catalog/monitors` | `create`, `get`, `list`, `update`, `cancel`, `delete`, `get-lineage` |
| `w.system_schemas` | `system-schemas` | `/api/2.1/unity-catalog/system-schemas` | `list`, `get`, `enable`, `disable` |
| `w.functions` | `functions` | `/api/2.1/unity-catalog/functions` | `create`, `get`, `list`, `update`, `delete` |
| `w.grants` | `grants` | `/api/2.1/unity-catalog/grants` | `get`, `update` |
| `w.resource_quotas` | `resource-quotas` | `/api/2.1/unity-catalog/resource-quotas` | `get`, `list` |
| `w.table_summaries` | `table-summaries` | `/api/2.1/unity-catalog/tables/summaries` | `get` |
| `w.online_stores` | N/A | `/api/2.0/online-stores` | `create`, `get`, `list`, `delete` |

---

## Jobs & Pipelines

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.jobs` | `jobs` | `/api/2.1/jobs` | `create`, `get`, `list`, `update`, `reset`, `delete`, `run_now`, `submit`, `list_runs`, `get_run`, `get_run_output`, `cancel_run`, `repair_run`, `cancel_all_runs`, `get_permissive`, `reset_permissive` |
| `w.jobs` (runs) | `jobs` | `/api/2.1/jobs/runs` | `get`, `list`, `cancel`, `cancel_all`, `repair`, `get_output`, `get_history` |
| `w.pipelines` | `pipelines` | `/api/2.0/pipelines` | `create`, `get`, `list`, `update`, `delete`, `start_update`, `stop`, `list_updates`, `get_update`, `list_events`, `start`, `deploy`, `un部署` |
| `w.submission_runs` | N/A | `/api/2.1/jobs/runs/submit` | `get_run`, `get_output` |

---

## Compute

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.clusters` | `clusters` | `/api/2.0/clusters` | `create`, `start`, `restart`, `terminate`, `delete`, `permanent_delete`, `get`, `list`, `list_node_types`, `list_Zones`, `spark_versions`, `get_permissions`, `set_permissions`, `policy_config` |
| `w.instance_pools` | `instance-pools` | `/api/2.0/instance-pools` | `create`, `get`, `list`, `update`, `delete` |
| `w.instance_profiles` | `instance-profiles` | `/api/2.0/instance-profiles` | `add`, `list`, `remove` |
| `w.libraries` | `libraries` | `/api/2.0/libraries` | `install`, `uninstall`, `all_cluster_statuses`, `cluster_status`, `all_jobs_statuses`, `job_status` |
| `w.policies` | `cluster-policies` | `/api/2.0/cluster-policies` | `create`, `get`, `list`, `edit`, `delete` |

---

## Workspace (Files & Notebooks)

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.workspace` | `workspace` | `/api/2.0/workspace` | `list`, `import`, `export`, `delete`, `mkdirs`, `get_status`, `import_dir`, `export_dir` |
| `w.files` | `fs` | `/api/2.0/files` | `upload`, `download`, `get_status`, `delete`, `list`, `mkdirs` (Volumes only, not DBFS) |
| `w.repos` | `repos` | `/api/2.0/repos` | `create`, `get`, `list`, `update`, `delete` |

---

## SQL & Dashboards

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.statement_execution` | `sql-statements` | `/api/2.0/sql/statements` | `execute_statement` |
| `w.warehouses` | `warehouses` | `/api/2.0/sql/warehouses` | `create`, `get`, `list`, `update`, `delete`, `start`, `stop`, `get_permissions`, `set_permissions` |
| `w.data_sources` | `data-sources` | `/api/2.0/sql/data-sources` | `list` |
| `w.alerts` | `alerts` | `/api/2.0/sql/alerts` | `create`, `get`, `list`, `update`, `delete` |
| `w.dashboards` | `dashboards` | `/api/2.0/sql/dashboards` | `create`, `get`, `list`, `update`, `delete` |
| `w.query_history` | `query-history` | `/api/2.0/sql/history/queries` | `list` |
| `w.query_visualizations` | N/A | `/api/2.0/sql/visualizations` | `create`, `delete`, `update` |
| `w.schedules` | `dashboard-schedules` | `/api/2.0/sql/schedules` | `create`, `get`, `list`, `update`, `delete` |
| `w.statement_results` | N/A | `/api/2.0/sql/statements` | Poll for async results |

---

## Databricks Apps

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.apps` | `apps` | `/api/2.0/apps` | `create`, `get`, `list`, `update`, `delete`, `start`, `stop`, `deploy`, `get_deployments`, `get_event_log` |

---

## IAM & Access Control

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.current_user` | `current-user` | `/api/2.0/preview/scim/v2/Me` | `me`, `get` |
| `w.groups` | `groups` | `/api/2.0/preview/scim/v2/Groups` | `create`, `get`, `list`, `patch`, `delete` |
| `w.users` | `users` | `/api/2.0/preview/scim/v2/Users` | `create`, `get`, `list`, `patch`, `delete` |
| `w.service_principals` | `service-principals` | `/api/2.0/preview/scim/v2/ServicePrincipals` | `create`, `get`, `list`, `patch`, `delete`, `get_permissions`, `set_permissions` |
| `w.account_level_saml_policies` | N/A | `/api/2.0/accounts/{account_id}/scim/v2/Policies` | `get`, `patch`, `list` |
| `w.ip_access_lists` | `ip-access-lists` | `/api/2.0/ip-access-lists` | `create`, `get`, `list`, `update`, `delete`, `replace`, `append` |
| `w.token_management` | `token-management` | `/api/2.0/token-management` | `create_obo_token`, `get_token_permission_levels`, `list`, `get`, `delete`, `revoke`, `rotate` |
| `w.permission_levels` | `permissions` | `/api/2.0/permission_levels` | `get` |
| `w.permissions` | `permissions` | `/api/2.0/permissions` | `get`, `set`, `update` |

---

## Secrets

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.secrets` | `secrets` | `/api/2.0/secrets` | `put_secret`, `get_secret`, `list_scopes`, `list_secrets`, `create_scope`, `delete_scope`, `put_acl`, `get_acl`, `delete_acl`, `delete_secret` |

---

## Groups & Scim

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.groups` | `groups` | `/api/2.0/preview/scim/v2/Groups` | `create`, `get`, `list`, `patch`, `delete` |
| `w.users` | `users` | `/api/2.0/preview/scim/v2/Users` | `create`, `get`, `list`, `patch`, `delete` |
| `w.service_principals` | `service-principals` | `/api/2.0/preview/scim/v2/ServicePrincipals` | `create`, `get`, `list`, `patch`, `delete` |

---

## Networking & Access

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.ip_access_lists` | `ip-access-lists` | `/api/2.0/ip-access-lists` | `create`, `get`, `list`, `update`, `delete`, `replace`, `append` |
| `w.workspace_conf` | `workspace-conf` | `/api/2.0/workspace-conf` | `get`, `set` |

---

## Account APIs

Use `AccountClient` (not `WorkspaceClient`) for these. All require account-level OAuth credentials.

| SDK Service | REST API | Key Methods |
|---|---|---|
| `a.account_metastores` | `/api/2.0/accounts/{account_id}/metastores` | `create`, `get`, `list`, `update`, `delete`, `assign`, `unassign` |
| `a.account_compute` | `/api/2.0/accounts/{account_id}/instance-pools` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_networks` | `/api/2.0/accounts/{account_id}/networks` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_storage` | `/api/2.0/accounts/{account_id}/storage` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_credentials` | `/api/2.0/accounts/{account_id}/credentials` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_workspaces` | `/api/2.0/accounts/{account_id}/workspaces` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_users` | `/api/2.0/accounts/{account_id}/users` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_groups` | `/api/2.0/accounts/{account_id}/groups` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_service_principals` | `/api/2.0/accounts/{account_id}/service-principals` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_access_control` | `/api/2.0/accounts/{account_id}/access-control` | `get_permissions` |
| `a.account_ip_access_lists` | `/api/2.0/accounts/{account_id}/ip-access-lists` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_network_policy` | `/api/2.0/accounts/{account_id}/network-policies` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_settings` | `/api/2.0/accounts/{account_id}/settings` | `get`, `update` |
| `a.account_tags` | `/api/2.0/accounts/{account_id}/tags` | `create`, `get`, `list`, `update`, `delete` |
| `a.account_tag_policies` | `/api/2.0/accounts/{account_id}/tag-policies` | `get`, `update` |

---

## Workspace Settings

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.workspace_conf` | `workspace-conf` | `/api/2.0/workspace-conf` | `get`, `set` |
| `w.token_management` | `token-management` | `/api/2.0/token-management` | `create_obo_token`, `get_token_permission_levels`, `list`, `get`, `delete`, `revoke`, `rotate` |

---

## Experiments & MLflow

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.experiments` | `experiments` | `/api/2.0/mlflow/experiments` | `create`, `get`, `list`, `search`, `update`, `delete`, `restore`, `set_experiment_tag` |
| `w.experiments` (runs) | `experiments` | `/api/2.0/mlflow/runs` | `create`, `get`, `search`, `update`, `delete`, `restore`, `log_metric`, `log_param`, `log_batch`, `log_model`, `log_inputs`, `log_outputs`, `set_tag`, `get_history`, `list_artifacts` |
| `w.experiments` (logged models) | `experiments` | `/api/2.0/mlflow/logged-models` | `create`, `get`, `search`, `delete`, `finalize`, `log_params` |

---

## File Operations

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.files` | `fs` | `/api/2.0/files` | `upload`, `download`, `get_status`, `delete`, `list`, `mkdirs` |
| `w.dbfs` | `fs` | `/api/2.0/dbfs` | `open`, `get_status`, `list`, `put`, `delete`, `mkdirs`, `move`, `copy`, `get_contents` (DEPRECATED — use `w.files` for Volumes) |

---

## Reporting & Token Management

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.token_management` | `token-management` | `/api/2.0/token-management` | `create_obo_token`, `get_token_permission_levels`, `list`, `get`, `delete`, `revoke`, `rotate` |

---

## Git & Repos

| SDK Service | CLI Group | REST API | Key Methods |
|---|---|---|---|
| `w.repos` | `repos` | `/api/2.0/repos` | `create`, `get`, `list`, `update`, `delete` |
| `w.git_credentials` | `git-credentials` | `/api/2.0/git-credentials` | `create`, `get`, `list`, `update`, `delete` |

---

## Quick Lookup: CLI → SDK Mapping

```
databricks <CLI-group>       →  w.<sdk_service>
─────────────────────────────────────────────────
serving-endpoints             →  w.serving_endpoints
experiments                   →  w.experiments
registered-models             →  w.registered_models
model-versions                →  w.model_versions
model-registry                →  w.model_registry (legacy)
catalogs                      →  w.catalogs
schemas                       →  w.schemas
tables                        →  w.tables
volumes                       →  w.volumes
jobs                          →  w.jobs
pipelines                     →  w.pipelines
clusters                      →  w.clusters
instance-pools                →  w.instance_pools
instance-profiles             →  w.instance_profiles
libraries                     →  w.libraries
workspace                     →  w.workspace
fs                            →  w.files (Volumes) / w.dbfs (legacy)
repos                         →  w.repos
sql-statements                →  w.statement_execution
warehouses                    →  w.warehouses
alerts                        →  w.alerts
dashboards                    →  w.dashboards
secrets                       →  w.secrets
groups                        →  w.groups
users                         →  w.users
service-principals            →  w.service_principals
permissions                   →  w.permissions
token-management              →  w.token_management
ip-access-lists               →  w.ip_access_lists
apps                          →  w.apps
vector-search-endpoints       →  w.vector_search_endpoints
vector-search-indexes         →  w.vector_search_indexes
clean-rooms                   →  w.clean_rooms
```

## Quick Lookup: SDK Service → Python Import

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

# All services are accessed as w.<service_name>
# e.g., w.serving_endpoints, w.jobs, w.catalogs, etc.

# For account-level APIs:
from databricks.sdk import AccountClient
a = AccountClient()
# e.g., a.account_workspaces, a.account_metastores
```

## Gotchas

1. **`w.dbfs`** is DEPRECATED for Volumes — use `w.files` for UC Volumes (DBR 13.3 LTS+)
2. **`w.model_registry`** is DEPRECATED — use `w.registered_models` / `w.model_versions` for Unity Catalog
3. **CLI `catalogs list`** uses positional args: `databricks schemas list <CATALOG>` (NOT `--catalog`)
4. **REST API v2.0 vs v2.1**: UC APIs use `/api/2.1/`, workspace APIs use `/api/2.0/`
5. **`w.api_client.do(...)`** — generic REST fallback for any endpoint not covered by SDK services
6. **`databricks experimental`** commands and Beta flags can break in any MINOR release
7. **AccountClient** does NOT support notebook-native auth — must use explicit OAuth credentials
