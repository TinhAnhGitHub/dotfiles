---
name: mlflow
description: >
  MLflow skill suite for ML, GenAI, and agent engineering. Use this parent skill whenever
  the user mentions MLflow, mlflow.genai, MLflow Tracing, app/agent version tracking,
  GenAI flavors, Models from Code, ResponsesAgent, Agent Server, OpenTelemetry,
  AI Gateway, MCP Server, MCP Registry, AI Assistant, Model Registry, model
  versions/aliases, evaluation datasets, scorers, LLM judges, feedback, regression
  testing, production monitoring, or Databricks managed MLflow. Load this first,
  then load the matching sub-skill from the routing table.
---

# MLflow — Unified Skill Suite

Use this as the entry point for MLflow work. Route to the narrowest sub-skill so the
model loads only the references needed for the task.

## Sub-skill routing

| Topic | Sub-skill | Load when |
|---|---|---|
| Tracing and observability | [`tracing-observability`](tracing-observability/SKILL.md) | `@mlflow.trace`, autologging, OpenTelemetry/OTLP, distributed tracing, spans, integrations, trace UI/search, sessions/users, masking, token/cost, sampling, or production tracing |
| GenAI evaluation and monitoring | [`evaluation-monitoring`](evaluation-monitoring/SKILL.md) | Evaluation datasets, human feedback, expectations, scorers, LLM-as-a-judge, `mlflow.genai.evaluate`, prompt/agent/trace evaluation, `@mlflow.test`, review queues, issue detection, automatic evaluation, or production monitoring |
| AI Gateway governance | [`ai-gateway`](ai-gateway/SKILL.md) | LLM connections, provider credentials, unified/passthrough endpoints, traffic splitting, fallbacks, usage/cost, budgets, guardrails, Gateway benchmarks, or coding-agent model routing |
| GenAI app/agent version tracking | [`version-tracking`](version-tracking/SKILL.md) | LoggedModel, active-model context, Git-linked app versions, trace lineage, configuration snapshots, or comparing app versions |
| Prompt Registry and prompt optimization | [`prompt-registry`](prompt-registry/SKILL.md) | `register_prompt`, `load_prompt`, prompt URIs, immutable versions, aliases, templates, model config/cache, prompt lineage, `optimize_prompts`, rewrite, Playground, or Prompt Engineering UI |
| GenAI packaging and flavors | [`genai-flavors`](genai-flavors/SKILL.md) | LangChain/LangGraph, DSPy, LlamaIndex, PythonModel, Models from Code, ResponsesAgent, streaming, signatures, dependencies, or deployable app packaging |
| Agent serving | [`agent-serving`](agent-serving/SKILL.md) | Agent Server, `@invoke`, `@stream`, `/invocations`, Responses API validation, live agent hosting, streaming, or evaluating a served agent |
| MCP server catalog and lifecycle | [`mcp-registry`](mcp-registry/SKILL.md) | MLflow MCP Registry, server.json, MCP semantic versions/statuses/aliases, tool discovery/snapshots, access endpoints, or governed agent tools |
| MLflow MCP Server | [`mcp-server`](mcp-server/SKILL.md) | `mlflow mcp run`, MCP access to traces, field selection, trace feedback/expectations, assistant-driven analysis, or tool scoping with `MLFLOW_MCP_TOOLS` |
| MLflow AI Assistant | [`ai-assistant`](ai-assistant/SKILL.md) | Assistant panel/setup wizard, local coding-agent integration, project analysis, permission settings, or `uvx mlflow@latest agent setup` |
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
5. Treat AI Gateway endpoint names, MCP access endpoints, Agent Server URLs, and serving
   endpoints as different runtime boundaries; record their resolved configuration separately.
6. Keep MCP Registry (catalog/lifecycle), MLflow MCP Server (tracking-data access), and
   Agent Server (application hosting) distinct.
7. Keep a closed feedback loop: trace → human review → expectations → dataset → offline
   evaluation → regression gate → production monitoring → curate failures back into the
   dataset.
8. Keep version layers distinct: app `LoggedModel`, prompt version, packaged MLflow Model,
   Registered Model Version, and serving endpoint config answer different questions.
9. Prefer immutable numbered versions plus deliberate aliases. Record every alias resolution;
   never treat `latest` as approval or reproducible release evidence.
10. On Databricks, moving a UC model alias does not automatically update a serving endpoint
    whose served entity pins `entity_version`.

## Documentation

- MLflow GenAI: https://mlflow.org/docs/latest/genai/
- Tracing and observability: https://mlflow.org/docs/latest/genai/tracing/
- Evaluation and monitoring: https://mlflow.org/docs/latest/genai/eval-monitor/
- AI Gateway: https://mlflow.org/docs/latest/genai/governance/ai-gateway/
- Agent Server: https://mlflow.org/docs/latest/genai/serving/agent-server/
- Version tracking: https://mlflow.org/docs/latest/genai/version-tracking/
- Packaging and flavors: https://mlflow.org/docs/latest/genai/flavors/
- MCP Registry: https://mlflow.org/docs/latest/genai/mcp-registry/
- MLflow MCP Server: https://mlflow.org/docs/latest/genai/mcp/
- MLflow AI Assistant: https://mlflow.org/docs/latest/genai/getting-started/try-assistant/
- Model Registry: https://mlflow.org/docs/latest/ml/model-registry/
- Python API: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html
- Databricks MLflow 3 GenAI: https://docs.databricks.com/aws/en/mlflow3/genai/
