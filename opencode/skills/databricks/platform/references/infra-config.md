# Infrastructure & Configuration

## Secret Scopes

Secret scopes store keys, tokens, and credentials securely. Referenced via `{{secrets/scope/key}}`.

```bash
# Create scope
databricks secrets create-scope my-scope

# Add secret
databricks secrets put-secret my-scope my-key --string-value "value"
databricks secrets put-secret my-scope my-key --bytes-value "..."
databricks secrets put-secret my-scope api-key \
  --string-value "$(cat ~/.ssh/api-key)"

# Read (only in notebooks/CLI)
databricks secrets get-secret my-scope my-key

# List
databricks secrets list-scopes
databricks secrets list-secrets --scope my-scope

# ACL management
databricks secrets put-acl my-scope user@example.com --permission READ
databricks secrets get-acl my-scope --principal user@example.com
databricks secrets delete-acl my-scope --principal user@example.com

# Delete
databricks secrets delete-secret my-scope my-key
databricks secrets delete-scope my-scope
```

```python
# SDK
w.secrets.put_secret(scope='my-scope', key='api-key', string_value='sk-...')
for scope in w.secrets.list_scopes():
    print(scope.name)
for secret in w.secrets.list_secrets(scope='my-scope'):
    print(secret.key)

# dbutils (inside notebook)
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
dbutils = w.dbutils
value = dbutils.secrets.get(scope='my-scope', key='api-key')
```

### Secret References in Configs
```
{{secrets/my-scope/api-key}}           # In endpoint configs
{{secrets/my-scope/my-key}}            # In bundle variables via --var
```

## Cluster Configuration

### Cluster Types

| Type | Use Case | Lifecycle |
|------|----------|-----------|
| **All-purpose** | Interactive notebooks, development | Persistent, shared |
| **Job cluster** | Production jobs | Ephemeral, per run |
| **Instance pool** | Pre-warmed instances | Reusable pool |
| **Serverless** | Jobs, pipelines, endpoints | Managed by Databricks |

### Cluster JSON

```json
{
  "cluster_name": "my-cluster",
  "spark_version": "15.4.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 2,
  "autotermination_minutes": 30,
  "spark_conf": {
    "spark.sql.shuffle.partitions": "200"
  },
  "custom_tags": {
    "team": "data-engineering",
    "project": "etl-pipeline"
  },
  "init_scripts": [
    {
      "workspace": {
        "destination": "/Users/me/init-scripts/install.sh"
      }
    }
  ]
}
```

```bash
databricks clusters list
databricks clusters create --json '{"cluster_name": "my-cluster", ...}'
databricks clusters start <cluster-id>
databricks clusters permanent-delete <cluster-id>

# List node types and Spark versions
databricks clusters list-node-types
databricks clusters spark-versions

# Cluster events (for debugging)
databricks clusters events <cluster-id>
```

### Cluster Policies
Restrict how users configure clusters:

```bash
databricks cluster-policies list
databricks cluster-policies create --json '{
  "name": "basic-policy",
  "definition": "{\"node_type_id\": {\"type\": \"fixed\", \"value\": \"i3.xlarge\"}}"
}'
```

## Auth Profiles (`~/.databrickscfg`)

```ini
[DEFAULT]
host       = https://production.cloud.databricks.com
client_id  = <service-principal-id>
client_secret = <oauth-secret>

[DEV]
host       = https://dev.cloud.databricks.com
token      = dapi...

[STAGING]
host       = https://staging.cloud.databricks.com
azure_tenant_id        = <tenant-id>
azure_client_id        = <client-id>
azure_client_secret    = <client-secret>
```

**Priority order:** SDK config fields > environment variables > config profile.

**Notes:**
- Add `.databrickscfg` to `.gitignore`
- Set restrictive file permissions
- Use service principals for production, not PATs
- Use descriptive profile names

## Authentication Methods

### OAuth M2M (Service Principal) — Recommended for Automation
```python
w = WorkspaceClient(
    host='https://workspace.cloud.databricks.com',
    client_id='your-client-id',
    client_secret='your-client-secret'
)
# Tokens auto-generated, refreshed hourly
```

### OAuth U2M (User) — Interactive Development
```bash
databricks auth login --host https://workspace.cloud.databricks.com
```
Stores cached token at `.databricks/token-cache.json`.

### With Workload Identity Federation (GitHub Actions)
```yaml
env:
  DATABRICKS_AUTH_TYPE: github-oidc
  DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
  DATABRICKS_CLIENT_ID: ${{ secrets.DATABRICKS_CLIENT_ID }}
```

## Global Init Scripts

Run on every cluster start:

```bash
databricks global-init-scripts list
databricks global-init-scripts create --name install-tools \
  --script "$(base64 -i init.sh)"
databricks global-init-scripts update <id> --name new-name
databricks global-init-scripts delete <id>
```

## Instance Profiles (AWS)

Grant clusters access to AWS resources:

```bash
databricks instance-profiles list
databricks instance-profiles add <instance-profile-arn>
databricks instance-profiles remove <instance-profile-arn>
```

## Instance Pools

Pre-warmed instances for faster cluster startup:

```bash
databricks instance-pools list
databricks instance-pools create --json '{
  "instance_pool_name": "my-pool",
  "node_type_id": "i3.xlarge",
  "min_idle_instances": 2,
  "max_capacity": 10
}'
```

## Library Management

```bash
# Install
databricks libraries install <cluster-id> --json '{"pypi": {"package": "pandas"}}'
databricks libraries install <cluster-id> --json '{"maven": {"coordinates": "org.apache:lib:1.0.0"}}'

# Check status
databricks libraries cluster-status <cluster-id>
databricks libraries all-cluster-statuses

# Uninstall
databricks libraries uninstall <cluster-id> --json '{"pypi": {"package": "pandas"}}'
```

## Workspace Environments (Serverless)

Manage base environments for serverless notebooks/jobs:

```bash
databricks environments list-workspace-base-environments
databricks environments create-workspace-base-environment --json '{
  "environment_name": "my-env",
  "dependencies": ["pandas", "numpy"],
  "environment_version": "5"
}'
```

## Identity & Access Management (IAM)

### Users

```bash
databricks users list
databricks users get <user-id>
databricks users create --user-name "user@example.com"
databricks users delete <user-id>
databricks users patch <user-id> --json @patch.json    # partial update
databricks users update <user-id> --json @user.json    # full replace
```

### Groups

```bash
databricks groups list
databricks groups get <group-id>
databricks groups create --display-name "data-engineers"
databricks groups delete <group-id>
databricks groups patch <group-id> --json @patch.json
databricks groups update <group-id> --json @group.json
```

### Service Principals

```bash
databricks service-principals list
databricks service-principals get <sp-id>
databricks service-principals create --display-name "prod-bot"
databricks service-principals delete <sp-id>
databricks service-principals patch <sp-id> --json @patch.json
databricks service-principals update <sp-id> --json @sp.json
```

### Permissions (Generic Object-Level)

```bash
# Works for any securable: clusters, jobs, pipelines, serving endpoints, etc.
databricks permissions get /jobs/<job-id>/permissions
databricks permissions get-permission-levels /clusters/<cluster-id>/permissions
databricks permissions set /jobs/<job-id>/permissions \
  --json '{"access_control_list": [{"user_name": "user@example.com", "permission_level": "CAN_MANAGE"}]}'
databricks permissions update /clusters/<cluster-id>/permissions --json @patch.json
```

## Tags (Governed Tag Policies)

Tag policies enforce governed tags on Databricks resources.

```bash
# Tag policy management (account-level)
databricks tag-policies create-tag-policy --json @policy.json
databricks tag-policies get-tag-policy <policy-id>
databricks tag-policies list-tag-policies
databricks tag-policies update-tag-policy <policy-id> --json @policy.json
databricks tag-policies delete-tag-policy <policy-id>

# Tag assignments on workspace-scoped objects
databricks workspace-entity-tag-assignments create-tag-assignment \
  --entity-id <id> --entity-type <type> --key "env" --value "prod"
databricks workspace-entity-tag-assignments get-tag-assignment <assignment-id>
databricks workspace-entity-tag-assignments list-tag-assignments
databricks workspace-entity-tag-assignments update-tag-assignment <assignment-id> --value "staging"
databricks workspace-entity-tag-assignments delete-tag-assignment <assignment-id>
```

## Postgres / Lakebase (OLTP Database CLI)

Lakebase provides Postgres-compatible OLTP databases. Commands use hierarchical resource names.

```bash
# Projects
databricks postgres create-project --json '{"display_name":"my-project","region":"aws-us-east-1"}'
databricks postgres get-project <project-id>
databricks postgres list-projects
databricks postgres update-project <project-id> --json @patch.json
databricks postgres delete-project <project-id>

# Branches (within a project)
databricks postgres create-branch --project-id <pid> --json '{"display_name":"dev"}'
databricks postgres get-branch --project-id <pid> --branch-id <bid>
databricks postgres list-branches --project-id <pid>
databricks postgres update-branch --project-id <pid> --branch-id <bid> --json @patch.json
databricks postgres delete-branch --project-id <pid> --branch-id <bid>

# Compute endpoints
databricks postgres create-endpoint --project-id <pid> --branch-id <bid> --json @ep.json
databricks postgres get-endpoint --project-id <pid> --branch-id <bid> --endpoint-id <eid>
databricks postgres list-endpoints --project-id <pid> --branch-id <bid>
databricks postgres update-endpoint --project-id <pid> --branch-id <bid> --endpoint-id <eid>
databricks postgres delete-endpoint --project-id <pid> --branch-id <bid> --endpoint-id <eid>

# Roles
databricks postgres create-role --project-id <pid> --branch-id <bid> --json '{"name":"readonly"}'
databricks postgres get-role --project-id <pid> --branch-id <bid> --role-name <role>
databricks postgres list-roles --project-id <pid> --branch-id <bid>
databricks postgres delete-role --project-id <pid> --branch-id <bid> --role-name <role>

# Synced tables (UC ↔ Postgres)
databricks postgres create-synced-table --project-id <pid> --branch-id <bid> --json @table.json
databricks postgres get-synced-table --project-id <pid> --branch-id <bid> --name <table>
databricks postgres update-synced-table --project-id <pid> --branch-id <bid> --name <table> --json @patch.json
databricks postgres delete-synced-table --project-id <pid> --branch-id <bid> --name <table>

# OAuth credentials for database connection
databricks postgres generate-database-credential --project-id <pid> --branch-id <bid>
# Returns: client_id, client_secret, host, port, and connection strings

# Database catalog registration in UC
databricks postgres create-catalog --project-id <pid> --branch-id <bid> ...
databricks postgres delete-catalog --project-id <pid> --branch-id <bid> --name <name>

# For direct SQL: use 'databricks psql' or 'databricks database'
```

## Notification Destinations

```bash
databricks notification-destinations list
databricks notification-destinations create --json @dest.json
databricks notification-destinations get <dest-id>
databricks notification-destinations update <dest-id> --json @patch.json
databricks notification-destinations delete <dest-id>
```

## Tokens & API Access

```bash
# Personal access tokens
databricks tokens list
databricks tokens create --comment "my token" --lifetime-seconds 86400
databricks tokens delete <token-id>

# Admin-level token management
databricks token-management list
databricks token-management delete <token-id>
databricks token-management create-obo-token \
  --application-id <sp-id> --lifetime-seconds 3600
```

## Network & Security

```bash
# IP Access Lists
databricks ip-access-lists list
databricks ip-access-lists create --json '{
  "label": "office-vpn",
  "list_type": "ALLOW",
  "ip_addresses": ["203.0.113.0/24"]
}'

# Network connectivity configs (for external models)
databricks account network-connectivity list
databricks account private-access list
```

## Workspace Settings

```bash
databricks workspace-conf get-status enableResultsDownloading
databricks workspace-conf set-status enableResultsDownloading=false

# Updated API
databricks workspace-settings-v2 list-workspace-settings-metadata
databricks workspace-settings-v2 get-public-workspace-setting \
  --settings-type automatic-cluster-update
```

## Key Limits

| Resource | Limit |
|----------|-------|
| Serving endpoints per workspace | 1000 |
| PATs per user | 600 |
| Concurrent task runs per workspace | 2000 |
| Jobs per workspace | 12000 |
| Jobs created per hour | 10000 |
| Tasks per job | 1000 |
| Rate limits per endpoint | 20 |
| Group-specific rate limits | 5 |
| Libraries per cluster | Configurable via policy |
| Endpoint create/update ops | 50 per 5 minutes |

## Gotchas

1. **PAT auto-revoke**: inactive 90 days → deleted. Use OAuth M2M for long-running automation.
2. **PAT scope**: workspace-scoped only. No account-level API access.
3. **Notebook auth**: SDK auto-auth works in notebooks but not on executors or for `AccountClient`.
4. **Cluster policies**: override user settings silently — unexpected configurations if not carefully designed.
5. **Init scripts**: stored in workspace files, max 64 KB. Use global init scripts for org-wide tools.
6. **Environment versions**: serverless environments use versioned specs; pin dependencies explicitly.
7. **Instance profiles**: require workspace admin to add. Region-specific.
8. **Network configs**: NCC for external models (including PrivateLink) is in Public Preview.
9. **Postgres/Lakebase** CLI commands require **CLI v0.294.0+** and the hierarchical path API (`projects/<pid>/branches/<bid>/endpoints/<eid>`).
10. **Groups must be account-level** (not workspace-local) for Unity Catalog GRANT management.
11. **Tag policies** are enforced at the account level; workspace-level overrides are not supported.
12. **Permission changes** via the generic `permissions` endpoint may be overridden by bundle deployments — manage permissions through bundles or the API, not both.
