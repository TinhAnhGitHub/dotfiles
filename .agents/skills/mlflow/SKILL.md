---
name: mlflow
description: >
  MLflow skill suite for ML, GenAI, and agent engineering. Use this parent skill whenever
  the user mentions MLflow, mlflow.genai, MLflow Tracing, app/agent version tracking,
  GenAI flavors, Models from Code, ResponsesAgent, MCP Registry, Model Registry,
  model versions/aliases, evaluation datasets, scorers, LLM judges, feedback,
  regression testing, production monitoring, or Databricks managed MLflow. Load this
  first, then load the matching sub-skill from the routing table.
---

# MLflow — Unified Skill Suite

Use this as the entry point for MLflow work. Route to the narrowest sub-skill so the
model loads only the references needed for the task.

## Sub-skill routing

| Topic | Sub-skill | Load when |
|---|---|---|
| GenAI evaluation and monitoring | [`evaluation-monitoring`](evaluation-monitoring/SKILL.md) | Evaluation datasets, human feedback, expectations, scorers, LLM-as-a-judge, `mlflow.genai.evaluate`, prompts, agents, traces, `@mlflow.test`, issue detection, automatic evaluation, or production monitoring |
| GenAI app/agent version tracking | [`version-tracking`](version-tracking/SKILL.md) | LoggedModel, active-model context, Git-linked app versions, trace lineage, configuration snapshots, or comparing app versions |
| Prompt Registry and prompt optimization | [`prompt-registry`](prompt-registry/SKILL.md) | `register_prompt`, `load_prompt`, prompt URIs, immutable versions, aliases, templates, model config, prompt lineage, `optimize_prompts`, or model migration |
| GenAI packaging and flavors | [`genai-flavors`](genai-flavors/SKILL.md) | LangChain/LangGraph, DSPy, LlamaIndex, PythonModel, Models from Code, ResponsesAgent, streaming, signatures, dependencies, or deployable app packaging |
| MCP server catalog and lifecycle | [`mcp-registry`](mcp-registry/SKILL.md) | MLflow MCP Registry, server.json, MCP semantic versions/statuses/aliases, tool discovery/snapshots, access endpoints, or governed agent tools |
| Model Registry and serving lifecycle | [`model-registry`](model-registry/SKILL.md) | Registered models/versions, signatures, aliases/tags, promotion/rollback/CI, OSS registry, Unity Catalog models, or the bridge to Databricks served entities and traffic |

Future MLflow topics should be added as sibling subfolders and listed here rather than
expanding this parent into a monolith.

## Cross-suite routing

Load the narrow MLflow sub-skill first for lifecycle semantics and API patterns. Also load:

| Context | Companion skill |
|---|---|
| Any Databricks workspace/API/auth task | `databricks`, then `databricks-core` |
| Unity Catalog trace storage, managed monitoring, platform permissions | `databricks-platform` |
| Agent/model endpoint invocation or deployment | `databricks-model-serving` |
| Scheduled evaluation or backfill orchestration | `databricks-jobs` |
| Bundle deployment of jobs/apps/resources | `databricks-dabs` |
| End-to-end LLMOps release workflow | `databricks-llmops` |
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
6. Keep version layers distinct: app `LoggedModel`, prompt version, packaged MLflow Model,
   Registered Model Version, and serving endpoint config answer different questions.
7. Prefer immutable numbered versions plus deliberate aliases. Record every alias resolution;
   never treat `latest` as approval or reproducible release evidence.
8. On Databricks, moving a UC model alias does not automatically update a serving endpoint
   whose served entity pins `entity_version`.

## Documentation

- MLflow GenAI: https://mlflow.org/docs/latest/genai/
- Evaluation and monitoring: https://mlflow.org/docs/latest/genai/eval-monitor/
- Version tracking: https://mlflow.org/docs/latest/genai/version-tracking/
- Packaging and flavors: https://mlflow.org/docs/latest/genai/flavors/
- MCP Registry: https://mlflow.org/docs/latest/genai/mcp-registry/
- Model Registry: https://mlflow.org/docs/latest/ml/model-registry/
- Python API: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html
- Databricks MLflow 3 GenAI: https://docs.databricks.com/aws/en/mlflow3/genai/
