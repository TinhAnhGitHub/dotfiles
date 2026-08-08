# User API Models

These examples target stable Pydantic v2 APIs. The evaluation workspace has no
project dependency files; its available Python 3.12.3 environment does not have
Pydantic or pytest installed. The snippets were verified in an ephemeral uv
environment with eight focused tests passing.

This is a create-style request: `id` is assigned by the server and appears on
the response. Any request model that accepts an ID should use the same
`UserId` alias.

## `models.py`

```python
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


UserId = Annotated[int, Field(strict=True)]
NonEmptyTag = Annotated[str, Field(strict=True, min_length=1)]


class UserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # No default makes this field required; the union still permits JSON null.
    nickname: str | None
    tags: list[NonEmptyTag] = Field(default_factory=list)


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UserId
    nickname: str | None
    tags: list[NonEmptyTag]
```

`UserId` rejects values such as `"42"` (and `True`) instead of coercing them to
an integer. `NonEmptyTag` is the item type of the list, so each item must be a
string with length at least one; the list itself is not merely constrained as a
whole. `tags` is optional on the create request and gets a fresh empty list per
instance, but it is required in a response. There are no aliases or custom
serializers; `model_dump()` and `model_dump_json()` use the declared field names.

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


def test_response_accepts_an_integer_id_and_valid_tags() -> None:
    user = UserResponse.model_validate(
        {"id": 42, "nickname": "Ada", "tags": ["admin", "beta"]}
    )

    assert user.model_dump() == {
        "id": 42,
        "nickname": "Ada",
        "tags": ["admin", "beta"],
    }


@pytest.mark.parametrize("bad_id", ["42", True])
def test_response_id_rejects_non_strict_ids(bad_id: object) -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserResponse.model_validate(
            {"id": bad_id, "nickname": "Ada", "tags": ["admin"]}
        )

    error = exc_info.value.errors(include_url=False)[0]
    assert error["type"] == "int_type"
    assert error["loc"] == ("id",)


@pytest.mark.parametrize(
    ("bad_tags", "error_type", "error_loc"),
    [
        ([""], "string_too_short", ("tags", 0)),
        (["admin", ""], "string_too_short", ("tags", 1)),
        ([123], "string_type", ("tags", 0)),
    ],
)
def test_each_tag_must_be_a_non_empty_string(
    bad_tags: list[object], error_type: str, error_loc: tuple[object, ...]
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        UserRequest.model_validate({"nickname": "Ada", "tags": bad_tags})

    error = exc_info.value.errors(include_url=False)[0]
    assert error["type"] == error_type
    assert error["loc"] == error_loc
```

Run the focused tests in a project environment with:

```bash
PYTHONPATH=. uv run --with 'pydantic>=2,<3' --with 'pytest>=8,<9' pytest -q tests/test_models.py
```

The tests assert Pydantic's machine-oriented error `type` and the model field
locations, rather than human-readable error messages.
