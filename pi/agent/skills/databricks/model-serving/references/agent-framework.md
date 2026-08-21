# Databricks Agent Framework — Beyond ResponsesAgent

Source: [Databricks Agent Framework docs](https://docs.databricks.com/aws/en/generative-ai/agent-framework/build-agents),
[Author custom agents](https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent),
[MLflow ResponsesAgent](https://mlflow.org/docs/latest/genai/flavors/responses-agent-intro/)

---

## Overview

The Databricks Agent Framework provides end-to-end tooling for building, evaluating, deploying, and monitoring AI agents. It supports any authoring library (LangGraph, LangChain, OpenAI, LlamaIndex) and integrates with MLflow Tracing, Agent Evaluation, and production monitoring.

**Three entry points:**

| Path | When to Use |
|------|-------------|
| **AI Playground** (no-code) | Prototype and test agents quickly; export to code |
| **Knowledge Assistant** | Domain-specific chatbots via an intuitive UI |
| **Custom agents (Python)** | Full control — any framework, any orchestration logic |

---

## AI Playground (No-Code Starting Point)

1. Navigate to **AI Playground** in the Databricks UI
2. Select an LLM (Foundation Model API endpoint)
3. Add tools (UC functions, vector search indexes, etc.)
4. Chat with the agent to test responses
5. Export the configuration to Python code for further customization

---

## Knowledge Assistant

Pre-built domain-specific AI chatbots. Configured through an intuitive interface — no code required. See [Knowledge Assistant docs](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/knowledge-assistant).

---

## Custom Agents (MLflow `ResponsesAgent`)

This is the recommended approach for hand-rolled agents. See:
- **[genai-agents.md](genai-agents.md)** — Full end-to-end example with LangGraph + UC Function Toolkit + Vector Search
- **MLflow ResponsesAgent guide** — Framework-agnostic; wraps any LLM, LangGraph, or custom logic

### Key Concepts

```python
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)
```

**`ResponsesAgent`** is a subclass of `PythonModel` that provides:
- OpenAI-compatible request/response (`{input: [{role, content}]}` → `{output: [...]}`)
- Streaming support via `predict_stream`
- Multi-agent support
- Compatibility with MLflow logging, tracing, and serving

**Migration from `ChatAgent`:**
- Text responses: `{"role": "assistant", "content": "..."}` → `{"type": "message", "content": [{"type": "output_text", "text": "..."}]}`
- Tool calls: `{"role": "assistant", "tool_calls": [...]}` → `{"type": "function_call", "id": "fc_1", ...}`
- Tool results: `{"role": "tool", "content": "..."}` → `{"type": "function_call_output", "call_id": "...", "output": "..."}`

**Helper methods for output items:**
- `create_text_output_item(text, id)` — text response
- `create_function_call_item(id, call_id, name, arguments)` — tool call
- `create_function_call_output_item(call_id, output)` — tool result
- `create_reasoning_item(...)` — reasoning/thinking content
- `create_mcp_approval_request_item(...)` — MCP human-in-the-loop
- `create_mcp_approval_response_item(...)` — MCP approval response
- `create_text_delta(delta, item_id)` — streaming text delta
- `create_annotation_added(...)` — streaming annotation

---

## Agent Tools

| Tool Type | Description | How to Create |
|-----------|-------------|---------------|
| **UC Functions** | Call registered SQL/Python functions | `UCFunctionToolkit(function_names=[...]).tools` |
| **Vector Search** | Retrieve from vector indexes | `VectorSearchRetrieverTool(index_name=..., num_results=5)` |
| **MCP Servers** | Connect to MCP-compatible tools | Configure via `databricks.tools.mcp` |
| **Custom tools** | Any Python function | Wrap as LangChain tool or OpenAI function |
| **External APIs** | Call external services | Implement in custom tool code |

See [AI agent tools](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool).

---

## MCP (Model Context Protocol)

Databricks supports MCP as a standardized interface for connecting agents to data and tools:

- **MCP approval requests**: `create_mcp_approval_request_item()` — human-in-the-loop for sensitive tool calls
- **MCP servers**: Configure external MCP servers as tool providers

See [MCP on Databricks](https://docs.databricks.com/aws/en/generative-ai/mcp/).

---

## Evaluate, Debug & Monitor

| Stage | Tool | Description |
|-------|------|-------------|
| **Development** | MLflow Tracing | End-to-end observability — log every step |
| **Pre-deploy** | Agent Evaluation | Measure quality, cost, latency via LLM judges |
| **Post-deploy** | Production Monitoring | Same eval config as offline evaluation |
| **Review** | Built-in Review Apps | Stakeholder/SME feedback collection |

**Log + deploy flow:**

```python
# Agent evaluation before deployment
from mlflow.metrics.genai import make_genai_metric

# Create custom LLM judge
professionalism = make_genai_metric(
    name="professionalism",
    definition="Agent responses should be professional and clear.",
    grading_prompt="Rate from 1-5: ...",
    model="endpoints:/databricks-claude-sonnet-4-6",
)

eval_result = mlflow.evaluate(
    model=logged_agent_info.model_uri,
    data=eval_dataset,
    model_type="databricks-agent",
    evaluators="databricks-agent",
    evaluator_config={"model_type": "databricks-agent"},
    extra_metrics=[professionalism],
)
```

**Monitoring in production:**

```python
# Reuse the same evaluation config for online monitoring
agent = agents.deploy(model_name, version)
# Monitor at: https://<workspace-url>/mlflow/endpoints/<endpoint-name>/monitoring
```

See:
- [Agent Evaluation](https://docs.databricks.com/aws/en/generative-ai/agent-evaluation/)
- [MLflow Tracing](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/)
- [Production Monitoring](https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/production-monitoring)

---

## ResponsesAgent Quick Reference

```python
# agent.py — "Models from Code" pattern
import mlflow
from mlflow.pyfunc import ResponsesAgent

class MyAgent(ResponsesAgent):
    def predict(self, request):
        return ResponsesAgentResponse(output=[
            self.create_text_output_item(text="Answer", id="msg_1"),
        ])

    def predict_stream(self, request):
        # streaming implementation
        ...

mlflow.models.set_model(MyAgent())

# log_model.py
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        python_model="agent.py",        # file path, NOT instance
        resources=[...],                # auto-auth — DO NOT skip
        registered_model_name="catalog.schema.model",
    )

# deploy
from databricks import agents
agents.deploy("catalog.schema.model", "1", endpoint_name="my-agent")
```
