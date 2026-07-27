# Agentic AI & Model Serving

## Agent Patterns on Databricks

Databricks supports multiple agent frameworks:

### 1. ResponsesAgent (MLflow-based)
The recommended pattern for serving agents on Databricks. Extends MLflow's pyfunc with request/response handling.

```python
import mlflow
from databricks import agents

class MyAgent(mlflow.pyfunc.PythonModel):
    def predict(self, context, model_input, params=None):
        # Get messages from the request
        messages = model_input.get("messages", [])
        # Build and execute agent logic
        response = self.agent.invoke(messages)
        return response

# Log and deploy
with mlflow.start_run():
    model_info = mlflow.pyfunc.log_model(
        python_model=MyAgent(),
        artifact_path="agent",
        pip_requirements=["databricks-agents", "langchain", ...],
        resources=[DatabricksServingEndpoint(endpoint_name="databricks-claude-sonnet-4-5")],
        model_config={...}
    )

    agents.deploy(
        model_name="main.default.my_agent",
        model_version=int(model_info.registered_model_version.version),
        endpoint_name="my-agent-endpoint",
        scale_to_zero=True
    )
```

### 2. LangGraph Agent
Full control over agent reasoning loops with tool execution:

```python
from databricks_langchain import ChatDatabricks
from langchain.agents import create_agent
from mlflow.langchain import autolog

llm = ChatDatabricks(model="databricks-claude-sonnet-4-5")

agent = create_agent(
    llm,
    tools=[sql_tool, visualization_tool, python_tool],
    system_prompt="You are a data analyst...",
    checkpointer=memory  # optional: persistence between turns
)

# Deploy via ResponsesAgent wrapper
autolog()
```

### 3. AI Functions (SQL-based)
Call foundation models directly from SQL for batch inference:

```sql
SELECT ai_query("databricks-claude-sonnet-4-5", "Summarize: " || review_text) AS summary
FROM main.default.reviews
LIMIT 100
```

### 4. Function Calling / Tool Use
Available via `tools` parameter in chat/completions. Supported by most foundation models:

```python
from openai import OpenAI

client = OpenAI(
    api_key="dapi-your-token",
    base_url="https://workspace.cloud.databricks.com/serving-endpoints"
)

response = client.chat.completions.create(
    model="databricks-claude-sonnet-4-5",
    messages=[{"role": "user", "content": "What's in my table?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Run a SQL query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        }
    }],
    tool_choice="auto"  # or "required", "none", or specific function
)
```

**Tool Use Limitations:**
- Max 32 functions in `tools` array
- Max 16 keys in JSON schema
- No `pattern`, `anyOf/oneOf/allOf`, `$ref` in schema
- No parallel function calling
- Optimized for single-turn (multi-turn best with Claude)

## Model Serving Endpoints

Three categories:

### A. Foundation Models (Databricks-Hosted)
Pay-per-token or provisioned throughput. Endpoint names use `databricks-` prefix:

| Provider | Key Models |
|----------|-----------|
| **OpenAI** | `databricks-gpt-5-5-pro`, `databricks-gpt-5-4`, `databricks-gpt-5-mini`, `databricks-gpt-oss-20b` |
| **Anthropic Claude** | `databricks-claude-sonnet-4-6`, `databricks-claude-haiku-4-5`, `databricks-claude-opus-4-7` |
| **Google Gemini** | `databricks-gemini-3-1-pro`, `databricks-gemini-3-flash`, `databricks-gemini-2-5-pro` |
| **Meta Llama** | `databricks-llama-4-maverick`, `databricks-meta-llama-3-3-70b-instruct`, `databricks-meta-llama-3-1-405b-instruct` |
| **Embeddings** | `databricks-gte-large-en`, `databricks-bge-large-en` |

**Provisioned throughput**: Performance guarantees for production, supports fine-tuned models.

### B. Custom Models
Python models packaged with MLflow (any framework):

```python
# Create via SDK
w.serving_endpoints.create(
    name="my-custom-endpoint",
    config={
        "served_entities": [{
            "entity_name": "main.default.my_model",
            "entity_version": "1",
            "scale_to_zero_enabled": True,
            "workload_size": "Small"  # Small(0-4), Medium(8-16), Large(16-64)
        }]
    }
)
```

**GPU types:** `GPU_SMALL` (1xT4/16GB), `GPU_MEDIUM` (1xA10G/24GB), `MULTIGPU_MEDIUM` (4xA10G/96GB)

### C. External Models
Proxy to third-party providers with centralized credential management:

```python
import mlflow.deployments

client = mlflow.deployments.get_deploy_client("databricks")
client.create_endpoint(
    name="openai-endpoint",
    config={
        "served_entities": [{
            "external_model": {
                "name": "gpt-4o",
                "provider": "openai",
                "task": "llm/v1/chat",
                "openai_config": {
                    "openai_api_key": "{{secrets/my-scope/openai-key}}"
                }
            }
        }]
    }
)
```

**Supported providers:** `openai` (direct + Azure + Entra ID), `anthropic`, `cohere`, `amazon-bedrock` (Anthropic/Cohere/AI21Labs/Amazon), `google-cloud-vertex-ai`, `ai21labs`, `custom` (OpenAI-compatible), `databricks-model-serving`.

**Provider auth patterns:**
- OpenAI/Azure: `openai_api_key` or `openai_api_key_plaintext`
- Anthropic: `anthropic_api_key`
- Amazon Bedrock: `aws_region` + (`uc_service_credential_name` | `instance_profile_arn` | `aws_access_key_id`+`aws_secret_access_key`) + `bedrock_provider`
- Google Vertex AI: `private_key` + `region` + `project_id`
- Custom: `custom_provider_url` + `bearer_token_auth` or `api_key_auth`

## AI Gateway (Governance Layer)

Configured per endpoint. Feature availability varies by model type:

| Feature | External Models | Pay-per-Token | Prov. Throughput | Agents | Custom |
|---------|:---:|:---:|:---:|:---:|:---:|
| Usage tracking | Yes | Yes | Yes | No | Yes |
| Payload logging | Yes | Yes | Yes | Yes | Yes |
| Rate limiting | Yes | Yes | Yes | No | Yes |
| AI Guardrails | Yes | Yes | Yes | No | No |
| Fallbacks | Yes | No | No | No | No |
| Traffic splitting | Yes | No | Yes | No | Yes |

### Rate Limiting
- Query-based (QPM) and token-based (TPM)
- Levels: Endpoint-wide, per-user, per-service-principal, per-group
- Max 20 rate limits per endpoint, up to 5 group-specific limits

### AI Guardrails
- **Safety filtering**: Meta Llama Guard 2-8B for violence, self-harm, hate speech
- **PII detection**: Microsoft Presidio for credit cards, emails, phones, bank accounts, SSN (primarily US categories)
- Modes: Block or Mask
- Not supported for embeddings or streaming
- Batch size with guardrails limited to 16

### Usage Tracking
- Logs to `system.serving.endpoint_usage` system table
- Tracks tokens, character counts, request times, status codes, requester identity
- `usage_context` map for cost attribution: `end_user_to_charge`, `project`, `a_b_test_group`

### Payload Logging (Inference Tables)
- Requests/responses logged to Delta tables in Unity Catalog
- Payloads > 1 MiB not logged
- Streaming supported (response aggregates all chunks)

## Serving Endpoints — CLI Commands

### Create & Manage

```bash
# Standard endpoint
databricks serving-endpoints create --json @endpoint.json
databricks serving-endpoints get <endpoint-name>
databricks serving-endpoints list
databricks serving-endpoints delete <endpoint-name>

# Provisioned throughput endpoint
databricks serving-endpoints create-provisioned-throughput-endpoint --json @pt-ep.json
databricks serving-endpoints update-provisioned-throughput-endpoint-config <ep-name> --json @pt-update.json

# Update config (served entities, traffic split, scale)
databricks serving-endpoints update-config <endpoint-name> --json @config.json
```

### Operate

```bash
# Query
databricks serving-endpoints query <endpoint-name> \
  --json '{"messages": [{"role": "user", "content": "Hello"}]}'

# Logs (for custom model deployments)
databricks serving-endpoints logs <endpoint-name>
databricks serving-endpoints build-logs <endpoint-name> --served-model-name <entity>

# Metrics & schema
databricks serving-endpoints export-metrics <endpoint-name>
databricks serving-endpoints get-open-api <endpoint-name>    # OpenAPI spec

# Rate limits
databricks serving-endpoints put <endpoint-name> \
  --json '{"rate_limits": [{"key": "user/abc", "calls": 100, "renewal_period": "1 minute"}]}'
```

### AI Gateway

```bash
# Configure AI Gateway features (rate limiting, guardrails, payload logging)
databricks serving-endpoints put-ai-gateway <endpoint-name> --json '{
  "guardrails": {
    "input_safety_filters": [...],
    "output_safety_filters": [...],
    "pii_filters": [
      {"filter_type": "BLOCK", "behavior": "BLOCK_ALL"},
      {"filter_type": "EMAIL", "behavior": "MASK"}
    ]
  },
  "usage_tracking": {"enabled": true},
  "payload_logging": {"enabled": true},
  "rate_limits": [
    {"calls": 1000, "renewal_period": "minute", "key": "endpoint"},
    {"calls": 100, "renewal_period": "minute", "key": "user/default"}
  ]
}'

# Notification settings (email, webhook)
databricks serving-endpoints update-notifications <endpoint-name> \
  --json '{"notifications": [{"email": "team@example.com"}]}'

# Tags
databricks serving-endpoints patch <endpoint-name> \
  --json '{"tags": [{"key": "env", "value": "prod"}]}'
```

### Permission Management

```bash
databricks serving-endpoints get-permission-levels <endpoint-name>
databricks serving-endpoints get-permissions <endpoint-name>
databricks serving-endpoints set-permissions <endpoint-name> --json @perms.json
```

## Experiments (MLflow Tracking) — CLI Commands

```bash
# Create / manage experiments
databricks experiments create-experiment --name "/Users/me/my-experiment"
databricks experiments list-experiments
databricks experiments get-experiment <exp-id>
databricks experiments get-by-name --name "/Users/me/my-experiment"
databricks experiments delete-experiment <exp-id>
databricks experiments restore-experiment <exp-id>

# Runs
databricks experiments create-run --experiment-id <exp-id>
databricks experiments get-run <run-id>
databricks experiments search-runs --experiment-ids <exp-id>
databricks experiments list-artifacts --run-id <run-id>
databricks experiments delete-run <run-id>
databricks experiments restore-run <run-id>
databricks experiments delete-runs --experiment-id <exp-id> --max-timestamp-millis <ts>
databricks experiments restore-runs --experiment-id <exp-id> --min-timestamp-millis <ts>

# Log data
databricks experiments log-metric --run-id <run-id> --key "accuracy" --value 0.95
databricks experiments log-param --run-id <run-id> --key "learning_rate" --value "0.001"
databricks experiments log-batch --run-id <run-id> \
  --json '{"metrics": [{"key": "f1", "value": 0.92}]}'
databricks experiments log-model --run-id <run-id> --model-json '{"artifact_path":"model"}'
databricks experiments log-inputs --run-id <run-id> --datasets ...
databricks experiments log-outputs --run-id <run-id> --outputs ...
databricks experiments set-tag --run-id <run-id> --key "env" --value "prod"
databricks experiments set-experiment-tag --experiment-id <exp-id> --key "team" --value "ml"
databricks experiments get-history --run-id <run-id> --metric-key "accuracy"

# Logged models (within runs)
databricks experiments create-logged-model --run-id <run-id> --json @model.json
databricks experiments get-logged-model <logged-model-id>
databricks experiments search-logged-models
databricks experiments finalize-logged-model <logged-model-id>
databricks experiments delete-logged-model <logged-model-id>
databricks experiments log-logged-model-params --logged-model-id <id> --json @params.json
```

## Model Registry (Legacy Workspace) — CLI Commands

Databricks recommends Unity Catalog models (`registered-models` / `model-versions`) instead.

```bash
# Models
databricks model-registry create-model --name "my_model"
databricks model-registry get-model --name "my_model"
databricks model-registry list-models
databricks model-registry search-models --max-results 100
databricks model-registry rename-model --name "my_model" --new-name "renamed_model"
databricks model-registry delete-model --name "my_model"

# Model versions
databricks model-registry create-model-version --name "my_model" --source "dbfs:/artifacts/model"
databricks model-registry get-model-version --name "my_model" --version 1
databricks model-registry get-latest-versions --name "my_model" --stages "Production"
databricks model-registry get-model-version-download-uri --name "my_model" --version 1
databricks model-registry search-model-versions
databricks model-registry update-model-version --name "my_model" --version 1 --description "v1"
databricks model-registry delete-model-version --name "my_model" --version 1

# Stage transitions
databricks model-registry transition-stage --name "my_model" --version 1 --stage "Staging"
databricks model-registry approve-transition-request --name "my_model" --version 1 --stage "Production"
databricks model-registry reject-transition-request --name "my_model" --version 1 --stage "Staging"
databricks model-registry list-transition-requests --name "my_model" --version 1

# Tags
databricks model-registry set-model-tag --name "my_model" --key "env" --value "prod"
databricks model-registry set-model-version-tag --name "my_model" --version 1 --key "accuracy" --value "0.95"
databricks model-registry delete-model-tag --name "my_model" --key "env"
databricks model-registry delete-model-version-tag --name "my_model" --version 1 --key "accuracy"

# Comments
databricks model-registry create-comment --name "my_model" --version 1 --comment "Ready for review"
databricks model-registry update-comment <comment-id> --comment "Approved after testing"
databricks model-registry delete-comment <comment-id>

# Webhooks
databricks model-registry create-webhook --event "MODEL_VERSION_TRANSITION_REQUEST_CREATED" --url "https://..."
databricks model-registry list-webhooks
databricks model-registry update-webhook <webhook-id> --url "https://..."
databricks model-registry delete-webhook <webhook-id>
databricks model-registry test-registry-webhook <webhook-id>
```

## Vector Search — CLI Commands

```bash
# Endpoints (compute for vector index hosting)
databricks vector-search-endpoints create-endpoint --name "my-vs-endpoint" --endpoint-type "STANDARD"
databricks vector-search-endpoints get-endpoint <endpoint-name>
databricks vector-search-endpoints list-endpoints
databricks vector-search-endpoints patch-endpoint <endpoint-name> --json @patch.json
databricks vector-search-endpoints delete-endpoint <endpoint-name>
databricks vector-search-endpoints retrieve-user-visible-metrics <endpoint-name>
databricks vector-search-endpoints update-endpoint-budget-policy <endpoint-name> --json @policy.json

# Indexes
databricks vector-search-indexes create-index --json '{
  "name": "main.default.my_index",
  "endpoint_name": "my-vs-endpoint",
  "primary_key": "id",
  "index_type": "DELTA_SYNC",
  "delta_sync_index_spec": {
    "source_table": "main.default.my_table",
    "embedding_vector_columns": [{
      "embedding_model_endpoint_name": "databricks-gte-large-en",
      "embedding_source_column": "content"
    }]
  }
}'
databricks vector-search-indexes get-index <index-name>
databricks vector-search-indexes list-indexes --endpoint-name <ep-name>
databricks vector-search-indexes query-index <index-name> --json '{"columns": [{"name": "content"}], "query_vector": [0.1, 0.2, ...]}'
databricks vector-search-indexes query-next-page --page-token <token>
databricks vector-search-indexes scan-index <index-name> --json @scan.json
databricks vector-search-indexes sync-index <index-name>
databricks vector-search-indexes upsert-data-vector-index <index-name> --json @data.json
databricks vector-search-indexes delete-data-vector-index <index-name> --json '{"primary_key": ["id_123"]}'
databricks vector-search-indexes delete-index <index-name>
```

**Breaking change (CLI v0.299.2)**: `min_qps` renamed to `target_qps` in both DABs config and CLI flags. Update all existing bundle YAML and scripts.

## Clean Rooms — CLI Commands

```bash
# Clean room management
databricks clean-rooms create --json @cleanroom.json
databricks clean-rooms get <cr-id>
databricks clean-rooms update <cr-id> --json @patch.json
databricks clean-rooms delete <cr-id>

# Assets (tables, volumes, notebooks shared within the clean room)
databricks clean-room-assets create --clean-room-id <cr-id> --json @asset.json
databricks clean-room-assets get --clean-room-id <cr-id> --asset-id <aid>
databricks clean-room-asset-revisions list --clean-room-id <cr-id> --asset-id <aid>

# Task runs (notebook execution in clean room)
databricks clean-room-task-runs list --clean-room-id <cr-id>
databricks clean-room-task-runs get --clean-room-id <cr-id> --run-id <rid>

# Auto-approval rules
databricks clean-room-auto-approval-rules create --clean-room-id <cr-id> --json @rule.json
```

## Querying Endpoints

```python
# Databricks OpenAI client (inside Databricks)
from databricks_openai import DatabricksOpenAI
client = DatabricksOpenAI()
response = client.chat.completions.create(
    model="databricks-claude-sonnet-4-5",  # or custom endpoint name
    messages=[{"role": "user", "content": "What is Databricks?"}],
    max_tokens=256
)

# Standard OpenAI client (outside Databricks)
from openai import OpenAI
client = OpenAI(
    api_key="dapi-your-token",
    base_url="https://workspace.cloud.databricks.com/serving-endpoints"
)

# REST API
import requests
headers = {"Authorization": "Bearer dapi..."}
resp = requests.post(
    "https://workspace.cloud.databricks.com/serving-endpoints/my-endpoint/invocations",
    headers=headers,
    json={"messages": [{"role": "user", "content": "Hello"}]}
)

# LangChain
from databricks_langchain import ChatDatabricks
llm = ChatDatabricks(model="databricks-claude-sonnet-4-5")

# MLflow Deployments SDK
client = mlflow.deployments.get_deploy_client("databricks")
response = client.predict(endpoint="my-endpoint", inputs={"messages": [...]})
```

## Capabilities

### Structured Outputs
OpenAI-compatible, available via Foundation Model APIs. For batch conversion of unstructured to structured data.

### Prompt Caching
Supported for Databricks-hosted Claude models:
```json
{"content": [{"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}}]}
```
Caches text, thinking/reasoning, image (base64), and tool content.

### Vision
Supported by GPT-5.x, Gemini, Claude, Llama 4 Maverick, Gemma 3. For object detection, image classification, document understanding.

### Streaming
`stream: true` in chat/completions. Supported by OpenAI, Anthropic, Cohere, Amazon Bedrock (Anthropic). All chunks in OpenAI-compatible `choices[].delta` format.

### API Endpoint Naming
- `databricks-` prefix reserved for Databricks-hosted models
- Endpoint creator identity permanently tied to endpoint (must delete/recreate to change)

## Gotchas

1. **Region requirements**: Not all models available in all regions. Google Gemini 3 and some GPT-5.x models require cross-geography routing.
2. **Cold start**: Scale-to-zero adds latency. Not recommended for production.
3. **Model retirement**: Databricks retires older foundation models. Check availability before building dependencies.
4. **Payload limits**: 16 MB for custom models, 4 MB for agents.
5. **Request timeout**: 597 seconds per request.
6. **Max endpoints**: 1000 per workspace. Max 50 create/update ops per 5 minutes.
7. **Streaming + guardrails**: Output guardrails not supported during streaming.
8. **PII scope**: Detection primarily US categories (credit cards, SSNs, etc.).
9. **Embeddings batch**: Limited to 16 with guardrails enabled.
10. **Vector search `min_qps` → `target_qps`** breaking change in CLI v0.299.2 — update all bundle YAML and scripts referencing the old field.
11. **Endpoint creator identity** is permanently tied to the endpoint — to change it, delete and recreate the endpoint.
12. **`databricks-` prefix** is reserved for Databricks-hosted foundation models; custom endpoints cannot use it.
13. **Model Registry (workspace)** is deprecated — use Unity Catalog `registered-models` / `model-versions` for new deployments.
14. **Streaming + guardrails** are incompatible — disable guardrails when streaming is required.
