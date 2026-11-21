---
name: genai-flavors
description: >
  Package, validate, load, and serve GenAI applications with MLflow flavors: LangChain,
  LangGraph, DSPy, LlamaIndex, custom PythonModel, Models from Code, and ResponsesAgent
  including streaming, tool-calling schemas, and Agent Server deployment boundaries. Use
  whenever users ask how to log an agent, choose a flavor, preserve dependencies/resources,
  build a deployable MLflow Model, connect it to Agent Server, or migrate ChatAgent/ChatModel
  code. Load the parent `mlflow` skill first.
compatibility: MLflow 3.x; 3.18.0 adds model-code execution gates and pickle-free serialization; framework flavors, ResponsesAgent, Agent Server, and several APIs are experimental or version-gated
metadata:
  version: "0.3.0"
  docs-reviewed: "2026-11-21"
---

# MLflow GenAI Flavors and Packaging

A flavor defines the **executable contract**: source/object serialization, dependencies,
signature, load interface, streaming behavior, and resources. It is not a substitute for app
version lineage, evaluation evidence, registry approval, or endpoint operations.

## Mandatory preflight

1. Load parent `mlflow`; inspect MLflow, Python, framework, Pydantic, and provider SDK versions.
2. Choose native framework loading versus generic `mlflow.pyfunc` serving or Agent Server.
3. Define input/output/streaming schemas and a realistic `input_example`.
4. Inventory remote resources: endpoints, functions, vector indexes, MCP servers, secrets, and
   network access.
5. Decide object serialization versus **Models from Code**. Prefer code when objects contain
   dynamic/unpickleable state or partner packages.
6. Trace and evaluate before registration/deployment.
7. Run `python scripts/inspect_flavors.py` in the target environment.

## Selection matrix

| Application | Primary choice | Key constraint |
|---|---|---|
| LangChain chain/retriever | `mlflow.langchain` | Flavor is experimental; partner-package models favor Models from Code |
| LangGraph compiled graph | `mlflow.langchain` + Models from Code | Object/legacy autolog model serialization is not the supported packaging path |
| DSPy program | `mlflow.dspy` | Experimental; log the optimized/compiled program for production |
| LlamaIndex index/engine | `mlflow.llama_index` | `engine_type` fixes the PyFunc interface |
| LlamaIndex Workflow/external vector store | LlamaIndex + Models from Code | PyFunc inference is synchronous; remote data is not embedded |
| Framework-agnostic agent | `ResponsesAgent` + Models from Code | Preferred over `ChatModel`/`ChatAgent`; Pydantic 2 required |
| Live Responses API service | Agent Server | `@invoke`/`@stream`, `/invocations`, and current Agent Server version gate |
| Generic non-agent behavior | `PythonModel` + Models from Code | You own schemas, state, streaming, security, and resource declarations |

`mlflow.openai.log_model()` is deprecated for saving prompts. Put prompts in Prompt Registry and
package application logic separately.

## Canonical packaging workflow

```text
trace working app
  → choose flavor and interface
  → move executable definition into reviewed source file
  → mlflow.models.set_model(model)
  → log_model(path, name, input_example, dependencies/resources)
  → inspect inferred signature and environment
  → load natively and through pyfunc
  → validate isolated prediction and streaming
  → evaluate on fixed dataset
  → register approved immutable artifact
  → deploy through Agent Server or model-serving boundary and monitor
```

## Models from Code core pattern

`app_model.py`:

```python
import mlflow

model = build_application_from_environment()
mlflow.models.set_model(model)
```

Logging process:

```python
import mlflow

info = mlflow.pyfunc.log_model(
    python_model="app_model.py",
    name="agent",
    input_example={"input": [{"role": "user", "content": "Hello"}]},
    pip_requirements=["mlflow==<PINNED_VERSION>", "pydantic>=2,<3"],
)
loaded = mlflow.pyfunc.load_model(info.model_uri)
```

The source file executes during logging/loading. Never embed credentials; avoid network writes,
index creation, destructive initialization, and uncontrolled import-time work.

## ResponsesAgent and Agent Server boundary

`ResponsesAgent` is the structured model interface for Responses API-compatible inputs, tool
calling, multiple output messages, multi-turn conversations, custom outputs, streaming events,
and token tracking. The Agent Server is the FastAPI runtime that registers `@invoke`/`@stream`
functions and serves `/invocations`. Package the agent when model identity and isolated loading
matter; use Agent Server when a live process should own the framework runtime. Load `agent-serving`
for request/event tests, `get_invoke_function`, deployment, and auth/scaling details.

Preserve Pydantic 2 schemas, the documented task metadata, default input example, tool approval
items, and final stream event. Test native, PyFunc, and HTTP behavior separately.

## Security and serialization (MLflow 3.18.0+)

`MLFLOW_ALLOW_MODEL_CODE_EXECUTION` (default `true`) controls whether MLflow will
load model-supplied code. Set it to `false` to refuse loading any model that needs
code execution; it replaces/deprecates `MLFLOW_ALLOW_PICKLE_DESERIALIZATION`, which
still works but is pickle-only. With the flag `false`, loading raises for
`mlflow.pyfunc.load_model()` (including Spark UDFs and `mlflow models serve`),
pickle/cloudpickle models, `code_paths`/`infer_code_paths` models, **Models from
Code**, models on the Python path, Transformers custom code, and LlamaIndex models
whose saved `Settings` names LLM/embedding classes. Checks are skipped in Databricks
Runtime and Model Serving. Pickle-free formats are becoming the default:
`serialization_format="skops"` (sklearn/LightGBM), `"pt2"` for PyTorch (needs
`input_example`, torch >= 2.4, or >= 2.10 with the flag `false`), and DSPy
`use_dspy_model_save=True` (dspy > 3.1.0). See
<https://mlflow.org/docs/latest/ml/tracking/pickle-free-models/>.

```python
import os
os.environ["MLFLOW_ALLOW_MODEL_CODE_EXECUTION"] = "false"  # 3.18.0+

import mlflow
from mlflow.models import set_model
from mlflow.pyfunc import PythonModel

class Normalizer(PythonModel):
    def predict(self, context, model_input, params=None):
        return [str(x).strip() for x in model_input]

set_model(Normalizer())
```

```python
import mlflow
info = mlflow.pyfunc.log_model(
    python_model="normalizer.py", name="normalizer",
    pip_requirements=["mlflow==3.18.0"],  # pin: inference would otherwise load the model
    input_example=["  hello  "],
)
print(mlflow.pyfunc.load_model(info.model_uri).predict([" hi "]))
```

## ResponsesAgent helper surface

Only construct `ResponsesAgentResponse` and `ResponsesAgentStreamEvent` directly.
Use the instance helpers for items: `create_text_output_item`, `create_reasoning_item`,
`create_function_call_item`, `create_mcp_approval_request_item`,
`create_mcp_approval_response_item`, `create_annotation_added`, and `create_text_delta`.
`request.custom_inputs` and `custom_outputs` pass through arbitrary metadata.
`mlflow.types.responses_helpers` is for dict validation, not item construction.
Conversion helpers `to_chat_completions_input()` and
`output_to_responses_items_stream()` bridge Chat Completions and Responses formats.

```python
import mlflow
from mlflow.models import set_model
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse

class SupportAgent(ResponsesAgent):
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        return ResponsesAgentResponse(
            output=[
                self.create_reasoning_item(
                    summary=[{"type": "summary_text", "text": "Checked policy"}]
                ),
                self.create_text_output_item(text="Refunds need an order ID.", id="msg_1"),
            ],
            custom_outputs={"source": "policy-v12"},
        )

set_model(SupportAgent())
```

## Reference router

| Need | Read |
|---|---|
| Choice, common workflow, signatures, dependency/resource rules | [`references/selection-and-contract.md`](references/selection-and-contract.md) |
| LangChain/LangGraph autologging, Models from Code, streaming, gotchas | [`references/langchain-langgraph.md`](references/langchain-langgraph.md) |
| DSPy and LlamaIndex packaging, optimizers, engines, workflows | [`references/dspy-llamaindex.md`](references/dspy-llamaindex.md) |
| Custom `PythonModel`, `ResponsesAgent`, streaming and tool-call contract | [`references/custom-responses-agent.md`](references/custom-responses-agent.md) |
| Validation, evaluation, registry, OSS serving, Databricks serving | [`references/reproducibility-serving.md`](references/reproducibility-serving.md) |
| Official page inventory, Agent Server, and feature gates | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Produce runnable files, not isolated fragments. Pin the target environment, use immutable prompt
and external-resource identities, include realistic examples/signatures, test native/PyFunc/HTTP
interfaces as applicable, exercise streaming to completion, declare resources explicitly, redact
secrets, and show evaluation plus rollout/rollback. Do not recommend unsafe deserialization of
untrusted artifacts or unrestricted code-execution tools.
