# Promotion, rollback, and CI/CD

## Evidence-driven promotion

Promotion is a policy transaction, not “choose the highest version.” Gate on:

- reproducible source, environment, and signature;
- offline metrics/scorers on a versioned dataset;
- critical slice and regression pass/fail, not only global averages;
- robustness, security, privacy, bias/fairness where applicable;
- load/integration tests and serving compatibility;
- human approval for high-risk releases;
- rollback artifact and operational capacity.

Load `evaluation-monitoring` for GenAI/agent gates and `version-tracking` for app lineage.

## Champion/challenger

```python
candidate = client.get_model_version_by_alias(MODEL_NAME, "candidate")
current = client.get_model_version_by_alias(MODEL_NAME, "champion")

if release_gate_passed(candidate, current):
    client.set_registered_model_alias(MODEL_NAME, "rollback", current.version)
    client.set_registered_model_alias(MODEL_NAME, "champion", candidate.version)
```

Make alias updates idempotent and re-read targets after each operation. If registry and endpoint
updates span systems, record a release state machine and compensating rollback; do not pretend the
operations are one atomic transaction.

## Separate environment models

For strong environment isolation (especially Unity Catalog), use environment-specific catalogs or
registered models and copy approved versions:

```python
promoted = client.copy_model_version(
    src_model_uri="models:/staging.ml.support_agent@candidate",
    dst_name="prod.ml.support_agent",
)
```

The destination receives a new version number. Record source/destination lineage and reevaluate
environment-specific dependencies. Whether to use one model plus aliases or separate names depends
on governance boundaries, permissions, and deployment architecture.

## Rollback

Registry rollback moves an alias back:

```python
previous = client.get_model_version_by_alias(MODEL_NAME, "rollback")
client.set_registered_model_alias(MODEL_NAME, "champion", previous.version)
```

Databricks endpoint rollback separately restores served entities/traffic to the prior version. If
batch jobs load `@champion` at execution time, an alias move can affect the next job; long-running
processes may cache a loaded model and require controlled restart/reload.

## Pipeline stages

```text
build/log artifact
  → signature/dependency/model validation
  → register candidate version + pending tags
  → deterministic tests
  → systematic evaluation and slice comparison
  → security/compliance approval
  → candidate alias
  → canary endpoint/entity
  → observe quality and health
  → champion alias + full traffic
  → post-release verification
```

Persist a release manifest containing source model URI/model ID, registered version, alias state,
endpoint config version, served entity IDs, evaluation evidence, approver, timestamps, and rollback
instructions.

## Webhooks/event-driven automation

Current self-hosted MLflow documentation describes experimental registry webhooks for events such
as model-version creation, tags, and aliases. Verify backend support and installed APIs before use.
Secure webhook receivers with HTTPS, HMAC verification, freshness/replay checks, payload schema
validation, allow-lists, and idempotency.

Event workflow:

1. version-created event queues validation;
2. validator writes a signed/authorized approval tag;
3. promotion controller re-reads version and evidence;
4. controller moves alias and updates deployment;
5. post-deploy verifier confirms readiness/health;
6. failure executes compensating endpoint and alias rollback.

Do not let any caller self-assert `approved=true` and trigger production without authorization.

## Legacy stages

Legacy stages (`Staging`, `Production`, `Archived`) remain visible in older APIs/workflows but are
deprecated/replaced by aliases in modern MLflow designs and are not the Unity Catalog promotion
pattern. Migrate consumers to aliases and environment-specific registered models where needed.
