# Azure Databricks model serving bridge

Load `databricks`, `databricks-core`, and `databricks-model-serving`; that suite owns exact current
CLI/SDK endpoint operations. This reference explains how Registry evidence connects to runtime.

## Deployment object relationships

| Object | Version/identity | Notes |
|---|---|---|
| UC registered model | `catalog.schema.model` | governed model container |
| UC model version | integer/string `entity_version` | exact artifact served |
| Served entity | name + model + version + compute | deployment unit in endpoint |
| Endpoint config | `config_version` | set of entities and traffic routes |
| Endpoint | stable endpoint name/ID | REST interface, ACLs, AI Gateway, telemetry |

Registry alias resolution and endpoint config are separate. Resolve the approved alias to a
numbered UC version, then explicitly create/update a served entity with that version.

## Create endpoint REST shape

Use the live API/SDK schema because route field names have evolved (`served_model_name` is present
in documented REST examples while newer SDK models may expose `served_entity_name`). A documented
custom-model shape is:

```json
{
  "name": "support-agent-endpoint",
  "config": {
    "served_entities": [
      {
        "name": "support-agent-v7",
        "entity_name": "catalog.schema.support_agent",
        "entity_version": "7",
        "min_provisioned_concurrency": 4,
        "max_provisioned_concurrency": 12,
        "scale_to_zero_enabled": false
      }
    ],
    "traffic_config": {
      "routes": [
        {"served_model_name": "support-agent-v7", "traffic_percentage": 100}
      ]
    }
  }
}
```

Concurrency values have documented multiple-of-four constraints. For development, workload-size
configuration may be simpler. Scale-to-zero reduces idle cost but adds cold-start latency and is
not the production default when predictable capacity is required.

## Canary two versions

```json
{
  "served_entities": [
    {
      "name": "champion-v7",
      "entity_name": "catalog.schema.support_agent",
      "entity_version": "7",
      "workload_size": "Small",
      "scale_to_zero_enabled": false
    },
    {
      "name": "challenger-v8",
      "entity_name": "catalog.schema.support_agent",
      "entity_version": "8",
      "workload_size": "Small",
      "scale_to_zero_enabled": false
    }
  ],
  "traffic_config": {
    "routes": [
      {"served_model_name": "champion-v7", "traffic_percentage": 90},
      {"served_model_name": "challenger-v8", "traffic_percentage": 10}
    ]
  }
}
```

Traffic totals must equal 100. Querying an individual served model/entity path bypasses the traffic
split and is useful for smoke tests. Do not compare canary quality without recording served entity
identity in request/trace/inference evidence.

## Zero-downtime update and rollback

Databricks keeps the old working config serving while the new config builds. During this period:

- both old and new configurations may incur cost;
- `state.ready` can be READY because the old config works;
- wait for `state.config_update == NOT_UPDATING` as well;
- inspect `pending_config` and per-entity deployment state;
- only one config update can proceed at a time.

Rollback is another config update that restores previous entities/routes. Preserve the previous
config and UC model version; do not rely only on a `rollback` registry alias.

## Identity and permissions

Endpoint creation/update validates model access. The endpoint creator identity is operationally
important and cannot simply be swapped; removal can require endpoint recreation. Typical UC
requirements include `USE CATALOG`, `USE SCHEMA`, and `EXECUTE` on the model plus transitive
resources. Endpoint ACLs commonly expose `CAN_QUERY` and `CAN_MANAGE`.

Route-optimized endpoints use distinct routing/auth behavior and documented OAuth-only access;
verify the target URL and client. Use service principals/OAuth for automation rather than embedded
PATs.

## Logs, inference tables, and telemetry

Two immediate diagnostics:

- build logs: container/environment construction;
- runtime logs: loaded model process stdout/stderr and errors.

AI Gateway inference tables persist sampled requests/responses and served-entity identity to Unity
Catalog. Protect raw payloads, apply retention/access controls, and account for payload logging
limits. Join by served entity for canary analysis.

Custom model serving telemetry can persist OpenTelemetry logs, spans, and metrics into managed UC
tables. It has region, table-name, size, delivery, and schema-evolution constraints; verify the
provided Azure region before enabling. This telemetry is separate from MLflow GenAI trace storage
and from model-quality evaluation.

Metrics include latency, request/error rate, CPU/memory and GPU utilization. Export APIs can feed
external monitoring. Health metrics do not establish model quality; combine them with inference
samples/traces and `evaluation-monitoring` workflows.

## Preview/version gates observed in current Azure docs

- endpoint OpenAPI query schema: Public Preview;
- route-optimized inference tables: Public Preview;
- serverless usage policies: Public Preview;
- Protobuf tensor input: Public Preview for eligible newer endpoints;
- request/assessment logs for older agent patterns: deprecated in favor of current observability
  paths;
- express deployments require newer MLflow/Databricks SDK and supported serverless environment;
- UC custom endpoint telemetry is region-limited.

Always re-open current Azure docs and inspect CLI/SDK help before production changes.
