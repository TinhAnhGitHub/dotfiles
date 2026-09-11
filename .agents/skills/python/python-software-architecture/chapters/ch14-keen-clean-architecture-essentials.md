# Chapter 14: Clean Architecture Essentials: Transforming Python Development

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 1: Foundations of Clean Architecture in Python (Chapter 1)

## Core Idea
Clean Architecture organizes software into concentric layers where dependencies point strictly inward toward high-level business rules, freeing core logic from external frameworks, databases, and UI delivery mechanisms.

## Frameworks Introduced
- **The Onion / Concentric Ring Architecture**:
  - When to use: When developing scalable systems that must survive database migrations, framework deprecations, and changing external requirements.
  - How: Organize code into four primary layers:
    1. **Enterprise Business Rules (Entities / Domain)** — Center
    2. **Application Business Rules (Use Cases)**
    3. **Interface Adapters (Controllers, Presenters, Gateways)**
    4. **Frameworks & Drivers (Web, DB, Devices, External APIs)** — Outermost
  - **The Dependency Rule**: Source code dependencies must point only inward. Nothing in an inner circle can know anything about something in an outer circle.
- **The Planning-Agility Balance Framework**:
  - When to use: Deciding how much architectural scaffolding to introduce at early project phases.
  - How: Start with explicit domain boundaries and ports without premature microservice decomposition; clean modular architecture maximizes future agility by keeping options open.

## Key Concepts
- **Dependency Rule**: The absolute architectural invariant that inner layers have zero knowledge of outer layers.
- **Independence of Frameworks**: Architecture does not depend on the existence of some library of feature-laden software (e.g. Django or FastAPI are plugins, not the foundation).
- **Testability**: Business rules can be tested without the UI, database, web server, or any other external element.
- **Independence of UI**: The UI can change easily without changing the rest of the system (e.g. swapping a CLI for a Web interface).
- **Independence of Database**: Swapping PostgreSQL for MongoDB or SQLite doesn't touch business rules.

## Mental Models
- **Think of Frameworks as Ephemeral Tools, Not Foundations**: Your application is not a "FastAPI application"; it is a "Healthcare Management application" that happens to expose a FastAPI web port.
- **Concentric Circles of Stability**: The center (domain) changes only when business policy changes; the outer rim (drivers) changes whenever technology libraries change.

## Anti-patterns
- **Framework-Bound Architecture**: Structuring the entire project directory around Django (`models.py`, `views.py`, `urls.py`) where domain logic is scattered across view functions and ORM hooks.
- **Inward-Pointing Contamination**: Importing database models or HTTP request objects inside use case or entity classes.
- **Premature Distributed Architecture**: Jumping straight to microservices and Kubernetes before establishing clean modular boundaries in a monolithic codebase.

## Code Examples

```python
# Demonstrating the Dependency Rule in pure Python

# 1. Core Domain Layer (No external imports)
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Task:
    id: str
    title: str
    completed: bool = False
    created_at: datetime = datetime.now()

    def complete(self) -> "Task":
        return Task(self.id, self.title, completed=True, created_at=self.created_at)

# 2. Application Layer (Knows only Domain)
from typing import Protocol

class TaskRepository(Protocol):
    def get_by_id(self, task_id: str) -> Task | None:
        ...
    def save(self, task: Task) -> None:
        ...

class CompleteTaskUseCase:
    def __init__(self, repo: TaskRepository):
        self._repo = repo

    def execute(self, task_id: str) -> Task:
        task = self._repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        completed_task = task.complete()
        self._repo.save(completed_task)
        return completed_task
```
- **What it demonstrates**: The inner domain (`Task`) and application use case (`CompleteTaskUseCase`) depend only on a standard Python `Protocol`, with zero framework or database dependencies.

## Reference Tables

| Architectural Layer | Typical Components | What It Knows About |
|---|---|---|
| **1. Domain (Entities)** | Entities, Value Objects, Domain Exceptions | Absolutely nothing outside itself |
| **2. Application (Use Cases)**| Use Case Interactors, Input/Output Ports | Only Domain Entities |
| **3. Interface Adapters** | Controllers, Presenters, Gateways, DTOs | Application & Domain |
| **4. Frameworks & Drivers** | FastAPI, SQLAlchemy, CLI, Redis, Boto3 | Adapters, Application, Domain |

## Worked Example
Separating a task completion feature from a web framework:

Before (Fat FastAPI Endpoint):
```python
# Tightly coupled: domain rules, db queries, and HTTP response merged
@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404)
    task.completed = True
    db.commit()
    return {"id": task.id, "status": "completed"}
```

After (Clean Architecture):
```python
# Interface Adapter (FastAPI Driver) delegates to Use Case
@app.post("/tasks/{task_id}/complete")
def complete_task_endpoint(
    task_id: str,
    use_case: CompleteTaskUseCase = Depends(get_complete_task_use_case)
):
    try:
        task = use_case.execute(task_id)
        return {"id": task.id, "completed": task.completed}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```
Now `CompleteTaskUseCase` can be run from a CLI script, a cron job, or tested with an in-memory repository without spinning up FastAPI.

## Key Takeaways
1. Source code dependencies must strictly point inward toward business rules.
2. High-level policy must never depend on low-level technological details.
3. Frameworks, databases, and user interfaces are external details and plugins.
4. Business logic should be testable without starting a web server or database.

## Connects To
- **Ch 15**: SOLID principles that form the foundations of Clean Architecture.
- **Ch 18**: Detailed design of Use Case Interactors in the Application Layer.
- **Ch 20**: Managing Frameworks and Drivers cleanly at the perimeter.
