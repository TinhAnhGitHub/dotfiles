# Chapter 3: A Brief Interlude: On Coupling and Abstractions

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part I: Building an Architecture to Support Domain Modeling

## Core Idea
Coupling is the cost of software change; by introducing the right abstractions and separating core domain rules from external effects, systems become resilient to changes in infrastructure and requirements.

## Frameworks Introduced
- **The Abstraction Choice Framework**:
  - When to use: When deciding how to separate domain logic from external systems (filesystem, external APIs, notifications).
  - How:
    1. Identify the core logic (computations, decisions).
    2. Identify stateful interactions or I/O side-effects.
    3. Define an explicit abstraction representing the effect.
    4. Inject the abstraction rather than calling external systems directly.
- **Fakes vs. Mocks in Edge-to-Edge Testing**:
  - When to use: When deciding testing strategy across architectural boundaries.
  - How: Favor *Fakes* (working in-memory implementations of an interface) over *Mocks* (`unittest.mock.patch`). Mocks bind tests to internal implementation details, whereas Fakes verify behavior through the public contract.

## Key Concepts
- **Coupling**: The degree of interdependence between software modules. High coupling means changing one module breaks another.
- **Cohesion**: The degree to which elements within a single module belong together.
- **Edge-to-Edge Testing**: Testing a full workflow from the entry point to the system boundary using fake adapters instead of mocks.
- **Monkeypatching / Patching**: Replacing runtime objects or functions with mock doubles using `patch()`; fragile when refactoring internal names.

## Mental Models
- **Think of Abstractions as Sockets**: The domain code expects a standard socket; production plugs in an electrical cable (real I/O), while tests plug in a battery (fake adapter).
- **Mocks Couple Tests to Implementation; Fakes Couple Tests to Interfaces**: When you refactor a method name, mocks silently break or give false passes; fakes enforce interface compliance.

## Anti-patterns
- **Mocking What You Don't Own**: Mocking external third-party library internals (e.g. `requests.post` or SQLAlchemy internals) instead of wrapping them in your own adapter.
- **Leaky Abstractions**: An abstraction that forces callers to understand its underlying implementation (e.g. exposing SQL cursors from a repository).
- **Over-Abstraction**: Introducing generic interfaces for things that will never have more than one implementation or will never need testing in isolation.

## Code Examples

```python
# Synchronizing two file directories: Coupling vs. Clean Abstraction
import os
import shutil
from pathlib import Path
from typing import Dict

# Uncoupled Domain Decision:
def determine_actions(
    source_hashes: Dict[str, str], dest_hashes: Dict[str, str]
) -> tuple[list[str], list[str], list[str]]:
    to_copy = []
    to_delete = []
    to_update = []
    for path, sha in source_hashes.items():
        if path not in dest_hashes:
            to_copy.append(path)
        elif dest_hashes[path] != sha:
            to_update.append(path)
    for path in dest_hashes:
        if path not in source_hashes:
            to_delete.append(path)
    return to_copy, to_update, to_delete
```
- **What it demonstrates**: Separating domain computation (figuring out which files need copying/deleting) from the filesystem I/O (`shutil.copy`).

## Reference Tables

| Criteria | Mocks (`unittest.mock`) | Fakes (`FakeRepository`, `FakeStorage`) |
|---|---|---|
| **Coupling** | High (coupled to internal function calls) | Low (coupled only to the abstract interface) |
| **Refactoring Safety** | Poor (renaming internal methods breaks tests) | High (interface contract preserved) |
| **Execution Speed** | Fast | Fast |
| **Fidelity** | Low (mocks return whatever they are told) | High (fakes preserve realistic state transitions) |

## Worked Example
Testing the file synchronization logic without creating temporary folders or disk I/O:

```python
def test_detects_new_and_modified_files():
    source = {"file1.txt": "hash_a", "file2.txt": "hash_b"}
    dest = {"file1.txt": "hash_a_old"}
    
    to_copy, to_update, to_delete = determine_actions(source, dest)
    
    assert to_copy == ["file2.txt"]
    assert to_update == ["file1.txt"]
    assert to_delete == []
```
Notice how disk I/O and hash calculations are entirely decoupled from the core synchronization decision.

## Key Takeaways
1. Separate core business logic from stateful I/O side effects.
2. Design abstractions around what the caller needs, not how the provider works.
3. Prefer in-memory fakes over monkeypatching to make tests refactor-proof.
4. Only abstract when you need to decouple for testability or varied implementations.

## Connects To
- **Ch 2**: Repository is a prime example of an abstraction over state.
- **Ch 4**: Service layer acts as the orchestrator combining abstractions.
- **Ch 30**: Ronald Mak's principles of encapsulation and information hiding.
