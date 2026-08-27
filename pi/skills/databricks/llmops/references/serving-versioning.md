# Custom serving endpoint versioning

Load this reference when a user asks how to version, promote, canary, or roll
back a custom MLflow/PyFunc/ResponsesAgent endpoint.

## Keep the identity layers separate

| Layer | Example | What it answers |
|---|---|---|
| App/prompt version | `support-agent@12` | What behavioral source was reviewed? |
| LoggedModel | `m-abc...` | What executable candidate and traces were created? |
| UC registered model version | `catalog.schema.support_agent:17` | Which immutable package is approved? |
| Served entity | `support-agent-v17` | Which package/config is loaded on the endpoint? |
| Endpoint config | `support-agent config 42` | Which entities and traffic routes are active? |
| Stable endpoint | `support-agent` | What client contract remains stable? |

Moving `@champion`, `@prod`, or `latest-model` is not a deployment. Resolve the
alias, record the integer version, and update the endpoint configuration. A
serving endpoint may continue to pin the previous entity after an alias moves.

## Release sequence

1. Evaluate the candidate using the approved dataset and baseline.
2. Log the executable with code, resources, signature, prompt/config, and
   evaluation evidence.
3. Register it in Unity Catalog and apply tags describing Git/release identity.
4. Resolve the approved alias to a numbered model version.
5. Create or update a uniquely named served entity for that version.
6. Configure the route, traffic split, scaling, permissions, AI Gateway, and
   logging according to current endpoint capabilities.
7. Wait for the endpoint to be ready and for its config update to finish.
8. Smoke-test the entity directly where supported and the stable endpoint.
9. Verify trace tags/inference evidence contain endpoint and served-entity IDs.
10. Start a watch window with quality, safety, latency, error, and cost alerts.

## Canary and traffic splitting

Use separate entity names for champion and challenger. Record the exact route:

```yaml
served_entities:
  - name: support-agent-v17
    entity_version: "17"
  - name: support-agent-v18
    entity_version: "18"
traffic:
  support-agent-v17: 90
  support-agent-v18: 10
```

Traffic percentages must sum to 100. Include `served_entity` and release ID in
inference/trace evidence; otherwise a quality comparison mixes two versions.
Use the same evaluation slices for champion and challenger, and stratify real
traffic comparisons by tenant, request type, and safety category.

Do not assume every custom agent endpoint supports every AI Gateway feature.
Check the live capability matrix for the workspace/runtime and distinguish
payload logging, usage tracking, rate limiting, guardrails, fallbacks, and
traffic splitting.

## Readiness and update semantics

After creation or `update-config`, verify both:

```text
state.ready == READY
state.config_update == NOT_UPDATING
```

The old configuration may continue serving while the new one is built. A
`READY` state alone can therefore describe the old config. Inspect pending and
per-entity deployment state, build logs, and runtime logs before declaring a
release live.

## Rollback

Preserve the previous endpoint config, served entity, model version, routes,
resource settings, and release manifest. Roll back with a new explicit config
update that restores those values. Then verify readiness and stable-endpoint
behavior. Do not delete the failed entity before capturing logs and traces.

After rollback, preserve the failure as an evaluation case and decide whether
the fix belongs in code, prompt, tool schema, retrieval, model choice,
guardrails, endpoint capacity, or the deployment process.

## Custom ResponsesAgent metadata

At deployment time inject values such as:

```text
GIT_SHA
RELEASE_ID
MODEL_VERSION
MODEL_SERVING_ENDPOINT_NAME
MLFLOW_EXPERIMENT_ID
DEPLOYMENT_RUN_ID
```

Pass stable `session_id` and `client_request_id` from the caller when the agent
supports multi-turn behavior. These IDs let operators connect client logs,
endpoint/inference records, MLflow traces, and user feedback.

## Auth and resources

Declare model resources and downstream dependencies when logging the model.
For shared applications, decide whether service-principal identity or
on-behalf-of-user access is required. Use the narrower identity possible and
grant only required UC, endpoint, SQL, MCP, and Lakebase permissions. Keep all
credentials in secret scopes/OAuth and reference them at runtime.

## API discipline

Endpoint route field names, preview features, and deployment helpers change.
Before writing commands or SDK code:

1. Inspect `databricks serving-endpoints -h` and the specific subcommand help.
2. Inspect the current OpenAPI/schema for the endpoint.
3. Re-open current cloud-specific Model Serving/Agent Framework docs.
4. Validate against the target workspace/runtime and installed SDK.
5. Store the resulting endpoint config snapshot in release evidence.
