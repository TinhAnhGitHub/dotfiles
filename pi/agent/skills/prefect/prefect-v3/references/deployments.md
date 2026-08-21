# Prefect 3 deployments, configuration, events, and automations

Use this reference for the control-plane boundary around a flow. Canonical
sources: [Deployments](https://docs.prefect.io/v3/concepts/deployments),
[Schedules](https://docs.prefect.io/v3/concepts/schedules),
[Create deployments](https://docs.prefect.io/v3/how-to-guides/deployments/create-deployments),
[Prefect YAML](https://docs.prefect.io/v3/how-to-guides/deployments/prefect-yaml),
[Automations](https://docs.prefect.io/v3/concepts/automations),
[Events](https://docs.prefect.io/v3/concepts/events), and
[Event triggers](https://docs.prefect.io/v3/concepts/event-triggers).

## Choose `serve`, `deploy`, or YAML

| Pattern | What it creates | Choose it when |
|---|---|---|
| `flow.serve()` | A deployment plus a long-lived local process | Code and dependencies already live on one always-on host. |
| `flow.deploy()` / `prefect deploy` | A deployment bound to a work pool | Each run should be submitted to worker or provider infrastructure. |
| `prefect.yaml` | Declarative build, push, pull, and deployment definitions | CI/CD, reproducible code packaging, or multiple deployments. |
| `flow.from_source(...).deploy()` | A deployment whose pull step retrieves code | The worker should fetch Git or object-store code at run time. |

The scheduler only creates scheduled runs. A worker or serving process must
execute them. A deployment run inside another flow is a subflow by default;
use `as_subflow=False` when it should be an independent run.

### Long-lived local deployment

```python
from prefect import flow


@flow(log_prints=True)
def hourly_report():
    print("report generated")


if __name__ == "__main__":
    hourly_report.serve(
        name="hourly-report",
        cron="0 * * * *",
        pause_on_shutdown=False,
    )
```

The serving process must stay alive. By default, schedules can be paused on
shutdown; set `pause_on_shutdown=False` only when the host lifecycle is
deliberately managed.

### Worker-backed deployment

Create a compatible work pool first, then deploy from a Python file:

```python
from prefect import flow


@flow(log_prints=True)
def hello(name: str = "world"):
    print(f"Hello, {name}!")


if __name__ == "__main__":
    hello.deploy(
        name="hello-production",
        work_pool_name="my-process-pool",
        cron="0 9 * * 1-5",
        parameters={"name": "team"},
        job_variables={"env": {"APP_ENV": "production"}},
    )
```

For Docker/image builds, pass an image or `DockerImage`; `push=False` is for a
local registry/worker and `build=False` skips an already-built image. The
worker's pool template determines which `job_variables` are legal.

## `prefect.yaml` and code retrieval

The only required top-level action is normally `pull`; `build` and `push` are
optional. Step IDs expose outputs to later steps, and templates can reference
step outputs, environment variables (`{{ $NAME }}`), blocks, and variables.

```yaml
prefect-version: null
name: customer-project

build:
  - prefect_docker.deployments.steps.build_docker_image:
      id: image
      requires: prefect-docker>=0.7.1
      image_name: registry.example/customer-flow
      tag: latest
      dockerfile: auto

push:
  - prefect_docker.deployments.steps.push_docker_image:
      image_name: "{{ image.image_name }}"
      tag: "{{ image.tag }}"

pull:
  - prefect.deployments.steps.set_working_directory:
      directory: /opt/prefect

deployments:
  - name: customer-production
    entrypoint: flows/customer.py:hello
    parameters:
      name: team
    work_pool:
      name: my-docker-pool
      job_variables:
        image: "{{ image.image }}"
```

`pull: []` explicitly disables an automatically generated pull action. Removing
the `schedules` key does not delete existing schedules; use the schedule clear
command. `run_shell_script` needs `shell: true` for shell operators and
`expand_env_vars: true` for expansion; avoid passing untrusted values into a
shell. For private Git, prefer credentials/Secret blocks or the Cloud GitHub
App over long-lived tokens in YAML. The canonical `GitRepository` constructor
uses `url=`; an older official example uses `repo_url=`, so verify the installed
version before copying that spelling.

## Schedules and ad-hoc runs

Prefect supports Cron, Interval, and RRule schedules. The newer schedule API
(`prefect.schedules.Interval` and `schedule=`/`schedules=` forms) is documented
for Prefect `>=3.1.16`; older clients show `IntervalSchedule` and a different
keyword. Pin the version and use the matching page before mixing examples.

```python
from prefect import flow
from prefect.schedules import Cron


@flow
def notify(to: str, message: str = "hello"):
    print(to, message)


if __name__ == "__main__":
    notify.serve(
        name="morning-notify",
        schedules=[
            Cron("0 8 * * *", slug="team", parameters={"to": "team@example.com"}),
        ],
    )
```

Manage schedules with:

```bash
prefect deployment schedule ls <flow>/<deployment>
prefect deployment schedule pause <flow>/<deployment> --all
prefect deployment schedule resume <flow>/<deployment> --all
prefect deployment schedule clear <flow>/<deployment> --all
```

Review the current workspace/profile before bulk operations. Scheduler limits
and time-zone/DST behavior are backend settings; it materializes a bounded
window of future runs rather than an infinite queue.

Trigger an existing deployment:

```bash
prefect deployment run customer-pipeline/production \
  --param customer_id=42 --start-in "2 hours" --watch \
  --flow-run-name "customer-42"
```

```python
from datetime import datetime, timedelta, timezone
from prefect.deployments import run_deployment


run = run_deployment(
    name="customer-pipeline/production",
    parameters={"customer_id": 42},
    job_variables={"env": {"RUN_REASON": "manual"}},
    scheduled_time=datetime.now(timezone.utc) + timedelta(hours=2),
    timeout=300,
    as_subflow=False,
)
```

## Deployment versions and job variables

Deployment version history, promotion, and rollback are Prefect Cloud features.
For reproducibility, pin Git commit/image digest even when version history is
available. Job variables can be set in YAML, `flow.deploy`, a manual run, the
CLI, an Automation, or Terraform. Treat `job_variables` as infrastructure
configuration, not an application secret channel.

## Variables, blocks, settings, and profiles

Variables are shared, JSON-like configuration and are **not encrypted**. Use
Secret blocks or integration credential blocks for sensitive values:

```python
from prefect.blocks.system import Secret
from prefect.variables import Variable


Variable.set("batch_size", 100, overwrite=True)
batch_size = Variable.get("batch_size", default=50)

secret = Secret(value="value-from-a-secret-manager")
secret.save("api-token", overwrite=True)
token = Secret.load("api-token").get()
```

Never print `token` or store it in a Variable. Blocks store typed configuration
and encrypted `SecretStr` fields; the block class itself must be available in
the execution environment. Use `prefect block register` when an integration
block type is not registered.

Settings precedence is environment variables, `.env`, `prefect.toml`/
`pyproject.toml`, active profile, then defaults. Check or modify settings with:

```bash
prefect config view --show-defaults
prefect config validate
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
prefect config unset PREFECT_API_URL
prefect profile create ci --from ephemeral
prefect profile use ci
```

`prefect.toml` and `[tool.prefect]` require Prefect `>=3.1`; `.env` support
requires `>=3.0.5`. Keep profiles out of source control if they contain
workspace credentials. Telemetry is anonymous and can be disabled with
`DO_NOT_TRACK=1` and/or `PREFECT_SERVER_ANALYTICS_ENABLED=false`.

## Events and automations

An event has a name, resource identity, optional related resources, occurrence,
and payload. An Automation matches event/metric/proactive conditions and runs
actions; a deployment trigger is an Automation attached to a deployment.
Cloud-only actions include email/incident actions and metric triggers; the
events/automations backend itself is available in Prefect 3 OSS.

### Chain deployments

```python
from prefect import flow, serve
from prefect.events import DeploymentEventTrigger


@flow
def upstream():
    print("upstream")


@flow
def downstream():
    print("downstream")


if __name__ == "__main__":
    serve(
        upstream.to_deployment(name="upstream"),
        downstream.to_deployment(
            name="downstream",
            triggers=[
                DeploymentEventTrigger(
                    expect={"prefect.flow-run.Completed"},
                    match_related={"prefect.resource.name": "upstream"},
                )
            ],
        ),
    )
```

### Pass event payloads to a flow

```python
from typing import Any
from prefect import flow, serve
from prefect.events import DeploymentEventTrigger, emit_event


@flow(log_prints=True)
def process_webhook(payload: dict[str, Any]):
    print(payload.get("action"))


if __name__ == "__main__":
    deployment = process_webhook.to_deployment(
        name="webhook-processor",
        triggers=[
            DeploymentEventTrigger(
                expect={"api.webhook.received"},
                parameters={
                    "payload": {
                        "__prefect_kind": "json",
                        "value": {
                            "__prefect_kind": "jinja",
                            "template": "{{ event.payload | tojson }}",
                        },
                    }
                },
            )
        ],
    )
    # Run this process to serve the deployment. Emit the event from a separate
    # producer process or an HTTP webhook handler after the server is running.
    serve(deployment)

# Producer process example:
# emit_event(
#     event="api.webhook.received",
#     resource={"prefect.resource.id": "webhook-handler"},
#     payload={"action": "created"},
# )
```

Deployment event triggers must match the deployment resource form documented by
the current page. If the source system emits a burst, use both `within` and
`schedule_after` with the same window: `within` suppresses repeated triggers
and `schedule_after` delays the run until the burst settles. The Automation
receives the triggering event, not a complete event history; make the flow
query the source system and be idempotent.

For custom event grammar, emit stable names such as `order.created` and
`order.complete`, match `after`/`expect`, and use `for_each` to isolate resources.
For zombie detection, use flow heartbeats and a proactive Automation with a
window of at least three heartbeat intervals; include wildcard custom state
names to avoid false positives.

## Custom notifications and templates

Custom Webhook notification blocks can render `{{ subject }}` and `{{ body }}`
into a provider-specific JSON request. Store the webhook URL/token in a block,
not source. Automation action templates can use `flow_run.parameters[...]`,
`event.payload`, `event.resource`, `tojson`, and literal values. Treat every
template input as untrusted and validate it at the flow boundary.

## Cloud versus self-hosted

Use `prefect cloud login --key ... --workspace account/workspace` in CI and
store the key in the CI secret store. Cloud workspaces and roles scope access;
worker credentials need the Worker role. A self-hosted Server defaults to
SQLite and has no authentication by default; use the self-hosted guidance for
Postgres, auth, TLS, and network restrictions before exposing it.
