# Pydantic Migration

For the existing `pydantic>=2.6,<2.11` constraint, replace the patch's
`validate_by_name` setting with the older alias configuration:

```python
from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
```

`populate_by_name=True` is the compatible Pydantic v2.6-v2.10 equivalent for
accepting field names as well as aliases during validation. Do not upgrade the
dependency range for this change. `validate_by_name` was introduced in
Pydantic 2.11; if the project later moves to 2.11+, the equivalent explicit
configuration is `ConfigDict(validate_by_name=True, validate_by_alias=True)`.
