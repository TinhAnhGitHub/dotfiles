# Component lineage and release manifest

The purpose of a release manifest is to answer this question after deployment:

> Which exact code, prompt, model/provider, tools, context, policy, evaluation,
> dependency set, infrastructure, and approval produced this response?

## Minimum lineage graph

```text
trace/request
  -> release_id
  -> endpoint + endpoint_config + served_entity
  -> registered_model_version + LoggedModel
  -> git_sha + dependency_lock_digest
  -> prompt_version + generation_config
  -> provider_model / embedding / judge model
  -> retriever index + source snapshot + sync state
  -> tools/MCP server versions + tool schema digest
  -> memory/policy/guardrail versions
  -> evaluation dataset + scorer/judge configuration
  -> deployment job/run + approver
```

Every edge does not need to be represented by a single product. It does need to
be represented by a stable ID or digest and joined through a documented key.

## Suggested manifest schema

```yaml
release_id: <stable-human-readable-id>
created_at: <UTC timestamp>
owner: <team>
intended_use: <business purpose>
risk_tier: <low|medium|high>
source:
  repository: <URL or name>
  git_sha: <40-char commit>
  branch_or_tag: <optional>
  dirty: false
  source_digest: sha256:<digest>
  dependency_lock_digest: sha256:<digest>
application:
  logged_model_id: <MLflow LoggedModel ID>
  model_uri: <MLflow model URI>
  registered_model: <catalog.schema.model>
  registered_model_version: <integer>
  alias_resolved_from: <alias or policy pointer>
  code_entrypoint: <module/path>
  response_contract: <schema/version>
prompts:
  - uri: prompts:/<name>/<version>
    sha256: <template digest>
    role: system
    compatibility: <model/context notes>
models:
  provider: <provider>
  generation_model: <pinned model ID>
  embedding_model: <pinned endpoint/model ID>
  judge_model: <pinned model ID>
  parameters_digest: sha256:<digest>
context:
  source_tables: [<UC FQNs and table versions/commits>]
  index: <catalog.schema.index>
  index_type: <delta_sync|direct_access|other>
  embedding_endpoint: <endpoint>
  chunking_config_digest: sha256:<digest>
  retrieval_config_digest: sha256:<digest>
tools:
  mcp_servers: [<server name/version or alias resolved to version>]
  tool_schema_digest: sha256:<digest>
  permissions_digest: sha256:<digest>
memory:
  store: <Lakebase/other>
  schema_version: <version>
  retention_policy: <policy ID>
safety:
  guardrails: [<policy/version>]
  redaction_mode: <log|enforce>
  human_review_policy: <policy ID>
evaluation:
  dataset: <name>
  dataset_digest: sha256:<digest>
  dataset_snapshot: <version/commit>
  scorers: [<name/version>]
  judge_config_digest: sha256:<digest>
  baseline_release_id: <release>
  metrics: {<metric>: <value>}
  gates: {<metric>: <threshold>}
  target: <dev|acc|prd>
  bundle_run_id: <run ID>
  deployment_job_run_id: <run ID>
  endpoint_name: <stable name>
  endpoint_config_version: <version>
  served_entities: [<entity/version/routes>]
  traffic_config_digest: sha256:<digest>
evidence:
  reviewers: [<identity>]
  approvers: [<identity>]
  evaluation_run_id: <run ID>
  change_ticket: <ticket>
```

## Metadata placement

Use the appropriate store for each value:

| Data | Preferred location |
|---|---|
| Immutable artifact/version | MLflow/Unity Catalog |
| Trace/span/request metadata | MLflow Tracing and governed trace storage |
| Endpoint/entity/config state | Model Serving API snapshot and release manifest |
| Source and configuration | Git commit, release manifest, CI artifacts |
| Dataset/index version | Delta/UC history, index metadata, dataset digest |
| Approvals and gates | CI/CD evidence, MLflow run tags/metrics, change record |
| Secrets | Secret scope/OAuth; reference only, never store values |

Avoid putting very large payloads or private data into tags. Use IDs and secure
references, then enforce retention and access controls on the referenced data.

## Trace enrichment

At request start, attach stable low-cardinality tags such as:

```text
release_id, git_sha, prompt_version, registered_model_version,
endpoint_name, served_entity, endpoint_config_version, environment,
tenant_class, session_id, client_request_id
```

At each span, capture the relevant model/tool/retriever identity, input/output
schema, duration, status, retry count, and token usage. Redact or hash PII and
secrets before persistence. Use a request ID to join external client logs and a
session ID to group multi-turn evaluations.

## Release manifest invariants

Reject or flag a release when:

- the Git source is dirty or missing and no CI-supplied source identity exists;
- a prompt/model/tool/retriever change has no new evaluation evidence;
- a registry alias cannot be resolved to an immutable version;
- endpoint state is not ready or its config update is still running;
- a canary route lacks served-entity identity in telemetry;
- the baseline or dataset digest is missing;
- a secret appears in the manifest, tag set, prompt, or source diff;
- an approval is absent for the target risk tier.
