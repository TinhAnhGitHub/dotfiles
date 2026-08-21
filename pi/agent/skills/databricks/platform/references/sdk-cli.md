# SDK & CLI Reference

## Databricks CLI — Command Groups

Version: 0.218+ minimum (current stable: 0.298+). All commands support `-p/--profile`, `-o/--output json|text`, `-t/--target`, `--debug`.

### Essential Commands by Domain

**Workspace:**
```bash
databricks workspace list /path
databricks workspace import ./notebook.py /Users/me/notebook --language PYTHON
databricks workspace export /Users/me/notebook ./downloaded.py
databricks workspace mkdirs /Users/me/new-folder
databricks workspace delete /Users/me/notebook
databricks workspace export-dir /Users/me/folder ./local-folder   # bulk export
databricks workspace import-dir ./local-folder /Users/me/folder   # bulk import

databricks fs ls dbfs:/            # DBFS file system
databricks fs cp local.txt dbfs:/remote.txt --overwrite
databricks fs cp dbfs:/Volumes/cat/sch/vol/file.csv ./local.csv
databricks fs cat dbfs:/path/to/file.txt   # print remote file contents
databricks fs rm -r dbfs:/path/to/dir      # recursive remove

databricks repos create --url https://github.com/org/repo --provider gitHub
databricks repos update /Repos/me/repo --branch main
databricks repos list
databricks git-credentials create --personal-access-token <pat> --git-provider gitHub
```

**Standalone Sync (local → workspace):**
```bash
# Use for general local→workspace file sync (not just bundles).
# Sync is unidirectional; never deletes pre-existing remote files.
databricks sync ./local-dir /Users/me/my-folder              # one-shot
databricks sync ./local-dir /Users/me/my-folder --watch     # continuous
databricks sync ./local-dir /Users/me/my-folder --full      # ignore snapshot
databricks sync ./local-dir /Users/me/my-folder --exclude '*.pyc' --exclude '.git/**'
databricks sync ./local-dir /Users/me/my-folder --dry-run   # preview
# Stores incremental snapshot under .databricks/ in the source tree.
```

**Compute:**
```bash
databricks clusters list
databricks clusters get 1234-567890-abcde123
databricks clusters create --json-file cluster.json
databricks clusters start 1234-567890-abcde123
databricks clusters permanent-delete 1234-567890-abcde123

databricks clusters list-node-types                # Available instance types
databricks clusters spark-versions                 # Available Spark versions
databricks libraries install 1234-567890 --json '{"pypi": {"package": "pandas"}}'

databricks instance-pools list
databricks instance-profiles list
```

**Jobs:**
```bash
databricks jobs list
databricks jobs get <job-id>
databricks jobs run-now <job-id>
databricks jobs submit --json '{"tasks": [...], "run_name": "one-off"}'
databricks jobs list-runs <job-id>
databricks jobs get-run <run-id>
databricks jobs get-run-output <run-id>
databricks jobs cancel-run <run-id>
databricks jobs repair-run <run-id>
databricks jobs reset <job-id> --json-file updated-job.json
```

**Pipelines (DLT):**
```bash
databricks pipelines list-pipelines
databricks pipelines get <pipeline-id>
databricks pipelines start-update <pipeline-id>
databricks pipelines stop <pipeline-id>
databricks pipelines list-updates <pipeline-id>
```

**Unity Catalog:**
```bash
databricks catalogs list
databricks schemas list --catalog-name main
databricks tables list --catalog-name main --schema-name default
databricks volumes list --catalog-name main --schema-name default
databricks grants get --securable-type catalog --full-name main
databricks external-locations list
databricks storage-credentials list
databricks metastores list
```

**Serving Endpoints:**
```bash
databricks serving-endpoints list
databricks serving-endpoints get <endpoint-name>
databricks serving-endpoints query <endpoint-name> --json '{"messages": [...]}'
```

**Secrets:**
```bash
databricks secrets list-scopes
databricks secrets list-secrets --scope my-scope
databricks secrets create-scope my-scope
databricks secrets put-secret my-scope my-key --string-value "my-value"
databricks secrets get-acl my-scope --principal user@example.com
```

**Identity:**
```bash
databricks users list
databricks groups list
databricks service-principals list
databricks current-user me
```

**Auth (CLI) — `databricks auth <subcommand>`:**
```bash
# Debug: show which credentials are in use and from where
databricks auth describe                 # text
databricks auth describe -o json         # structured
databricks auth describe --sensitive     # include tokens (careful in CI logs)

# Browser OAuth (U2M) — saves to ~/.databrickscfg profile
databricks auth login                              # opens browser to login.databricks.com
databricks auth login DEV                           # saves to profile [DEV]
databricks auth login --host https://adb-xxx.azuredatabricks.net
databricks auth login --host 'https://.../?o=<ws_id>&account_id=<id>'  # URL query params
databricks auth login --scopes all-apis             # or restrict scopes
databricks auth login --configure-cluster          # also configure default cluster
databricks auth login --configure-serverless       # also configure serverless

# Token management
databricks auth token                # get OAuth token from local cache for DEFAULT profile
databricks auth token DEV            # for profile [DEV]
databricks auth token --force-refresh --timeout 5m

# Profile management
databricks auth profiles                        # list all profiles in ~/.databrickscfg
databricks auth profiles --skip-validate        # don't probe each profile
databricks auth switch DEV                      # set [DEV] as the default

# Logout (U2M only)
databricks auth logout                          # interactive picker
databricks auth logout DEV                      # specific profile
databricks auth logout DEV --delete             # also remove profile from cfg
databricks auth logout --auto-approve           # CI-friendly
```

**Generic REST API (passthrough):**
```bash
# For endpoints not yet covered by a dedicated CLI command group
# (e.g. newest preview APIs, or one-off calls).
databricks api get    /api/2.0/clusters/list
databricks api post   /api/2.0/jobs/create        -d @job.json
databricks api put    /api/2.0/clusters/edit/1234  -d @edit.json
databricks api patch  /api/2.0/serving-endpoints/my-ep -d @patch.json
databricks api delete /api/2.0/clusters/permanent-delete/1234
databricks api head   /api/2.0/preview/scim/v2/Me  # headers only
# Use --output json (global flag) to capture the response for scripting.
```

**`databricks configure` (interactive):**
```bash
# Writes a profile to ~/.databrickscfg. Non-interactive reads token from stdin.
databricks configure                                  # interactive, profile DEFAULT
databricks configure --host https://adb-xxx.azuredatabricks.net
databricks configure --profile DEV --configure-cluster
```

**Shell autocompletion (CLI v0.290.0+):**
```bash
databricks completion install        # auto-detect shell, write rc file
databricks completion status         # verify it's wired up
databricks completion uninstall      # remove autocompletion
# Supports: bash, zsh, fish, powershell
```

**`databricks aitools` (CLI v1.0.0+) — install Databricks skills into coding agents:**
```bash
# Installs Databricks agent skills (assistant-ui / agent skills) into your
# local coding agent: Claude Code, Cursor, Codex CLI, OpenCode, GitHub Copilot.
databricks aitools install
databricks aitools uninstall
databricks aitools status
# Use this to onboard a developer onto Databricks-aware agent skills.
```

**`databricks labs` — community Labs ecosystem:**
```bash
# List and install community-contributed Labs projects.
databricks labs install ucx          # Unity Catalog migration toolkit (most common)
databricks labs install sandbox      # experimental projects (requires v0.210.1+)
databricks labs install lsql         # Labs SQL toolkit
databricks labs list                 # show installed
databricks labs ucx ...              # run subcommands of a labs project

# UCX (Unity Catalog Upgrade) guides the user through prompts to configure
# the inventory database + SQL warehouse, then runs table/view migration,
# permission remapping, and compatibility assessment. Best practice: install
# in a dedicated venv per environment to avoid dependency conflicts.
```

**`databricks lakebase` (CLI v0.294.0+) — OLTP Postgres-compatible database:**
```bash
# Lakebase is Databricks' OLTP database capability. Resources are addressed
# via hierarchical names like projects/<id>/branches/<id>/endpoints/<id>.
databricks lakebase create-project   --json @project.json
databricks lakebase create-branch    --project-id <pid> --json @branch.json
databricks lakebase create-endpoint  --project-id <pid> --branch-id <bid> --json @ep.json
databricks lakebase list-projects
databricks lakebase list-branches --project-id <pid>
databricks lakebase list-endpoints --project-id <pid> --branch-id <bid>
databricks lakebase generate-database-credential --project-id <pid> --branch-id <bid>
# Use 'databricks postgres' for newer branch/endpoint/role/synced-table operations
# (renamed in v0.298+).
```

**`databricks feature-engineering` (v0.270.0+) — feature store:**
```bash
# Feature store CRUD (tables, functions, models)
databricks feature-engineering ...
```

**`databricks lakeview` / `lakeview-embedded` — AI/BI dashboards:**
```bash
# Manage Lakeview (AI/BI) dashboards and embedded variants
databricks lakeview create --json @dashboard.json
databricks lakeview list
databricks lakeview-embedded ...     # token-based APIs for external embedding
```

**`databricks clean-rooms` — privacy-preserving data collaboration:**
```bash
databricks clean-rooms create --json @cleanroom.json
databricks clean-room-asset-revisions ...
databricks clean-room-assets ...
databricks clean-room-auto-approval-rules ...
databricks clean-room-task-runs ...
```

**`databricks quality-monitors` / `quality-monitor-v2` / `data-quality`:**
```bash
# Original quality monitor API
databricks quality-monitors create --json @monitor.json
databricks quality-monitors get <table-fqn>
databricks quality-monitors delete <table-fqn>

# Updated v2 API
databricks quality-monitor-v2 create --json @monitor.json

# Data quality monitoring (v2 unified API)
databricks data-quality ...
```

**Account-level commands (require `--account-id` or account host):**
```bash
# All account-* groups require account-level auth.
databricks account users list
databricks account groups list
databricks account service-principals list
databricks account workspaces list
databricks account metastores list
databricks account metastores assign --workspace-id <id> --metastore-id <id>
databricks account storage list
databricks account network-connectivity ...
databricks account private-access ...
databricks account account-iam-v2 ...
databricks account access-control ...
# AccountClient from the Python SDK is recommended over the CLI for
# repetitive account-level operations.
```

**SQL:**
```bash
databricks warehouses list
databricks warehouses start <id>
databricks warehouses stop <id>
databricks warehouses get-workspace-warehouse-config

databricks queries list
databricks queries create --json @query.json
databricks queries get <id>
databricks queries update <id> --json @query.json
databricks queries delete <id>

databricks alerts list
databricks alerts create --json @alert.json

databricks dashboards list           # legacy dashboards (deprecated)
databricks dashboards get <id>
databricks dashboards restore <id>

databricks lakeview list            # AI/BI dashboards (preferred)
databricks query-history list       # audit SQL history

databricks data-sources list        # discover warehouse data_source_id
```

**Output conventions (see `docs/output.md` in the CLI repo):**
- **stdout** = primary command result. Composable for `jq`, `>>`, pipes.
- **stderr** = errors, progress, logs. Safe to redirect `2>/dev/null` in CI.
- **Progress** is only printed when stderr is a TTY (or logging is disabled) — non-TTY CI runs are silent.
- **`--output json`** for machine-readable output. Most commands return JSON arrays or objects.
- **`--output text`** (default) for humans; pipe-friendly only when output is single-value.
- **`--debug`** enables request/response logging (auth headers, retries, status codes). Use when triaging "Unable to parse response" errors.
- **JSON events** (e.g., `databricks sync`) use newline-delimited JSON with a `type` discriminator (`start` / `progress` / `complete`) and a `seq` field for run association.

**Utility:**
```bash
databricks version
databricks api get /api/2.0/clusters/list          # Raw REST API call
databricks configure                               # Interactive setup
```

## Databricks SDK for Python

Install: `pip install databricks-sdk>=0.72.0` (pin minor version in production).

### Authentication Methods

**Zero-config (default):**
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()  # Tries all methods automatically
```

Authentication order: SDK config fields > environment variables > `~/.databrickscfg` profile.

**OAuth M2M (recommended for automation):**
```python
w = WorkspaceClient(
    host='https://dbc-xxxx.cloud.databricks.com',
    client_id='your-client-id',
    client_secret='your-client-secret'
)

# Account-level
from databricks.sdk import AccountClient
a = AccountClient(
    host='https://accounts.cloud.databricks.com',
    account_id='your-account-id',
    client_id='your-client-id',
    client_secret='your-client-secret'
)
```

**PAT (legacy):**
```python
w = WorkspaceClient(
    host='https://dbc-xxxx.cloud.databricks.com',
    token='dapi...'  # Not recommended in source code
)
```

**Config profiles:**
```ini
# ~/.databrickscfg
[DEFAULT]
host = https://production.cloud.databricks.com
client_id = <id>
client_secret = <secret>

[DEV]
host = https://dev.cloud.databricks.com
client_id = <dev-id>
client_secret = <dev-secret>
```
```python
w = WorkspaceClient(profile='DEV')
# Or: export DATABRICKS_CONFIG_PROFILE=DEV
```

**Azure-specific:**
```python
# Azure CLI auth (local dev)
w = WorkspaceClient(host='https://adb-xxxx.azuredatabricks.net')

# Azure SP with workspace resource ID
w = WorkspaceClient(
    host='https://adb-xxxx.azuredatabricks.net',
    azure_workspace_resource_id='/subscriptions/.../resourceGroups/.../providers/Microsoft.Databricks/workspaces/...',
    azure_tenant_id='...', azure_client_id='...', azure_client_secret='...'
)
```

### Key Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABRICKS_HOST` | Workspace URL |
| `DATABRICKS_TOKEN` | Personal Access Token |
| `DATABRICKS_CLIENT_ID` | OAuth client ID |
| `DATABRICKS_CLIENT_SECRET` | OAuth client secret |
| `DATABRICKS_ACCOUNT_ID` | Account ID (account ops) |
| `DATABRICKS_CONFIG_PROFILE` | Profile name in `.databrickscfg` |
| `DATABRICKS_CONFIG_FILE` | Alt config file location |
| `DATABRICKS_AUTH_TYPE` | Force specific auth method |
| `DATABRICKS_CLUSTER_ID` | Cluster ID for Connect/dbutils |
| `DATABRICKS_RATE_LIMIT` | Max requests/second |

### WorkspaceClient — Key Service Objects

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

# Clusters
for c in w.clusters.list():
    print(c.cluster_name, c.state)

info = w.clusters.create_and_wait(
    cluster_name='my-cluster',
    spark_version='15.4.x-scala2.12',
    node_type_id='i3.xlarge',
    autotermination_minutes=15,
    num_workers=1
)
w.clusters.permanent_delete(cluster_id='...')

# Jobs
from databricks.sdk.service.jobs import Task, NotebookTask, Source

j = w.jobs.create(
    name='my-job',
    tasks=[Task(
        task_key='notebook_task',
        notebook_task=NotebookTask(
            notebook_path='/Users/me/notebook',
            source=Source("WORKSPACE")
        ),
    )]  # Serverless by default — no cluster_id needed
)

w.jobs.run_now(job_id=j.job_id)
for run in w.jobs.list_runs(job_id=j.job_id, expand_tasks=False):
    print(run.state.result_state)

# Files (Unity Catalog volumes — use w.files, NOT dbutils.fs)
w.files.create_directory('/Volumes/main/default/my-volume/folder')
w.files.upload_from(
    '/Volumes/main/default/my-volume/folder/data.csv',
    './local.csv',
    overwrite=True
)
for f in w.files.list_directory_contents('/Volumes/main/default/my-volume'):
    print(f.path)
w.files.download_to('/Volumes/.../data.csv', './downloaded.csv')

# Secrets
w.secrets.put_secret(scope='my-scope', key='my-key', string_value='value')
for s in w.secrets.list_secrets(scope='my-scope'):
    print(s.key)

# Serving Endpoints
for ep in w.serving_endpoints.list():
    print(ep.name, ep.state.config_served_entities[0].state)

response = w.serving_endpoints.query(
    name='my-endpoint',
    inputs=[{'messages': [{'role': 'user', 'content': 'Hello'}]}]
)

# Unity Catalog
for cat in w.catalogs.list():
    print(cat.name)
for table in w.tables.list(catalog_name='main', schema_name='default'):
    print(table.name)
w.grants.get(securable_type='catalog', full_name='main')

# dbutils integration
d = w.dbutils
files = d.fs.ls('/')
secrets = d.secrets.list_scopes()
d.widgets.text("param", "default", "Label")
value = d.widgets.get("param")

# SQL
from databricks.sdk.service.sql import StatementParameterListItem
w.statement_execution.execute_statement(
    warehouse_id='...',
    statement='SELECT * FROM main.default.my_table LIMIT 10',
    catalog='main',
    schema='default'
)
```

### AccountClient — Account-Level Operations

```python
from databricks.sdk import AccountClient

a = AccountClient()
for g in a.groups.list():
    print(g.display_name)
for ws in a.workspaces.list():
    print(ws.workspace_name)

# Cross-workspace: get a WorkspaceClient from AccountClient
wss = list(a.workspaces.list())
w = a.get_workspace_client(wss[0])
```

### Testing Patterns

```python
from unittest.mock import create_autospec
from databricks.sdk import WorkspaceClient

# Mock WorkspaceClient
mock_client = create_autospec(WorkspaceClient)
mock_client.clusters.create.return_value.cluster_id = '123abc'

# Call your function with mock
response = create_cluster(w=mock_client, cluster_name='test', ...)
assert response.cluster_id == '123abc'
```

### Notebook-Specific Notes

- SDK pre-installed on DBR 13.3 LTS+ clusters
- Auto-generates temporary PAT (deleted after notebook stops)
- `WorkspaceClient()` works with zero config inside notebooks
- `AccountClient` does NOT support notebook-native auth — requires explicit credentials
- Notebook auth only works on the driver node, not executor nodes
- Config profiles not supported in notebooks

## Scripting with the CLI

### JSON Parsing with `jq`

```bash
# Get a specific job ID by name
JOB_ID=$(databricks jobs list -o json | jq -r '.[] | select(.settings.name == "my-job") | .job_id')

# List running clusters
databricks clusters list -o json | jq '[.[] | select(.state == "RUNNING")]'

# Inspect a run's result state
databricks jobs get-run $RUN_ID -o json | jq -r '.state.result_state'

# Endpoint status
databricks serving-endpoints get my-endpoint -o json | jq '.state'
```

### Error Handling & Rate Limits

```bash
#!/bin/bash
set -euo pipefail
MAX_RETRIES=3
RETRY_DELAY=10
for i in $(seq 1 $MAX_RETRIES); do
  if databricks bundle deploy -t prod 2>&1; then
    break
  else
    if [ $i -lt $MAX_RETRIES ]; then
      echo "Retry $i/$MAX_RETRIES in ${RETRY_DELAY}s..."
      sleep $RETRY_DELAY
      RETRY_DELAY=$((RETRY_DELAY * 2))  # exponential backoff
    else
      exit 1
    fi
  fi
done
```

- API returns **HTTP 429** on rate-limit with `Retry-After` header — implement exponential backoff with jitter.
- Per-workspace limits apply separately per API endpoint — long loops of calls benefit from `sleep` or batching.

## CI/CD Auth — OIDC Workload Identity Federation (Secretless)

OIDC federation lets the CI provider issue short-lived tokens, avoiding stored secrets.

**GitHub Actions:**
```yaml
env:
  DATABRICKS_AUTH_TYPE: github-oidc
  DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
  DATABRICKS_CLIENT_ID: ${{ secrets.DATABRICKS_CLIENT_ID }}
steps:
  - uses: actions/checkout@v4
  - uses: databricks/setup-cli@main   # or microsoft/install-databricks-cli@v1
  - run: databricks bundle deploy -t prod --auto-approve
```

**Azure DevOps:**
```yaml
env:
  DATABRICKS_AUTH_TYPE: azure-devops-oidc
  DATABRICKS_HOST: $(DATABRICKS_HOST)
  DATABRICKS_CLIENT_ID: $(DATABRICKS_CLIENT_ID)
steps:
  - bash: curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
  - bash: databricks bundle deploy -t prod
```

**GitLab CI:**
```yaml
deploy:
  image: ghcr.io/databricks/cli:latest
  variables:
    DATABRICKS_HOST: $DATABRICKS_HOST
    DATABRICKS_TOKEN: $DATABRICKS_TOKEN
  script:
    - databricks bundle deploy -t prod
```

**Known gotcha:** in v0.290.0, profile names are now correctly wired through OAuth argument resolution — `--profile` works with M2M flows. v0.290.1 added clearer errors when an auth token is used with an M2M profile.

## Versioning & Stability

- **v1.0.0 GA (2026-05-21)**: semantic versioning enforced. Breaking changes only in MAJOR (stable) / MINOR (Beta / Private Preview / Experimental) bumps.
- **Stable by default**: commands and flags not marked Beta / Private Preview / Experimental.
- **`databricks experimental`** is the explicit opt-in group for early-access commands — may break in any MINOR.
- **Pin minor version** in production CI: `databricks/setup-cli@v0.298.0` not `@main`.
- **Air-gapped environments**: use Docker image `ghcr.io/databricks/cli:<version>`.

### Gotchas

1. **Pin SDK version** in production: `databricks-sdk>=0.72.0,<0.73.0`
2. **"Unable to parse response"** error almost always = auth misconfiguration. Check host URL, auth method, firewall/proxy.
3. **PAT limitations**: workspace-scoped only, 90-day auto-revoke, max 600/user.
4. **For volumes from SDK**: use `w.files` (not `dbutils.fs` from local code).
5. **Long-running ops**: use `.result(timeout=timedelta(minutes=10))` or `.result(callback=print_status)`.
6. **Azure CLI auth**: works for local dev but not for production CI/CD — use M2M with service principal.
7. **Auth resolution divergence**: `bundle` and non-bundle CLI commands may resolve auth differently — running a bundle command from inside a bundle directory can infer host from `databricks.yml` and override your `--profile` or `DATABRICKS_HOST`. Run non-bundle commands from a non-bundle directory if you hit this.
8. **`--var` doesn't carry to `bundle run`**: variables set via `--var=key=value` on `deploy` are not re-applied to `run` — re-specify them.
9. **CLI binary is now `databricks` only**: the legacy Python `databricks-cli` (v0.18 and below) is deprecated — migrate to the Go-based CLI.
