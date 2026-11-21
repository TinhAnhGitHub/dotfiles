---
name: skill-registry
description: >
  MLflow Skill Registry (experimental, MLflow 3.18.0+): register and import Agent
  Skills from local folders, Git, OCI, or ZIP sources; manage immutable versions,
  statuses, and aliases; resolve `skills:/` URIs; pull/install skills into coding
  agents; and verify digests and source credentials. Use whenever a user asks to
  share, version, discover, install, or govern reusable agent skills with MLflow.
  Load the parent `mlflow` skill first.
compatibility: MLflow >=3.18.0; Skill Registry and all its Python entities are experimental
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-11-21"
---

# MLflow Skill Registry

Skill Registry is an experimental, centralized catalog for **Agent Skills** — a
directory with a root `SKILL.md` plus optional scripts and reference files. It
lets a team discover, version, and install reusable skills across agents and
projects. It does **not** execute skill code or automatically load skills into an
agent: MLflow pulls files; the agent harness decides what to do with them.

Treat a registered skill as untrusted third-party content until reviewed. A
registry `READ` grant is not approval of the skill's scripts, and it does not grant
access to the underlying Git/OCI source.

## Mandatory preflight

1. Confirm `mlflow.__version__ >= 3.18.0` and that the feature is enabled on the
   target server. All APIs below are experimental and may change or be removed.
2. Set `MLFLOW_TRACKING_URI`. Local folder uploads require an HTTP tracking server
   with artifact serving enabled.
3. Identify the source type: local folder, Git (`GitSource`), OCI image
   (`OCISource`), or public ZIP (`ZipSource`). Git/OCI pulls use the caller's
   credentials; ZIP URLs must be public.
4. Decide the trust boundary: prefer immutable Git commits, OCI digests, and
   immutable ZIPs so the content digest can be verified.
5. Distinguish Skill Registry from adjacent concepts: a `SkillVersion` is **not**
   an app `LoggedModel` version (`version-tracking`), not a `prompts:/` prompt
   version (`prompt-registry`), and not an MCP server (`mcp-registry`).

## Entity model

| Entity | Meaning |
|---|---|
| `Skill` | Parent identity `(organization, name, workspace)`, description, tags, aliases, and metadata derived from its resolved latest version |
| `SkillVersion` | Immutable integer version with source, source type (`git`/`oci`/`zip`/`mlflow`), optional digest, status, aliases, and version tags |
| Alias | Mutable name such as `production` pointing to one version; `latest` is reserved and dynamic |
| Status | `draft → active → deprecated → deleted`; `deleted` is terminal, draft/deprecated versions remain pullable |

Names are 1–64 lowercase ASCII letters, digits, and hyphens. Organization-qualified
URIs use `skills:/@org/name`; aliases append `@alias`, for example
`skills:/@acme/code-review@production`.

`latest` resolution prefers the highest-numbered **active** version, then the
highest draft/deprecated version — a newer draft does not override an older active
version. Never use `latest` as a reproducible release input; pin a version or a
deliberately managed alias.

## Register, version, and alias

```python
import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("http://localhost:5000")

# Register a local skill folder as a draft version.
version = mlflow.genai.register_skill(
    source="./code-review",
    organization="acme",
    status="draft",
)
print(version.name, version.version, version.status)

client = MlflowClient()
client.update_skill_version(
    name=version.name, organization="acme",
    version=version.version, status="active",
)
client.set_skill_alias(
    name=version.name, organization="acme",
    alias="production", version=version.version,
)
resolved = client.get_skill_version_by_alias(
    name=version.name, organization="acme", alias="production"
)
print(resolved.version)
```

Bulk-import multiple skills from one Git repository:

```python
import mlflow
from mlflow.genai.sources import GitSource

versions = mlflow.genai.import_skills(
    source=GitSource(url="https://github.com/acme/agent-skills.git", ref="v1.2.0"),
    organization="acme",
    skill_names=["code-review", "sql-helper"],
    status="active",
)
for v in versions:
    print(v.name, v.version, v.digest)
```

## Pull and install into an agent

```python
from pathlib import Path
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")

skill_dir = Path(mlflow.genai.pull(
    "skills:/@acme/code-review@production",
    destination=".agents/skills/code-review",
))
instructions = (skill_dir / "SKILL.md").read_text()

def agent(user_input: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_input},
    ]
```

The UI's **Use → Install for** action writes skills to agent-specific destinations
(Claude Code, Codex, Cursor, GitHub Copilot, or an arbitrary directory). Pulled
scripts may execute only if the agent chooses to run them; review them first.

## CLI quick reference

```bash
mlflow skills register --source ./code-review
mlflow skills register git --url URL --ref TAG --subpath PATH
mlflow skills register oci --image IMAGE --subpath PATH
mlflow skills register zip --url URL --subpath PATH
mlflow skills import --source URL --skill-name NAME
mlflow skills search
mlflow skills set-alias skills:/name --alias production --version 2
mlflow skills pull skills:/name@production --destination .agents/skills/name
```

## Security and governance

- External content is fetched by the client with the pulling user's credentials;
  a registry `READ` permission does not grant Git/OCI access.
- Digest verification protects registered content. Low-level `MlflowClient`
  registrations may omit a digest, disabling verification — prefer high-level APIs.
- Workspace permissions are `READ`, `EDIT`, and `MANAGE`; organization names do not
  grant access by themselves.
- Pin immutable sources and review scripts before an agent can execute them.

## Reference router

| Need | Read |
|---|---|
| Exact Python APIs, entities, source classes, pagination | [`references/api.md`](references/api.md) |
| CLI/UI workflows and installation destinations | [`references/cli-ui.md`](references/cli-ui.md) |
| Source credentials, digests, permissions, trust boundaries | [`references/source-security.md`](references/source-security.md) |
| Official source URLs and version notes | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Produce: the installed MLflow version and experimental caveat; the chosen source
type and trust assessment; a pinned version or managed alias (never bare `latest`);
runnable code with imports; and an explicit statement that pulling does not execute
or auto-load skills. Do not claim a digest was verified unless it was actually checked.
