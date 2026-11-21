---
name: version-tracking
description: >
  MLflow GenAI application and agent version tracking with LoggedModel, active-model
  contexts, Git-linked versions, trace lineage, configuration snapshots, and systematic
  version comparison. Use whenever users ask which app version produced a trace, how to
  version an agent or prompt-driven application, how to track Git/dirty state, compare
  application versions, or connect GenAI versions to evaluation and deployment. Load the
  parent `mlflow` skill first.
compatibility: MLflow 3.x; automatic Git model versioning is experimental and requires a compatible newer minor release
metadata:
  version: "0.2.0"
  docs-reviewed: "2026-11-21"
---

# MLflow GenAI Version Tracking

Treat an application version as an auditable snapshot of **code + prompts + configuration +
dependencies + traces + evaluation evidence**. A provider model name alone is not an app
version.

## Mandatory preflight

1. Load the parent `mlflow` skill and inspect `mlflow.__version__`.
2. Determine OSS MLflow versus Databricks managed MLflow and the tracking experiment.
3. Identify the source revision, prompt versions, provider model IDs, tool/retriever versions,
   and runtime dependency lock that must be reproducible.
4. Decide whether the app is packaged as an MLflow Model or tracked externally.
5. Define the comparison decision: debug lineage, choose a candidate, gate a release, or
   explain a production regression.
6. Run `python scripts/inspect_capabilities.py` when the target environment is available.

## Do not confuse these version layers

| Layer | MLflow object | Mutable indirection | What it answers |
|---|---|---|---|
| GenAI app/agent snapshot | `LoggedModel` + active model | app-specific naming/context | Which code/config produced this trace? |
| Prompt | Prompt Registry version | prompt alias | Which template/config was rendered? |
| Packaged executable | MLflow Model/LoggedModel artifact | model URI | What code and environment can run? |
| Governed deployable model | Registered Model Version | registered model alias | Which immutable artifact is approved? |
| Databricks deployment | served entity + endpoint config version | traffic routes | Which UC model version receives traffic? |
| Provider runtime | Gateway endpoint/model route | traffic split/fallback | Which provider/model actually answered? |

An alias move in the Model Registry does **not** automatically prove that a Databricks serving
endpoint changed; endpoint configs pin `entity_version` and must be inspected or updated.
Likewise, an AI Gateway endpoint name can remain stable while its provider/model route changes;
capture the resolved route in trace/release evidence.

## Canonical workflow

```text
source revision + prompt/config/tool versions
  → create/select LoggedModel
  → log model parameters and source metadata
  → set active model before traced execution
  → collect traces and evaluation results against a fixed dataset
  → compare quality, cost, latency, and failure slices
  → package/register/deploy the selected artifact
  → record deployment identity and monitor production traces
```

### Stable manual Git pattern

```python
import mlflow
from mlflow.utils.git_utils import get_git_commit

mlflow.set_experiment("customer-support-agent")
commit = get_git_commit(".") or "local-dev"
version_name = f"customer-support-agent-{commit[:12]}"

with mlflow.set_active_model(name=version_name) as active_model:
    mlflow.log_model_params(
        {
            "provider_model": "<PINNED_MODEL_ID>",
            "temperature": 0.2,
            "prompt_uri": "prompts:/support-system/7",
            "retriever_index": "support-docs-v12",
        },
        model_id=active_model.model_id,
    )
    response = traced_agent("How do I reset my password?")
```

Use explicit prompt versions for reproducible evaluation. Use an alias only when deliberate
runtime indirection is desired and capture the resolved version on the trace.

### Automatic Git pattern

```python
import mlflow

with mlflow.genai.enable_git_model_versioning() as git_context:
    result = traced_agent("How do I reset my password?")
    print(git_context.info.branch, git_context.info.commit, git_context.info.dirty)
```

This API is experimental and current docs require **MLflow >= 3.4**. It captures
branch/commit/dirty state and the dirty diff, deduplicates versions by
branch+commit+dirty state, records the repository URL and `mlflow.git.diff`, and
links traces to an application `LoggedModel`. It is unsupported in Databricks Git
Folders. Feature-detect it, pin MLflow, and use the manual pattern when it is
unavailable or when Git metadata cannot be read.

```python
import mlflow

with mlflow.genai.enable_git_model_versioning(remote_name="origin") as ctx:
    print(ctx.info.branch, ctx.info.commit, ctx.info.dirty)
    traced_agent("How do I reset my password?")

mlflow.genai.disable_git_model_versioning()
```

Agent Server's `setup_mlflow_git_based_version_tracking()` helper requires
**MLflow >= 3.6.0** (see `agent-serving`).

## Compare application versions

Compare candidates on the same dataset, scorer definitions, judge model/configuration, and
traffic slices. Include:

- quality and pass/fail deltas, not only aggregate averages;
- latency, token usage, cost, error/tool failure rates;
- prompt/model/tool/retriever/Gateway route identity;
- Git commit and dirty-state status;
- trace examples and assessment provenance;
- deployment endpoint/entity/config revision.

The version-comparison UI helps inspect trace and performance differences. In
**MLflow 3.18.0** the experimental `mlflow.genai.compare_evaluations()` API adds
automated statistical gating: it pairs rows by evaluation request ID or input hash,
selects McNemar (binary) or Wilcoxon (numeric) tests, requires at least six pairs,
reports bootstrap confidence intervals and effect sizes, and exposes
`ComparisonResult.assert_improved()` for a CI release gate. Set `greater_is_better`
per scorer and note that no multiple-comparison correction is applied.

```python
import mlflow
from mlflow.genai.scorers import scorer

@scorer
def exact_match(outputs, expectations):
    return outputs == expectations["expected_response"]

data = [
    {"inputs": {"question": f"q{i}"},
     "expectations": {"expected_response": "good"}}
    for i in range(6)
]
baseline = mlflow.genai.evaluate(
    data=data, predict_fn=lambda question: "bad", scorers=[exact_match]
)
candidate = mlflow.genai.evaluate(
    data=data, predict_fn=lambda question: "good", scorers=[exact_match]
)

comparison = mlflow.genai.compare_evaluations(
    candidate.run_id, baseline.run_id, log_results=True
)
print(comparison.summary())
comparison.assert_improved(scorers=["exact_match"], alpha=0.05)
```

The UI alone remains evidence collection, not automatic approval. Preserve the
selected artifact plus rollback target even when `assert_improved()` passes.

## Reference router

| Need | Read |
|---|---|
| LoggedModel semantics, lifecycle, active-model context, parameters | [`references/logged-model-lifecycle.md`](references/logged-model-lifecycle.md) |
| Git/manual versioning, comparison, CI and production lineage | [`references/workflows.md`](references/workflows.md) |
| Boundaries with prompts, flavors, registry, evaluation, and Databricks | [`references/integration-map.md`](references/integration-map.md) |
| Official documentation inventory and feature status | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Every implementation should state environment and MLflow version assumptions, use a stable
source identifier, capture all behavior-changing dependencies, trace before comparing, evaluate
candidates on the same dataset/scorers, preserve dirty-state provenance, and record the exact
deployed endpoint/entity/Gateway route version. Never label a moving alias or `latest` as
reproducible evidence.
