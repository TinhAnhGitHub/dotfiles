# GenAI flavors source ledger

Reviewed 2026-08-01. Verify `/latest/` examples against installed package signatures.

| Official source | Coverage/status |
|---|---|
| https://mlflow.org/docs/latest/genai/flavors/ | Integration overview; OpenAI model logging deprecation |
| https://mlflow.org/docs/latest/genai/flavors/langchain/ | LangChain/LangGraph flavor, Models from Code, streaming; experimental |
| https://mlflow.org/docs/latest/genai/flavors/langchain/autologging/ | LangChain trace/model autologging controls |
| https://mlflow.org/docs/latest/genai/flavors/langchain/guide/ | Detailed chain, agent, retriever, dependency patterns |
| https://mlflow.org/docs/latest/genai/flavors/langchain/notebooks/langchain-quickstart/ | End-to-end LangChain example |
| https://mlflow.org/docs/latest/genai/flavors/langchain/notebooks/langchain-retriever/ | Retriever and loader/deserialization example |
| https://mlflow.org/docs/latest/genai/flavors/dspy/ | DSPy logging/loading/streaming; experimental |
| https://mlflow.org/docs/latest/genai/flavors/dspy/notebooks/dspy_quickstart/ | DSPy quickstart |
| https://mlflow.org/docs/latest/genai/flavors/dspy/optimizer/ | Optimizer autologging and compiled programs |
| https://mlflow.org/docs/latest/genai/flavors/llama-index/ | Index/engine/Workflow/Settings and external stores |
| https://mlflow.org/docs/latest/genai/flavors/llama-index/notebooks/llama_index_quickstart/ | Index quickstart |
| https://mlflow.org/docs/latest/genai/flavors/llama-index/notebooks/llama_index_workflow_tutorial/ | Workflow/agent packaging |
| https://mlflow.org/docs/latest/genai/flavors/custom-pyfunc-for-llms/ | Legacy custom PyFunc guide; points to ResponsesAgent and Models from Code |
| https://mlflow.org/docs/latest/genai/flavors/custom-pyfunc-for-llms/notebooks/custom-pyfunc-advanced-llm/ | Advanced custom PyFunc tutorial |
| https://mlflow.org/docs/latest/genai/flavors/responses-agent-intro/ | Preferred MLflow 3 agent interface, tools, streaming, migration |
| https://mlflow.org/docs/latest/genai/flavors/chat-model-intro/ | ChatModel background; ResponsesAgent preferred in current docs |
| https://mlflow.org/docs/latest/genai/flavors/chat-model-guide/ | ChatModel authoring/migration context |
| https://mlflow.org/docs/latest/ml/model/models-from-code/ | Source-based model logging, execution, security, config |
| https://mlflow.org/docs/latest/ml/model/signatures/ | Input/output/params signatures and type hints |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.langchain.html | LangChain flavor API |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.dspy.html | DSPy flavor API |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.llama_index.html | LlamaIndex flavor API |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html | PythonModel, ResponsesAgent, logging/loading APIs |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.types.html | Responses request/response/event/helper schemas |
| https://mlflow.org/docs/latest/genai/tracing/ | Tracing packaged applications |
| https://mlflow.org/docs/latest/genai/eval-monitor/ | Evaluation before promotion |
| https://mlflow.org/docs/latest/genai/serving/ | OSS application/model serving |

## High-risk gates

- LangChain and DSPy flavors are marked experimental.
- LangGraph packaging uses Models from Code.
- Models from Code and generic streaming are documented from MLflow 2.12.2 onward.
- LlamaIndex Workflow support requires LlamaIndex 0.11.0+ and MLflow 2.17.0+.
- DSPy streaming requires a compatible DSPy release, logged signature, and string outputs.
- ResponsesAgent requires Pydantic 2 and is preferred over ChatModel/ChatAgent in MLflow 3 docs.
- Unity Catalog model versions require signatures.
