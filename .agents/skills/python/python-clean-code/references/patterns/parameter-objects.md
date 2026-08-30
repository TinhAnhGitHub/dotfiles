# Parameter objects

## Use when

Use a parameter object when a cohesive group of fields is passed through a high-level workflow and
several helpers share its meaning: validation, cache-key creation, query building, tracking, and
filtering. The fields should describe one domain concept and change together.

## Why

A parameter object gives one place to validate related fields and derive values that must stay in
sync, such as a cache key. A frozen dataclass is a good default for trusted internal configuration:
it is immutable, comparable, and simple to construct in tests.

Keyword-only arguments improve call-site clarity, but they do not solve duplicated data shape: each
helper still repeats the same fields and can silently omit one. Keep lower-level helpers narrow; for
example, `normalize_region(region: str)` should receive only the region it normalizes, not the whole
search object, to avoid stamp coupling.

For an untrusted or external boundary, use a Pydantic `BaseModel` when runtime validation,
serialization, or JSON Schema is part of the contract. Use a frozen dataclass for trusted internal
configuration when those boundary features are unnecessary.

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
    max_results: int

params = TypeAdapter(SearchParams).validate_python(payload)
```

Keep lower-level helpers on individual values even when a parameter object coordinates the
workflow. Passing the whole object creates stamp coupling: a helper that only normalizes
`region` would become dependent on every unrelated field added to the request.

## When not to use

Do not create a parameter object for unrelated values used by one function, or for a lower-level
helper that needs only one scalar. Do not add one merely because a function has several arguments;
first confirm that the fields form a cohesive concept.

Structural pattern matching is a useful optional consumer of a parameter object, not a reason to
introduce one. Add it when named cases clarify branching; ordinary attribute access is enough for
routine query construction.

## Trade-offs

Centralizing validation and derived values reduces drift, but the object can become a grab bag if
its fields do not share a lifecycle or change axis. Immutability prevents accidental mutation while
requiring construction of a new value for changes. Pydantic adds useful validation and schema
behavior at boundaries, with more runtime machinery than a dataclass.

## Tests

Test required and default fields, invalid combinations, immutability, and stable derived cache keys.
For Pydantic models, test rejected extra fields, JSON serialization, and generated schema. Test that
lower-level helpers accept only the narrow value they need, and cover each structural-match case if
matching is used.

## Example

The [ArjanCodes parameter-object video](https://www.youtube.com/watch?v=43sDzyanzR0) and its
[2026 parameter-object examples](https://github.com/ArjanCodes/examples/tree/main/2026/param) turn
a repeated video-search parameter shape into one immutable domain value.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class VideoSearchQuery:
    query: str
    region: str = "US"
    max_results: int = 20

    @property
    def cache_key(self) -> str:
        return f"{self.query}:{self.region}:{self.max_results}"

def search_videos(search: VideoSearchQuery) -> list[Video]:
    return limit_results(execute_search(build_search_query(search)), search.max_results)
```

Adapted from [`after.py`](https://github.com/ArjanCodes/examples/blob/main/2026/param/after.py).
The high-level workflow can pass one object through validation, caching, query building, and
tracking, while a leaf helper remains focused:

```python
def build_search_query(search: VideoSearchQuery) -> dict[str, object]:
    return {"region": normalize_region(search.region), "text": search.query}

def normalize_region(region: str) -> str:
    return region.upper()
```

The lower-level function receives only `region`, avoiding stamp coupling. Structural matching is
an optional readability feature, as shown in [`pattern_matching.py`](https://github.com/ArjanCodes/examples/blob/main/2026/param/pattern_matching.py):

```python
def choose_query(search: VideoSearchQuery) -> dict[str, object]:
    match search:
        case VideoSearchQuery(sort_by="views", max_results=limit):
            return build_trending_query(limit)
        case _:
            return build_default_query(search)
```

The original repeated-signature design remains useful for comparison in
[`before.py`](https://github.com/ArjanCodes/examples/blob/main/2026/param/before.py).

## Framework examples

### Pydantic — validated external search parameters

Use `BaseModel` when request data crosses an untrusted boundary or must be rejected on unknown
fields, serialized, or published as JSON Schema. A frozen model preserves the parameter-object
contract after validation, and `computed_field` derives a cache key from validated fields.

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, computed_field

class SearchRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')

    query: str
    sort_by: Literal['relevance', 'upload_date', 'views'] = 'relevance'
    region: str = 'US'
    max_results: int = 20

    @computed_field
    @property
    def cache_key(self) -> str:
        return f'{self.query}:{self.sort_by}:{self.region}:{self.max_results}'
```

This solves the external-boundary problem that a trusted dataclass does not: runtime validation,
serialization, and schema generation are explicit. Keep downstream helpers narrow anyway, such as
`normalize_region(request.region)`, rather than passing `SearchRequest` into every helper.
Adapted from Pydantic's [model documentation](https://docs.pydantic.dev/latest/concepts/models/)
and [configuration reference](https://docs.pydantic.dev/latest/api/config/).

## ArjanCodes 2026 boundary checks (adapted)

The [2026 `clean` examples](https://github.com/ArjanCodes/examples/tree/main/2026/clean) reinforce
that a parameter object belongs at a cohesive workflow boundary. Do not pass it through every leaf
function just because it is available:

```python
def build_query(params: SearchParams) -> dict[str, str]:
    return {"q": normalize_query(params.query), "region": normalize_region(params.region)}


def normalize_region(region: str) -> str:
    return region.strip().upper()


def normalize_query(query: str) -> str:
    return query.strip()
```

The parameter object coordinates the workflow, while each helper accepts only the value it owns.
This avoids stamp coupling and keeps tests small.

The [2026 `god` examples](https://github.com/ArjanCodes/examples/tree/main/2026/god) provide the
negative pressure: a context object that accumulates every service and option becomes a god object.
Split it by lifecycle or responsibility before adding more fields.

```python
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ExportOptions:
    format: Literal["csv", "json"] = "json"
    include_headers: bool = True


def export_rows(rows: Iterable[Row], options: ExportOptions) -> str:
    return render_rows(rows, options.format, options.include_headers)
```

The existing [parameter-object video](https://www.youtube.com/watch?v=43sDzyanzR0) and [2026
`param` tree](https://github.com/ArjanCodes/examples/tree/main/2026/param) show the positive case:
repeated, cohesive search fields become one immutable value rather than a grab bag.


## zedr clean-code-python diagnostics (adapted)

The [zedr clean-code-python table of contents](https://github.com/zedr/clean-code-python#table-of-contents)
suggests two or fewer arguments as a diagnostic, not a hard limit. A parameter object is justified
when the fields describe one cohesive request and let derived work move onto the value.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class MenuConfig:
    title: str
    body: str
    button_text: str
    cancellable: bool = False


def create_menu(config: MenuConfig) -> None:
    render_menu(config.title, config.body, config.button_text)
```

Do not use a generic dictionary here: named fields make the contract searchable and validation
local. Do not bundle unrelated arguments merely to satisfy an arbitrary parameter count.
