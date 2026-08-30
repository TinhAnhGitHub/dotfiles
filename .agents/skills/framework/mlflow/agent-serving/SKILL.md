---
name: agent-serving
description: >
  MLflow Agent Server and agent deployment: FastAPI `/invocations`, `@invoke` and
  `@stream` registration, Responses API request/response validation, automatic
  tracing, Git-linked app versions, `ResponsesAgent`, structured tool-calling,
  streaming events, evaluation, and custom app serving. Use whenever a user asks
  how to host, invoke, stream, package, or evaluate an MLflow agent service.
  Load the parent `mlflow` skill first.
compatibility: MLflow 3.x; Agent Server examples require MLflow 3.6.0+ and compatible OpenAI Agents/Pydantic versions
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-30"
---

# MLflow Agent Serving

Separate the serving plane from the packaged-model and registry planes. Agent Server hosts a
Responses API-compatible application behind FastAPI, validates requests/responses, aggregates
traces, and can associate executions with Git-based app versions. `ResponsesAgent` is the
structured MLflow Model interface for multi-turn/tool-calling agents. A serving endpoint is
still responsible for authentication, authorization, scaling, secrets, and network policy.

## Mandatory preflight

1. Inspect MLflow, `openai-agents`/framework, Pydantic, and provider SDK versions.
2. Choose a live Agent Server, a packaged `ResponsesAgent` MLflow Model, or a generic custom app.
3. Define the request/response/event contract, sync versus streaming behavior, tool allow-list,
   concurrency, timeouts, and client compatibility.
4. Configure tracking URI/experiment and decide whether Git app version tracking is enabled.
5. Trace and evaluate the agent before registration/deployment; use `evaluation-monitoring` for
   scorer and dataset design.
6. Load `genai-flavors` for Models from Code, model signatures, dependencies, and registry/serving
   operations. Load Databricks serving skills for workspace deployment.

## Choose the serving interface

| Need | Recommended interface | Contract |
|---|---|---|
| FastAPI service around a live agent | Agent Server | Register `@invoke()` and optional `@stream()` functions; serve `/invocations` |
| Packaged structured agent model | `ResponsesAgent` | PyFunc-compatible request/response with Responses API items, tools, and streaming events |
| Generic legacy/custom application | Custom app/PyFunc | You own request validation, state, streaming, and trace wiring |

Use Agent Server when the process should own the live framework agent. Use `ResponsesAgent` when
the executable artifact, signature, and model lifecycle need MLflow packaging/registry semantics.
Do not silently treat a custom PyFunc string response as a valid Responses API agent.

## Minimal Agent Server shape

`agent.py`:

```python
from agents import Agent, Runner
from mlflow.genai.agent_server import invoke, stream
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse

agent = Agent(
    name="support-agent",
    instructions="Resolve support questions without requesting secrets.",
)


@invoke()
async def non_streaming(request: ResponsesAgentRequest) -> ResponsesAgentResponse:
    messages = [item.model_dump() for item in request.input]
    result = await Runner.run(agent, messages)
    return ResponsesAgentResponse(
        output=[item.to_input_item() for item in result.new_items]
    )


# Add @stream() only after implementing and testing ResponsesAgentStreamEvent output.
```

`start_server.py`:

```python
import agent  # noqa: F401  # Registers @invoke/@stream functions.

from mlflow.genai.agent_server import AgentServer, setup_mlflow_git_based_version_tracking

agent_server = AgentServer("ResponsesAgent")
app = agent_server.app
setup_mlflow_git_based_version_tracking()


if __name__ == "__main__":
    agent_server.run(app_import_string="start_server:app")
```

Install and run the current documented baseline:

```bash
pip install -U openai-agents 'mlflow>=3.6.0'
python3 start_server.py --reload
```

Use `--workers N` for concurrent workers and `--port N` for a non-default port. Import the
module that registers functions before constructing/running the server. Do not use reload as a
production process manager; deploy behind an authenticated, monitored service boundary.

## Invocation and streaming contract

The server accepts a Responses API-shaped request at `/invocations`:

```bash
curl -X POST http://localhost:8000/invocations \
  -H 'Content-Type: application/json' \
  -d '{"input":[{"role":"user","content":"How do I reset access?"}]}'
```

Set `"stream": true` only when `@stream` is registered and the client consumes the documented
stream event format. Validate request items, tool calls, approval/denial items, custom outputs,
and final messages in contract tests. Tool dispatch must be allow-listed and authorized by the
application; an LLM-generated tool name is not permission.

`ResponsesAgent` supports structured tool-calling, multiple output messages, multi-turn input,
custom outputs, token tracking, and Responses API compatibility. Its model metadata uses the
Responses-agent task contract and the default Responses input example; inspect the installed
signature/schema before implementing a custom client.

## Package and deploy

For a packaged agent:

1. Put the reviewed agent definition in a Models-from-Code source file.
2. Set the MLflow model with `mlflow.models.set_model(...)` or use the documented agent model
   logging API.
3. Include pinned MLflow/framework/Pydantic/provider dependencies and a realistic input example.
4. Load both the native and PyFunc interfaces in an isolated environment.
5. Test sync, streaming, tool-call errors, multi-turn state, cancellation, and empty/invalid
   inputs.
6. Evaluate the loaded callable on a fixed dataset, register only after quality/security gates,
   then deploy with an immutable artifact identity.

Use `genai-flavors` for packaging details and `model-registry` for registered model aliases and
Databricks served-entity semantics. Do not bake API keys or external vector-store state into the
artifact; use an approved runtime secret/resource mechanism.

## Evaluate the live invoke function

The Agent Server docs expose the registered callable for evaluation. Keep the request wrapper
aligned with the server contract:

```python
import asyncio
import mlflow
from mlflow.genai.scorers import RelevanceToQuery, Safety
from mlflow.genai.agent_server import get_invoke_function
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse


def predict_fn(request: dict) -> ResponsesAgentResponse:
    invoke_fn = get_invoke_function()
    return asyncio.run(invoke_fn(ResponsesAgentRequest(**request)))


mlflow.genai.evaluate(
    data=[
        {
            "inputs": {
                "request": {
                    "input": [{"role": "user", "content": "What is 2 + 2?"}]
                }
            },
            "expected_response": "4",
        }
    ],
    predict_fn=predict_fn,
    scorers=[RelevanceToQuery(), Safety()],
)
```

The exact `predict_fn` input keys and scorer support depend on the target release; inspect the
installed examples/signatures. Add trace-aware tool/retrieval judges for agent behavior, not only
the final text response.

## Production safety and operations

- Put the service behind authentication and per-user authorization; `/invocations` is not an
  authorization mechanism.
- Use environment-backed secrets and short-lived credentials. Never log authorization headers or
  raw tool secrets in traces.
- Set explicit request, provider, tool, and stream timeouts; handle cancellation and partial
  streams without leaving state or spans open.
- Record app Git version, prompt version, model/provider, tool/MCP versions, and endpoint identity.
- Monitor trace exporter health, latency, token/cost, errors, tool failures, and session behavior.
- Roll out new agent artifacts behind a tested endpoint/configuration boundary and retain a rollback
  artifact. A Git change or MLflow model alias move alone is not deployment evidence.

## Reference router

| Need | Read |
|---|---|
| Agent Server implementation, invocation, streaming, evaluation | [`references/agent-server.md`](references/agent-server.md) |
| Agent Server, ResponsesAgent, custom apps, and version gates | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Every serving answer must specify the interface and versions, show the real request/response
contract, test streaming and tool behavior, protect secrets, trace/version executions, include
evaluation evidence, and define auth, scaling, health, rollback, and deployment identity.

## Related skills

- `genai-flavors` for Models from Code, ResponsesAgent packaging, signatures, and dependencies.
- `tracing-observability` for automatic/manual tracing and production export.
- `evaluation-monitoring` for datasets, judges, regression tests, and monitoring.
- `version-tracking` for Git/LoggedModel lineage.
- `model-registry` for model registration and serving lifecycle.
- `ai-gateway` for provider credentials, routing, guardrails, and budgets.
