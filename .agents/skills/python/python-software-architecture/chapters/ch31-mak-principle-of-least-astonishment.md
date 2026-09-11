# Chapter 31: Don’t Surprise Your Users

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 3: Design the Application Right (Chapter 6)

## Core Idea
The Principle of Least Astonishment (POLA) dictates that software components, APIs, and classes should behave in the manner users and fellow programmers naturally expect, adhering to standard Python idioms and conventions.

## Frameworks Introduced
- **The POLA Design Audit Checklist**:
  - When to use: Reviewing APIs, class interfaces, and function signatures.
  - How: Verify against four expectations:
    1. **Predictable Side Effects**: A function named `get_x()` or `calculate_y()` must not mutate state or perform network I/O.
    2. **Idiomatic Return Types**: Methods return standard types or raise standard exceptions; never return `False` on error when callers expect exceptions.
    3. **Pythonic Conventions**: Implement magic methods (`__len__`, `__iter__`, `__repr__`) when classes represent collections or quantifiable concepts.
    4. **Consistent Signatures**: Order parameters consistently across related methods (e.g. always `(source, destination)`, never alternating).

## Key Concepts
- **Principle of Least Astonishment (POLA)**: If a design feature has a high degree of surprise for a reasonable user or programmer, redesign it.
- **Pythonic Idiom**: Writing code that follows established Python community norms (e.g. PEP 8, duck typing, context managers, rich comparisons).
- **Silent Failure**: Swallowing exceptions or returning `None` instead of raising an informative error.
- **Defensive API Design**: Designing interfaces so that common mistakes are either prevented or surfaced immediately with clear messages.

## Mental Models
- **The Door Handle Analogy (Norman Doors)**: If a door has a handle, you pull it; if it has a flat plate, you push it. A door with a handle that requires pushing violates POLA. Class methods should match their visual and semantic handles.
- **Surprise Is a Bug**: Every time a developer reading your code says "Wait, why does it do that?", you have discovered an architectural defect.

## Anti-patterns
- **Hidden Side Effects**: A query method `get_total()` that silently clears the shopping cart or logs into a remote database.
- **Returning Error Codes Instead of Exceptions**: Returning `-1` or `None` on failure, forcing callers to write endless `if res == -1:` checks.
- **Inconsistent Parameter Ordering**: Having `copy(src, dest)` and `move(dest, src)` in the same module.
- **Mutable Default Arguments**: Writing `def add_item(item, items=[])`, where the list persists across function invocations.

## Code Examples

```python
# Astonishing API (Anti-pattern)
class ShoppingCart:
    def __init__(self):
        self.items = []

    def total(self) -> float:
        # Astonishing! A query method that has a hidden mutation side effect!
        self.items = [i for i in self.items if i.is_valid]
        return sum(i.price for i in self.items)

    def find_item(self, name: str):
        # Astonishing! Returns -1 instead of None or raising KeyError
        for i in self.items:
            if i.name == name:
                return i
        return -1

# Least Astonishing API (Pythonic & Predictable)
class CleanShoppingCart:
    def __init__(self):
        self._items: list = []

    def __len__(self) -> int:
        # Idiomatic Python: len(cart) works naturally!
        return len(self._items)

    def __iter__(self):
        # Idiomatic Python: for item in cart works naturally!
        return iter(self._items)

    def calculate_total(self) -> float:
        # Pure query; zero mutation side-effects
        return sum(item.price for item in self._items)

    def get_item(self, name: str):
        for item in self._items:
            if item.name == name:
                return item
        raise KeyError(f"Item '{name}' not found in cart")
```
- **What it demonstrates**: Eliminating hidden mutations and non-standard return codes in favor of Python magic methods (`__len__`, `__iter__`) and standard exceptions.

## Reference Tables

| Practice | Astonishing (Avoid) | Least Astonishing (Prefer) |
|---|---|---|
| **Query Methods** | Modifies object state | Pure query; zero side effects |
| **Missing Lookup** | Returns `-1` or `False` | Raises `KeyError` or returns `None` |
| **Collection Length** | `cart.get_number_of_items()` | `__len__()` -> `len(cart)` |
| **Display String** | Default `<Object at 0x7f...>` | Implements clean `__repr__` and `__str__` |
| **Default Arguments** | `def func(lst=[])` | `def func(lst=None): lst = lst or []` |

## Worked Example
Redesigning a file parser to adhere to POLA:
- *Astonishing Behavior*: Calling `parser.read_records()` reads the file and closes it, so calling it a second time raises `ValueError: I/O operation on closed file`.
- *Refactored Behavior*:
```python
class RecordParser:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self) -> list[dict]:
        # Opens and closes file within a context manager on every parse call
        with open(self.filepath, "r", encoding="utf-8") as f:
            return [self._parse_line(line) for line in f]
```
Now callers can invoke `.parse()` repeatedly without surprising I/O closures.

## Key Takeaways
1. Design APIs so their behavior matches the natural expectations of Python developers.
2. Query methods must never produce hidden state-mutating side effects.
3. Use Python magic methods (`__len__`, `__iter__`, `__getitem__`) to make custom classes behave like native objects.
4. Raise standard exceptions rather than returning cryptic sentinel values (`-1`, `False`).

## Connects To
- **Ch 30**: Encapsulation and clean interface design.
- **Ch 32**: Designing subclasses that do not surprise callers (Liskov Substitution).
- **Ch 16**: Type-enhanced Python for clear method contracts.
