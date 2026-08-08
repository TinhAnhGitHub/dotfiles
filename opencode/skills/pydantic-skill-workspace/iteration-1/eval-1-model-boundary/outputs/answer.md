# User API Models

The following Pydantic v2 models keep a create request's `nickname` required while allowing its value to be `null`. The response exposes a strict integer `id`. Tags are constrained at the list-item level, so every item must be a non-empty string.

## `models.py`

```python
from typing import Annotated

from pydantic import BaseModel, Field, StrictInt, StrictStr


NonEmptyTag = Annotated[StrictStr, Field(min_length=1)]


class UserRequest(BaseModel):
    # Field(...) makes the field required; the union still permits JSON null.
    nickname: StrictStr | None = Field(...)
    tags: list[NonEmptyTag] = Field(default_factory=list)


class UserResponse(BaseModel):
    id: StrictInt
    nickname: StrictStr | None
    tags: list[NonEmptyTag]
```

`nickname` has no `None` default, so omitting it is invalid while `nickname=None` is valid. `StrictInt` rejects numeric strings (and booleans), and `StrictStr` prevents Pydantic from coercing non-string tag values before `min_length=1` is checked.

## `test_models.py`

```python
import pytest
from pydantic import ValidationError

from models import UserRequest, UserResponse


def test_request_accepts_explicit_null_nickname():
    user = UserRequest(nickname=None, tags=["admin"])

    assert user.nickname is None


def test_request_requires_nickname_even_when_nullable():
    with pytest.raises(ValidationError) as exc_info:
        UserRequest(tags=["admin"])

    assert any(error["loc"] == ("nickname",) for error in exc_info.value.errors())


@pytest.mark.parametrize("tags", [[""], ["ok", ""], [123], ["ok", 456]])
def test_request_rejects_empty_or_non_string_tag_items(tags):
    with pytest.raises(ValidationError):
        UserRequest(nickname="Ada", tags=tags)


def test_response_accepts_an_integer_id():
    user = UserResponse(id=7, nickname=None, tags=[])

    assert user.id == 7


@pytest.mark.parametrize("bad_id", ["7", True])
def test_response_rejects_non_strict_ids(bad_id):
    with pytest.raises(ValidationError):
        UserResponse(id=bad_id, nickname="Ada", tags=[])
```

Run with:

```bash
pytest -q
```
