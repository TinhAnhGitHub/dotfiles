# Declarative Automation Bundles & Deployment

## Overview

Declarative Automation Bundles (formerly Databricks Asset Bundles) are the recommended IaC approach for Databricks. Define resources, variables, and targets in YAML; deploy via `databricks bundle` commands.

CLI requirement: `databricks` CLI v0.218.0+.

## `databricks.yml` — All Top-Level Keys

The root config must be named `databricks.yml`. One per project:

```yaml
bundle:            # Required: identity + metadata
  name: string     # Required: programmatic name
  databricks_cli_version: ">= 0.218.0"
  cluster_id: string
  deployment: { fail_on_active_runs, lock }
  git: { origin_url, branch }

resources:         # Databricks resource definitions (30+ types supported)
  jobs: {}
  pipelines: {}
  models: {}
  experiments: {}
  dashboards: {}
  volumes: {}
  schemas: {}
  catalogs: {}
  secret_scopes: {}
  apps: {}
  model_serving_endpoints: {}
  sql_warehouses: {}
  alerts: {}
  clusters: {}
  registered_models: {}
  quality_monitors: {}
  database_instances: {}
  postgres_projects: {}
  external_locations: {}
  lakebase_projects: {}     # OLTP databases (CLI v0.294.0+)
  vector_search_endpoints: {}
  vector_search_indexes: {}
  online_tables: {}
  feature_store: {}
  lakeview_dashboards: {}
  clean_rooms: {}
  connections: {}
  grants: {}
  # ... and more

targets:           # Deployment environments (dev, staging, prod)
  dev:
    default: true
    mode: development  # or production
    workspace: { host, profile, root_path, ... }
    resources: {}      # per-target overrides
    variables: {}       # per-target variable values

variables:         # Custom variables (string or complex type)
  my_var:
    description: string
    default: string_or_map
    type: complex      # only needed for complex variables
    lookup:             # auto-resolve IDs by name
      cluster: "my cluster name"

workspace:         # Connection settings
  host: "https://..."
  profile: "DEFAULT"
  root_path: "/Workspace/Users/.../.bundle/${bundle.name}/${bundle.target}"
  artifact_path: "${workspace.root}/artifacts"
  file_path: "${workspace.root}/files"

artifacts:         # Build artifacts (Python wheels, JARs)
  default:
    type: whl        # or jar
    build: "uv build --out-dir dist"
    path: "."
    files:
      - source: "dist/*.whl"

include:           # Split config across files
  - "resources/*.yml"
  - "targets.yml"

sync:              # File sync rules for workspace
  include: [...]
  exclude: [...]
  paths: [...]

scripts:           # Named scripts for `bundle run`
  test:
    content: "pytest -m unit"

permissions:       # Applied to all resources
  - level: CAN_MANAGE
    group_name: engineers

run_as:            # Identity to run bundle resources
  service_principal_name: "sp-id"
  # OR user_name: "user@example.com"

python:            # Python-based bundle config
  venv_path: ".venv"
  resources: ["my_project.resources:load"]

experimental:      # Feature flags
  python_wheel_wrapper: true
```

## Variable Substitution

### Built-in References

| Syntax | Resolves To |
|--------|-------------|
| `${bundle.name}` | Bundle programmatic name |
| `${bundle.target}` | Current target name (dev, prod) |
| `${bundle.git.branch}` | Current Git branch |
| `${workspace.host}` | Databricks workspace URL |
| `${workspace.current_user.userName}` | Deploying user's email |
| `${workspace.current_user.short_name}` | User's short name |
| `${workspace.root_path}` | Workspace root path |
| `${workspace.file_path}` | Workspace file path |
| `${workspace.artifact_path}` | Artifact storage path |
| `${resources.jobs.<name>.id}` | Deployed job ID |
| `${resources.pipelines.<name>.name}` | Pipeline name |

### Custom Variables

```yaml
# Simple string variable
variables:
  catalog:
    description: "UC catalog name"
    default: "main"

# Complex variable (entire map)
variables:
  my_cluster:
    type: complex
    default:
      spark_version: "15.4.x-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 2

# Usage
resources:
  jobs:
    my_job:
      tasks:
        - existing_cluster_id: ${var.catalog}      # simple
          new_cluster: ${var.my_cluster}             # complex
```

### Lookup Variables
Auto-resolve IDs by name. Supported types: `alert`, `cluster`, `cluster_policy`, `dashboard`, `instance_pool`, `job`, `metastore`, `notification_destination`, `pipeline`, `query`, `service_principal`, `warehouse`.

```yaml
variables:
  my_cluster_id:
    lookup:
      cluster: "12.2 shared"
```

### Variable Precedence (highest first)
1. `--var="key=value"` CLI flag
2. `BUNDLE_VAR_<name>` environment variable
3. `.databricks/bundle/<target>/variable-overrides.json`
4. `targets.<target>.variables.<name>` in YAML
5. `variables.<name>.default` in YAML

## Target Configuration

```yaml
targets:
  dev:
    default: true
    mode: development
    workspace:
      host: https://dev-workspace.databricks.com
    presets:
      name_prefix: "[dev] "
      trigger_pause_status: PAUSED
      jobs_max_concurrent_runs: 10
      tags:
        environment: dev
    variables:
      catalog: "dev_catalog"

  prod:
    mode: production
    workspace:
      host: https://prod-workspace.databricks.com
    git:
      branch: main
    run_as:
      service_principal_name: "prod-sp-id"
    presets:
      name_prefix: "[prod] "
      trigger_pause_status: UNPAUSED
    variables:
      catalog: "prod_catalog"
```

### Development Mode Defaults
- Resource names prefixed with `[dev <user>]`
- Tags jobs with `dev`
- Pauses all schedules/triggers
- Enables concurrent job runs
- Allows `--cluster-id` override
- Disables deployment lock

### Production Mode Requirements
- Validates current branch matches `git.branch`
- Validates `run_as` and `permissions` are specified
- Disallows cluster ID overrides

## Presets

Applied automatically based on mode, overridable by individual resource settings:

| Preset | Type | Description |
|--------|------|-------------|
| `name_prefix` | String | Prefix prepended to all resource names |
| `tags` | Map | Tags applied to all taggable resources |
| `trigger_pause_status` | PAUSED or UNPAUSED | Pause status for schedules |
| `jobs_max_concurrent_runs` | Integer | Max concurrent runs for all jobs |
| `pipelines_development` | Boolean | Set development mode on all pipelines |
| `source_linked_deployment` | Boolean | Resources point to source files in workspace |
| `artifacts_dynamic_version` | Boolean | Dynamically update whl artifact versions |

Override precedence: Individual resource > preset > mode default.

## Lifecycle Commands

```bash
# Create from template (TEMPLATE = default-python | default-sql | default-minimal |
#                      default-scala | dbt-sql | mlops-stacks | pydabs | <git-url> | <path>)
databricks bundle init [TEMPLATE]
databricks bundle init default-python --output-dir ./my-project
databricks bundle init --template-dir ./my-template --config-file ./init-params.json

# Validate config (catches schema errors before deploy)
databricks bundle validate

# Preview changes (dry run) — text or JSON plan
databricks bundle plan
databricks bundle plan -o json > plan.json   # save plan for review/CI gates

# Deploy to target (apply a plan file in direct engine mode)
databricks bundle deploy -t dev
databricks bundle deploy -t dev --auto-approve --force-lock
databricks bundle deploy -t dev --plan plan.json           # apply pre-approved plan
databricks bundle deploy -t dev --fail-on-active-runs      # fail if jobs running
databricks bundle deploy -t dev -c <cluster-id-override>   # dev only
databricks bundle deploy -t dev --force                    # override Git branch validation

# Run a resource
databricks bundle run <job_or_pipeline_key> -t dev
databricks bundle run <job_key> --params key=value --no-wait
databricks bundle run <key> --refresh-all                 # refresh all dependent tasks
databricks bundle run -- echo "hello world"               # run inline script

# Open resource in browser
databricks bundle open <key>

# Show deployed resources with URLs
databricks bundle summary

# Sync local files to workspace (dev iteration)
databricks bundle sync
databricks bundle sync --watch
databricks bundle sync --watch --dry-run
databricks bundle sync --full                              # force full sync

# Destroy deployed resources
databricks bundle destroy --auto-approve

# Generate config from existing resource
databricks bundle generate job --existing-job-id 12345 --bind
databricks bundle generate pipeline --existing-pipeline-id abcd --bind
databricks bundle generate app --existing-app-name my-app
databricks bundle generate dashboard --existing-dashboard-id abc123
databricks bundle generate alert --existing-alert-id <id>

# Bind / unbind bundle resource to existing workspace resource
databricks bundle deployment bind <resource_key> <remote_id>
databricks bundle deployment unbind <resource_key>
# Two-step migration: generate first, then deploy (or use --bind for one-step)

# Output JSON schema for IDE auto-completion
databricks bundle schema > databricks-bundle.schema.json
```

## Deployment Engines: `terraform` vs `direct`

Since CLI v0.279.0, bundles support two deployment engines:

| Engine | Default? | State file | Speed | Notes |
|--------|----------|------------|-------|-------|
| `terraform` | Yes (legacy) | `.databricks/bundle/<target>/terraform/tfstate.json` | Slower | Downloads Terraform + provider; works behind custom registries |
| `direct` | No (becoming the only engine in 2026) | `.databricks/bundle/<target>/resources.json` | Faster | Self-contained binary; 2-step diff; no external deps |

**Select an engine:**

```yaml
# In databricks.yml — bundle level
bundle:
  name: my-project
  engine: direct             # applies to all targets

# Or per-target
targets:
  prod:
    engine: terraform        # opt back into terraform for this target
```

```bash
# Or via env var (YAML wins if both are set)
DATABRICKS_BUNDLE_ENGINE=direct databricks bundle deploy -t dev
```

**Migrating from terraform to direct:**

```bash
# 1. Ensure a clean terraform-state deploy
databricks bundle deploy -t my_target --auto-approve

# 2. Convert state locally (creates resources.json, backs up tfstate.json)
databricks bundle deployment migrate -t my_target

# 3. Verify the plan is empty (no drift)
databricks bundle plan -t my_target
# → should show "no changes"

# 4. (Optional rollback) restore terraform state
mv .databricks/bundle/my_target/terraform/tfstate.json.backup \
   .databricks/bundle/my_target/terraform/tfstate.json
rm .databricks/bundle/my_target/resources.json

# 5. Finalize by deploying (syncs resources.json to the workspace)
databricks bundle deploy -t my_target
```

**Direct engine specifics:**

- **2-step diff**: (1) local config vs. last-deployed snapshot, (2) remote state vs. last-deployed snapshot. Every local config change triggers an update — never silently ignored.
- **No "Provider produced inconsistent result after apply" errors** — direct engine handles resource fields that terraform rejects, but resources may show as drift on the next plan.
- **`$resources` field resolution**: ALL/STATE fields resolve from local config; ALL/REMOTE fields resolve from remote. See `acceptance/bundle/refschema/out.fields.txt` in the CLI repo for the full schema.
- **State file location**: `.databricks/bundle/<target>/resources.json` (not `terraform/tfstate.json`).

**Plan-based deploy (direct engine only):**

```bash
# Generate a JSON plan for review / CI gating
databricks bundle plan -o json > plan.json

# Review the plan with jq
jq '.[] | {resource: .resource_key, action: .action, reason: .reason}' plan.json

# Apply the exact same plan (replay-safe, audit-friendly)
databricks bundle deploy --plan plan.json
```

## Deployment State Gotchas

- If the deployment state is lost (manual workspace edits, partial deletes), `bundle run` may fail with "deployment state not found". Fix: `bundle deploy --force-lock` to resync.
- Concurrent CI/CD deploys to the same target cause lock conflicts — serialize per target or use `--force-lock` carefully.
- For 50+ jobs, intermittent create/delete failures are possible during `deploy` / `destroy` — run with `--auto-approve` and monitor output, or split the bundle.

### Passing Job Parameters

```bash
# Job-level parameters (preferred)
databricks bundle run my_job --params catalog=main --params schema=default

# Task-specific parameters
databricks bundle run my_job --python-named-params catalog=main

# Inline script
databricks bundle run -- echo "hello world"
```

## CI/CD with GitHub Actions

### Prerequisites
- Databricks CLI in workflow: `databricks/setup-cli@main` or `@v0.9.0` (pinned)
- Auth: OAuth M2M service principal with `DATABRICKS_TOKEN` or workload identity federation
- Bundle config in repo root

### Dev Deployment (PR Trigger)

```yaml
# .github/workflows/dev-deploy.yml
name: Dev deployment
on:
  pull_request:
    types: [opened, synchronize]
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - run: databricks bundle deploy
        env:
          DATABRICKS_TOKEN: ${{ secrets.SP_TOKEN }}
          DATABRICKS_BUNDLE_ENV: dev

  # Optional: run a job after deploy
  run_job:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - run: databricks bundle run sample_job --refresh-all
        env:
          DATABRICKS_TOKEN: ${{ secrets.SP_TOKEN }}
          DATABRICKS_BUNDLE_ENV: dev
```

### Prod Deployment (Push to Main)

```yaml
# .github/workflows/prod-deploy.yml
name: Production deployment
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main
      - run: databricks bundle deploy
        env:
          DATABRICKS_TOKEN: ${{ secrets.SP_TOKEN }}
          DATABRICKS_BUNDLE_ENV: prod
```

### Service Principal Setup for CI/CD

1. Create a service principal in the Databricks account console
2. Generate an OAuth secret (client ID + client secret)
3. Create a token: `POST /api/2.0/token-management/on-behalf-of/tokens`
4. Store the token as a GitHub secret (e.g., `SP_TOKEN`)
5. For enhanced security, use workload identity federation: `DATABRICKS_AUTH_TYPE: github-oidc`

## Common Bundle Patterns

### Multi-File Split

```yaml
# databricks.yml
bundle:
  name: my-project
include:
  - "resources/*.yml"
  - "targets.yml"
```

### Python Wheel Job

```yaml
# resources/job.yml
resources:
  jobs:
    ingestion:
      name: csv_ingestion
      tasks:
        - task_key: ingest
          python_wheel_task:
            package_name: my_package
            entry_point: run_ingestion
            named_parameters:
              catalog: ${var.catalog}
              schema: ${var.schema}
          environment_key: default

      environments:
        - environment_key: default
          spec:
            environment_version: "5"
            dependencies:
              - ${workspace.artifact_path}/${var.wheel_name}
```

### DLT Pipeline

```yaml
resources:
  pipelines:
    etl_pipeline:
      name: my_etl
      catalog: ${var.catalog}
      schema: ${var.schema}
      serverless: true
      libraries:
        - notebook:
            path: ../src/transformations/
      edition: ADVANCED
```

## Key Gotchas

1. One `databricks.yml` per project root — cannot have multiple root configs.
2. Target override merges, not replaces — `resources` in target merges with top-level `resources`.
3. `${bundle.target}` resolves at deploy time, not at build time.
4. `--var` flag overrides override all other sources — powerful but can mask config issues.
5. `bundle run` with `--no-wait` doesn't report run status — use `databricks jobs get-run` to check.
6. In development mode, resource names are auto-prefixed — CI/CD should inject overrides for consistent naming.
7. Workspace paths are auto-prefixed with `/Workspace` if not already present.
8. **`--var` on `deploy` does not carry to `run`** — re-specify variables on the `run` command.
9. **CLI infers host from `databricks.yml`** when run from inside a bundle directory — can override intended `--profile` / `DATABRICKS_HOST`. Run non-bundle commands from outside the bundle, or use `bundle --target <t> --var ...` instead of `DATABRICKS_HOST=...`.
10. **Concurrent deploys** to the same target cause lock conflicts — serialize or use `--force-lock` carefully.
11. **`bundle validate`** can fail when the deploying user differs from `run_as` for pipelines — use the same identity for validation and deploy.
12. **AI/BI dashboard resources** in bundles fail when deployed from the Databricks Web Terminal — use local or CI deployment.
13. **CLI v0.274.0+ requires exactly one job owner** — multi-owner job deployments fail.
14. **Lakebase resources** in bundles require CLI v0.292.0+ and target engine compatibility.
15. **Vector search `min_qps` → `target_qps`** breaking change in CLI v0.299.2 — update all bundle YAML.
