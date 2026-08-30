# LLMOps integration

## Agent version lineage

Load `version-tracking`. An app version that consumes MCP tools should record:

- MCP server names and resolved semvers;
- requested alias and resolved version;
- access endpoint ID/transport and gateway/proxy identity;
- tool snapshot/schema digest;
- authorization policy version (not credentials);
- relevant feature flags and timeout/retry policy.

This prevents an app commit from appearing unchanged while a moving MCP alias changed its tools.

## Package the consumer

Load `genai-flavors`. A `ResponsesAgent` can represent MCP approval request/response items and tool
calls, but the registry itself does not inject tools into the agent. Consumer code must discover or
resolve approved endpoints, establish authenticated sessions, validate tool schemas, and trace
calls. Avoid resolving `latest` at runtime.

## Evaluation before activation

Load `evaluation-monitoring`. Test the candidate MCP server/version with the consuming agent:

1. deterministic tool selection and exact argument checks;
2. expected tool result handling and citation/grounding;
3. denial, timeout, malformed schema, empty result, and unavailable server;
4. prompt injection and untrusted tool-output cases;
5. side-effect authorization and approval;
6. multi-turn state and duplicate-call behavior;
7. latency/cost and critical business slices.

Save evaluation run/dataset/scorer identities as release evidence and version tags, then activate
and move aliases.

## CI/CD promotion

```text
validate signed server.json
  → register draft with discovery disabled
  → discover tools in isolated approved runner
  → schema/security diff
  → integration tests + traced systematic evaluation
  → save approved snapshot and release tags
  → mark active
  → move staging alias
  → canary consumers
  → move production alias
  → monitor and retain rollback target
```

Rollback moves the alias/access path to the previous active version and verifies consumer health.
Do not delete the prior version until migration/retention policy permits.

## Databricks bridge

Load `databricks` and the applicable agent/model-serving skill when a Databricks-served agent
consumes MCP. Keep responsibilities separate:

- MLflow MCP Registry: MCP metadata, versions, aliases, tool snapshots, access endpoints.
- Databricks Agent Framework/Model Serving: hosted agent runtime, identity, endpoint, scaling,
  traffic, logs, and inference/trace observability.
- Unity Catalog: governed models/functions/data where applicable.

Declare remote dependencies/resources required by the packaged agent where the Databricks API
supports it, configure least-privilege service identity, and verify network reachability from
serverless model serving. Endpoint rollout remains separate from MCP alias promotion; coordinate
both in one release record.

## Production feedback loop

Trace MCP calls with server/version/tool/endpoint metadata. Sample failures, slow calls, permission
denials, unexpected tool selections, and user-negative feedback. Curate validated failures into
the evaluation dataset and add focused regression tests before changing app, tool server, alias,
or policy.
