# Databricks Apps — Deployment & Development

## Overview

Databricks Apps are containerized web applications running on the Databricks serverless platform. They integrate natively with Unity Catalog, Databricks SQL, OAuth 2.0, MLflow, and Lakeflow Jobs.

**Use cases:** Interactive dashboards, RAG chat apps, data entry forms, custom analytics, AI-powered interfaces.

**Default compute:** Ubuntu 22.04 LTS, Python 3.11, Node.js 22.16, 2 vCPUs, 6 GB RAM. Compute size configurable (`MEDIUM`, `LARGE`).

**Billing:** Per hour while running. Stopped/Deploying/Crashed apps incur no charges.

**Limits:** 100 apps per workspace. Individual files max 10 MB.

## Supported Frameworks

### Python (auto-configured port/host)
| Framework | Auto-set Variables |
|-----------|-------------------|
| Streamlit | `STREAMLIT_SERVER_PORT`, `STREAMLIT_SERVER_ADDRESS=0.0.0.0`, `STREAMLIT_SERVER_HEADLESS=true` |
| Gradio | `GRADIO_SERVER_PORT`, `GRADIO_SERVER_NAME=0.0.0.0` |
| Dash | `PORT` |
| Flask | `FLASK_RUN_PORT`, `FLASK_RUN_HOST=0.0.0.0` |
| FastAPI | `UVICORN_PORT`, `UVICORN_HOST=0.0.0.0` |
| Shiny | (supported) |

### Node.js
Express (`PORT`), React, Angular, Svelte. No Node.js libraries pre-installed.

### Hybrid
Combine Python + Node.js (e.g., React frontend + FastAPI backend). Both `requirements.txt` and `package.json` can coexist. Use `concurrently` to run both.

## Pre-installed Python Libraries

No need to list in `requirements.txt` unless overriding version:

| Library | Version | Library | Version |
|---------|---------|---------|---------|
| databricks-sql-connector | 3.4.0 | databricks-sdk | 0.33.0 |
| mlflow-skinny | 2.16.2 | gradio | 4.44.0 |
| streamlit | 1.38.0 | shiny | 1.1.0 |
| dash | 2.18.1 | flask | 3.0.3 |
| fastapi | 0.115.0 | uvicorn | 0.30.6 |
| gunicorn | 23.0.0 | plotly | 5.24.1 |

**With `uv` (`pyproject.toml` + `uv.lock`):** No pre-installed libraries; declare all.

## `app.yaml` Configuration

Must be at project root. `.yaml` and `.yml` both accepted. Optional — defaults apply if absent.

```yaml
# Custom startup command
command: ['streamlit', 'run', 'app.py']
# OR
command:
  - gunicorn
  - app:app
  - -w
  - 4

# Environment variables
env:
  - name: LOG_LEVEL          # Hardcoded value
    value: 'debug'
  - name: WAREHOUSE_ID       # From workspace resource (configured in UI)
    value: 'abc1234567890'
  - name: MY_API_KEY         # From secret (resolved at runtime)
    valueFrom: secret        # "secret" = resource key in UI
```

**Key rules:**
- Command is NOT run in a shell — external env vars unavailable. Exception: `DATABRICKS_APP_PORT` is substituted at runtime.
- Never hardcode secrets in `value`. Use `valueFrom` for sensitive data.
- `DATABRICKS_APP_PORT` is the only env var substituted in the command.

## Environment Variables

### Always Available

| Variable | Description |
|----------|-------------|
| `DATABRICKS_APP_NAME` | Name of the running app |
| `DATABRICKS_WORKSPACE_ID` | Workspace unique ID |
| `DATABRICKS_HOST` | Workspace URL |
| `DATABRICKS_APP_PORT` | Port the app must listen on |
| `DATABRICKS_CLIENT_ID` | Service principal OAuth client ID |
| `DATABRICKS_CLIENT_SECRET` | Service principal OAuth secret |

### How to access in code
```python
import os
warehouse_id = os.getenv("WAREHOUSE_ID")
port = os.getenv("DATABRICKS_APP_PORT")
```

## Authentication & Authorization

### Two Identity Models

**App Authorization (service principal):**
- All users share the app's auto-provisioned service principal identity
- Use for: background tasks, logging, shared config, calling external services
- Credentials: `DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET` (auto-injected)
- SDK auto-detects: `WorkspaceClient()` works with zero config

**User Authorization (on-behalf-of-user, Preview):**
- App acts with individual user's identity
- Token arrives via `x-forwarded-access-token` HTTP header
- Respects user's Unity Catalog permissions (row-level filters, column masks)
- Requires users to be in the same Databricks account, signed in via SSO
- Must declare OAuth scopes (e.g., `sql`, `files.files`)

### Framework-specific Token Retrieval

```python
# Streamlit
token = st.context.headers.get('x-forwarded-access-token')

# Gradio
def predict(input, request: gr.Request):
    token = request.headers.get("x-forwarded-access-token")

# Flask / Dash
token = request.headers.get('x-forwarded-access-token')

# Express (Node.js)
const token = req.header('x-forwarded-access-token');
```

## Data Access — Resource Types

Apps access Databricks services through declared resources (configured in Apps UI):

| Resource Type | `valueFrom` Resolves To | Permissions |
|---------------|------------------------|-------------|
| SQL Warehouse | Warehouse ID | Can use, manage |
| UC Table | Full table name (`catalog.schema.table`) | Select, Modify |
| UC Volume | Volume path (`/Volumes/...`) | Can read, read+write |
| UC Connection | Connection name | Use Connection |
| Model Serving Endpoint | Endpoint name | Can view, query, manage |
| Lakeflow Job | Job ID | Can view, manage run, manage |
| Genie Space | Space ID | Can view, run, edit, manage |
| Secret | Decrypted secret value | Can read, write, manage |
| Vector Search Index | Index full name | Can select |
| MLflow Experiment | Experiment ID | Can read, edit, manage |
| User-Defined Function | Function full name | Can execute |
| Lakebase Database | Endpoint path | Can connect and create |

### Querying UC Tables from App

```python
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()
conn = sql.connect(
    server_hostname=cfg.host,
    http_path="/sql/1.0/warehouses/<warehouse-id>",
    credentials_provider=lambda: cfg.authenticate,
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM main.default.my_table LIMIT 100")
df = cursor.fetchall_arrow()
```

### State Persistence

Apps do NOT preserve in-memory state after restarts. Use:

| Storage | Use Case |
|---------|----------|
| UC Tables (via SQL) | Persistent structured data |
| UC Volumes | Persistent files with governance |
| Workspace Files | Persistent files |
| Lakebase Database | PostgreSQL-compatible relational storage |
| In-memory / local FS | Temporary only (lost on restart) |

## Deployment

### Project Structure

```
my-app/
  app.yaml              # Optional: command, env vars
  app.py                # Entry point (Python)
  requirements.txt      # Python deps (pip) -- OR:
  pyproject.toml        # Python deps (uv)
  uv.lock               # Lock file
  package.json          # Node.js deps (optional)
  static/               # Static assets (optional)
```

### CLI Commands

```bash
# Create app
databricks apps create my-app [--compute-size LARGE] [--no-compute]

# Deploy from workspace
databricks apps deploy my-app \
  --source-code-path /Workspace/Users/me/my-app \
  --mode AUTO_SYNC        # or SNAPSHOT

# Deploy from Git
databricks apps deploy my-app --json '{"git_source": {"branch": "main"}}'
databricks apps deploy my-app --json '{"git_source": {"tag": "v1.0.0"}}'
databricks apps deploy my-app --json '{"git_source": {"commit": "abc123"}}'
databricks apps deploy my-app --json '{"git_source": {"branch": "main", "source_code_path": "apps/my-app"}}'

# Logs
databricks apps logs my-app --follow --tail-lines 100
databricks apps logs my-app --source APP --search "error"

# Status / management
databricks apps get my-app
databricks apps list
databricks apps start my-app
databricks apps stop my-app
databricks apps delete my-app --auto-approve

# Deployments
databricks apps list-deployments my-app
databricks apps get-deployment my-app <deployment-id>

# Local development
databricks apps run-local --prepare-environment --debug

# Sync files to workspace (watches for changes)
databricks sync --watch . /Workspace/Users/me/my-app
```

### Deploy Flags

| Flag | Description |
|------|-------------|
| `--source-code-path` | Workspace path of source code |
| `--mode` | `AUTO_SYNC` (continuous sync) or `SNAPSHOT` |
| `--deployment-id` | Custom deployment ID |
| `--json` | Inline JSON or `@path` with request body |
| `--force` | Force-override Git branch validation |
| `--no-wait` | Don't wait for SUCCEEDED state |
| `--skip-validation` | Skip build/typecheck/lint |
| `--timeout` | Max time to reach SUCCEEDED (default: 20m) |

### Deployment Logic

**If `package.json` present:**
1. `npm install`
2. `pip install -r requirements.txt` (or `uv sync`)
3. `npm run build` (if `build` script exists)
4. Run `command` from `app.yaml`, or `npm run start`

**If `package.json` absent:**
1. `pip install -r requirements.txt` (or `uv sync` if both `pyproject.toml` + `uv.lock` exist)
2. Run `command` from `app.yaml`, or `python <my-app>.py`

**Dependency precedence:** `requirements.txt` > (`pyproject.toml` + `uv.lock`) for Python.

### Rollback

No explicit rollback command. Options:
1. Redeploy a specific Git commit: `databricks apps deploy my-app --json '{"git_source": {"commit": "abc123"}}'`
2. List past deployments: `databricks apps list-deployments my-app`, then redeploy
3. Revert workspace files and redeploy

## Monitoring & Observability

### Application Logs

```bash
# CLI
databricks apps logs my-app --follow --tail-lines 200 --source APP

# Direct URL
# https://<app-name>-<workspace-id>.<region>.databricksapps.com/logz
```

**Important:** Logs are NOT persisted when compute shuts down. For persistence:
- Enable App Telemetry (Beta) to Unity Catalog tables
- Use external APM (New Relic, Datadog)
- Write logs to UC volumes/tables

### Health Checks (Insights Tab — Beta)

| Signal | Meaning |
|--------|---------|
| App service health | Databricks infrastructure availability |
| App availability | Whether app is serving requests |

### App Telemetry (Beta)

Collects traces, logs, metrics to UC tables via OpenTelemetry.

**Setup:**
1. App details > Settings > App telemetry > Add
2. Select catalog + schema. Creates: `otel_metrics`, `otel_spans`, `otel_logs`
3. Redeploy app

**Custom instrumentation by framework:**

| Framework | app.yaml command | Key dependencies |
|-----------|-----------------|------------------|
| Streamlit | `opentelemetry-instrument streamlit run app.py` | `opentelemetry-distro`, `opentelemetry-exporter-otlp-proto-grpc` |
| Flask | `opentelemetry-instrument flask --app app.py run --no-reload` | `opentelemetry-distro`, `opentelemetry-instrumentation-flask` |
| FastAPI | `opentelemetry-instrument uvicorn app:app --host 0.0.0.0 --port 8000` | `opentelemetry-distro`, `opentelemetry-instrumentation-fastapi` |
| Dash | `opentelemetry-instrument python app.py` | `opentelemetry-distro[otlp]`, `opentelemetry-instrumentation-flask` |
| Node.js | `node -r ./otel.js app.js` | `@opentelemetry/sdk-node`, `@opentelemetry/auto-instrumentations-node` |

Set `OTEL_TRACES_SAMPLER=always_on` in `app.yaml` env for all frameworks.

### Cost Monitoring

```sql
SELECT
  us.usage_date,
  us.usage_metadata.app_name,
  SUM(us.usage_quantity) AS dbus,
  SUM(us.usage_quantity * lp.pricing.effective_list.default) AS dollars
FROM system.billing.usage us
LEFT JOIN system.billing.list_prices lp ON lp.sku_name = us.sku_name
WHERE billing_origin_product = 'APPS'
  AND us.usage_unit = 'DBU'
  AND us.usage_date >= DATE_SUB(NOW(), 30)
GROUP BY ALL
```

### Audit Logs

All app-related events in `system.access.audit`:
- `changeAppsAcl` — permission changes
- `createApp`/`updateApp` — app lifecycle events
- OAuth OBO events — user authorization actions

## Embedding

```html
<iframe
  src="https://your-workspace.databricks.com/apps/your-app-name"
  width="100%"
  height="600px"
  frameborder="0">
</iframe>
```

- Users must be authenticated Databricks users
- Users need appropriate app permissions
- App must be running

## Best Practices

### Architecture
- **Offload data processing** to Databricks SQL, Lakeflow Jobs, Model Serving — app compute is for UI only
- **Graceful shutdown**: must complete within 15 seconds of `SIGTERM` or gets `SIGKILL`
- **Bind correctly**: listen on `0.0.0.0` and the port from `DATABRICKS_APP_PORT`
- **Support H2C** (HTTP/2 cleartext) — Databricks handles TLS termination
- **Minimize startup time**: lazy-load heavy resources, avoid blocking at init

### Security
- **Least privilege**: `CAN USE` instead of `CAN MANAGE` unless needed
- **One service principal per app**: never share credentials
- **Use `valueFrom`** for secrets, never hardcode
- **Parameterized SQL**: prevent injection
- **Isolate environments**: separate dev/staging/prod workspaces
- **Restrict outbound network**: allow only needed domains
- **Audit monitoring**: set up alerts for unusual access patterns

### Data
- **Access data through compute** (SQL warehouses, Model Serving, Jobs), not directly
- **Persist state** in UC tables, volumes, or Lakebase — not in-memory
- **Scope OAuth carefully**: request only needed scopes

### Dependencies
- Use `uv` with lock file (recommended), or pin exact versions in `requirements.txt`
- Private PyPI: set `PIP_INDEX_URL` via `valueFrom` referencing a secret
- Install wheels from UC Volumes: `/Volumes/<catalog>/<schema>/<volume>/my_package.whl`

## App URL Format

```
https://<app-name>-<workspace-id>.<region>.databricksapps.com
```

Cannot be changed after creation. To get a different URL, create a new app.

## CLI Commands (App Lifecycle)

```bash
# Create & deploy
databricks apps create --json '{"display_name": "my-app", "app_type": "PYTHON_STREAMLIT"}'
databricks apps deploy <app-name> --source-code-path ./my-app
databricks apps get-deployment <app-name> --deployment-id <dep-id>
databricks apps list-deployments <app-name>

# Start / Stop
databricks apps start <app-name>
databricks apps stop <app-name>

# Monitor
databricks apps get <app-name>
databricks apps list
databricks apps logs <app-name>                     # app runtime logs

# Development
databricks apps run-local <app-name>               # run locally for development
databricks apps import --json '{"url":"https://..."}'  # import existing app as bundle

# Management
databricks apps create-update <app-name> --json @update.json
databricks apps get-update <app-name> --update-id <uid>
databricks apps update <app-name> --json @patch.json
databricks apps delete <app-name>

# Thumbnail
databricks apps update-app-thumbnail <app-name> --image @icon.png
databricks apps delete-app-thumbnail <app-name>
```

**CI/CD integration**: Bundle-based deployment with `databricks bundle deploy` is the recommended production path. CLI commands above are for ad-hoc management and debugging.

## Key Gotchas

1. **Logs not persisted** on compute shutdown — enable telemetry or external APM.
2. **15-second SIGTERM window** — implement graceful shutdown or risk SIGKILL.
3. **No `apt-get`/`yum`/`apk`** — apps run as non-privileged users. Use PyPI/npm only.
4. **No custom TLS** — Databricks handles TLS termination. Support H2C only.
5. **`devDependencies` skipped** if `NODE_ENV=production` — list all needed packages in `dependencies`.
6. **`requirements.txt` takes precedence** over `pyproject.toml` for dependency resolution.
7. **User authorization requires SSO** — cannot embed for anonymous/non-Databricks users.
8. **Workspace admins can enforce Git-only** deployments — disables workspace folder deploys.
9. **10 MB per file limit** — deployment fails if any single file exceeds this.
10. **App compute is for UI** — offload heavy processing to Databricks SQL, Jobs, or Model Serving.
