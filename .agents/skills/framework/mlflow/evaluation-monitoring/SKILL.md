---
name: evaluation-monitoring
description: >
  MLflow GenAI evaluation and monitoring. Use whenever a task involves evaluation
  datasets, feedback, expectations, scorers, LLM-as-a-judge, `mlflow.genai.evaluate`,
  `predict_fn`, prompt or agent evaluation, trace evaluation, RAG/tool/multi-turn quality,
  judge alignment, scorer versioning, Judge Builder, review queues, conversation simulation,
  `@mlflow.test`, regression CI, automatic issue detection, automatic evaluation, production
  monitoring, or Databricks MLflow 3 tracing and Unity Catalog. Load the parent `mlflow` skill
  first. This skill should trigger even when the user asks generally how to test, measure,
  monitor, or improve an LLM app or agent with MLflow.
compatibility: MLflow 3.x; some workflows require newer minor versions or Databricks managed MLflow
metadata:
  version: "0.2.0"
  docs-reviewed: "2026-08-30"
---

# MLflow GenAI Evaluation & Monitoring

Use this skill to build an **evaluation-driven development loop**, not a one-off score.

The current GenAI evaluation index spans offline evaluation, trace/session-based automatic
evaluation, built-in and custom judges, scorer registration/versioning, evaluation datasets,
conversation simulation, review queues, regression testing, and AI-assisted issue discovery.
Keep each capability behind its documented MLflow/Databricks version and preview status.

```text
app/agent
  → manual feedback and trace review (inner loop)
  → expectations and curated evaluation dataset
  → systematic offline evaluation
  → regression tests and CI gate
  → automatic/production monitoring (outer loop)
  → failing or representative real-world traces
  → new dataset records and expectations
  → fixes to app/agent, prompts, tools, retrieval, or judges
```

## Mandatory preflight

Before writing implementation code:

1. Determine the environment: OSS tracking server, Databricks managed MLflow, or both.
2. Inspect `mlflow.__version__`; identify preview/experimental features.
3. Identify tracking URI, experiment, trace storage backend, and judge model endpoint.
4. Confirm whether evaluation regenerates outputs (`predict_fn`) or scores existing
   outputs/traces (no `predict_fn`).
5. Define the release decision: exploratory metrics, comparison, regression gate, or
   continuous monitoring.
6. Decide whether automatic evaluation will score new traces/sessions and configure an AI
   Gateway judge endpoint, or whether `mlflow.genai.evaluate()` will score a fixed dataset.
7. For Databricks, load `databricks` plus the relevant companion skill before proposing
   credentials, Unity Catalog, SQL warehouse, serving endpoint, Job, or bundle code.

Run the bundled capability inspector when a local environment is available:

```bash
python scripts/inspect_capabilities.py
```

Interpret `unavailable` as a version/package capability gap, not an instruction to guess
an older API. Pin the target environment, then inspect its documented signature.

## Reference router

Read only the files relevant to the request.

| Need | Read |
|---|---|
| Philosophy, quickstart, evaluation contract, automation blueprint | [`references/lifecycle-quickstart.md`](references/lifecycle-quickstart.md) |
| Create, merge, search, version, and curate evaluation datasets | [`references/datasets.md`](references/datasets.md) |
| Human/end-user feedback, expectations, annotation, review workflows | [`references/feedback-expectations.md`](references/feedback-expectations.md) |
| Full scorer inventory, custom scorers, LLM judges, alignment | [`references/scorers-judges.md`](references/scorers-judges.md) |
| Data setup, `predict_fn`, output/result handling, parallel execution | [`references/running-evaluations.md`](references/running-evaluations.md) |
| Prompt iteration/optimization, agents, RAG, tools, traces, multi-turn | [`references/prompts-agents-traces.md`](references/prompts-agents-traces.md) |
| `@mlflow.test`, pytest-xdist, CI gating | [`references/regression-ci.md`](references/regression-ci.md) |
| Automatic issue detection, five stages, CLEARS, triage | [`references/issue-detection.md`](references/issue-detection.md) |
| OSS automatic evaluation and Databricks production monitoring | [`references/production-monitoring.md`](references/production-monitoring.md) |
| Databricks tracing, manual/auto instrumentation, UC storage, PII | [`references/databricks-tracing.md`](references/databricks-tracing.md) |
| Databricks evaluation, permissions, Review App, backfill, cross-skill routing | [`references/databricks-integration.md`](references/databricks-integration.md) |
| Version gates, source-of-truth order, known documentation drift | [`references/version-source-guardrails.md`](references/version-source-guardrails.md) |
| Exhaustive current OSS evaluation index and subpages | [`references/source-ledger.md`](references/source-ledger.md) |

## Canonical evaluation contract

Every systematic evaluation has three components:

```python
import mlflow
from mlflow.genai.scorers import Correctness, Guidelines

data = [
    {
        "inputs": {"question": "What is MLflow?"},
        "expectations": {
            "expected_facts": ["MLflow is an open-source AI and ML platform"],
        },
        "tags": {"slice": "documentation"},
    }
]


def predict_fn(question: str) -> str:
    # Parameter names must match keys in data[i]["inputs"].
    return app(question)


result = mlflow.genai.evaluate(
    data=data,
    predict_fn=predict_fn,
    scorers=[
        Correctness(),
        Guidelines(name="concise", guidelines="The response must be concise."),
    ],
)

print(result.metrics)
print(result.result_df)
```

- **Dataset** supplies representative inputs, optional pre-generated outputs, ground
  truth expectations, source lineage, and slice tags.
- **`predict_fn`** generates the candidate output and trace. Omit it when scoring
  pre-generated outputs or existing traces.
- **Scorers** convert behavior into `Feedback`: deterministic code checks, built-in LLM
  judges, custom judges, or trace-aware checks.

## Workflow selection

| Situation | Workflow |
|---|---|
| Early prototype, few examples | List-of-dicts data + manual trace review + 2–4 scorers |
| Stable benchmark | Named `EvaluationDataset` + version/slice tags + pinned prompts/models/judges |
| Prompt/model/tool comparison | Same dataset and scorer suite; separate evaluation runs; compare deltas and failures |
| Existing production behavior | Search traces; evaluate them directly without `predict_fn`; annotate failures |
| Known regression | One focused `@mlflow.test`; assert `result.passed`; run on every PR |
| Continuous quality | Register LLM judges with sampling/filtering for OSS automatic evaluation; on Databricks use managed production monitoring and optional code scorers |
| Multi-turn product behavior | Preserve session IDs; use conversation simulation for reproducible scenarios and session judges for trace-level monitoring |
| Human labeling at scale | Use a review queue/annotation workflow; approve expectations before adding release dataset records |
| Unknown failure modes | Run automatic issue detection, verify clusters, then translate validated failures into expectations/scorers/tests |

## Scorer design order

1. Start with deterministic code scorers for schema, invariants, latency, exact tool
   arguments, and business rules.
2. Add built-in judges for broadly defined semantics.
3. Use `Guidelines` for simple domain rules.
4. Use `make_judge` for custom categorical/numeric criteria or trace exploration.
5. Calibrate against human labels; align and version judges when disagreement matters.
6. Register only stable LLM judges for automatic evaluation; code-based scorers remain offline-only in OSS.
7. Never treat a single non-deterministic judge score as unquestionable ground truth.

## Automation pattern

Automate the stable parts of the loop:

1. Trace every candidate and production execution.
2. Nightly or event-driven: select representative, negative-feedback, error, and slow
   traces; deduplicate by semantic case and input identity.
3. Queue ambiguous cases for human annotation; log expectations and reviewer identity.
4. Merge approved cases into the evaluation dataset with provenance and slice tags.
5. Run offline evaluation on each PR; run fast deterministic tests first and budgeted
   LLM judges second.
6. Block release on explicit pass/fail gates, not merely on an aggregate average.
7. Deploy; monitor sampled live traces; alert/triage externally where needed.
8. Convert validated production failures into permanent regression cases.

## Environment branching

### OSS MLflow

- Evaluation datasets require a SQL backend; FileStore is unsupported.
- Automatic evaluation uses server-side LLM judges and an AI Gateway endpoint.
- Automatic evaluation does not support code-based scorers.
- Automatic issue detection is available through the UI; the MCP/CLI AI issue discovery
  flow is separate.
- Newly enabled judges evaluate only eligible recent traces/sessions and do not backfill old
  assessments automatically; configure sampling/filtering and session inactivity deliberately.

### Databricks managed MLflow

- Use workspace auth and an MLflow experiment; load `databricks-core` for auth/profile
  guidance.
- Unity Catalog evaluation datasets and UC trace storage add governance and SQL access.
- Managed production monitoring is Beta and can run supported `@scorer` functions in
  addition to LLM judges, with notebook serialization constraints.
- UC traces may require a SQL warehouse; monitoring may require a serverless budget
  policy; privileges and feature availability are workspace-dependent.

## Current feature gates

- Expectations: current docs identify MLflow 3.2+.
- `make_judge`: current docs identify MLflow 3.4+; trace-based judges need an explicit model.
- Prompt optimization/rewrite: route to `prompt-registry`, where current docs identify 3.5+.
- Multi-turn built-in judges are experimental; the full conversation-simulation workflow is newer
  and requires a compatible recent MLflow release.
- Judge Builder UI: current docs identify MLflow 3.9+.
- `@mlflow.test` regression workflow: current CI docs use MLflow 3.14+.
- Review queues: current docs identify the feature as experimental and added in MLflow 3.14.0.
- Automatic evaluation and issue detection are operational/preview-sensitive; inspect the target
  server, endpoint, permissions, and installed signatures rather than assuming parity with offline
  evaluation.

## Quality bar for answers and implementations

When using this skill, produce:

1. An environment/version assumptions block.
2. The selected workflow and why it fits the release decision.
3. Complete runnable code with imports and realistic schemas.
4. Dataset fields and scorer input requirements.
5. Cost, privacy, nondeterminism, and permission implications.
6. A closed-loop automation plan from production failures back to tests.
7. Official source URLs for preview or rapidly changing APIs.

Do not copy stale examples blindly. If docs disagree, use the environment-specific page,
the installed API signature, and the rules in `version-source-guardrails.md`.
