---
name: mlflow
description: >
  MLflow skill suite for ML, GenAI, and agent engineering. Use this parent skill whenever
  the user mentions MLflow, mlflow.genai, MLflow Tracing, evaluation datasets, scorers,
  LLM judges, feedback, expectations, prompt evaluation, agent evaluation, regression
  testing, automatic evaluation, production monitoring, or Databricks managed MLflow.
  Load this first, then load the matching sub-skill from the routing table.
---

# MLflow — Unified Skill Suite

Use this as the entry point for MLflow work. Route to the narrowest sub-skill so the
model loads only the references needed for the task.

## Sub-skill routing

| Topic | Sub-skill | Load when |
|---|---|---|
| GenAI evaluation and monitoring | [`evaluation-monitoring`](evaluation-monitoring/SKILL.md) | Evaluation datasets, human feedback, expectations, scorers, LLM-as-a-judge, `mlflow.genai.evaluate`, prompts, agents, traces, `@mlflow.test`, issue detection, automatic evaluation, or production monitoring |

Future MLflow topics should be added as sibling subfolders and listed here rather than
expanding this parent into a monolith.

## Cross-suite routing

Load the MLflow sub-skill first for evaluation semantics and API patterns. Also load:

| Context | Companion skill |
|---|---|
| Any Databricks workspace/API/auth task | `databricks`, then `databricks-core` |
| Unity Catalog trace storage, managed monitoring, platform permissions | `databricks-platform` |
| Agent/model endpoint invocation or deployment | `databricks-model-serving` |
| Scheduled evaluation or backfill orchestration | `databricks-jobs` |
| Bundle deployment of jobs/apps/resources | `databricks-dabs` |
| Databricks app that collects or displays trace feedback | `databricks-apps` |
| pytest regression suites | `pytest-databricks` |

## Shared operating rules

1. Identify **OSS MLflow vs Databricks managed MLflow** before proposing code. Their
   offline evaluation APIs overlap, while online scorer capabilities, storage, limits,
   permissions, and release status differ.
2. Check the installed MLflow version before using recently added APIs. The latest docs
   move quickly and some pages can temporarily disagree.
3. Prefer current `mlflow.genai.evaluate()` over legacy MLflow 2 LLM-evaluation APIs.
4. Trace first when evaluating agents, RAG, tools, or multi-turn conversations; final
   outputs alone cannot reveal execution failures.
5. Keep a closed feedback loop: trace → human review → expectations → dataset → offline
   evaluation → regression gate → production monitoring → curate failures back into the
   dataset.

## Documentation

- MLflow GenAI: https://mlflow.org/docs/latest/genai/
- Evaluation and monitoring: https://mlflow.org/docs/latest/genai/eval-monitor/
- Python API: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html
- Databricks MLflow 3 GenAI: https://docs.databricks.com/aws/en/mlflow3/genai/
