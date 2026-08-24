# Databricks Integration for MLflow Evaluation and Monitoring

## Contents

1. Environment setup and cross-skill routing
2. Databricks evaluation architecture
3. Evaluation datasets
4. Endpoint and agent evaluation
5. Human feedback and Review App
6. Production monitoring
7. Permissions and infrastructure
8. Automation with Jobs and bundles
9. Managed vs OSS decision matrix

## 1. Environment setup and cross-skill routing

For any Databricks implementation, load:

1. `mlflow` and `evaluation-monitoring` for quality workflow;
2. `databricks` and `databricks-core` for authentication, profiles, and workspace basics;
3. additional skill by operation:

| Operation | Companion skill |
|---|---|
| Unity Catalog trace storage, permissions, SQL | `databricks-platform` |
| Model Serving endpoint or ResponsesAgent | `databricks-model-serving` |
| Scheduled offline evaluation/backfill | `databricks-jobs` |
| Bundle-managed jobs/apps/resources | `databricks-dabs` |
| App that collects feedback | `databricks-apps` |
| pytest and Databricks test fixtures | `pytest-databricks` |

Baseline notebook setup:

```python
%pip install --upgrade "mlflow[databricks]"
dbutils.library.restartPython()
```

```python
import mlflow

mlflow.set_tracking_uri("databricks")
experiment = mlflow.set_experiment("/Shared/support-agent-evaluation")
```

Use unified authentication outside notebooks. Prefer OAuth for automation; do not place
PATs in code or bundle YAML.

## 2. Databricks evaluation architecture

```text
App / Agent / Model Serving
  → MLflow traces in experiment or Unity Catalog
  → human feedback / Review App / labeling sessions
  → Unity Catalog evaluation dataset
  → mlflow.genai.evaluate on candidate
  → evaluation run and assessments
  → CI/release decision
  → managed production scorers (Beta)
  → backfill/archive/SQL dashboards
  → curated production failures back into dataset
```

The same scorer definition should be tested offline before managed scheduling.

## 3. Evaluation datasets

Databricks documents UC-backed evaluation datasets with lineage and governance.

```python
from mlflow.genai.datasets import create_dataset

dataset = create_dataset(name="main.agent_eval.support_regression")
dataset.merge_records(records_or_traces)
```

Exact naming and package requirements have evolved. Verify current workspace docs and
installed SDK. Current Databricks docs also describe explicit limits such as maximum rows
and expectations per record and restrictions for some encrypted catalogs.

Privileges typically include `USE CATALOG`, `USE SCHEMA`, and `CREATE TABLE` or object
permissions in the target schema.

Labeling-session synchronization can promote reviewed traces into an evaluation dataset.
Preserve reviewer identity, source trace, and guideline version.

## 4. Endpoint and agent evaluation

### Wrap a serving endpoint

```python
predict_fn = mlflow.genai.to_predict_fn("endpoints:/support-agent")

result = mlflow.genai.evaluate(
    data=dataset,
    predict_fn=predict_fn,
    scorers=scorers,
)
```

Before evaluation:

1. use `databricks-model-serving` to verify endpoint readiness and request schema;
2. confirm the caller has `CAN QUERY`;
3. test one request;
4. check that returned traces include required tool/retriever spans;
5. configure rate limits/concurrency.

### Agent Framework

When deploying a Databricks agent, set the intended experiment before deployment so
production traces go to the right quality location. Git-folder/notebook experiment
behavior can differ; current docs recommend an explicit non-Git experiment in affected
flows.

### Candidate comparison

Compare endpoint/model/prompt candidates using the same UC dataset and scorer versions.
Store endpoint name, served entity/model version, prompt version, and git SHA as run tags.

## 5. Human feedback and Review App

Databricks human-feedback workflows include:

- developer annotation on traces;
- interactive expert testing through Review App Chat UI;
- labeling sessions for systematic review;
- end-user feedback through trace assessment APIs.

Review App users need the documented account/workspace and endpoint query permissions.
Do not assume all reviewers should receive direct workspace or raw trace-table access.

SDK assessment pattern:

```python
from mlflow.entities import AssessmentSource

mlflow.log_feedback(
    trace_id=trace_id,
    name="response_quality",
    value="good",
    rationale="Accurate and actionable",
    source=AssessmentSource(source_type="HUMAN", source_id=reviewer_id),
)
```

Databricks also documents a REST assessment endpoint under the MLflow traces API. Prefer
the SDK unless a separate service requires REST; verify API version and auth from the
current workspace docs.

## 6. Production monitoring

Databricks production quality monitoring is Beta. Workspace admins can control preview
access.

Supported categories include:

- built-in judges;
- Guidelines;
- custom `make_judge` judges;
- self-contained `@scorer` code functions registered from notebooks;
- multi-turn judges on session-tagged traces.

Unsupported: class-based custom scorers for managed execution.

```python
from mlflow.genai.scorers import Safety, ScorerSamplingConfig

safety = Safety().register(name="safety")
safety = safety.start(
    sampling_config=ScorerSamplingConfig(
        sample_rate=1.0,
        filter_string="attributes.status = 'OK'",
    )
)
```

Databricks monitoring pages currently show `attributes.status` in examples, while current
general trace-search docs use `trace.status`. Treat filter syntax as service/version
specific: copy from the target service's current page and test it before enabling future
traces.

Managed operations include lifecycle management, historical scorer backfill, and trace
archival to Delta. These are Beta and package signatures can change.

## 7. Permissions and infrastructure

Checklist:

- Workspace/experiment: permission to read traces and edit/register monitoring.
- Judge model/endpoint: query permission.
- Evaluation dataset schema: `USE CATALOG`, `USE SCHEMA`, `CREATE TABLE` and object grants.
- UC traces: SQL warehouse `CAN USE`, explicit `SELECT` and `MODIFY` on OTel tables.
- Production monitoring: serverless budget policy if default creation is disabled.
- Review App: reviewer and endpoint permissions.
- Jobs: service principal permissions on experiment, dataset, endpoints, secrets, and
  warehouse.

For UC traces, set the currently documented warehouse configuration, such as:

```python
import os
os.environ["MLFLOW_TRACING_SQL_WAREHOUSE_ID"] = "<warehouse-id>"
```

Some managed monitoring APIs provide a helper to set the monitoring warehouse. Verify the
current import rather than mixing helper versions.

## 8. Automation with Jobs and bundles

### Scheduled offline evaluation job

Task flow:

```text
load immutable dataset
  → resolve candidate endpoint/prompt/model parameters
  → run mlflow.genai.evaluate
  → calculate release policy
  → persist run ID and status
  → notify/stop promotion on failure
```

Use `databricks-jobs` for job/task/parameter design and `databricks-dabs` for deployment.
Keep judge/provider keys in Databricks secrets or approved endpoint resources.

### Backfill job

Backfill after introducing or materially changing a scorer to establish a historical
baseline. Do not compare old and new scorer values as one uninterrupted metric without
marking the version boundary.

### CI

Local/CI pytest can point `MLFLOW_TRACKING_URI` at Databricks with workload identity. Use
short critical tests on PRs and a Databricks Job for larger evaluations requiring private
data or high-volume endpoint access.

### Bundle resources

Bundle:

- scheduled evaluation job;
- environment-specific parameters;
- optional app that collects feedback;
- UC object grants where supported;
- monitoring setup notebook/job when direct resource support is unavailable.

Never assume Beta scorer schedules are fully represented as stable bundle resources;
validate against current DAB schema.

## 9. Managed vs OSS matrix

| Capability | OSS MLflow | Databricks managed |
|---|---|---|
| `mlflow.genai.evaluate` | Yes | Yes |
| SQL-backed EvaluationDataset | Yes | UC integration and managed UI |
| Human trace assessments | Yes | Yes + Review App/labeling workflows |
| Automatic evaluation with LLM judges | Yes, MLflow Server + AI Gateway | Yes, managed Beta monitoring service |
| Code scorer online execution | No | Supported `@scorer` functions with constraints |
| UC OTel trace storage | No | Yes, current docs require MLflow 3.14+ |
| Safety/RetrievalRelevance judges | Current OSS docs mark unavailable | Available |
| Historical scorer backfill | Not in generic automatic-eval flow | Beta managed API |
| Trace archival to Delta | Generic archival differs | Beta managed API |
| Automatic issue detection | Upstream UI/MCP workflow | Check current workspace availability/docs |

## Sources

- https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/production-monitoring
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/manage-production-scorers
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/backfill-scorers
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/archive-traces
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/build-eval-dataset
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/
