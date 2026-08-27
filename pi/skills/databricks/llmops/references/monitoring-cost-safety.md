# Monitoring, cost, safety, and governance

## Trace-first observability

Final output logs are insufficient for agents. Capture a trace tree with spans
for the agent chain, LLM calls, retrieval, embeddings, reranking, tools/MCP,
memory, guardrails, retries, and errors. Attach release and runtime identity to
the trace so operators can group incidents by version and endpoint.

At minimum retain:

```text
trace_id, client_request_id, session_id, request_time, status,
duration_ms, token usage, request/response references, release_id,
git_sha, prompt_version, model_version, endpoint, served_entity,
tool/retriever identities, safety assessments, human feedback
```

Do not persist secrets or unrestricted sensitive payloads merely because tracing
makes it convenient. Redact, hash, sample, encrypt, restrict, and retain
according to the application’s policy.

## Operational SLOs and alerts

Define thresholds before production:

| Dimension | Example signal |
|---|---|
| Availability | successful valid responses / requests |
| Latency | p50/p95/p99, queue, tool, and model duration |
| Reliability | timeout, retry, invalid response, tool failure, loop rate |
| Quality | correctness/groundedness/relevance/safety sample metrics |
| Context | empty retrieval, stale index, citation failure, token truncation |
| Cost | tokens/request, cost/request, cost/tenant, endpoint spend |
| Security | PII/jailbreak/secret detections, denied access, anomalous traffic |

Alert on both absolute thresholds and changes from the current approved release.
Make alert responses actionable: identify the release, endpoint/entity, owner,
runbook, safe fallback, and rollback command/path.

## Cost attribution

Apply usage policies or direct resource tags consistently. Record a project,
team, environment, and cost-center identity on serverless jobs, Model Serving,
AI Search, Lakebase, and other billable resources where supported. Verify policy
precedence so a default policy does not silently override the intended tag.

Join:

- `system.billing.usage` and `system.billing.list_prices` for Databricks-side
  resource usage;
- trace token/latency metadata for per-request and per-release attribution;
- provider invoices for external model token charges not present in Databricks
  billing tables.

Track idle resources as well as request cost. Some endpoints and indexes keep
billing while idle, so lifecycle ownership and deletion/scale policy matter.

## Safety controls

Use multiple layers:

1. Input validation and authentication/authorization.
2. Deterministic domain and schema constraints.
3. Retrieval/tool allowlists and permission boundaries.
4. Model-level and endpoint-level guardrails where supported.
5. Output validation, PII/secret redaction, and safe fallback.
6. Human review/override/stop for high-impact actions.
7. Trace assessments, incident review, and regression cases.

Start new controls in log mode only when the risk permits it. Measure false
positives and missed violations before switching to enforce. Do not assume AI
Gateway guardrails apply equally to external models, foundation model APIs,
custom PyFunc endpoints, and ResponsesAgent endpoints; verify the current
endpoint capability matrix.

## Security and identity

- Prefer OAuth/service principals for automation and secret scopes for values.
- Use least-privilege UC `USE`, `SELECT`, `EXECUTE`, endpoint, app, MCP, and
  Lakebase permissions.
- Use on-behalf-of-user access when each caller’s entitlements must govern
  downstream data; otherwise document the service identity’s boundary.
- Pin dependencies and CI actions to trusted versions/commits; scan direct and
  transitive dependencies.
- Test prompt injection, tool confusion, data exfiltration, PII leakage,
  secret exposure, denial of service, and unsafe tool side effects.
- Keep production changes auditable through protected branches and deployment
  approvals. Document break-glass changes and reconcile them back to Git.

## Governance evidence

Keep an evolving technical/release record with:

- intended purpose, limitations, architecture, data/context sources;
- risk assessment and mitigations;
- code/data/model/prompt/tool/index versions;
- evaluation metrics, thresholds, failures, and human decisions;
- endpoint/deployment logs, approvals, rollback evidence;
- operating instructions, escalation path, retention, and access policy.

Treat this as a lifecycle artifact updated in the same pull requests and release
workflow as the system, not as a one-time compliance document.
