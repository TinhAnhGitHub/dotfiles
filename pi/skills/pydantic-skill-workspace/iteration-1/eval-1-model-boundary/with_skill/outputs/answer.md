# User API Models

The examples target stable Pydantic v2 APIs. No project dependency files or
installed Pydantic package were present in the evaluation workspace, so use a
current v2 release and pin it in the application project.

This uses a create-style request: the server-generated `id` is present on the
response. Any other API model that accepts an ID should reuse `UserId`.

## `models.py`

```python
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


UserId = Annotated[int, Field(strict=True)]
NonEmptyTag = Annotated[str, Field(strict=True, min_length=1)]


class UserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # No default means this field is required, while | None allows null.
    nickname: str | None
    tags: list[NonEmptyTag] = Field(default_factory=list)


class UserResponse(UserRequest):
    id: UserId
```

`Field(strict=True)` prevents an input such as `"42"` from becoming the ID
`42`. The same setting on `NonEmptyTag` prevents non-string values from being
coerced, while `min_length=1` rejects empty strings. `Annotated` places the
constraint on each list item rather than on the list itself.

## `tests/test_models.py`

```python
import pytest
from pydantic import ValidationError

from models import UserRequest, UserResponse


def test_request_accepts_null_nickname_and_defaults_tags() -> None:
    user = UserRequest.model_validate({"nickname": None})

    assert user.nickname is None
    assert user.tags == []


def test_nickname_is_required_even_though_it_is_nullable() -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserRequest.model_validate({"tags": ["admin"]})

    error = exc_info.value.errors(include_url=False)[0]
    assert error["type"] == "missing"
    assert error["loc"] == ("nickname",)


def test_response_accepts_an_integer_id() -> None:
    user = UserResponse.model_validate(
        {"id": 42, "nickname": "Ada", "tags": ["admin", "beta"]}
    )

    assert user.id == 42
    assert user.model_dump() == {
        "id": 42,
        "nickname": "Ada",
        "tags": ["admin", "beta"],
    }


def test_response_id_rejects_a_string() -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserResponse.model_validate(
            {"id": "42", "nickname": "Ada", "tags": ["admin"]}
        )

    error = exc_info.value.errors(include_url=False)[0]
    assert error["type"] == "int_type"
    assert error["loc"] == ("id",)


@pytest.mark.parametrize(
    ("bad_tag", "expected_type"),
    [
        ("", "string_too_short"),
        (123, "string_type"),
    ],
)
def test_each_tag_must_be_a_non_empty_string(
    bad_tag: object, expected_type: str
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserRequest.model_validate({"nickname": "Ada", "tags": [bad_tag]})

    error = exc_info.value.errors(include_url=False)[0]
    assert error["type"] == expected_type
    assert error["loc"] == ("tags", 0)
```

Run the focused tests with:

```bash
uv run --with 'pydantic>=2,<3' --with 'pytest>=8,<9' pytest -q tests/test_models.py
```

The tests assert stable Pydantic error `type` and `loc` values rather than
version-sensitive human-readable messages.
