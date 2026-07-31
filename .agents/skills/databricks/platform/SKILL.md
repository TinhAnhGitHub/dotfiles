---
name: databricks-platform
description: >
  Databricks platform: CLI, Python SDK, DABs, UC, Jobs, Pipelines, Model Serving,
  AI/agents, secrets, clusters, CI/CD, auth, apps, SQL, vector search, MLflow,
  Lakebase, IAM, tags, clean rooms, data quality, Delta Sharing, feature store.
  Triggers: databricks CLI/SDK, bundle deploy, UC catalogs/schemas/tables/volumes,
  serving-endpoints, ai-gateway, secrets, clusters, serverless, Lakeflow/DLT/DLT,
  workspace, dbutils, auth login/describe/token, api, sync, aitools, labs, lakebase,
  completion, quality-monitors, lakeview, clean-rooms, OIDC/workload-identity,
  /Volumes, /Repos, OAuth M2M/U2M, metastore, service principals, MLflow/ChatDatabricks,
  bundle plan/direct engine/migrate, --output json, experimental, tag policies,
  feature-engineering, online-tables, system schemas, AI/BI dashboards, Postgres env.
---

# Databricks Platform Skill

## Topic Routing

Read the relevant reference file based on the user's intent:

| User Intent | Reference |
|---|---|
| Bundle config, `databricks.yml`, YAML spec, deploy, targets, variables, CI/CD | `references/bundles-deploy.md` |
| CLI commands, SDK Python, auth profiles, dbutils, testing | `references/sdk-cli.md` |
| Agents, model serving, LLMs, AI Gateway, function calling, streaming | `references/agentic-ai.md` |
| Jobs, tasks, pipelines/DTL, DLT, triggers, compute options | `references/data-engineering.md` |
| Unity Catalog, catalogs, schemas, tables, volumes, GRANTS, metastores | `references/unity-catalog.md` |
| Secrets, clusters, auth profiles, networking, init scripts, libraries | `references/infra-config.md` |
| Databricks Apps, app deployment, app.yaml, Streamlit/Gradio/Dash/Flask/FastAPI, embedding | `references/apps-deploy.md` |
| REST API URLs, SDK service → CLI mapping, all 80+ workspace API topics | `references/api-topics.md` |

For cross-cutting questions, read the relevant combo — most Databricks tasks touch 2-3 of these domains.

## Common Patterns

These conventions hold across all Databricks tooling:

- **Auth**: `--profile` flag or `DATABRICKS_CONFIG_PROFILE` env var. Config stored at `~/.databrickscfg` (Linux/macOS) or `%USERPROFILE%\.databrickscfg` (Windows). Use `databricks auth describe` to debug which method/host is being resolved.
- **UC FQN**: `catalog.schema.object` — three-level namespace for all governed data. Tables, views, volumes, functions, and models share this format.
- **Bundle variables**: `${var.name}` (custom), `${bundle.target}` (target name), `${workspace.host}` (workspace URL), `${resources.jobs.<name>.id}` (deployed resource ID). Resolution order: CLI `--var` > env `BUNDLE_VAR_*` > `.databricks/bundle/<target>/variable-overrides.json` > target YAML > variable default.
- **Job params**: `named_parameters` in YAML → `sys.argv` as `--key=value` → `argparse` in entrypoint. Job-level params override task-level params with the same key.
- **Volume path**: `/Volumes/catalog/schema/volume/path` — the `dbfs:/Volumes/...` alternative also works from Spark. Requires Databricks Runtime 13.3 LTS+.
- **Secret ref**: `{{secrets/scope/key}}` syntax in endpoint configs and bundle variables to avoid plaintext secrets.
- **Serverless vs classic**: Serverless is the default for new jobs, pipelines, and serving endpoints. Classic (all-purpose or job clusters) available for workloads needing custom configurations.
- **CLI output streams**: stdout = primary command result, stderr = errors + progress + logs. Progress only prints when stderr is a TTY (or logging is off). Use `--output json` for composability in scripts; `--debug` exposes the full request/response log. `databricks sync` uses newline-delimited JSON with `type` discriminator (`start`/`progress`/`complete`) and a `seq` field.
- **Bundle deployment engines**: `terraform` (default, legacy) vs `direct` (since CLI 0.279, becoming the only engine in 2026). Toggle via `bundle.engine` / `targets.<name>.engine` in `databricks.yml` or `DATABRICKS_BUNDLE_ENGINE` env var (YAML wins). `direct` is a self-contained binary (no Terraform download), faster, and produces a 2-step diff (local-vs-snapshot then remote-vs-snapshot). State files differ in format and location.

## Top Gotchas

These trip up most practitioners:

1. **Shared job clusters** persist driver JVM state across tasks — parallel tasks can corrupt each other's singleton state. Use separate clusters or sequential dependencies for isolation.
2. **Workspace bindings** (ISOLATED) supersede privilege grants — even users with explicit `SELECT` cannot access a catalog not bound to their workspace.
3. **Endpoint names** cannot use the `databricks-` prefix (reserved for Databricks-hosted models).
4. **AccountClient** does NOT support notebook-native auth — must be configured with explicit OAuth credentials.
5. **Volumes** require DBR 13.3 LTS+. Use `w.files` from the SDK (not `dbutils.fs`) for UC volume operations from local code.
6. **PATs** are workspace-scoped only — no account-level API access. Auto-revoke after 90 days of inactivity. Databricks recommends OAuth M2M for automation.
7. **Job clusters** (`new_cluster`) are ephemeral and terminated after run — cheaper and isolated. All-purpose clusters (`existing_cluster_id`) persist state and cost more.
8. **For each** task inputs are capped: 5,000 chars in UI, 48 KB via task values, 10 KB for job parameter values.
9. **Continuous jobs** cannot use task dependencies or `Trigger.ProcessingTime`/`Trigger.Continuous` on serverless.
10. **GRANT groups** must be account-level groups, not workspace-local groups.
11. **CORS** must be enabled on S3 buckets for managed volume uploads.
12. **Endpoint creator identity** is permanently tied to the endpoint — cannot be changed; must delete and recreate.
13. **`databricks experimental`** commands and any flag marked **Beta** / **Private Preview** in `--help` can break in any MINOR release. Stable features only get breaking changes in MAJOR bumps.
14. **`databricks bundle deployment migrate`** is one-way at the state file level — `terraform` and `direct` engines use different state schemas. Rollback requires restoring `tfstate.json.backup` and removing `resources.json`.
15. **`databricks sync`** is unidirectional and never deletes pre-existing remote files — only creates/overwrites. For local→workspace dev iteration use `bundle sync --watch`; for general tree sync use `databricks sync SRC DST`.

## Tool Reference

| Task | CLI Command | SDK Python |
|------|-------------|------------|
| Deploy bundle | `databricks bundle deploy -t dev` | N/A (CLI-only) |
| Run job | `databricks jobs run-now <id>` | `w.jobs.run_now(job_id=...)` |
| List clusters | `databricks clusters list` | `w.clusters.list()` |
| Upload file to volume | `databricks fs cp local dbfs:/Volumes/...` | `w.files.upload_from(path, local_path)` |
| Create secret | `databricks secrets put-secret scope key` | `w.secrets.put_secret(scope, key, value)` |
| Grant access | `databricks grants update catalog ...` | `w.grants.get(...)` |
| Create serving endpoint | `databricks serving-endpoints create` | `w.serving_endpoints.create(...)` |
| List workspace files | `databricks workspace list /path` | `w.workspace.list('/path')` |
| Execute SQL | `databricks queries create ...` | `w.statement_execution.execute_statement(...)` |
| Debug auth | `databricks auth describe` | N/A (CLI-only) |
| Browser OAuth login | `databricks auth login --host ...` | N/A (CLI-only) |
| Generic REST call | `databricks api get /api/2.0/...` | `w.api_client.do(...)` |
| Sync local→workspace | `databricks sync SRC DST --watch` | `w.workspace.import_dir(...)` |
| Migrate bundle engine | `databricks bundle deployment migrate -t dev` | N/A (CLI-only) |
| Plan-based deploy | `databricks bundle plan -o json > plan.json` | N/A (CLI-only) |
| Setup CLI in CI | `databricks/setup-cli@v0.9.0` (GitHub Action) | N/A |
