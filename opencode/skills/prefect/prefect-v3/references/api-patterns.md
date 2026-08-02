# Prefect 3 API and extensibility patterns

Use this reference when the user needs programmatic control, a generated SDK,
custom infrastructure, custom configuration blocks, or plugins. The primary
sources are [API client](https://docs.prefect.io/v3/advanced/api-client),
[custom base job templates](https://docs.prefect.io/v3/advanced/customize-base-job-templates),
[custom blocks](https://docs.prefect.io/v3/advanced/custom-blocks),
[custom workers](https://docs.prefect.io/v3/advanced/developing-a-custom-worker),
[plugins](https://docs.prefect.io/v3/advanced/plugins), and
[custom SDK generation](https://docs.prefect.io/v3/advanced/generate-custom-sdk).

## API client and pagination

Use the public client context manager rather than constructing an internal
HTTP client. It is asynchronous by default and has a synchronous variant:

```python
import asyncio
from prefect import get_client


async def list_recent_runs() -> list:
    async with get_client() as client:
        page = await client.read_flow_runs(limit=200, offset=0)
        return page


def health_check() -> dict:
    with get_client(sync_client=True) as client:
        response = client.hello()
        return response.json()


if __name__ == "__main__":
    print(health_check())
    print(asyncio.run(list_recent_runs()))
```

The server default page size is 200. For large result sets, use the returned
page's next-page mechanism or explicit `offset`/`limit`; never assume an
unbounded `read_*` call returns every object. Useful filters include
`FlowRunFilter`, `DeploymentFilter`, state filters, sorting, and `EventFilter`.
Use `set_flow_run_state` for controlled orchestration and `force=True` only
when the state transition is deliberately administrative.

Custom client headers can be supplied with
`PREFECT_CLIENT_CUSTOM_HEADERS` as JSON. Prefect protects `User-Agent`,
`Prefect-Csrf-Token`, and `Prefect-Csrf-Client`; an attempted override is
ignored. Keep API keys in environment/secret stores. A rendered API-client
artifact example in the docs uses mocked placeholders and is not a runnable
credential example.

## Base job templates

A work-pool base job template has `variables` and `job_configuration`. A
variable has no effect unless `job_configuration` references it with
`{{ variable_name }}`. Saving a custom template replaces the complete default,
so start from:

```bash
prefect work-pool get-default-base-job-template --type kubernetes
```

Then validate the JSON and preserve required image, command, namespace, and
metadata fields. Use Kubernetes Secret references rather than putting secret
values in the template. Removing a variable reference or leaving a variable
without a safe default can silently remove the corresponding configuration.

## Custom blocks

Blocks are typed, reusable configuration. Custom block classes should have
Pydantic fields, a stable block type name, and explicit save/load behavior.
Keep secret fields as `SecretStr` or a dedicated Secret block and package the
class in every environment that loads it.

```python
from typing import Optional
from pydantic import Field, SecretStr
from prefect.blocks.core import Block


class WarehouseConnection(Block):
    """Reusable, non-production-example connection configuration."""

    _block_type_name = "Warehouse Connection"
    host: str
    database: str
    username: str
    password: SecretStr
    schema: Optional[str] = Field(default=None)


if __name__ == "__main__":
    block = WarehouseConnection(
        host="warehouse.internal",
        database="analytics",
        username="flow-user",
        password=SecretStr("injected-at-runtime"),
    )
    block.save("analytics", overwrite=True)
    loaded = WarehouseConnection.load("analytics")
    print(loaded.host, loaded.database)
```

The example value above is deliberately non-secret placeholder text; inject
real secrets through a secret manager. The block class is not stored
server-side, so it must be importable where `load` runs. Register integration
blocks with `prefect block register` when auto-registration has not happened.
Check current Pydantic field names against the installed Prefect version; one
official custom-block example has a field-name mismatch in a migration snippet.

## Custom worker skeleton

Custom workers implement a job configuration, variable schema, worker, and
result. The exact provider API is version-sensitive; use the current page and
the installed integration worker as templates:

```python
from typing import Any
import anyio
from prefect.client.schemas.objects import FlowRun
from prefect.workers.base import (
    BaseJobConfiguration,
    BaseVariables,
    BaseWorker,
    BaseWorkerResult,
)
from pydantic import Field


class ExampleJobConfiguration(BaseJobConfiguration):
    image: str = Field(default="python:3.12-slim")
    cpu: int = Field(default=1, ge=1)


class ExampleVariables(BaseVariables):
    image: str = Field(default="python:3.12-slim")
    cpu: int = Field(default=1, ge=1)


class ExampleWorker(BaseWorker):
    type = "example"
    job_configuration = ExampleJobConfiguration
    job_configuration_variables = ExampleVariables

    async def launch_job(
        self,
        flow_run: FlowRun,
        configuration: ExampleJobConfiguration,
    ) -> str:
        raise NotImplementedError("connect this method to the target provider")

    async def watch_job(self, job_id: str) -> int:
        raise NotImplementedError("poll the provider and return its exit code")

    async def run(
        self,
        flow_run: FlowRun,
        configuration: ExampleJobConfiguration,
        task_status: Any = anyio.TASK_STATUS_IGNORED,
    ) -> BaseWorkerResult:
        job_id = await self.launch_job(flow_run, configuration)
        task_status.started(job_id)
        exit_code = await self.watch_job(job_id)
        return BaseWorkerResult(status_code=exit_code, identifier=str(job_id))
```

`launch_job` and `watch_job` above are provider-specific placeholders and must
be implemented; they are not Prefect APIs. A real worker should call
`super().prepare_for_flow_run(...)`, create infrastructure, call
`task_status.started(...)`, watch it, and return a `BaseWorkerResult`. Expose
the package through the `prefect.collections` entry-point group, for example:

```toml
[project.entry-points."prefect.collections"]
my_worker = "my_worker_module"
```

Test Pydantic validation, variable interpolation, cancellation, retries, and
the worker's least-privilege credentials before registering a production pool.
Variables used only as a template are not runtime validation; validate again
in the job configuration.

## Plugins

Plugins execute with the permissions of every Prefect process that imports
them. They are disabled by default and are a high-trust extension point.

```python
# my_plugin/__init__.py
from prefect.plugins import HookContext, SetupResult, register_hook

PREFECT_PLUGIN_API_REQUIRES = ">=0.1,<1"


@register_hook
def setup_environment(*, ctx: HookContext) -> SetupResult:
    logger = ctx.logger_factory("my-plugin")
    logger.info("configuring environment for %s", ctx.api_url)
    return SetupResult(
        env={"MY_SERVICE_MODE": "prefect"},
        note="configured",
        required=False,
    )
```

```toml
[project.entry-points."prefect.plugins"]
my_plugin = "my_plugin"
```

Enable and diagnose explicitly:

```bash
export PREFECT_PLUGINS_ENABLED=1
prefect plugins diagnose
```

Use `PREFECT_PLUGINS_ALLOW`/`DENY`, `PREFECT_PLUGINS_SAFE_MODE`,
`PREFECT_PLUGINS_SETUP_TIMEOUT_SECONDS`, and `PREFECT_PLUGINS_STRICT` to
control loading. Plugin errors are isolated unless a required plugin fails in
strict mode. Hooks may run more than once and order is not guaranteed; make
them idempotent and never log credentials. The legacy
`PREFECT_EXPERIMENTS_PLUGINS_*` names are deprecated, with the renamed setting
required by newer Prefect releases.

## Generate a custom SDK

The generated SDK is beta and is derived from server-side deployment metadata:

```bash
prefect sdk generate --output ./generated_prefect.py \
  --deployment customer-pipeline/production
```

Regenerate when deployments, parameters, or job-variable schemas change. The
command overwrites the output, so commit it only through a deliberate CI step.
Generated deployment handles can run synchronously or asynchronously and can
override documented tags, idempotency keys, schedules, and infrastructure
options. Keep the API connection used for generation trusted; do not embed
credentials in the generated file.

## Infrastructure as code

The official Terraform provider is active development toward API parity. Use
Terraform plans and separate state per environment. Pulumi can bridge the
provider (the official page documents Pulumi `>=3.147.0`); do not name the
Pulumi project `prefect`, `pulumi`, or `pulumi-prefect`. Provider credentials
must come from the CI secret store. Helm is appropriate for server/worker
resources; use the infrastructure reference for chart and database boundaries.
