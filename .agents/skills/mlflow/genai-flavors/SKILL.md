---
name: genai-flavors
description: >
  Package, validate, load, and serve GenAI applications with MLflow flavors: LangChain,
  LangGraph, DSPy, LlamaIndex, custom PythonModel, Models from Code, and ResponsesAgent
  including streaming and tool-calling schemas. Use whenever users ask how to log an agent,
  choose a flavor, preserve dependencies/resources, build a deployable MLflow Model, or
  migrate ChatAgent/ChatModel code. Load the parent `mlflow` skill first.
compatibility: MLflow 3.x; framework flavors and several APIs are experimental or version-gated
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-01"
---

# MLflow GenAI Flavors and Packaging

A flavor defines the **executable contract**: source/object serialization, dependencies,
signature, load interface, streaming behavior, and resources. It is not a substitute for app
version lineage, evaluation evidence, registry approval, or endpoint operations.

## Mandatory preflight

1. Load parent `mlflow`; inspect MLflow, Python, framework, Pydantic, and provider SDK versions.
2. Choose native framework loading versus generic `mlflow.pyfunc` serving.
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
  → deploy and monitor
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

## Reference router

| Need | Read |
|---|---|
| Choice, common workflow, signatures, dependency/resource rules | [`references/selection-and-contract.md`](references/selection-and-contract.md) |
| LangChain/LangGraph autologging, Models from Code, streaming, gotchas | [`references/langchain-langgraph.md`](references/langchain-langgraph.md) |
| DSPy and LlamaIndex packaging, optimizers, engines, workflows | [`references/dspy-llamaindex.md`](references/dspy-llamaindex.md) |
| Custom `PythonModel`, `ResponsesAgent`, streaming and tool-call contract | [`references/custom-responses-agent.md`](references/custom-responses-agent.md) |
| Validation, evaluation, registry, OSS serving, Databricks serving | [`references/reproducibility-serving.md`](references/reproducibility-serving.md) |
| Official page inventory and feature gates | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Produce runnable files, not isolated fragments. Pin the target environment, use immutable prompt
and external-resource identities, include realistic examples/signatures, test native and PyFunc
interfaces, exercise streaming to completion, declare resources explicitly, redact secrets, and
show evaluation plus rollout/rollback. Do not recommend unsafe deserialization of untrusted
artifacts or unrestricted code-execution tools.
