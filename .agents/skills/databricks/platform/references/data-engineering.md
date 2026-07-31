# Data Engineering — Jobs & Pipelines

## Lakeflow Jobs

### Task Types

| Type | YAML/JSON Key | When to Use |
|------|--------------|-------------|
| Notebook | `notebook_task` | Interactive development, dbutils.widgets for params |
| Python Script | `python_script_task` | Simple `.py` files with CLI args |
| Python Wheel | `python_wheel_task` | Packaged code, entry points, structured params |
| SQL | `sql_task` | Run SQL against warehouse |
| Pipeline | `pipeline_task` | Trigger a DLT pipeline |
| JAR | `spark_jar_task` | Java/Scala workloads |
| Spark Submit | `spark_submit_task` | spark-submit style tasks |
| Run Job | `run_job_task` | Trigger another saved job |
| If/Else | (conditional) | Branching logic based on task values |
| For Each | `for_each_task` | Loop over JSON array inputs |
| dbt | `dbt_task` | dbt CLI commands |
| Dashboard | `dashboard_task` | Refresh AI/BI dashboard |

### Compute Options

```yaml
# Serverless (default, recommended)
tasks:
  - task_key: my_task
    python_wheel_task:
      package_name: my_package
      entry_point: main

# Classic job cluster (ephemeral, per-run)
tasks:
  - task_key: my_task
    new_cluster:
      spark_version: "15.4.x-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 2
    python_wheel_task: ...

# All-purpose cluster (persistent — not for production)
tasks:
  - task_key: my_task
    existing_cluster_id: "1234-567890-abcde123"
    notebook_task: ...

# SQL warehouse (for SQL/dbt/alert tasks)
tasks:
  - task_key: my_task
    sql_warehouse_id: "abcd12345678"
    sql_task: ...
```

### Performance Modes
- **Standard**: Lower cost, 4-6 minute startup
- **Performance Optimized**: Faster startup/execution, time-sensitive workloads

### Named Parameters (Python Wheel)

```
YAML named_parameters → sys.argv as --key=value → argparse in entrypoint
```

```yaml
# Job definition
tasks:
  - task_key: ingest
    python_wheel_task:
      package_name: my_package
      entry_point: run_ingestion
      named_parameters:
        catalog: my_catalog
        schema: my_schema
        volume_file_path: "/Volumes/..."
```

```python
# Entrypoint
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--volume_file_path", default="")
    args = parser.parse_args()  # Parses sys.argv
    ...
```

### Parameter Types by Task

| Task Type | Param Mechanism |
|-----------|----------------|
| Notebook | `dbutils.widgets.get("key")` |
| Python Wheel (keyword) | `--key=value` → `argparse` |
| Python Wheel (positional) | JSON array → CLI positional args |
| Python Script | CLI positional args |
| SQL | Named params: `:param_name` |
| JAR / Spark Submit | Main method args |

### Parameter Precedence
**Job-level params override task-level params** with the same key. Job-level params auto-push to key-value accepting tasks (notebook, Python wheel kwargs, SQL, Run Job).

### Dynamic Value References
```yaml
{{job.parameters.catalog}}       # Job parameter
{{tasks.extract.values.file_count}}  # Upstream task value (set via dbutils.jobs.taskValues)
{{job.id}}                       # Job ID
{{job.run_id}}                   # Current run ID
```

### Triggers

```yaml
# Scheduled (Quartz cron)
schedule:
  quartz_cron_expression: "0 0 9 * * ?"
  timezone_id: "America/Los_Angeles"

# File arrival
file_arrival:
  url: "/Volumes/cat/sch/vol/path"

# Continuous (always running)
continuous: {}

# Table update trigger (for DLT)
table:
  table_names: ["main.default.source_table"]
```

### Retry Policies

```yaml
tasks:
  - task_key: my_task
    max_retries: 3
    min_retry_interval_millis: 10000  # 10 seconds
    retry_on_timeout: true
    # Serverless auto-optimization retries are ON by default
```

**Continuous jobs**: exponential backoff at task (3 retries) and job level (no limit).

### Key Limits
- 2000 concurrent task runs per workspace
- 1000 tasks per job
- 12000 saved jobs per workspace
- 10000 jobs created per hour
- For each task: 5000 chars (UI), 48 KB (task values), 10 KB (job params)
- Dynamic values: 10000 chars total for job parameters

## Lakeflow Spark Declarative Pipelines (DLT)

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Pipeline** | Unit of development/execution: streaming tables, materialized views, sinks |
| **Flow** | Read→Process→Write. Types: Append, AUTO CDC, Materialized View |
| **Streaming table** | UC managed, processes each record exactly once (append-only) |
| **Materialized view** | UC managed, batch target, incremental processing |
| **Sink** | Streaming target for external systems (Kafka, EventHubs, custom Python) |
| **View** | Intermediate transformation, recalculated on every query (not published) |

### Modes
- **Triggered**: Run once, then stop
- **Continuous**: Always running, processes data as it arrives

### Product Editions

| Edition | Features |
|---------|----------|
| **Core** | Streaming ingest only |
| **Pro** | Streaming ingest + CDC |
| **Advanced** | All features including data quality expectations |

### Data Quality Expectations

```python
# Python
import dlt

@dlt.expect("valid_age", "age BETWEEN 0 AND 120")
@dlt.table
def users():
    ...

@dlt.expect_all_or_drop({"valid_name": "name IS NOT NULL"})
@dlt.expect_all_or_fail({"has_id": "id IS NOT NULL"})

# SQL
CREATE OR REFRESH STREAMING TABLE filtered_users AS
SELECT * FROM STREAM(LIVE.users)
CONSTRAINT valid_age EXPECT (age BETWEEN 0 AND 120) ON VIOLATION DROP ROW
CONSTRAINT has_id EXPECT (id IS NOT NULL) ON VIOLATION FAIL UPDATE
```

| Action | Python Decorator | SQL Syntax | Behavior |
|--------|-----------------|------------|----------|
| Warn | `@dlt.expect` / `@dlt.expect_all` | `EXPECT` | Invalid records kept, metrics tracked |
| Drop | `@dlt.expect_or_drop` / `@dlt.expect_all_or_drop` | `ON VIOLATION DROP ROW` | Invalid records dropped |
| Fail | `@dlt.expect_or_fail` / `@dlt.expect_all_or_fail` | `ON VIOLATION FAIL UPDATE` | Update fails atomically |

### Compute Options

```yaml
# Serverless (recommended)
resources:
  pipelines:
    my_pipeline:
      serverless: true
      channel: CURRENT

# Classic with enhanced autoscaling
    my_pipeline:
      clusters:
        - label: default
          autoscale:
            min_workers: 2
            max_workers: 10
          node_type_id: "i3.xlarge"
```

### CLI Commands: Jobs

```bash
# Manage
databricks jobs create --json @job.json
databricks jobs get <job-id>
databricks jobs list
databricks jobs delete <job-id>
databricks jobs reset <job-id> --json @job.json    # full replace
databricks jobs update <job-id> --json @patch.json  # partial update

# Run
databricks jobs run-now <job-id>
databricks jobs submit --json '{"tasks":[...],"run_name":"one-off"}'
databricks jobs cancel-run <run-id>
databricks jobs cancel-all-runs <job-id>
databricks jobs repair-run <run-id> --rerun-all-failed
databricks jobs delete-run <run-id>

# Monitor
databricks jobs get-run <run-id>
databricks jobs list-runs <job-id>
databricks jobs get-run-output <run-id>
databricks jobs export-run <run-id>
```

### CLI Commands: Pipelines

```bash
# Management (workspace API)
databricks pipelines create --json-file pipeline.json
databricks pipelines update <id> --json-file pipeline.json
databricks pipelines delete <id>
databricks pipelines clone <id>

# Run / stop
databricks pipelines start-update <id>        # Trigger update
databricks pipelines stop <id>                # Stop running

# Monitor
databricks pipelines get <id>                 # Status
databricks pipelines list-pipelines
databricks pipelines list-updates <id>        # Update history
databricks pipelines get-update <id> <update-id>
databricks pipelines list-pipeline-events <id>
databricks pipelines logs <id>

# Bundle-style subcommands (developer workflow)
databricks pipelines deploy
databricks pipelines run
databricks pipelines destroy
databricks pipelines dry-run                  # validate DAG correctness
databricks pipelines generate                 # generate config from existing
databricks pipelines init                     # scaffold a new project
databricks pipelines open                     # open pipeline in browser
databricks pipelines history                  # retrieve past runs
databricks pipelines apply-environment        # apply latest environment
```

### Job Policy Compliance (CLI v0.298+)

```bash
databricks policy-compliance-for-jobs get-compliance <job-id>
databricks policy-compliance-for-jobs list-compliance
databricks policy-compliance-for-jobs enforce-compliance <job-id>
```

## Compute — CLI Command Reference

### Clusters (All-Purpose & Job)

```bash
databricks clusters create --json @cluster.json
databricks clusters get <cluster-id>
databricks clusters edit <cluster-id> --json @cluster.json
databricks clusters update <cluster-id> --json @patch.json   # partial update
databricks clusters list
databricks clusters start <cluster-id>
databricks clusters restart <cluster-id>
databricks clusters resize <cluster-id> --num-workers 5
databricks clusters delete <cluster-id>                      # terminate
databricks clusters permanent-delete <cluster-id>
databricks clusters pin <cluster-id>
databricks clusters unpin <cluster-id>
databricks clusters change-owner <cluster-id> --user-email user@example.com
databricks clusters events <cluster-id>
databricks clusters list-node-types
databricks clusters list-zones
databricks clusters spark-versions
```

### Cluster Policies

```bash
databricks cluster-policies create --json @policy.json
databricks cluster-policies get <policy-id>
databricks cluster-policies edit <policy-id> --json @policy.json
databricks cluster-policies list
databricks cluster-policies delete <policy-id>
```

### Policy Families (Databricks-managed best-practice templates)

```bash
databricks policy-families list
databricks policy-families get <family-id>
```

### Policy Compliance for Clusters

```bash
databricks policy-compliance-for-clusters get-compliance <cluster-id>
databricks policy-compliance-for-clusters list-compliance
databricks policy-compliance-for-clusters enforce-compliance <cluster-id>
```

### Instance Pools

```bash
databricks instance-pools create --json @pool.json
databricks instance-pools get <pool-id>
databricks instance-pools edit <pool-id> --json @pool.json
databricks instance-pools list
databricks instance-pools delete <pool-id>
```

### Instance Profiles (AWS)

```bash
databricks instance-profiles add --instance-profile-arn "arn:aws:iam::..."
databricks instance-profiles list
databricks instance-profiles edit --instance-profile-arn "..."
databricks instance-profiles remove --instance-profile-arn "..."
```

### Libraries

```bash
databricks libraries install <cluster-id> --json '{"pypi":{"package":"pandas"}}'
databricks libraries uninstall <cluster-id> --json '{"pypi":{"package":"pandas"}}'
databricks libraries cluster-status <cluster-id>
databricks libraries all-cluster-statuses
```

### Global Init Scripts

```bash
# Run on every node of every cluster in the workspace.
databricks global-init-scripts create --name "my-script" --script "@init.sh"
databricks global-init-scripts get <script-id>
databricks global-init-scripts list
databricks global-init-scripts update <script-id> --script "@init.sh" --name "my-script"
databricks global-init-scripts delete <script-id>
# Scripts run in order; non-zero exit prevents Spark container launch.
# Restart clusters to pick up changes.
```

## Environments (Workspace Base Environments)

Base environments define the runtime versions and dependencies for serverless notebooks and jobs.

```bash
databricks environments create-workspace-base-environment --json @env.json
databricks environments get-workspace-base-environment <env-id>
databricks environments list-workspace-base-environments
databricks environments update-workspace-base-environment <env-id> --json @env.json
databricks environments refresh-workspace-base-environment <env-id>
databricks environments get-default-workspace-base-environment
databricks environments update-default-workspace-base-environment --env-id <env-id>
databricks environments delete-workspace-base-environment <env-id>
databricks environments get-operation <op-id>                    # long-running op status
```

## Gotchas

1. **Shared job clusters** persist driver JVM state across tasks. Parallel tasks sharing a cluster can corrupt singletons/companion objects. Use separate clusters or sequential deps for isolation.
2. **Libraries on shared clusters**: must be added at task level, not in cluster config.
3. **Continuous mode**: no task dependencies, no `Trigger.ProcessingTime`/`Trigger.Continuous` on serverless.
4. **Pipeline params**: pipeline tasks in jobs do NOT support parameter passing between job and pipeline.
5. **Serverless requirements**: Unity Catalog must be enabled, workloads must support standard access mode.
6. **`runs/submit`**: one-time unsaved runs cannot be auto-optimized for serverless.
7. **Job params vs task params**: same key = job param wins. Job params only auto-push to key-value tasks.
8. **For each task**: not all task types supported as nested tasks. Check docs for compatibility.
