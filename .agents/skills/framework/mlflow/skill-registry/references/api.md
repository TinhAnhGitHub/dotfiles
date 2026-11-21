# Skill Registry Python API (experimental, MLflow 3.18.0+)

All symbols are experimental. Verify signatures against the installed release:
<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html>.

## High-level fluent APIs

```python
mlflow.genai.register_skill(
    *,
    source: GitSource | OCISource | ZipSource | str,
    name: str | None = None,
    organization: str = "",
    status: str = "active",
) -> SkillVersion

mlflow.genai.import_skills(
    *,
    source: GitSource | str,
    organization: str = "",
    skill_names: list[str] | None = None,
    status: str = "active",
) -> list[SkillVersion]

mlflow.genai.pull(
    uri: str,
    *,
    destination: str | os.PathLike | None = None,
) -> str

mlflow.genai.search_skills(
    *,
    filter_string: str | None = None,
    max_results: int = 100,
    order_by: list[str] | None = None,
    page_token: str | None = None,
    include_skill_identities: list[str] | None = None,
) -> PagedList[Skill]
```

## Source classes

```python
from mlflow.genai.sources import GitSource, OCISource, ZipSource

GitSource(url="https://github.com/org/repo.git", ref="v1.0.0", subpath="skills/review")
OCISource(image="registry.example.com/skills:sha-abc", subpath="skills")
ZipSource(url="https://example.com/skills.zip", subpath="skills")
```

- `GitSource` requires Git and caller credentials; pin `ref` to a commit or tag.
- `OCISource` requires image/container credentials; prefer a digest tag.
- `ZipSource` URLs must be public and ideally immutable.
- A plain string source is treated as a local folder path.

## Lower-level MlflowClient API

`create_skill`, `create_skill_version`, `get_skill`, `get_skill_version`,
`get_skill_version_by_alias`, `get_latest_skill_version`, `search_skills`,
`search_skill_versions`, `update_skill`, `update_skill_version`, `set_skill_alias`,
tag methods, and delete methods. See
<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html>.

```python
from mlflow import MlflowClient

client = MlflowClient()
versions = client.search_skill_versions(
    name="code-review", organization="acme", max_results=50
)
for v in versions:
    print(v.version, v.status, v.digest)
```

## Status and alias lifecycle

```python
from mlflow import MlflowClient

client = MlflowClient()
client.update_skill_version(
    name="code-review", organization="acme", version=2, status="active"
)
client.set_skill_alias(
    name="code-review", organization="acme", alias="production", version=2
)
print(client.get_skill_version_by_alias(
    name="code-review", organization="acme", alias="production"
).version)
```

Statuses: `draft → active → deprecated → deleted`. `deleted` is terminal; draft
and deprecated versions remain pullable. `latest` is reserved and dynamic — prefer
a managed alias for reproducible installs.

## URI forms

| URI | Meaning |
|---|---|
| `skills:/name` | Skill by name, resolved to latest version |
| `skills:/@org/name` | Organization-qualified skill |
| `skills:/name@production` | Skill at alias `production` |
| `skills:/name/3` | Skill at explicit version 3 (verify exact syntax against installed release) |
