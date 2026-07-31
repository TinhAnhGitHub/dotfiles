# Evaluation Dataset Management

## Contents

1. Dataset role and schema
2. Backend and environment requirements
3. Create, retrieve, search, tag, and delete
4. Merge records from dictionaries, DataFrames, and traces
5. Uniqueness, updates, lineage, and versioning
6. Curating production traces
7. Dataset design patterns
8. Automation and governance
9. Databricks differences

## 1. Dataset role and schema

An evaluation dataset is a living validation collection. It should encode the product's
quality contract and preserve provenance, not merely store convenient demo prompts.

Core record schema:

```python
record = {
    "inputs": {"question": "What is the refund window?"},
    "expectations": {
        "expected_facts": ["Refunds are available within 30 days"],
        "guidelines": ["Do not invent exceptions"],
    },
    "tags": {
        "intent": "refund_policy",
        "risk": "high",
        "source_stage": "production",
    },
    "source": {"trace": {"trace_id": "tr-..."}},
}
```

The core fields used directly by evaluation are:

| Field | Required | Purpose |
|---|---:|---|
| `inputs` | Yes | JSON-serializable keyword arguments for `predict_fn` |
| `expectations` | No | Human ground truth and row-specific criteria |
| `outputs` | No | Pre-generated candidate output for answer-sheet evaluation |
| `tags` | No | Slice, priority, source, risk, and governance labels |
| `source` | No | Human, document, trace, code, or unspecified lineage |

Managed datasets add record IDs, create/update timestamps and identities, inferred schema,
profile statistics, and a content digest.

### Reserved expectation keys

| Key | Consumer | Meaning |
|---|---|---|
| `expected_facts` | `Correctness` | Facts the response should support |
| `expected_response` | `Correctness`, `Equivalence` patterns | Reference response |
| `guidelines` | `ExpectationsGuidelines` | Per-record natural-language rules |
| `expected_retrieved_context` | document-recall patterns | Documents/chunks that should be retrieved |

Custom scorers may define additional keys. Document each key and its expected type.

## 2. Backend and environment requirements

OSS MLflow evaluation datasets require an MLflow Tracking Server with a SQL backend such
as PostgreSQL, MySQL, SQLite, or MSSQL. FileStore is unsupported.

Before creating a dataset:

```python
import mlflow

print(mlflow.__version__)
print(mlflow.get_tracking_uri())
```

For Databricks, confirm the workspace, catalog/schema privileges, package requirements,
and the currently documented dataset limits. Databricks docs have documented limits such
as 2,000 records and 20 expectations per record; do not apply those limits to OSS unless
the target backend documents them.

## 3. CRUD and discovery

### Create

```python
import mlflow
from mlflow.genai.datasets import create_dataset

experiment = mlflow.set_experiment("support-agent-eval")

dataset = create_dataset(
    name="support-agent-regression",
    experiment_id=experiment.experiment_id,
    tags={
        "owner": "support-ai",
        "stage": "validation",
        "semantic_version": "1.0.0",
    },
)
print(dataset.dataset_id)
```

The current API accepts a single experiment ID or a list for multi-experiment linkage.
Inspect the installed signature if supporting older MLflow minors.

### Get

```python
from mlflow.genai.datasets import get_dataset

by_id = get_dataset(dataset_id="d-...")
by_name = get_dataset(name="support-agent-regression")
```

### Search

```python
from mlflow.genai.datasets import search_datasets

datasets = search_datasets(
    experiment_ids=[experiment.experiment_id],
    filter_string="tags.stage = 'validation' AND name LIKE '%support%'",
    order_by=["last_update_time DESC"],
    max_results=20,
)
```

Search supports field/tag comparisons and `AND`; `OR` is not currently supported in the
documented dataset filter grammar.

### Manage tags

```python
from mlflow.genai.datasets import delete_dataset_tag, set_dataset_tags

set_dataset_tags(
    dataset_id=dataset.dataset_id,
    tags={"status": "approved", "semantic_version": "1.1.0"},
)
delete_dataset_tag(dataset_id=dataset.dataset_id, key="deprecated")
```

### Delete records or dataset

```python
record_ids = dataset.to_df()["dataset_record_id"].tolist()
deleted_count = dataset.delete_records(record_ids[:2])

from mlflow.genai.datasets import delete_dataset
delete_dataset(dataset_id=dataset.dataset_id)  # permanent
```

Treat dataset deletion as destructive; export or snapshot metadata first when governance
requires recoverability.

## 4. Merge records

`merge_records` is the primary upsert API.

### Dictionaries

```python
dataset.merge_records(
    [
        {
            "inputs": {"question": "How do I reset my password?"},
            "expectations": {
                "expected_facts": [
                    "Use the Forgot Password flow",
                    "A reset link is sent by email",
                ],
                "guidelines": ["Never ask for the current password"],
            },
            "tags": {"priority": "critical", "intent": "password_reset"},
        }
    ]
)
```

### Pandas DataFrame

```python
import pandas as pd

df = pd.DataFrame(
    [
        {
            "inputs": {"question": "When are you open?"},
            "expectations": {"expected_facts": ["Monday through Friday"]},
            "tags": {"intent": "business_hours"},
        }
    ]
)
dataset.merge_records(df)
```

### Traces

```python
traces = mlflow.search_traces(
    locations=[experiment.experiment_id],
    filter_string="tag.environment = 'production'",
    max_results=100,
    return_type="list",
)
dataset.merge_records(traces)
```

When a trace has assessments, its expectations can become dataset ground truth. Review
and normalize them before merging at scale.

## 5. Uniqueness, updates, lineage, and versioning

### Input-hash identity

Managed dataset records are matched by a hash of the entire `inputs` dictionary. Merging
the same inputs updates/merges expectations and tags rather than adding a duplicate.

Consequences:

- A temperature, locale, user tier, or context value inside `inputs` changes identity.
- Operational fields that should not define the case belong in `tags`, not `inputs`.
- Adding a new expectation to the same input is an upsert.
- Semantically equivalent but textually different inputs remain separate records unless
  curation deduplicates them.

### Source lineage

Current docs describe source types for trace, human, code, document, and unspecified
records. Source inference occurs during `merge_records`; an explicit source can override
inference.

Preserve:

- trace ID or document URI;
- annotator/reviewer identity;
- annotation guideline version;
- app/prompt/model version that produced the failure;
- curation timestamp and decision;
- issue or incident ID.

### Versioning strategy

Evaluation datasets evolve in place, so a dataset tag alone is not an immutable snapshot.
Use one of these patterns:

1. **Named snapshots:** create `support-eval-v1`, `support-eval-v2`; never mutate released
   snapshots.
2. **Release tags plus export:** tag a dataset revision and export its rows/digest to
   version-controlled or governed storage.
3. **Champion + candidate:** maintain an immutable release dataset and a mutable incoming
   curation dataset; promote reviewed records periodically.

Record the dataset ID, digest, and record count on every evaluation run.

### Export, import, and portability

Export a release snapshot rather than relying on a mutable name/tag alone:

```python
snapshot = dataset.to_df()
snapshot.to_json("support-eval-v1.jsonl", orient="records", lines=True)
snapshot.to_parquet("support-eval-v1.parquet", index=False)
```

Import through `merge_records` so MLflow applies input-hash identity and source inference:

```python
import pandas as pd
from mlflow.genai.datasets import create_dataset

portable = pd.read_parquet("support-eval-v1.parquet")
target = create_dataset(
    name="support-eval-v1",
    experiment_id=target_experiment_id,
)
target.merge_records(portable)
```

For cross-workspace transfer, preserve nested JSON types, source trace identifiers,
dataset digest, schema/profile, reviewer policy version, and an export manifest. A source
trace ID may not resolve in the target workspace, so retain it as lineage rather than
assuming the trace was migrated.

## 6. Curating production traces

### Candidate selection

Select more than errors:

- negative/low user feedback;
- judge failures or low scores;
- exceptions and timeouts;
- high latency/token/cost outliers;
- rare intents and user cohorts;
- newly introduced tools, models, or prompt versions;
- random baseline sample to avoid feedback-only bias;
- high-value successes for positive examples.

```python
negative = mlflow.search_traces(
    locations=[experiment.experiment_id],
    filter_string="feedback.user_satisfaction = 'false'",
    return_type="list",
)
errors = mlflow.search_traces(
    locations=[experiment.experiment_id],
    filter_string="trace.status = 'ERROR'",
    return_type="list",
)
```

Filter fields depend on MLflow version and storage backend. Verify grammar against the
target runtime before automating.

### Curation steps

1. Redact or exclude sensitive data before reviewer access or dataset merge.
2. Group by session for multi-turn cases.
3. Deduplicate exact inputs and near-duplicate semantic cases.
4. Assign issue category, priority, risk, and slice tags.
5. Have domain experts add measurable expectations.
6. Resolve reviewer disagreement; preserve raw feedback separately.
7. Merge only approved cases into the release dataset.
8. Add a focused regression test for critical incidents.

Do not use the original bad output as the expected response. Expectations describe the
desired behavior, while the source trace preserves what actually happened.

## 7. Dataset design patterns

### Stratified benchmark

Maintain target counts by intent, language, risk, user segment, tool, and difficulty.
Evaluate aggregate and per-slice metrics. Aggregate improvement can hide a critical slice
regression.

### Failure-mode suite

Each validated issue category gets at least:

- one canonical failure case;
- one close negative that should not trigger the same judgment;
- one edge/boundary case;
- expected behavior and rationale;
- stable deterministic checks where possible.

### RAG suite

Include expected retrieved documents/chunks, answer facts, and abstention behavior.
Evaluate retrieval relevance, sufficiency, groundedness, and final answer separately.

### Tool/agent suite

Store expected tool names/arguments/trajectory only when exact behavior is truly required.
Otherwise score outcome and constraints without overfitting to one valid trajectory.

### Multi-turn suite

Preserve session order, persona/goal, stateful facts, and final resolution criteria. Full
conversation simulation requires newer/experimental APIs; version-gate it.

## 8. Automation and governance

Automate ingestion and reports, not ground-truth authority:

```text
scheduled trace query
  → privacy filter
  → candidate ranking and deduplication
  → human review queue
  → approved expectations
  → merge into candidate dataset
  → evaluation on champion and candidate app
  → promotion decision
```

Controls:

- least-privilege dataset access;
- PII classification and retention;
- reviewer attribution;
- audit log for changed/deleted expectations;
- immutable release snapshots;
- no prompt optimizer training on the held-out release test set.

## 9. Databricks differences

Databricks can store evaluation datasets as governed Unity Catalog objects and integrate
them with labeling sessions and production traces. Before implementation, verify:

- `CREATE TABLE`, `USE CATALOG`, and `USE SCHEMA` privileges;
- supported catalog encryption and regional limitations;
- Databricks-specific row/expectation limits;
- required `databricks-agents` package version;
- whether the target workflow uses Review App/labeling session synchronization.

Load `databricks`, `databricks-core`, and `databricks-platform` for workspace operations.

## Sources

- https://mlflow.org/docs/latest/genai/datasets/
- https://mlflow.org/docs/latest/genai/datasets/sdk-guide/
- https://mlflow.org/docs/latest/genai/datasets/end-to-end-workflow/
- https://mlflow.org/docs/latest/genai/concepts/evaluation-datasets/
- https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/build-eval-dataset
