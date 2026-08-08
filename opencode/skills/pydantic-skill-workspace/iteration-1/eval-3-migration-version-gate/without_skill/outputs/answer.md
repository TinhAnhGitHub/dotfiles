# Migration

Keep the dependency constraint as `pydantic>=2.6,<2.11`. Replace the unsupported
`validate_by_name` setting with the v2.6-v2.10 equivalent:

```python
from pydantic import BaseModel, ConfigDict, Field


class Payload(BaseModel):
    internal_name: str = Field(alias="externalName")

    # Accept both the field name and its alias during validation.
    model_config = ConfigDict(populate_by_name=True)
```

If the model already has other configuration, keep those options and change
only `validate_by_name=True` to `populate_by_name=True`.

`validate_by_name` was introduced in Pydantic 2.11, so it is not a supported
configuration option for the pinned 2.6 through 2.10 range. Do not upgrade the
dependency for this fix. If the project later moves to Pydantic 2.11 or newer,
the explicit equivalent of `populate_by_name=True` is:

```python
model_config = ConfigDict(
    validate_by_name=True,
    validate_by_alias=True,
)
```

Pydantic 2.11+ prefers the explicit `validate_by_name`/`validate_by_alias`
settings; `populate_by_name` is deprecated for a future major release.
