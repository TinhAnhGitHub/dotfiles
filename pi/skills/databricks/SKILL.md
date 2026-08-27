---
name: databricks
description: >
  Databricks unified skill suite: CLI, Python SDK, DABs, Unity Catalog, Jobs,
  Pipelines, Model Serving, AI/agents, Apps, Lakebase, serverless migration,
  vector search, LLMOps, app design, and platform operations. This is the
  parent/entry-point skill for ALL Databricks work. Load this first, then load
  the matching sub-skill from the routing table below.
---

# Databricks — Unified Skill Suite

This master skill covers the entire Databricks platform. Use the routing table
to identify the right sub-skill for your task, then load it alongside this one.

---

## Sub-Skill Routing

| Topic | Sub-skill | Load When… |
|-------|-----------|------------|
| **CLI basics, auth, profiles, data exploration** | [`core`](core/SKILL.md) | Setting up CLI, authenticating, browsing catalogs/schemas/tables, debugging auth issues |
| **Bundle (DABs) config, deploy, CI/CD** | [`dabs`](dabs/SKILL.md) | Creating/validating/deploying `databricks.yml` bundles, multi-environment targets |
| **Lakeflow Jobs (data engineering DAGs)** | [`jobs`](jobs/SKILL.md) | Orchestrating multi-task jobs, notebooks, Python wheels, SQL, dbt, triggers |
| **Lakeflow Spark Declarative Pipelines (DLT)** | [`pipelines`](pipelines/SKILL.md) | Building batch/streaming ETL pipelines with Python or SQL |
| **Model Serving & MLflow model development** | [`model-serving`](model-serving/SKILL.md) | Managing serving endpoints, registering models, PyFunc, batch scoring |
| **End-to-end LLMOps workflows** | [`llmops`](llmops/SKILL.md) | Designing or implementing Git-to-production workflows for agents and LLM applications, including component lineage, prompt/version management, evaluation gates, custom serving endpoint releases, monitoring, cost, rollback, and governance |
| **MLflow GenAI evaluation, tracing & monitoring** | [`evaluation-monitoring`](../mlflow/evaluation-monitoring/SKILL.md) | Evaluation datasets, human feedback/expectations, LLM judges/scorers, prompt/agent/trace evaluation, regression tests, automatic evaluation, UC traces, production monitoring |
| **MLflow app versioning & GenAI packaging** | [`version-tracking`](../mlflow/version-tracking/SKILL.md) + [`genai-flavors`](../mlflow/genai-flavors/SKILL.md) | LoggedModel/Git lineage, LangChain/LangGraph, DSPy, LlamaIndex, ResponsesAgent, Models from Code, signatures and resources |
| **MLflow Prompt Registry & prompt optimization** | [`prompt-registry`](../mlflow/prompt-registry/SKILL.md) | Prompt versions/aliases, `prompts:/` URIs, templates, model configuration, lineage, GEPA/MetaPromptOptimizer, and model migration |
| **MLflow Model Registry & UC promotion** | [`model-registry`](../mlflow/model-registry/SKILL.md) | Registered model versions/aliases, signatures, environment promotion, rollback, and the explicit bridge to served entities/traffic |
| **MLflow MCP Registry** | [`mcp-registry`](../mlflow/mcp-registry/SKILL.md) | Governed MCP server versions, aliases, tool snapshots, access endpoints, and Databricks-served agent dependencies |
| **Databricks Apps (full-stack deployment)** | [`apps`](apps/SKILL.md) | Building and deploying Streamlit, Gradio, Dash, Flask, FastAPI apps |
| **Data App UI/UX design** | [`app-design`](app-design/SKILL.md) | Designing dashboards, KPIs, charts, Genie/chat surfaces with proper layout and notation |
| **Lakebase Postgres (OLTP)** | [`lakebase`](lakebase/SKILL.md) | Provisioning Postgres projects, synced tables, Data API, connectivity |
| **Serverless compute migration** | [`serverless-migration`](serverless-migration/SKILL.md) | Migrating from classic clusters to serverless, Spark Connect fixes |
| **Vector Search (RAG/semantic)** | [`vector-search`](vector-search/SKILL.md) | Creating/managing/querying vector indexes for RAG |
| **Platform operations (all-in-one)** | [`platform`](platform/SKILL.md) | Cross-cutting: CLI/SDK reference, secrets, clusters, Unity Catalog, gotchas, tool reference table, full API topics reference (80+ workspace APIs) |

---

## Common Patterns (Shared Across All Databricks Skills)

- **Auth**: `--profile` flag or `DATABRICKS_CONFIG_PROFILE` env var. Config stored at `~/.databrickscfg` (Linux/macOS) or `%USERPROFILE%\.databrickscfg` (Windows). Use `databricks auth describe` to debug which method/host is being resolved.
- **UC FQN**: `catalog.schema.object` — three-level namespace for all governed data. Tables, views, volumes, functions, and models share this format.
- **Bundle variables**: `${var.name}` (custom), `${bundle.target}` (target name), `${workspace.host}` (workspace URL), `${resources.jobs.<name>.id}` (deployed resource ID). Resolution order: CLI `--var` > env `BUNDLE_VAR_*` > `.databricks/bundle/<target>/variable-overrides.json` > target YAML > variable default.
- **Job params**: `named_parameters` in YAML → `sys.argv` as `--key=value` → `argparse` in entrypoint. Job-level params override task-level params with the same key.
- **Volume path**: `/Volumes/catalog/schema/volume/path` — the `dbfs:/Volumes/...` alternative also works from Spark. Requires Databricks Runtime 13.3 LTS+.
- **Secret ref**: `{{secrets/scope/key}}` syntax in endpoint configs and bundle variables to avoid plaintext secrets.
- **Serverless vs classic**: Serverless is the default for new jobs, pipelines, and serving endpoints. Classic (all-purpose or job clusters) available for workloads needing custom configurations.
- **CLI output streams**: stdout = primary command result, stderr = errors + progress + logs. Progress only prints when stderr is a TTY (or logging is off). Use `--output json` for composability in scripts; `--debug` exposes the full request/response log.
- **Bundle deployment engines**: `terraform` (default, legacy) vs `direct` (since CLI 0.279, becoming the only engine in 2026). Toggle via `bundle.engine` / `targets.<name>.engine` in `databricks.yml` or `DATABRICKS_BUNDLE_ENGINE` env var (YAML wins).

---

## Top Gotchas (Cross-Cutting)

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
13. **`databricks experimental`** commands and any flag marked **Beta** / **Private Preview** can break in any MINOR release.
14. **`databricks bundle deployment migrate`** is one-way at the state file level — rollback requires restoring `tfstate.json.backup` and removing `resources.json`.
15. **`databricks sync`** is unidirectional — never deletes pre-existing remote files.

---

## Quick Reference (CLI)

```bash
# current user
databricks current-user me --profile <PROFILE>

# list resources
databricks apps list --profile <PROFILE>
databricks jobs list --profile <PROFILE>
databricks clusters list --profile <PROFILE>
databricks warehouses list --profile <PROFILE>
databricks pipelines list --profile <PROFILE>
databricks serving-endpoints list --profile <PROFILE>

# Unity Catalog — POSITIONAL arguments (NOT flags!)
databricks catalogs list --profile <PROFILE>
databricks schemas list <CATALOG> --profile <PROFILE>
databricks tables list <CATALOG> <SCHEMA> --profile <PROFILE>
databricks tables get <CATALOG>.<SCHEMA>.<TABLE> --profile <PROFILE>

# bundles
databricks bundle validate --profile <PROFILE>
databricks bundle deploy -t <TARGET> --profile <PROFILE>
databricks bundle run <RESOURCE> -t <TARGET> --profile <PROFILE>
```

## Data Exploration — Use AI Tools

```bash
databricks experimental aitools tools discover-schema catalog.schema.table --profile <PROFILE>
databricks experimental aitools tools query "SELECT * FROM table LIMIT 10" --profile <PROFILE>
databricks experimental aitools tools get-default-warehouse --profile <PROFILE>
```

**Names are literal.** Use catalog/schema/table names exactly as given — never change a hyphen to an underscore. In SQL, backtick-quote any name part with special characters.

---

## Workflow

1. **Load this skill** (`databricks`) first.
2. **Identify the sub-skill** from the routing table above and load it too.
3. For CLI/auth issues, also load [`core`](core/SKILL.md).
4. For platform-wide operations, also load [`platform`](platform/SKILL.md).
5. For any MLflow task, also load parent [`mlflow`](../mlflow/SKILL.md) and the narrow
   sub-skill listed above. Combine [`model-serving`](model-serving/SKILL.md) with
   [`model-registry`](../mlflow/model-registry/SKILL.md) for UC model promotion and endpoint
   rollout; combine it with [`genai-flavors`](../mlflow/genai-flavors/SKILL.md) when packaging
   custom PyFunc or ResponsesAgent artifacts.
6. For a production LLM application or agent, load [`llmops`](llmops/SKILL.md) as the
   orchestration layer, then add only the component skills needed by the implementation.
