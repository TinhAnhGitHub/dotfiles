# Azure Databricks MLflow 3 GenAI Source Ledger

This ledger records the Azure Databricks documentation discovered by recursive web-agent
crawls on **2026-07-31**. Use it as a URL inventory and progressive-disclosure map, not as
a substitute for re-checking current pages. Databricks docs change frequently.

## URL mapping

- Azure base: `https://learn.microsoft.com/en-us/azure/databricks/`
- AWS equivalents normally preserve the suffix under
  `https://docs.databricks.com/aws/en/`.
- Upstream MLflow equivalents normally start at
  `https://mlflow.org/docs/latest/genai/`, but slugs and feature availability differ.
- For OSS behavior, prefer upstream MLflow. For managed workspace behavior, prefer the
  target cloud's Databricks page.

## 1. Top-level, getting started, and migration

| Topic | Status | Azure URL |
|---|---|---|
| MLflow 3 for GenAI | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/ |
| Getting started hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/getting-started/ |
| Connect development environment | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/getting-started/connect-environment |
| Ten-minute evaluation demo | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/getting-started/eval |
| Ten-minute human-feedback demo | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/getting-started/human-feedback |
| Genie Code for observability/evaluation | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/getting-started/genie-code |
| Tracing notebook quickstart | GA/tutorial | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/getting-started/tracing/tracing-notebook |
| Tracing IDE quickstart | GA/tutorial | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/getting-started/tracing/tracing-ide |
| Migrate MLflow 2 Agent Evaluation to MLflow 3 | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/agent-eval-migration |
| Agent Evaluation migration reference | Reference | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/agent-eval-migration-reference |

## 2. Evaluation harness, datasets, and evaluation runs

| Topic | Status | Azure URL |
|---|---|---|
| Evaluate and monitor agents hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/ |
| End-to-end evaluate/improve tutorial | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/evaluate-app |
| Evaluation harness concepts and `mlflow.genai.evaluate` | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/eval-harness |
| Evaluation runs | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/evaluation-runs |
| Evaluation dataset reference | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/eval-datasets |
| Build evaluation datasets | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/build-eval-dataset |
| Evaluation examples: data and `predict_fn` | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/eval-examples |

## 3. Scorers and built-in judges

| Topic | Status | Azure URL |
|---|---|---|
| Scorers and LLM judges overview | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/scorers |
| Built-in LLM judges catalog | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/ |
| RelevanceToQuery and RetrievalRelevance | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/is_context_relevant |
| Safety | GA/managed | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/is_safe |
| RetrievalGroundedness | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/is_grounded |
| Correctness | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/is_correct |
| RetrievalSufficiency | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/is_context_sufficient |
| Guidelines and ExpectationsGuidelines | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/guidelines |

The crawl surfaced a link ending in `is_pii_detected`, but direct verification returned
404 on 2026-07-31. Do not treat it as an active judge page without rechecking.

## 4. Custom judges, code scorers, alignment, and third parties

| Topic | Status | Azure URL |
|---|---|---|
| Custom judges overview | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/custom-judge/ |
| Create a custom judge with `make_judge` | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/custom-judge/create-custom-judge |
| Code-based scorers overview | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/custom-scorers |
| Code-scorer development workflow | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/custom-scorer-dev-workflow |
| Code-based scorer examples | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/code-based-scorer-examples |
| Code-based scorer reference | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/custom-scorer-reference |
| Align judges with human feedback | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/align-judges |
| Third-party scorers hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/third-party-scorers/ |
| DeepEval scorers | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/third-party-scorers/deep-eval |
| RAGAS scorers | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/third-party-scorers/ragas |
| Arize Phoenix scorers | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/third-party-scorers/phoenix |
| TruLens scorers | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/third-party-scorers/trulens |
| Guardrails AI scorers | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/third-party-scorers/guardrails |

## 5. Conversations and production monitoring

| Topic | Status | Azure URL |
|---|---|---|
| Evaluate conversations | Experimental | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/evaluate-conversations |
| Conversation simulation | Experimental | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/conversation-simulation |
| Production monitoring | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/production-monitoring |
| Manage production scorers | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/manage-production-scorers |
| Production-quality monitoring API concepts | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring |
| Backfill historical traces with scorers | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/backfill-scorers |
| Archive traces to Delta | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/archive-traces |
| Serverless budget policy for experiment | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/serverless-budget-policy |

## 6. Human feedback, Review App, labeling schemas, and sessions

| Topic | Status | Azure URL |
|---|---|---|
| Human feedback hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/ |
| Developer annotations | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/dev-annotations |
| Review App live app testing | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/expert-feedback/live-app-testing |
| Label existing traces | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces |
| Labeling schemas | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/concepts/labeling-schemas |
| Labeling sessions | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/concepts/labeling-sessions |

## 7. Prompt Registry, evaluation, and application lineage

| Topic | Status | Azure URL |
|---|---|---|
| Prompt Registry hub | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/prompt-version-mgmt/prompt-registry/ |
| Prompt Registry examples | Reference | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/prompt-version-mgmt/prompt-registry/examples |
| Create and edit prompts | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts |
| Use prompts in deployed apps | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/prompt-version-mgmt/prompt-registry/use-prompts-in-deployed-apps |
| Evaluate and compare prompt versions | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/prompt-version-mgmt/prompt-registry/evaluate-prompts |
| Track prompt and app versions | Beta | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/prompt-version-mgmt/prompt-registry/track-prompts-app-versions |

## 8. Tracing concepts and instrumentation

| Topic | Status | Azure URL |
|---|---|---|
| Tracing hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/ |
| Trace concepts | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/tracing-101 |
| Span concepts | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/span-concepts |
| App instrumentation hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/ |
| Automatic tracing | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/automatic |
| Manual tracing hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/ |
| `@mlflow.trace` function decorator | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator |
| `mlflow.start_span` context manager | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/span-tracing |
| Low-level client APIs | GA/advanced | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/low-level-api |
| TypeScript SDK | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/typescript-sdk |
| Add context to traces | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/add-context-to-traces |
| Context tutorial | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/add-context-to-traces-tutorial |
| Attach tags and metadata | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/attach-tags/ |
| Collect end-user feedback | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/collect-user-feedback/ |
| Tracing MCP | Check current page | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/mlflow-mcp |
| Tracing FAQ | Reference | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/faq |

## 9. Unity Catalog trace storage, migration, production, and PII

| Topic | Status | Azure URL |
|---|---|---|
| UC OpenTelemetry trace storage | GA/version-gated | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/trace-unity-catalog |
| Migrate experiment traces to UC | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/migrate-traces-to-uc |
| Migrate legacy UC trace table prefix | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/migrate-uc-trace-table-prefix |
| Production tracing on Databricks | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/prod-tracing |
| Production tracing outside Databricks | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/prod-tracing-external |
| Redact PII before export with span processors | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/redact-pii-before-export |
| Redact PII from OTel traces in UC | GA/solution | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/redact-pii-otel-traces |
| OTel PII-redaction reference architecture | Reference | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/redact-pii-otel-traces-reference |
| Unity Catalog AI service policies | Platform companion | https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/service-policies |

## 10. Observe, query, and analyze traces

| Topic | Status | Azure URL |
|---|---|---|
| Observe with traces hub | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/ |
| Trace UI | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/ui-traces |
| Query via SDK | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/query-via-sdk |
| Access trace data | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/access-trace-data |
| Query UC OTel traces with DBSQL | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/query-dbsql |
| Analyze traces examples | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/analyze-traces |
| Search-trace examples | GA | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/search-traces-examples |

## 11. Complete tracing integration catalog

The integration page is:
https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/

| Integration | Main symbol | Azure URL |
|---|---|---|
| OpenAI | `mlflow.openai.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/openai |
| LangChain | `mlflow.langchain.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/langchain |
| LangGraph | `mlflow.langchain.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/langgraph |
| Anthropic | `mlflow.anthropic.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/anthropic |
| DSPy | `mlflow.dspy.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/dspy |
| Amazon Bedrock | `mlflow.bedrock.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/bedrock |
| AutoGen | `mlflow.autogen.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/autogen |
| Databricks Foundation Models | `mlflow.openai.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/databricks-foundation-models |
| AG2 | `mlflow.ag2.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/ag2 |
| Agno | `mlflow.agno.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/agno |
| Claude Code | `mlflow autolog claude` / Anthropic autolog | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/claude-code |
| CrewAI | `mlflow.crewai.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/crewai |
| DeepSeek | OpenAI-compatible autolog | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/deepseek |
| Gemini | `mlflow.gemini.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/gemini |
| Groq | `mlflow.groq.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/groq |
| Haystack | `mlflow.haystack.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/haystack |
| Instructor | underlying provider autolog | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/instructor |
| LiteLLM | `mlflow.litellm.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/litellm |
| LlamaIndex | `mlflow.llama_index.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/llama_index |
| Mistral | `mlflow.mistral.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/mistral |
| Ollama | OpenAI-compatible autolog | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/ollama |
| OpenTelemetry export | OTEL environment configuration | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/open-telemetry |
| OpenAI Agents | `mlflow.openai.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/openai-agent |
| PydanticAI | `mlflow.pydantic_ai.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/pydantic-ai |
| Semantic Kernel | `mlflow.semantic_kernel.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/semantic-kernel |
| Smolagents | `mlflow.smolagents.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/smolagents |
| Strands Agents SDK | `mlflow.strands.autolog()` | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/strands |
| OpenAI Swarm | deprecated; OpenAI autolog | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/swarm |
| txtai | `mlflow.txtai.autolog()` extension | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/integrations/txtai |

## 12. Third-party tracing/export

| Topic | Azure URL |
|---|---|
| Export Langfuse traces to Databricks MLflow | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/third-party/langfuse |
| Set OTel semantic attributes for MLflow | https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/third-party/otel-span-attributes |

## 13. External companion references discovered

| Topic | URL |
|---|---|
| Custom Review App template | https://github.com/databricks-solutions/custom-mlflow-review-app |
| Domain-expert feedback notebook | https://docs.databricks.com/notebooks/source/mlflow3/collect-domain-expert-feedback.html |
| Create/edit prompts notebook | https://docs.databricks.com/notebooks/source/mlflow3/create-edit-prompts.html |
| Evaluate prompts notebook | https://docs.databricks.com/notebooks/source/mlflow3/evaluate-prompts.html |
| Track prompt/app versions notebook | https://docs.databricks.com/notebooks/source/mlflow3/track-prompt-app-versions.html |
| Evaluate/improve app notebook | https://docs.databricks.com/notebooks/source/mlflow3/evaluate-improve-genai-app.html |
| Azure workspace API: create trace assessment v3 | https://docs.databricks.com/api/azure/workspace/mlflowexperimenttrace/createassessmentv3 |
| Author agent model serving | https://learn.microsoft.com/en-us/azure/databricks/agents/custom-agents/model-serving/author-agent-model-serving |
| Supported Foundation Model APIs | https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-model-apis/supported-models |

## 14. Confirmed broken or absent candidate paths

| Path | Result / replacement |
|---|---|
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/scorers` | 404; use `/eval-monitor/concepts/scorers` |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/eval-monitor/concepts/judges/is_pii_detected` | 404 on direct verification |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/sessions` | No standalone page; use context/session docs |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/archiving` | No standalone page; use `/eval-monitor/archive-traces` |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/export` | No standalone page; use OTel integration/access-data docs |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/troubleshooting` | No standalone page; troubleshooting is inline plus tracing FAQ |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/third-party/` | No index page; use the two child pages above |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/monitor/` | 404; use `/eval-monitor/production-monitoring` |
| `https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/evaluate/` | 404; use `/eval-monitor/` |

## 15. Upstream references that anchor environment-neutral behavior

- https://mlflow.org/docs/latest/genai/eval-monitor/
- https://mlflow.org/docs/latest/genai/eval-monitor/quickstart/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/eval-examples/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/prompts/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/agents/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/multi-turn/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/conversation-simulation/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/alignment/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/third-party/google-adk/
- https://mlflow.org/docs/latest/genai/eval-monitor/regression-testing/
- https://mlflow.org/docs/latest/genai/eval-monitor/automatic-evaluations/
- https://mlflow.org/docs/latest/genai/eval-monitor/ai-insights/detect-issues/
- https://mlflow.org/docs/latest/genai/datasets/
- https://mlflow.org/docs/latest/genai/datasets/sdk-guide/
- https://mlflow.org/docs/latest/genai/assessments/feedback/
- https://mlflow.org/docs/latest/genai/assessments/expectations/
- https://mlflow.org/docs/latest/genai/prompt-registry/
- https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/
- https://mlflow.org/docs/latest/genai/tracing/
- https://mlflow.org/docs/latest/genai/tracing/search-traces/
- https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html
