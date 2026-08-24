# Compatible Alias Configuration

Replace the unsupported setting:

```python
model_config = ConfigDict(validate_by_name=True)
```

with the v2.6-v2.10 equivalent:

```python
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    internal_name: str = Field(alias="externalName")
```

`populate_by_name=True` allows validation through either `internal_name` or
`externalName` while keeping the existing `pydantic>=2.6,<2.11` pin. Keep
`model_dump(by_alias=True)` when serialized output must use `externalName`.

`validate_by_name` and `validate_by_alias` were introduced in Pydantic 2.11.
Do not use them, or upgrade the dependency, under the current constraint. If
the lower bound is later raised to `>=2.11`, the explicit equivalent is
`ConfigDict(validate_by_name=True, validate_by_alias=True)`; `populate_by_name`
is the older setting for the pinned range.

References: [Pydantic aliases](https://docs.pydantic.dev/latest/concepts/alias/)
and the installed skill's `references/current-docs.md` and
`references/models-fields-types.md`.
