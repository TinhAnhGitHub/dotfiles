# Model Registry and Azure serving source ledger

Reviewed 2026-08-01. `/latest/` and Microsoft Learn pages are moving sources.

## MLflow

| Official source | Coverage/status |
|---|---|
| https://mlflow.org/docs/latest/ml/model-registry/ | Registry concepts, OSS and Databricks UC registration |
| https://mlflow.org/docs/latest/ml/model-registry/workflow/ | Register/load/search/annotate lifecycle |
| https://mlflow.org/docs/latest/ml/model-registry/tutorial/ | End-to-end registry tutorial |
| https://mlflow.org/docs/latest/ml/model/signatures/ | Signatures and type inference; UC requirement |
| https://mlflow.org/docs/latest/ml/model/ | MLflow Model format/flavors |
| https://mlflow.org/docs/latest/ml/mlflow-3/ | MLflow 3 storage/API migration notes |
| https://mlflow.org/docs/latest/self-hosting/architecture/backend-store/ | SQL backend requirements and database operations |
| https://mlflow.org/docs/latest/self-hosting/webhooks/ | Experimental self-hosted event automation/security |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html | Fluent log/register/registry URI APIs |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html | Registered model/version/alias/tag/copy/search APIs |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html | Generic model load and serving interface |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.webhooks.html | Webhook API when supported |

## Azure Databricks Model Serving

| Official source | Coverage/status observed during review |
|---|---|
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/glossary | Endpoint, served entity, concurrency, scale-to-zero concepts |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/manage-serving-endpoints | Endpoint CRUD/status/logs/OpenAPI/permissions; some features Preview |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/create-manage-serving-endpoints | Custom endpoint REST/SDK configuration |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/custom-model-serving-uc-logs | UC OpenTelemetry logs/spans/metrics; region-limited |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/custom-models | Supported custom model lifecycle |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/serve-multiple-models-to-serving-endpoint | Multiple entities and traffic splitting |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/model-serving-debug | Build/runtime troubleshooting |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/model-serving-limits | Quotas, payload/time/network/region limits |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/route-optimization | Route optimization and OAuth-specific access |
| https://learn.microsoft.com/en-us/azure/databricks/ai-gateway/inference-tables-serving-endpoints | AI Gateway inference tables; route-optimized support Preview |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/monitor-diagnose-endpoints | Health and quality observability |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/score-custom-model-endpoints | Request formats and direct model queries |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/express-deployments | Environment packing and faster deployment requirements |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/metrics-export-serving-endpoint | Metrics export integration |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/production-optimization | Capacity, latency, cost, and load-test practices |
| https://learn.microsoft.com/en-us/azure/databricks/machine-learning/model-serving/ | Model Serving overview |

## Guardrails

- Prefer aliases to legacy stages for new Model Registry workflows.
- Use the URI returned by `log_model()`; MLflow 3 model storage differs from older run-artifact
  assumptions.
- UC model versions require signatures and three-level naming.
- Endpoint served entities pin model version numbers; aliases do not auto-reconfigure endpoints.
- Field names and SDK dataclasses evolve; inspect current OpenAPI/SDK/CLI help.
