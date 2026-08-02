# Agent Model Serving Endpoint Configuration — SDK & API Reference

## Overview

This reference covers the full infrastructure configuration for agent and model serving endpoints:
- Creating/updating/deleting endpoints via SDK and CLI
- AI Gateway configuration (rate limits, guardrails, inference tables, fallbacks)
- Permission management (get/set/update)
- Provisioned throughput endpoints
- Registered model creation and alias management
- Agent app deployment and lifecycle

---

## Python SDK Quick Reference

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import (
    ServedEntityInput, EndpointCoreConfigInput, TrafficConfig,
    AiGatewayConfig, AiGatewayRateLimit, AiGatewayRateLimitKey,
    AiGatewayRateLimitRenewalPeriod, AiGatewayGuardrails,
    AiGatewayGuardrailParameters, AiGatewayGuardrailPiiBehavior,
    AiGatewayGuardrailPiiBehaviorBehavior,
    AiGatewayInferenceTableConfig, FallbackConfig
)
from databricks.sdk.service.catalog import RegisteredModelAlias
from databricks.sdk.service.iam import AccessControlRequest, PermissionLevel

w = WorkspaceClient()
```

---

## Full SDK Method Reference

**Class:** `databricks.sdk.service.serving.ServingEndpointsExt`
**Access:** `w.serving_endpoints`

### CRUD Operations

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `create` | `(name, *, ai_gateway, budget_policy_id, config, description, email_notifications, rate_limits, route_optimized, tags)` | `Wait[ServingEndpointDetailed]` | Create endpoint, returns waiter |
| `create_and_wait` | `(name, *, ..., timeout=20min)` | `ServingEndpointDetailed` | Create + block until ready |
| `create_provisioned_throughput_endpoint` | `(name, config, *, ...)` | `Wait[ServingEndpointDetailed]` | Create PT endpoint |
| `create_provisioned_throughput_endpoint_and_wait` | `(name, config, *, ..., timeout=20min)` | `ServingEndpointDetailed` | Create PT + block |
| `get` | `(name)` | `ServingEndpointDetailed` | Get endpoint details |
| `list` | `()` | `Iterator[ServingEndpoint]` | List all endpoints |
| `update_config` | `(name, *, auto_capture_config, served_entities, served_models, traffic_config)` | `Wait[ServingEndpointDetailed]` | Update config (zero-downtime) |
| `update_config_and_wait` | `(name, *, ..., timeout=20min)` | `ServingEndpointDetailed` | Update config + block |
| `update_provisioned_throughput_endpoint_config` | `(name, config)` | `Wait[ServingEndpointDetailed]` | Update PT config |
| `update_provisioned_throughput_endpoint_config_and_wait` | `(name, config, timeout=20min)` | `ServingEndpointDetailed` | Update PT + block |
| `delete` | `(name)` | `None` | Delete endpoint |

### AI Gateway

| Method | Signature | Returns |
|--------|-----------|---------|
| `put_ai_gateway` | `(name, *, fallback_config, guardrails, inference_table_config, rate_limits, usage_tracking_config)` | `PutAiGatewayResponse` |

### Permissions

| Method | Signature | Returns |
|--------|-----------|---------|
| `get_permission_levels` | `(serving_endpoint_id)` | `GetServingEndpointPermissionLevelsResponse` |
| `get_permissions` | `(serving_endpoint_id)` | `ServingEndpointPermissions` |
| `set_permissions` | `(serving_endpoint_id, *, access_control_list)` | `ServingEndpointPermissions` |
| `update_permissions` | `(serving_endpoint_id, *, access_control_list)` | `ServingEndpointPermissions` |

### Querying

| Method | Signature | Returns |
|--------|-----------|---------|
| `query` | `(name, *, client_request_id, dataframe_records, dataframe_split, extra_params, input, inputs, instances, max_tokens, messages, n, prompt, stop, stream, temperature, usage_context)` | `QueryEndpointResponse` |
| `get_open_api` | `(name)` | `GetOpenApiResponse` |
| `get_open_ai_client` | `(**kwargs)` | `OpenAI` (deprecated — use `databricks-openai`) |
| `get_langchain_chat_open_ai_client` | `(model)` | `Any` (deprecated — use `databricks-langchain`) |

### Logs & Metrics

| Method | Signature | Returns |
|--------|-----------|---------|
| `build_logs` | `(name, served_model_name)` | `BuildLogsResponse` |
| `logs` | `(name, served_model_name)` | `ServerLogsResponse` |
| `export_metrics` | `(name)` | `ExportMetricsResponse` |

### Tags & Notifications

| Method | Signature | Returns |
|--------|-----------|---------|
| `patch` | `(name, *, add_tags, delete_tags)` | `EndpointTags` |
| `update_notifications` | `(name, *, email_notifications)` | `UpdateInferenceEndpointNotificationsResponse` |
| `put` | `(name, *, rate_limits)` | `PutResponse` (deprecated — use `put_ai_gateway`) |

### Experimental

| Method | Signature | Returns |
|--------|-----------|---------|
| `http_request` | `(conn, method, path, *, headers, json, params)` | `Response` — make external service calls via UC Connection |

### Wait Helpers (used internally by `_and_wait` variants)

| Method | Signature |
|--------|-----------|
| `wait_get_serving_endpoint_not_updating` | `(name, timeout=20min, callback=None)` → `ServingEndpointDetailed` |

Polls `get()` until `state.config_update == NOT_UPDATING`. Default timeout is **20 minutes**.

---

## Complete Dataclass Reference

### Core Config Dataclasses

#### `EndpointCoreConfigInput`
| Field | Type | Required |
|-------|------|----------|
| `served_entities` | `Optional[List[ServedEntityInput]]` | No |
| `served_models` | `Optional[List[ServedModelInput]]` | No (deprecated) |
| `traffic_config` | `Optional[TrafficConfig]` | No |
| `auto_capture_config` | `Optional[AutoCaptureConfigInput]` | No (deprecated) |

#### `ServedEntityInput`
| Field | Type | Description |
|-------|------|-------------|
| `entity_name` | `Optional[str]` | UC model name (e.g., `catalog.schema.model`) |
| `entity_version` | `Optional[str]` | Model version number |
| `name` | `Optional[str]` | Served entity name (auto-generated if not set) |
| `workload_size` | `Optional[str]` | `"Small"`, `"Medium"`, `"Large"` |
| `workload_type` | `Optional[ServingModelWorkloadType]` | `CPU`, `GPU_SMALL`, `GPU_MEDIUM`, `GPU_LARGE`, `GPU_XLARGE`, `MULTIGPU_MEDIUM` |
| `scale_to_zero_enabled` | `Optional[bool]` | Enable scale-to-zero |
| `burst_scaling_enabled` | `Optional[bool]` | Enable burst scaling |
| `instance_profile_arn` | `Optional[str]` | AWS instance profile |
| `environment_vars` | `Optional[Dict[str, str]]` | Environment variables |
| `min_provisioned_concurrency` | `Optional[int]` | Min provisioned concurrency |
| `max_provisioned_concurrency` | `Optional[int]` | Max provisioned concurrency |
| `min_provisioned_throughput` | `Optional[int]` | Min provisioned throughput |
| `max_provisioned_throughput` | `Optional[int]` | Max provisioned throughput |
| `provisioned_model_units` | `Optional[int]` | PT model units |
| `external_model` | `Optional[ExternalModel]` | External model reference |

#### `TrafficConfig`
| Field | Type | Description |
|-------|------|-------------|
| `routes` | `Optional[List[Route]]` | Traffic routing rules |

#### `Route`
| Field | Type | Required |
|-------|------|----------|
| `traffic_percentage` | `int` | Yes |
| `served_model_name` | `Optional[str]` | No (deprecated) |
| `served_entity_name` | `Optional[str]` | No |

#### `ServingEndpointDetailed`
| Field | Type | Description |
|-------|------|-------------|
| `name` | `Optional[str]` | Endpoint name |
| `id` | `Optional[str]` | Endpoint ID (hex string) |
| `state` | `Optional[EndpointState]` | `config_update` + `ready` status |
| `config` | `Optional[EndpointCoreConfigOutput]` | Current config |
| `pending_config` | `Optional[EndpointPendingConfig]` | Pending config (during update) |
| `tags` | `Optional[List[EndpointTag]]` | Endpoint tags |
| `ai_gateway` | `Optional[AiGatewayConfig]` | AI Gateway config |
| `email_notifications` | `Optional[EmailNotifications]` | Notification settings |
| `route_optimized` | `Optional[bool]` | Route optimization enabled |
| `endpoint_url` | `Optional[str]` | Endpoint URL |
| `permission_level` | `Optional[ServingEndpointDetailedPermissionLevel]` | `CAN_MANAGE`, `CAN_QUERY`, `CAN_VIEW` |
| `budget_policy_id` | `Optional[str]` | Budget policy |
| `task` | `Optional[str]` | Task type |

#### `EndpointState`
| Field | Type | Values |
|-------|------|--------|
| `config_update` | `Optional[EndpointStateConfigUpdate]` | `IN_PROGRESS`, `NOT_UPDATING`, `UPDATE_CANCELED`, `UPDATE_FAILED` |
| `ready` | `Optional[EndpointStateReady]` | `NOT_READY`, `READY` |

### AI Gateway Dataclasses

#### `AiGatewayConfig`
| Field | Type | Description |
|-------|------|-------------|
| `fallback_config` | `Optional[FallbackConfig]` | Traffic fallback for HA |
| `guardrails` | `Optional[AiGatewayGuardrails]` | AI Guardrails (PII, content mod) |
| `inference_table_config` | `Optional[AiGatewayInferenceTableConfig]` | Payload logging |
| `rate_limits` | `Optional[List[AiGatewayRateLimit]]` | Rate limits |
| `usage_tracking_config` | `Optional[AiGatewayUsageTrackingConfig]` | Usage tracking |

#### `AiGatewayRateLimit`
| Field | Type | Values |
|-------|------|--------|
| `renewal_period` | `AiGatewayRateLimitRenewalPeriod` | `MINUTE` |
| `calls` | `Optional[int]` | Max calls per renewal period |
| `key` | `Optional[AiGatewayRateLimitKey]` | `ENDPOINT`, `USER`, `SERVICE_PRINCIPAL`, `USER_GROUP` |
| `principal` | `Optional[str]` | Principal for user/group level |
| `tokens` | `Optional[int]` | Max tokens per renewal period |

#### `AiGatewayGuardrails`
| Field | Type | Description |
|-------|------|-------------|
| `input` | `Optional[AiGatewayGuardrailParameters]` | Input guardrails |
| `output` | `Optional[AiGatewayGuardrailParameters]` | Output guardrails |

#### `AiGatewayInferenceTableConfig`
| Field | Type |
|-------|------|
| `catalog_name` | `Optional[str]` |
| `schema_name` | `Optional[str]` |
| `table_name_prefix` | `Optional[str]` |
| `enabled` | `Optional[bool]` |

### External Model Configs

#### `ExternalModel`
| Field | Type | Description |
|-------|------|-------------|
| `provider` | `ExternalModelProvider` | **Required** — see enum below |
| `name` | `str` | **Required** — model name |
| `task` | `str` | **Required** — e.g., `llm/v1/chat` |
| `openai_config` | `Optional[OpenAiConfig]` | OpenAI provider config |
| `anthropic_config` | `Optional[AnthropicConfig]` | Anthropic provider config |
| `amazon_bedrock_config` | `Optional[AmazonBedrockConfig]` | Bedrock provider config |
| `google_cloud_vertex_ai_config` | `Optional[GoogleCloudVertexAiConfig]` | Vertex AI config |
| `databricks_model_serving_config` | `Optional[DatabricksModelServingConfig]` | Cross-workspace config |
| `ai21labs_config` | `Optional[Ai21LabsConfig]` | AI21 Labs config |
| `cohere_config` | `Optional[CohereConfig]` | Cohere config |
| `custom_provider_config` | `Optional[CustomProviderConfig]` | Custom provider |
| `palm_config` | `Optional[PaLmConfig]` | PaLM config |

**`ExternalModelProvider` enum**: `AI21LABS`, `AMAZON_BEDROCK`, `ANTHROPIC`, `COHERE`, `CUSTOM`, `DATABRICKS_MODEL_SERVING`, `GOOGLE_CLOUD_VERTEX_AI`, `OPENAI`, `PALM`

### PT (Provisioned Throughput) Dataclasses

#### `PtEndpointCoreConfig`
| Field | Type |
|-------|------|
| `served_entities` | `Optional[List[PtServedModel]]` |
| `traffic_config` | `Optional[TrafficConfig]` |

#### `PtServedModel`
| Field | Type | Required |
|-------|------|----------|
| `entity_name` | `str` | Yes |
| `provisioned_model_units` | `int` | Yes |
| `name` | `Optional[str]` | No |
| `entity_version` | `Optional[str]` | No |
| `burst_scaling_enabled` | `Optional[bool]` | No |

### Permission Dataclasses

| Class | Key Fields |
|-------|-----------|
| `ServingEndpointPermissionLevel` | Enum: `CAN_MANAGE`, `CAN_QUERY`, `CAN_VIEW` |
| `ServingEndpointPermissions` | `access_control_list`, `object_id`, `object_type` |
| `ServingEndpointAccessControlRequest` | `group_name`, `user_name`, `service_principal_name`, `permission_level` |

---

## Endpoint CRUD with SDK

### Create Endpoint

```python
endpoint = w.serving_endpoints.create_and_wait(
    name="my-agent-endpoint",
    config=EndpointCoreConfigInput(
        served_entities=[
            ServedEntityInput(
                entity_name="catalog.schema.my_model",
                entity_version=1,
                workload_size="Small",
                scale_to_zero_enabled=False,
                min_provisioned_throughput=10,
                max_provisioned_throughput=100,
            )
        ],
        traffic_config=TrafficConfig(
            routes=[
                {"served_model_name": "my_model-1", "traffic_percentage": 100}
            ]
        ),
    ),
    route_optimized=True,
    tags=[{"key": "project", "value": "my-app"}],
    description="Production agent endpoint",
)
print(f"Endpoint ready: {endpoint.state.ready}")
```

### Get Endpoint Details

```python
endpoint = w.serving_endpoints.get(name="my-agent-endpoint")
print(f"State: {endpoint.state.ready}")
print(f"Config: {endpoint.config}")
# Check served entities
for entity in endpoint.config.served_entities:
    print(f"  Entity: {entity.name}, version={entity.entity_version}")
# Check traffic config
for route in endpoint.config.traffic_config.routes:
    print(f"  Route: {route.served_model_name} -> {route.traffic_percentage}%")
```

### Update Endpoint Config (zero-downtime version swap)

```python
w.serving_endpoints.update_config_and_wait(
    name="my-agent-endpoint",
    served_entities=[
        ServedEntityInput(
            entity_name="catalog.schema.my_model",
            entity_version=2,  # new version
            workload_size="Small",
            scale_to_zero_enabled=False,
        )
    ],
    traffic_config=TrafficConfig(
        routes=[
            {"served_model_name": "my_model-2", "traffic_percentage": 100}
        ]
    ),
)
```

### Canary Deployment with Traffic Split

```python
w.serving_endpoints.update_config_and_wait(
    name="my-agent-endpoint",
    served_entities=[
        ServedEntityInput(
            entity_name="catalog.schema.my_model",
            entity_version=1,  # current prod
            workload_size="Small",
            scale_to_zero_enabled=False,
        ),
        ServedEntityInput(
            entity_name="catalog.schema.my_model",
            entity_version=2,  # challenger
            workload_size="Small",
            scale_to_zero_enabled=False,
        ),
    ],
    traffic_config=TrafficConfig(
        routes=[
            {"served_model_name": "my_model-1", "traffic_percentage": 90},
            {"served_model_name": "my_model-2", "traffic_percentage": 10},
        ]
    ),
)
```

### Delete Endpoint

```python
w.serving_endpoints.delete(name="my-agent-endpoint")
```

---

## AI Gateway Configuration

Configure advanced features on serving endpoints:

```python
w.serving_endpoints.put_ai_gateway(
    name="my-agent-endpoint",
    rate_limits=[
        AiGatewayRateLimit(
            key=AiGatewayRateLimitKey.USER,
            principal="user_123",
            calls=100,
            renewal_period=AiGatewayRateLimitRenewalPeriod.MINUTE,
        )
    ],
    guardrails=AiGatewayGuardrails(
        input=AiGatewayGuardrailParameters(
            safety=True,
            pii=AiGatewayGuardrailPiiBehavior(
                behavior=AiGatewayGuardrailPiiBehaviorBehavior.MASK,
            ),
        ),
        output=AiGatewayGuardrailParameters(
            safety=True,
            pii=AiGatewayGuardrailPiiBehavior(
                behavior=AiGatewayGuardrailPiiBehaviorBehavior.MASK,
            ),
        ),
    ),
    inference_table_config=AiGatewayInferenceTableConfig(
        catalog_name="main",
        schema_name="monitoring",
        table_name_prefix="agent_inference",
        enabled=True,
    ),
    fallback_config=FallbackConfig(
        enabled=True,
        fallback_models=[
            {"entity_name": "catalog.schema.model_backup", "entity_version": 1}
        ],
    ),
)
```

### AI Gateway Features Table

| Feature | SDK Parameter | Description |
|---------|--------------|-------------|
| **Usage tracking** | `usage_tracking_config` | Enabled by default. Logs to `system.ai_gateway.usage` |
| **Inference tables** | `inference_table_config` | Log requests/responses to UC Delta tables |
| **Rate limits** | `rate_limits` | QPM or TPM at endpoint/user/group level |
| **Guardrails** | `guardrails` | PII detection, content moderation (dry run available) |
| **Fallbacks** | `fallback_config` | Auto-fallback to backup models on 429/5XX |
| **Traffic splitting** | Via `update_config` | A/B test across model versions |

---

## Permissions Management

### Via SDK (Serving Endpoints)

For `serving-endpoints`, use the dedicated permission methods:

```python
# Get permission levels available
levels = w.serving_endpoints.get_permission_levels(
    serving_endpoint_id="<endpoint-id>"  # hex string from get()
)
for level in levels.permission_levels:
    print(f"Level: {level.permission_level}, description: {level.description}")

# Get current permissions
perms = w.serving_endpoints.get_permissions(
    serving_endpoint_id="<endpoint-id>"
)
for entry in perms.access_control_list:
    print(f"  User/Group: {entry.user_name or entry.group_name}, level={entry.permission_level}")

# Set permissions (replaces all)
w.serving_endpoints.set_permissions(
    serving_endpoint_id="<endpoint-id>",
    access_control_list=[
        ServingEndpointAccessControlRequest(
            group_name="data-scientists",
            permission_level="CAN_QUERY",
        ),
        ServingEndpointAccessControlRequest(
            user_name="admin@example.com",
            permission_level="CAN_MANAGE",
        ),
    ],
)

# Update permissions (additive)
w.serving_endpoints.update_permissions(
    serving_endpoint_id="<endpoint-id>",
    access_control_list=[
        ServingEndpointAccessControlRequest(
            group_name="ml-engineers",
            permission_level="CAN_MANAGE",
        ),
    ],
)
```

### Via Generic Permissions API

Alternatively, use the generic permissions API:

```python
# Get permissions
perms = w.permissions.get(
    request_object_type="serving-endpoints",
    request_object_id="<endpoint-id>",
)

# Set permissions (replace)
w.permissions.set(
    request_object_type="serving-endpoints",
    request_object_id="<endpoint-id>",
    access_control_list=[
        AccessControlRequest(
            group_name="data-scientists",
            permission_level=PermissionLevel.CAN_QUERY,
        ),
    ],
)

# Update permissions (additive)
w.permissions.update(
    request_object_type="serving-endpoints",
    request_object_id="<endpoint-id>",
    access_control_list=[
        AccessControlRequest(
            group_name="ml-engineers",
            permission_level=PermissionLevel.CAN_MANAGE,
        ),
    ],
)
```

### Permission Levels

| Level | Capabilities |
|-------|-------------|
| `CAN_VIEW` | View endpoint details and metrics |
| `CAN_QUERY` | CAN_VIEW + query the endpoint |
| `CAN_MANAGE` | CAN_QUERY + update config, manage permissions, delete |

---

## Registered Models in Unity Catalog (CRUD)

### Create a Registered Model

```python
from databricks.sdk.service.catalog import RegisteredModelAlias

model = w.registered_models.create(
    name="my_model",
    catalog_name="main",
    schema_name="ml",
    comment="Customer churn prediction model",
    aliases=[RegisteredModelAlias(alias_name="challenger", version_num=1)],
    storage_location="/Volumes/main/ml/models/my_model",
)
print(f"Created model: {model.full_name}")
```

### Get / List Registered Models

```python
# Get a specific model
model = w.registered_models.get(
    full_name="main.ml.my_model",
    include_aliases=True,
)
print(f"Name: {model.name}, owner: {model.owner}")

# List models under a schema
for model in w.registered_models.list(
    catalog_name="main",
    schema_name="ml",
    max_results=100,
):
    print(f"  {model.full_name}")

# List all models in the metastore
for model in w.registered_models.list():
    print(f"  {model.full_name}")
```

### Set / Delete Aliases

```python
# Set alias (promote version)
w.registered_models.set_alias(
    full_name="main.ml.my_model",
    alias="prod",
    version_num=3,
)

# Delete alias
w.registered_models.delete_alias(
    full_name="main.ml.my_model",
    alias="challenger",
)
```

### Update a Registered Model

```python
w.registered_models.update(
    full_name="main.ml.my_model",
    new_name="my_model_v2",  # rename
    comment="Updated comment",
    owner="new-owner@example.com",
)
```

### Delete a Registered Model

```python
w.registered_models.delete(full_name="main.ml.my_model")
```

### Required Privileges

| Operation | Required Privileges |
|-----------|-------------------|
| Create | `USE_CATALOG` + `USE_SCHEMA` + `CREATE_MODEL` (or `CREATE_FUNCTION`) |
| Get/List | `EXECUTE` on model, `USE_CATALOG` + `USE_SCHEMA` |
| Update/Delete | Owner of model, `USE_CATALOG` + `USE_SCHEMA` |
| Set alias | Owner of model |
| Apply tags | `APPLY_TAG` on model |

---

## Provisioned Throughput Endpoints

```python
from databricks.sdk.service.serving import PtEndpointCoreConfig

# Create PT endpoint
endpoint = w.serving_endpoints.create_provisioned_throughput_endpoint_and_wait(
    name="my-pt-endpoint",
    config=PtEndpointCoreConfig(
        served_entities=[{
            "entity_name": "system.ai.llama-4-maverick",
            "entity_version": "1",
        }]
    ),
    tags=[{"key": "project", "value": "production"}],
)

# Update PT endpoint config
w.serving_endpoints.update_provisioned_throughput_endpoint_config_and_wait(
    name="my-pt-endpoint",
    config=PtEndpointCoreConfig(
        served_entities=[{
            "entity_name": "system.ai.claude-sonnet-4",
            "entity_version": "1",
        }]
    ),
)
```

---

## Notification Settings

```python
# Update email notifications for endpoint state changes
w.serving_endpoints.update_notifications(
    name="my-agent-endpoint",
    email_notifications={
        "emails": ["alerts@example.com"],
        "on_state_change": True,
    },
)
```

---

## Endpoint Tags

```python
# Add tags
w.serving_endpoints.patch(
    name="my-agent-endpoint",
    add_tags=[{"key": "environment", "value": "prod"}],
)

# Delete tags
w.serving_endpoints.patch(
    name="my-agent-endpoint",
    delete_tags=["temporary-tag"],
)

# Get endpoint (includes tags)
endpoint = w.serving_endpoints.get(name="my-agent-endpoint")
for tag in endpoint.tags:
    print(f"  {tag.key}: {tag.value}")
```

---

## Logs & Metrics

```python
# Build logs (during container build)
build_logs = w.serving_endpoints.build_logs(
    name="my-agent-endpoint",
    served_model_name="my_model-1",
)
print(build_logs.logs)

# Runtime server logs
server_logs = w.serving_endpoints.logs(
    name="my-agent-endpoint",
    served_model_name="my_model-1",
)
print(server_logs.logs)

# Prometheus metrics
metrics = w.serving_endpoints.export_metrics(name="my-agent-endpoint")
print(metrics.metrics)
```

---

## Agent Endpoint Lifecycle (Quick Checklist)

```python
# 1. Register model in UC
model = w.registered_models.create(name="my_agent", catalog_name="main", schema_name="ml")

# 2. Create endpoint (with AI Gateway)
endpoint = w.serving_endpoints.create_and_wait(
    name="my-agent-endpoint",
    config=EndpointCoreConfigInput(...),
    route_optimized=True,
    tags=[{"key": "type", "value": "agent"}],
)

# 3. Configure AI Gateway (rate limits, guardrails, inference tables)
w.serving_endpoints.put_ai_gateway(name="my-agent-endpoint", ...)

# 4. Set permissions
w.serving_endpoints.set_permissions(serving_endpoint_id="...", ...)

# 5. Monitor via metrics/notifications
# 6. Version swap via update_config (when new model version is ready)
# 7. Delete when done
```

---

## Agent Quickstart (Databricks Apps Template)

For a production agent with a chat UI:

1. In Databricks UI: **+ New → App → Agents → Agent - OpenAI Agents SDK**
2. Creates an app with:
   - **MLflow AgentServer** — Async FastAPI server with `/invocations` endpoint
   - **OpenAI Agents SDK** — Conversation management + tool orchestration
   - **ResponsesAgent interface** — Framework-agnostic wrapping
   - **MCP servers** — Connect to Databricks tools and data sources
3. Deploys automatically to a managed compute resource
4. Get the app URL to chat with the agent

See the [agent-quickstart](https://docs.databricks.com/aws/en/generative-ai/tutorials/agent-quickstart).
