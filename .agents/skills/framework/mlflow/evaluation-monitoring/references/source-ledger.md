# MLflow GenAI Evaluation and Monitoring Source Ledger

Reviewed 2026-08-30. Use the installed MLflow signature and environment-specific docs when
the moving `/latest/` pages disagree with a package or managed workspace.

## Evaluation indexes and execution

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/eval-monitor/ | Evaluation-driven development, datasets, feedback, judges, monitoring |
| https://mlflow.org/docs/latest/genai/eval-monitor/quickstart/ | First evaluation workflow |
| https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/ | Running evaluations and result handling |
| https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/eval-examples/ | Prompt, agent, trace, and conversation evaluation examples |
| https://mlflow.org/docs/latest/genai/eval-monitor/regression-testing/ | `@mlflow.test`, pytest plugin, CI regression gates |
| https://mlflow.org/docs/latest/genai/eval-monitor/automatic-evaluations/ | Server-side automatic LLM-judge evaluation, sampling, filters, sessions |
| https://mlflow.org/docs/latest/genai/eval-monitor/scorers/ | Built-in/custom scorers and judge navigation |
| https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/ | Built-in response, RAG, tool, and multi-turn judges |
| https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/custom-judges/ | `make_judge`, variables, trace/conversation-aware judges |
| https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/ | Code-based `@scorer` and offline custom scorers |
| https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/alignment/ | Human alignment and judge optimization |
| https://mlflow.org/docs/latest/genai/eval-monitor/scorers/versioning/ | Registered scorer versions and retrieval |

## Datasets, assessments, and AI insights

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/datasets/ | Evaluation dataset concepts and constraints |
| https://mlflow.org/docs/latest/genai/datasets/sdk-guide/ | `create_dataset`, `merge_records`, schema, lineage |
| https://mlflow.org/docs/latest/genai/datasets/conversation-simulation/ | Reproducible multi-turn simulation records |
| https://mlflow.org/docs/latest/genai/datasets/end-to-end-workflow/ | Trace-to-dataset curation workflow |
| https://mlflow.org/docs/latest/genai/assessments/feedback/ | Feedback assessment API |
| https://mlflow.org/docs/latest/genai/assessments/expectations/ | Expectation/ground-truth API |
| https://mlflow.org/docs/latest/genai/assessments/review-queues/ | Experimental trace review queues and reviewer answers |
| https://mlflow.org/docs/latest/genai/eval-monitor/ai-insights/detect-issues/ | UI automatic issue detection and CLEARS workflow |
| https://mlflow.org/docs/latest/genai/eval-monitor/ai-insights/ai-issue-discovery/ | MCP/CLI hypothesis-driven experiment analysis |
| https://mlflow.org/docs/latest/genai/eval-monitor/faq/ | Evaluation troubleshooting and limitations |
| https://mlflow.org/docs/latest/genai/eval-monitor/legacy-llm-evaluation/ | Migration from legacy MLflow 2 `mlflow.evaluate()` |
| https://mlflow.org/docs/latest/genai/concepts/evaluation-datasets/ | Dataset concepts and field semantics |

## Status notes

- OSS automatic evaluation uses LLM judges through an AI Gateway endpoint and does not run
  code-based scorers online. Databricks managed production monitoring has separate Beta and
  serialization/permission constraints.
- Multi-turn judges and conversation simulation are experimental/version-sensitive; preserve
  session IDs and verify the installed API.
- Review queues and Judge Builder are recent UI/managed capabilities; treat their release status
  and permissions as environment-specific.
- Automatic issue detection and AI issue discovery propose hypotheses. Human-verify issues before
  turning them into expectations, release gates, or production actions.
