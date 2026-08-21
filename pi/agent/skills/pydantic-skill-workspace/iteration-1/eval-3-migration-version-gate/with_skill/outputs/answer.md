# Use the pre-2.11 configuration

The declared project constraint is `pydantic>=2.6,<2.11`. Replace the patch's
`validate_by_name` setting with `populate_by_name=True`:

```python
from pydantic import BaseModel, ConfigDict, Field


class Payload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")


Payload(userId=1)  # alias input
Payload(user_id=1)  # field-name input
```

`populate_by_name=True` is the compatible Pydantic v2.6-v2.10 behavior for
accepting an aliased field by either its alias or its Python field name. Do not
use this patch under the current version range:

```python
# Requires Pydantic >=2.11
ConfigDict(validate_by_name=True, validate_by_alias=True)
```

`validate_by_name` and `validate_by_alias` were introduced in Pydantic 2.11.
They are the newer, more granular replacement for `populate_by_name`; enabling
both is equivalent to `populate_by_name=True`. Therefore, keep
`populate_by_name=True` while the upper bound remains `<2.11`. If the project
later raises its minimum to `2.11`, migrate to the two `validate_by_*` settings
and pin/test the intended alias behavior. The current docs discourage
`populate_by_name` from 2.11 onward and indicate it will be deprecated in v3.

The relevant input boundary here is model validation of aliased external data;
this setting does not change serialization. Continue to use
`model_dump(by_alias=True)` when the output contract requires aliases.

References:

- Pydantic alias configuration: <https://pydantic.dev/docs/validation/latest/concepts/alias/>
- Pydantic migration guide: <https://pydantic.dev/docs/validation/latest/get-started/migration/>
- Skill compatibility map: `references/current-docs.md`
- Skill migration guidance: `references/migration.md`

The exact installed patch version was not provided, so this answer gates on the
declared range rather than claiming a specific resolved version. No project
test suite was run; a focused test should validate both `userId` and `user_id`
inputs, plus the expected `model_dump(by_alias=True)` output.
