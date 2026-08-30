# Unity Catalog

## Three-Level Namespace

All governed data is addressed as `catalog.schema.object`:

```
<catalog>.<schema>.<table|view|volume|function|model>
```

- **Catalog**: Top-level organization (by team, env, domain)
- **Schema**: Groups related objects within a catalog
- **Object**: The asset itself

Naming rules: max 255 chars, no periods/spaces/slashes/control chars, stored as lowercase.

**CLI requirement**: All Unity Catalog CLI commands require CLI v0.218+.

## Catalog Management

```sql
-- Create
CREATE CATALOG IF NOT EXISTS my_catalog
  MANAGED LOCATION 's3://my-bucket/path'
  COMMENT 'My catalog';

-- Alter
ALTER CATALOG my_catalog RENAME TO new_catalog;
ALTER CATALOG my_catalog SET OWNER TO `group@domain.com`;

-- Drop
DROP CATALOG IF EXISTS my_catalog CASCADE;

-- List
SHOW CATALOGS;
```

```bash
databricks catalogs list
databricks catalogs get my-catalog
databricks catalogs create --name my-catalog
databricks catalogs update my-catalog --json '{"name": "new-name"}'
databricks catalogs delete my-catalog
```

## Schema Management

```sql
CREATE SCHEMA IF NOT EXISTS my_catalog.my_schema
  COMMENT 'My schema';

ALTER SCHEMA my_catalog.my_schema RENAME TO new_schema;

DROP SCHEMA IF EXISTS my_catalog.my_schema CASCADE;

SHOW SCHEMAS IN my_catalog;
```

```bash
databricks schemas list --catalog-name my-catalog
databricks schemas create --catalog-name my-catalog --name my-schema
databricks schemas get my-catalog.my-schema
databricks schemas delete my-catalog.my-schema
```

## Tables

### Managed Tables
- Storage lifecycle managed by UC
- Always Delta Lake or Apache Iceberg format
- Storage location: schema > catalog > metastore hierarchy

### External Tables
- Data lifecycle managed externally (cloud tools)
- UC governs access from Databricks only
- Formats: Delta, CSV, JSON, Avro, Parquet, ORC, Text
- Must reference path in a valid external location

```sql
-- Managed
CREATE TABLE my_catalog.my_schema.my_table (
  id INT,
  name STRING,
  value DECIMAL(10,2)
) USING DELTA;

-- External
CREATE TABLE my_catalog.my_schema.external_table
  LOCATION 's3://my-bucket/external/path';

-- CTAS
CREATE TABLE my_catalog.my_schema.new_table
  AS SELECT * FROM my_catalog.my_schema.source_table;

-- Clone (Delta only)
CREATE TABLE my_catalog.my_schema.clone DEEP CLONE my_catalog.my_schema.source;
```

```bash
databricks tables list --catalog-name my-catalog --schema-name my-schema
databricks tables get my-catalog.my-schema.my-table
databricks tables delete my-catalog.my-schema.my-table
```

## Volumes

Govern non-tabular data (files) in cloud storage.

### Managed vs External
- **Managed**: UC manages storage and deletion (7-day retention on delete)
- **External**: Registered against existing cloud path; data persists when volume dropped

```sql
-- Managed
CREATE VOLUME my_catalog.my_schema.my_volume
  COMMENT 'My volume';

-- External
CREATE EXTERNAL VOLUME my_catalog.my_schema.external_volume
  LOCATION 's3://my-bucket/path';

-- List
SHOW VOLUMES IN my_catalog.my_schema;
```

```bash
databricks volumes list --catalog-name my-catalog --schema-name my-schema
databricks volumes create --catalog-name my-catalog --schema-name my-schema --name my-volume
```

### File Access

```
/Volumes/catalog/schema/volume/path/to/file
dbfs:/Volumes/catalog/schema/volume/path/to/file  # Spark alternative
```

```python
# Workspace (dbutils)
dbutils.fs.ls("/Volumes/cat/sch/vol/")
dbutils.fs.head("/Volumes/cat/sch/vol/file.csv")
dbutils.fs.cp("/Volumes/...", "/Volumes/...")

# SDK
w.files.upload_from("/Volumes/cat/sch/vol/file.csv", "./local.csv", overwrite=True)
w.files.download_to("/Volumes/cat/sch/vol/file.csv", "./local.csv")

# Spark
df = spark.read.csv("/Volumes/cat/sch/vol/file.csv")
df.write.save("/Volumes/cat/sch/vol/output/")
```

## Connections (External Data Sources)

Connections bridge to external databases (Postgres, MySQL, Snowflake, SQL Server, etc.).

```bash
databricks connections create --json '{
  "name": "my-postgres-conn",
  "connection_type": "POSTGRESQL",
  "connection_url": "jdbc:postgresql://host:5432/mydb",
  "read_only": false,
  "properties": {
    "user": "myuser",
    "password": "{{secrets/my-scope/pwd}}"
  }
}'
databricks connections list
databricks connections get <connection-id>
databricks connections update <connection-id> --json @patch.json
databricks connections delete <connection-id>
```

## Service Credentials

Credentials for authenticating to external cloud services. Different from storage credentials — these are for non-storage services (external model endpoints, etc.).

```bash
databricks credentials create-credential --json @cred.json
databricks credentials get-credential <cred-id>
databricks credentials list-credentials
databricks credentials update-credential <cred-id> --json @patch.json
databricks credentials delete-credential <cred-id>
databricks credentials validate-credential <cred-id>
databricks credentials generate-temporary-service-credential <cred-id>
```

## Functions (UDFs)

User-Defined Functions in Unity Catalog — SQL expressions or queries callable in SQL.

```bash
databricks functions create --json '{
  "catalog_name": "main",
  "schema_name": "default",
  "name": "add_one",
  "input_params": [{"name": "x", "type_text": "INT"}],
  "data_type": "INT",
  "routine_body": "SQL",
  "routine_definition": "SELECT x + 1"
}'
databricks functions list --catalog-name main --schema-name default
databricks functions get main.default.add_one
databricks functions delete main.default.add_one
databricks functions update main.default.add_one --json @patch.json
```

## Registered Models & Model Versions (UC MLflow)

UC models replace the legacy workspace model registry.

```bash
# Registered models
databricks registered-models create \
  --catalog-name prod --schema-name ml --name "iris-classifier"
databricks registered-models list --catalog-name prod --schema-name ml
databricks registered-models get prod.ml.iris-classifier
databricks registered-models set-alias --full-name prod.ml.iris-classifier \
  --alias "production" --version-id 2
databricks registered-models delete-alias --full-name prod.ml.iris-classifier \
  --alias staging
databricks registered-models delete prod.ml.iris-classifier

# Model versions (created by MLflow client, managed via CLI)
databricks model-versions list --catalog-name prod --schema-name ml
databricks model-versions get --full-name prod.ml.iris-classifier --version-id 2
databricks model-versions get-by-alias --full-name prod.ml.iris-classifier --alias "production"
databricks model-versions update --full-name prod.ml.iris-classifier --version-id 2 --json @patch.json
databricks model-versions delete --full-name prod.ml.iris-classifier --version-id 1
```

**Note**: The securable type for models is `FUNCTION`. Use `FUNCTION` when working with grants/tagging.

## Online Tables

Low-latency serving tables for real-time lookup from Delta tables.

```bash
databricks online-tables create --json '{
  "name": "main.default.my_online_table",
  "spec": {
    "run_triggered": {
      "run_trigger_mode": "RULES"
    },
    "source_table_full_name": "main.default.my_source_table",
    "primary_key": ["id"]
  }
}'
databricks online-tables get main.default.my_online_table
databricks online-tables delete main.default.my_online_table
```

## System Schemas

Built-in schemas in the `system` catalog for audit, billing, and lineage data.

```bash
databricks system-schemas list  # shows enabled/available schemas
databricks system-schemas enable billing  # enable billing system schema
databricks system-schemas disable billing
# Access system schemas via SQL: SELECT * FROM system.billing.usage
```

## Artifact Allowlists

Allow specific libraries and init scripts on shared-access mode compute.

```bash
databricks artifact-allowlists list --artifact-type LIBRARY
databricks artifact-allowlists ...  # CRUD for allowlist entries
```

## Quality Monitors

Data quality monitoring on UC objects (tables, schemas).

```bash
# Original API
databricks quality-monitors create \
  --table-name main.default.my_table --json '{
    "inference_log": {"granularities": ["DAY"]},
    "time_series": {"timestamp_col": "event_time", "granularities": ["DAY"]}
  }'
databricks quality-monitors get main.default.my_table
databricks quality-monitors delete main.default.my_table

# Updated v2 API
databricks quality-monitor-v2 create --json @monitor.json

# Data quality monitoring unified API
databricks data-quality ...
```

## External Lineage

Define and manage lineage relationships between Databricks objects and external systems.

```bash
databricks external-lineage ...
```

## Resource Quotas

Unity Catalog enforces resource quotas on all securable objects.

```bash
databricks resource-quotas list --parent-securable catalog --parent-full-name main
```

## Temporary Credentials

Short-lived, downscoped credentials for accessing external cloud storage.

```bash
databricks temporary-path-credentials list
databricks temporary-table-credentials list
```

## Table Constraints

Primary and foreign key constraints on Delta tables.

```bash
databricks table-constraints create --json '{
  "catalog_name": "main",
  "schema_name": "default",
  "table_name": "orders",
  "constraint": {
    "foreign_key_constraint": {
      "name": "fk_customer",
      "child_columns": ["customer_id"],
      "parent_table": "main.default.customers",
      "parent_columns": ["customer_id"]
    }
  }
}'
databricks table-constraints delete --full-name "main.default.orders.fk_customer"
```

## Delta Sharing

```bash
databricks shares list
databricks shares create --name "my-share"
databricks providers list
databricks recipients list
databricks recipient-activation ...
databricks recipient-federation-policies ...
```

## Permissions (GRANTS)

### Privilege Types

| Object | Key Privileges |
|--------|---------------|
| **Metastore** | `CREATE CATALOG`, `CREATE STORAGE CREDENTIAL`, `CREATE EXTERNAL LOCATION` |
| **Catalog** | `USE CATALOG`, `CREATE SCHEMA`, `CREATE TABLE`, `SELECT`, `MODIFY`, `BROWSE` |
| **Schema** | `USE SCHEMA`, `CREATE TABLE`, `CREATE VOLUME`, `SELECT`, `MODIFY` |
| **Table** | `SELECT`, `MODIFY`, `ALL PRIVILEGES` |
| **View** | `SELECT`, `MANAGE` |
| **Volume** | `READ VOLUME`, `WRITE VOLUME`, `MANAGE` |
| **Function/Model** | `EXECUTE`, `CREATE MODEL VERSION` |
| **External Location** | `CREATE TABLE`, `READ FILES`, `WRITE FILES` |
| **Storage Credential** | `CREATE EXTERNAL LOCATION`, `READ FILES`, `WRITE FILES` |

### Inheritance
- Catalog → all child schemas, tables, views, volumes, functions
- Schema → all child objects
- Metastore → does NOT inherit to child objects

### Common Patterns

```sql
-- Give team read access to entire catalog
GRANT USE CATALOG ON CATALOG main TO `data-team`;
GRANT USE SCHEMA ON SCHEMA main.default TO `data-team`;
GRANT SELECT ON SCHEMA main.default TO `data-team`;

-- Give table creation rights
GRANT CREATE TABLE ON SCHEMA main.default TO `engineers`;

-- Give volume access
GRANT READ VOLUME, WRITE VOLUME ON VOLUME main.default.data_volume TO `analysts`;

-- Give model execution rights
GRANT EXECUTE ON FUNCTION prod.ml.iris_model TO `ml-team`;

-- Revoke
REVOKE SELECT ON SCHEMA main.default FROM `departed-team`;

-- Show grants
SHOW GRANTS ON CATALOG main;
SHOW GRANTS `user@example.com` ON TABLE main.default.sales;
```

```bash
# CLI
databricks grants update catalog main \
  --json '{"changes": [{"principal": "data-team", "add": ["USE CATALOG"]}]}'

databricks grants get --securable-type catalog --full-name main
databricks grants get-effective --securable-type table --full-name main.default.sales
```

**Critical: Groups for GRANTs must be account-level groups, NOT workspace-local groups.**

### Managing Ownership

```sql
ALTER CATALOG main SET OWNER TO `admin-group`;
ALTER SCHEMA main.default SET OWNER TO `team-owner`;
ALTER TABLE main.default.sales SET OWNER TO `table-owner`;
```

## Storage Credentials

Authentication for cloud storage (AWS IAM role, Azure SP, GCP SA):

```sql
CREATE STORAGE CREDENTIAL my_storage_cred
  WITH AWS_IAM_ROLE ARN 'arn:aws:iam::123456789012:role/my-role';
```

```bash
databricks storage-credentials list
databricks storage-credentials create --json '{"name": "...", "aws_iam_role": {"role_arn": "..."}}'
databricks storage-credentials delete my_storage_cred
```

## External Locations

Bridge cloud storage paths to storage credentials:

```sql
CREATE EXTERNAL LOCATION my_location
  URL 's3://my-bucket/prefix/'
  WITH (STORAGE CREDENTIAL my_storage_cred);
```

```bash
databricks external-locations create --name my-location \
  --url s3://my-bucket/path --storage-credential-name my-storage-cred

databricks external-locations validate --url s3://my-bucket/path \
  --cred-name my-storage-cred
```

## Metastores

Top-level UC container. One per region, shared across workspaces:

```bash
databricks metastores list
databricks metastores assign --workspace-id <ws-id> --metastore-id <ms-id> \
  --default-catalog-name main
databricks metastores get-summary
```

### Metastore Admin
Powerful role — can take ownership of any object. Assign to a GROUP, not an individual.

## Workspace Bindings (ISOLATED vs OPEN)

Control which workspaces can access a catalog:

```sql
-- Set to ISOLATED (restrict to specific workspaces)
ALTER CATALOG my_catalog SET ISOLATION_MODE ISOLATED;

-- Bind workspace to catalog
ALTER CATALOG my_catalog SET WORKSPACE_BINDING (workspace_id = '12345')
  WITH BINDING_TYPE READ_WRITE;  -- or READ_ONLY
```

```bash
databricks catalogs update my-catalog --isolation-mode ISOLATED
databricks workspace-bindings update-bindings catalog my-catalog \
  --json '{"add": [{"workspace_id": 123, "binding_type": "BINDING_TYPE_READ_WRITE"}]}'
```

**Workspace bindings supersede privilege grants**: even users with explicit GRANTs cannot access an unbound catalog.

## Gotchas

1. **Account-level groups required** for GRANTS — workspace-local groups won't work.
2. **Managed storage hierarchy**: schema location > catalog location > metastore location. Set at catalog level for best isolation.
3. **Volumes require DBR 13.3 LTS+**. `/Volumes` is a reserved path; can't list at catalog level.
4. **CORS must be enabled** on S3 buckets for managed volume uploads.
5. **Compute must use standard or dedicated access mode** to access UC data.
6. **Shallow clone**: managed-to-managed or external-to-external only (no cross-type cloning).
7. **DBFS root is legacy** — Databricks recommends UC volumes for all file operations.
8. **Storage credentials** can be workspace-bound, not just catalogs.
9. **Metastore admin** can take ownership of any object — use sparingly, assign to groups.
10. **Resource quotas**: enforced on all securable objects. Contact Databricks if nearing limits.
