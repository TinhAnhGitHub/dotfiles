# User API Models

The following uses Pydantic v2. A create request has no server-generated ID;
the response includes one.

## `models.py`

```python
from typing import Annotated

from pydantic import BaseModel, Field


UserId = Annotated[int, Field(strict=True)]
NonEmptyTag = Annotated[str, Field(strict=True, min_length=1)]


class UserRequest(BaseModel):
    # No default makes this required; the union still permits null.
    nickname: str | None
    tags: list[NonEmptyTag] = Field(default_factory=list)


class UserResponse(UserRequest):
    id: UserId
```

`strict=True` on `UserId` prevents a value such as `"42"` from being coerced
to the integer `42`. The tag constraint is attached to the list item type, so
each tag must be a strict string with at least one character.

## `tests/test_models.py`

```python
import pytest
from pydantic import ValidationError

from models import UserRequest, UserResponse


def test_request_accepts_null_nickname_and_defaults_tags() -> None:
    user = UserRequest.model_validate({"nickname": None})

    assert user.nickname is None
    assert user.tags == []


def test_nickname_is_required_even_when_nullable() -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserRequest.model_validate({"tags": ["admin"]})

    error = exc_info.value.errors(include_url=False)[0]
    assert error["loc"] == ("nickname",)
    assert error["type"] == "missing"


def test_response_accepts_integer_id_and_valid_tags() -> None:
    user = UserResponse.model_validate(
        {"id": 42, "nickname": "Ada", "tags": ["admin", "beta"]}
    )

    assert user.id == 42
    assert user.tags == ["admin", "beta"]


def test_response_rejects_string_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserResponse.model_validate(
            {"id": "42", "nickname": "Ada", "tags": ["admin"]}
        )

    error = exc_info.value.errors(include_url=False)[0]
    assert error["loc"] == ("id",)
    assert error["type"] == "int_type"


@pytest.mark.parametrize(
    "bad_tag",
    ["", 123, None],
)
def test_each_tag_must_be_a_non_empty_string(bad_tag: object) -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserRequest.model_validate({"nickname": "Ada", "tags": [bad_tag]})

    error = exc_info.value.errors(include_url=False)[0]
    assert error["loc"] == ("tags", 0)
    assert error["type"] in {"string_too_short", "string_type"}
```

Run the focused tests with:

```bash
pytest -q tests/test_models.py
```
