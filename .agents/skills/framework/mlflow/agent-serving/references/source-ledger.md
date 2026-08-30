# MLflow Agent Serving Source Ledger

Reviewed 2026-08-30. Check the installed MLflow, Pydantic, framework, and provider versions
before using the moving `/latest/` serving APIs.

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/serving/agent-server/ | Agent Server features, decorators, `/invocations`, run/test/evaluate workflow |
| https://mlflow.org/docs/latest/genai/serving/responses-agent/ | ResponsesAgent contract, structured outputs, tools, streaming, model metadata |
| https://mlflow.org/docs/latest/genai/serving/custom-apps/ | Generic custom application serving |
| https://mlflow.org/docs/latest/genai/serving/ | Serving and deployment navigation |
| https://mlflow.org/docs/latest/genai/flavors/responses-agent-intro/ | ResponsesAgent flavor and migration context |
| https://mlflow.org/docs/latest/genai/flavors/custom-pyfunc-for-llms/ | Custom PyFunc packaging boundary |
| https://mlflow.org/docs/latest/ml/model/models-from-code/ | Source-based model logging, execution, security, config |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.agent_server.html | Agent Server API reference |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.types.html | Responses request/response/event schemas |
| https://mlflow.org/docs/latest/genai/tracing/ | Tracing and production observability |
| https://mlflow.org/docs/latest/genai/eval-monitor/ | Evaluation and monitoring |

## Status notes

- Current Agent Server examples require `mlflow>=3.6.0` and `openai-agents`.
- Agent Server, packaged `ResponsesAgent`, and generic custom apps are distinct interfaces;
  select one explicitly.
- Streaming, tool approval items, custom outputs, and schema metadata are contract-sensitive;
  inspect the installed version and write end-to-end tests.
