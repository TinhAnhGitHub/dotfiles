# Parameter Object

## Intent

Group cohesive data for one high-level workflow into a named value object, so the workflow passes
one meaningful object instead of repeating a long list of related keyword arguments.

## Use when

Use a Parameter Object when several arguments travel together through a workflow, share validation
rules, or have a derived identity such as a cache key. The fields should describe one coherent
request or operation, not merely be convenient storage for unrelated values.

## Why

A parameter object removes keyword-argument duplication between validation, caching, backend-query
construction, tracking, and filtering. A frozen dataclass makes trusted internal workflow data
stable after construction; `__post_init__` can enforce invariants and a property can derive a
consistent `cache_key` from the fields that define the request.

Choose the representation by the boundary and the shape of the data:

- Use a frozen stdlib `dataclass` for trusted internal immutable values.
- Use a Pydantic `BaseModel` for external or untrusted data that needs validation, serialization,
  or a generated schema.
- Use `TypedDict` for a dict-shaped static contract; validate it at a boundary with Pydantic
  `TypeAdapter` when runtime checks are needed.
- Use a plain `dict` only for genuinely open-ended or transient data without a stable schema.

An adapted `TypedDict` boundary preserves a dict-shaped contract while adding runtime validation:

```python
from typing import TypedDict
from pydantic import TypeAdapter

class SearchParams(TypedDict):
    query: str
    region: str
    max_results: int

params = TypeAdapter(SearchParams).validate_python(payload)
```

Keep lower-level helpers on individual values even when a parameter object coordinates the
workflow. Passing the whole object creates stamp coupling: a helper that only normalizes
`region` would become dependent on every unrelated field added to the request.

## When not to use

Keep a direct function signature when there are only a few arguments or when callers use different
subsets that do not form a meaningful concept. Do not pass a large parameter object into every
lower-level helper: that creates stamp coupling, where unrelated helpers become dependent on the
whole request and change whenever an unrelated field is added.

## Trade-offs

The object is another abstraction to name, construct, and maintain. It can grow into a bag of
unrelated options, and a derived cache key can become stale if it omits a field that changes
behavior. Frozen dataclasses are lightweight but do not parse untrusted input; Pydantic adds
validation and schema behavior with additional dependency and runtime cost.

## Tests

Test blank or invalid values at construction, boundary values such as `max_results`, immutability,
and whether every behavior-changing field contributes to `cache_key`. Test the high-level workflow
with one object, and test lower-level helpers with their narrow individual-value contracts so they
do not accidentally depend on the entire parameter object.

## Example

The before/after pair shows the problem and the refactoring: repeated keyword arguments are
replaced by one cohesive `VideoSearchQuery`. The example below is adapted from [before.py](https://github.com/ArjanCodes/examples/blob/main/2026/param/before.py)
and [after.py](https://github.com/ArjanCodes/examples/blob/main/2026/param/after.py).

```python
from dataclasses import dataclass
from typing import Literal

SortOrder = Literal["relevance", "upload_date", "views"]
Duration = Literal["short", "medium", "long"]

@dataclass(frozen=True)
class VideoSearchQuery:
    query: str
    sort_by: SortOrder = "relevance"
    duration: Duration | None = None
    region: str = "US"
    include_shorts: bool = True
    max_results: int = 20

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query cannot be empty")
        if not 1 <= self.max_results <= 50:
            raise ValueError("max_results must be between 1 and 50")

    @property
    def cache_key(self) -> str:
        return ":".join(
            str(value)
            for value in (
                self.query, self.sort_by, self.duration, self.region,
                self.include_shorts, self.max_results,
            )
        )

def search_videos(search: VideoSearchQuery) -> list[Video]:
    backend_query = build_search_query(
        query=search.query,
        sort_by=search.sort_by,
        region=search.region,
        limit=search.max_results,
    )
    results = execute_search(backend_query)
    return exclude_shorts(results, search.include_shorts)

def build_search_query(*, query: str, sort_by: SortOrder,
                       region: str, limit: int) -> dict[str, object]:
    return {"text": query, "sort": sort_by, "region": region.upper(), "limit": limit}

def exclude_shorts(videos: list[Video], include_shorts: bool) -> list[Video]:
    return [video for video in videos if include_shorts or not video.is_short]
```

The condition is a workflow whose validation, cache lookup, query construction, tracking, and
post-processing all need the same search data. The object solves duplicated calls and positional
misalignment at the high-level boundary. Lower-level functions still receive individual values,
so `build_search_query()` is not coupled to filtering or future fields such as `language`.

Structural pattern matching is optional when the workflow needs readable branching on the object;
it is not a reason by itself to introduce one:

```python
def choose_query(search: VideoSearchQuery) -> dict[str, object]:
    match search:
        case VideoSearchQuery(sort_by="views", max_results=limit):
            return build_trending_query(limit)
        case VideoSearchQuery(sort_by="upload_date"):
            return build_recent_query()
        case _:
            return build_default_query()
```

This is adapted from [pattern_matching.py](https://github.com/ArjanCodes/examples/blob/main/2026/param/pattern_matching.py)
and the accompanying [ArjanCodes Parameter Object video](https://www.youtube.com/watch?v=43sDzyanzR0).

## Framework examples

### Pydantic — `BaseModel` at an external boundary

Yes, a Parameter Object can be Pydantic. Use a Pydantic `BaseModel` when the object is created from
external, untrusted, or schema-driven data and needs parsing, validation, serialization, and
unknown-field policy. For trusted internal workflow data, the frozen dataclass above is usually the
smaller and faster choice.

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, computed_field, field_validator

class VideoSearchRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')

    query: str
    sort_by: Literal["relevance", "upload_date", "views"] = "relevance"
    duration: Literal["short", "medium", "long"] | None = None
    max_results: int = 20

    @field_validator("query")
    @classmethod
    def non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query cannot be empty")
        return value

    @field_validator("max_results")
    @classmethod
    def bounded(cls, value: int) -> int:
        if not 1 <= value <= 50:
            raise ValueError("max_results must be between 1 and 50")
        return value

    @computed_field
    @property
    def cache_key(self) -> str:
        return f"{self.query}:{self.sort_by}:{self.duration}:{self.max_results}"
```

This solves the problem of accepting an HTTP, JSON, or configuration payload without allowing
silently ignored fields or invalid search limits into the workflow. `BaseModel` fits the external
boundary because it turns untrusted input into a validated, immutable parameter object; the
computed `cache_key` keeps cache identity derived from the validated values. See the official
[Pydantic models documentation](https://docs.pydantic.dev/latest/concepts/models/) and
[configuration API](https://docs.pydantic.dev/latest/api/config/).
