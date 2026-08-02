# Version tracking source ledger

Reviewed 2026-08-01. Treat `/latest/` as moving documentation and verify the installed API.

| Official source | Purpose/status |
|---|---|
| https://mlflow.org/docs/latest/genai/version-tracking/ | LoggedModel-based application versioning overview and manual Git quick pattern |
| https://mlflow.org/docs/latest/genai/version-tracking/quickstart/ | End-to-end introductory version workflow |
| https://mlflow.org/docs/latest/genai/version-tracking/track-application-versions-with-mlflow/ | Git-based app versioning; automatic API is experimental |
| https://mlflow.org/docs/latest/genai/version-tracking/compare-app-versions/ | Compare traces and performance across app versions |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.LoggedModel | LoggedModel entity contract |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html | Fluent LoggedModel, active-model, parameter, and tag APIs |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html | GenAI Git versioning, prompt, trace, and evaluation APIs |
| https://mlflow.org/docs/latest/genai/prompt-registry/ | Prompt versions, aliases, model config, and lineage |
| https://mlflow.org/docs/latest/genai/tracing/ | Trace association and instrumentation |
| https://mlflow.org/docs/latest/genai/eval-monitor/ | Evaluation-driven development and monitoring |
| https://mlflow.org/docs/latest/genai/datasets/ | Evaluation dataset curation and versioning |
| https://mlflow.org/docs/latest/genai/flavors/ | Packaging an application snapshot as an executable model |
| https://docs.databricks.com/aws/en/mlflow3/genai/ | Databricks managed MLflow 3 GenAI integration |

## Status notes

- The root guide states MLflow 3.x and Python prerequisites; minor-version gates must be checked.
- `mlflow.genai.enable_git_model_versioning()` is experimental and documented for newer MLflow 3
  releases; it has limitations in Databricks Git Folders.
- Examples on some overview pages may still use legacy `mlflow.evaluate()`. For current GenAI
  workflows use `mlflow.genai.evaluate()` and the `evaluation-monitoring` skill.
- Model Registry lifecycle stages are legacy/deprecated for new designs; prefer aliases.
