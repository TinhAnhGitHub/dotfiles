---
name: prefect
description: Use for Prefect workflow orchestration, including Prefect 3 flows and tasks, retries, caching, deployments, schedules, work pools, workers, automations, events, Prefect Cloud, self-hosted servers, and Prefect integrations. When a request mentions Prefect, prefect.yaml, @flow, @task, prefect deploy, work pools, workers, or Prefect Cloud, route to the Prefect v3 subskill unless the user explicitly requests an older Prefect version.
---

# Prefect

This is the routing skill for Prefect. Prefect's current documentation and APIs
are versioned; avoid silently mixing Prefect 2.x examples with Prefect 3.x.

## Routing

For Prefect 3.x work, read and follow:

- `prefect-v3/SKILL.md` — the complete practical workflow and decision guide.
- `prefect-v3/references/workflows.md` — flows, tasks, states, retries,
  concurrency, caching, results, assets, artifacts, logging, testing, and
  interactive/background workflows.
- `prefect-v3/references/deployments.md` — deployments, schedules, code
  retrieval, job variables, configuration, events, and automations.
- `prefect-v3/references/infrastructure.md` — work pools, workers, local and
  managed infrastructure, Cloud, self-hosting, health checks, CI/CD, and
  operations.
- `prefect-v3/references/api-patterns.md` — API client, blocks, custom workers,
  plugins, base job templates, custom SDKs, and IaC.
- `prefect-v3/references/troubleshooting.md` — failure diagnosis, security,
  permissions, limits, and version caveats.

Use the official source ledger at
`prefect-v3/references/source-ledger.md` when a detail is version-sensitive or
needs a direct citation.
