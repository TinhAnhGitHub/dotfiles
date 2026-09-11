# Chapter 24: Legacy to Clean: Refactoring Python for Maintainability

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 3: Advanced Practices and Real-World Application (Chapter 11)

## Core Idea
Migrating legacy Python codebases to Clean Architecture should not be done via high-risk big-bang rewrites; instead, use the Strangler Fig pattern and Anti-Corruption Layers to incrementally carve out clean boundaries around high-value features.

## Frameworks Introduced
- **The Strangler Fig Migration Pattern**:
  - When to use: Replacing a legacy monolithic application with Clean Architecture.
  - How:
    1. Intercept incoming requests at the perimeter (reverse proxy or API gateway).
    2. Direct new features or selected routes to the new Clean Architecture module.
    3. Old routes continue hitting the legacy codebase.
    4. Gradually migrate legacy routes until the legacy system is completely strangled and decommissioned.
- **Anti-Corruption Layer (ACL)**:
  - When to use: When the new Clean Architecture system must interact with the legacy database or legacy services without adopting their messy schemas.
  - How: Build an adapter between the legacy system and the new domain model that translates legacy dictionaries/models into clean domain entities.

## Key Concepts
- **Brownfield Development**: Building new software on top of or alongside existing legacy systems.
- **Seam**: A place where you can alter behavior in a program without editing source code in that place (Michael Feathers).
- **Anti-Corruption Layer (ACL)**: A translation layer that prevents legacy concepts and bad design from leaking into a clean domain model.
- **Characterization Tests**: Tests written against legacy code to capture its current observable behavior before refactoring begins.

## Mental Models
- **Strangler Fig Vines**: Like a fig tree that grows around an old host tree until the host tree dies, the clean architecture grows around the legacy system until the legacy system can be unplugged.
- **ACL as Hazmat Quarantine**: The legacy database has messy columns and unvalidated nulls; the ACL is a decontamination airlock where data is scrubbed into pristine domain entities before entering the clean core.

## Anti-patterns
- **The Big Bang Rewrite**: Halting all feature development for 12 months to rewrite the application from scratch; almost always fails or goes over budget.
- **Leaking Legacy Models into New Code**: Importing legacy Django ORM models directly into the new use cases, instantly contaminating the new architecture.
- **Refactoring Without Characterization Tests**: Changing legacy code before having automated tests that lock down existing behavior.

## Code Examples

```python
# Anti-Corruption Layer (ACL) protecting the new Clean Domain from legacy chaos

# 1. Legacy Mess: Untyped, inconsistent dictionary from legacy system
legacy_customer_row = {
    "CUST_NUM": "98124",
    "F_NAME": "Alice",
    "L_NAME": "Smith",
    "STAT": 1,  # 1 means active, 0 inactive, -1 suspended
    "STREET_1": "123 Main St",
    "ZIP": "94105",
}

# 2. New Clean Domain Entity
@dataclass(frozen=True)
class Customer:
    id: str
    full_name: str
    is_active: bool
    postal_code: str

# 3. Anti-Corruption Adapter (Port Implementation)
class LegacyCustomerAclAdapter:
    def __init__(self, legacy_db_connection):
        self._db = legacy_db_connection

    def get_customer(self, customer_id: str) -> Customer | None:
        raw_data = self._db.query_legacy_table(customer_id)
        if not raw_data:
            return None
        # Translate and sanitize into pristine domain entity
        return Customer(
            id=str(raw_data["CUST_NUM"]),
            full_name=f"{raw_data['F_NAME']} {raw_data['L_NAME']}",
            is_active=(raw_data["STAT"] == 1),
            postal_code=str(raw_data["ZIP"]),
        )
```
- **What it demonstrates**: An Anti-Corruption Layer translating legacy data structures into clean domain models, protecting new code from legacy contamination.

## Reference Tables

| Strategy | Big Bang Rewrite | Strangler Fig + ACL |
|---|---|---|
| **Risk Level** | Extremely High | Low & Incremental |
| **Business Value Delivery**| Deferred until full launch | Continuous on every sprint |
| **Rollback Option** | All-or-nothing | Route-by-route at API gateway |
| **Architecture Purity** | High initially, but vulnerable | High in new modules via ACL |

## Worked Example
Step-by-step refactoring of an untestable script into a clean use case:
1. **Step 1**: Write Characterization Tests asserting the script's output given fixed test inputs.
2. **Step 2**: Identify the Seam (e.g. where the script fetches data vs. where it calculates prices).
3. **Step 3**: Extract pure calculation into a Domain Entity with zero I/O.
4. **Step 4**: Wrap the legacy database query in an ACL repository.
5. **Step 5**: Write a Use Case Interactor orchestrating the ACL and Domain Entity.
6. **Step 6**: The original script now becomes a 3-line wrapper calling the new Use Case.

## Key Takeaways
1. Never attempt a big-bang rewrite of a functioning legacy system.
2. Use the Strangler Fig pattern to migrate feature-by-feature via API routing.
3. Insulate new Clean Architecture modules using Anti-Corruption Layers.
4. Lock down legacy behavior with characterization tests before refactoring.

## Connects To
- **Ch 11**: Percival's microservice migration strategies.
- **Ch 14**: Re-establishing the Dependency Rule in brownfield code.
- **Ch 35**: Ronald Mak's Adapter and Facade patterns.
