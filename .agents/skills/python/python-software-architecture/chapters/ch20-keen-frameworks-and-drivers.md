# Chapter 20: The Frameworks and Drivers Layer: External Interfaces

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 2: Implementing Clean Architecture Layers (Chapter 7)

## Core Idea
The outermost layer consists of frameworks and tools like FastAPI, SQLAlchemy, Redis, and CLI libraries; in Clean Architecture, these are treated as volatile plugin details that can be replaced without modifying core business rules.

## Frameworks Introduced
- **The Plugin Architecture Pattern**:
  - When to use: Connecting infrastructure libraries (web servers, databases, third-party cloud SDKs).
  - How: Define interfaces (Ports) in the application layer. Implement concrete classes in the `infrastructure/` or `drivers/` package that plug into those interfaces.
- **Database Driver Isolation via Repository Adapters**:
  - When to use: Integrating SQLAlchemy or other ORMs.
  - How: Keep ORM models (`Table`, `Base`) strictly inside the infrastructure layer. The repository converts between ORM row objects and pure domain entities upon read and write.

## Key Concepts
- **Frameworks as Details**: The architectural principle that frameworks are delivery mechanisms, not the architecture itself.
- **Driver**: A low-level component interacting with hardware, operating systems, databases, or third-party networks.
- **Imperative Mapping**: Configuring ORM tables to map to domain classes or mapping explicitly in repository methods.
- **Composition Root**: The startup file (`main.py` or `bootstrap.py`) where drivers and adapters are instantiated and wired together.

## Mental Models
- **Frameworks Are Guests in Your House**: Don't let the guest rearrange all your furniture. Your core application sets the house rules; frameworks must adapt to them.
- **The Wall of Plugs**: Think of your core application as a device with standard USB-C ports. The database driver is just one specific cable plugged into a port.

## Anti-patterns
- **Deriving Domain Entities from Framework Base Classes**: Having domain entities inherit from `flask_sqlalchemy.Model` or Django's `models.Model`.
- **Framework Bleed**: Letting framework decorators (e.g. `@app.get()`, `@celery.task`) annotate domain functions or use case interactors.
- **Scattered Driver Initialization**: Initializing database connections, Redis clients, and third-party API clients in various service files.

## Code Examples

```python
# infrastructure/db/models.py (SQLAlchemy ORM Model - Outermost layer)
from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TaskRecord(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)

# infrastructure/db/task_repository.py (Concrete Driver Adapter)
from domain.model import Task
from application.ports import TaskRepository
from sqlalchemy.orm import Session

class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, task_id: str) -> Task | None:
        record = self._session.query(TaskRecord).filter_by(id=task_id).first()
        if not record:
            return None
        # Convert ORM row to Pure Domain Entity
        return Task(id=record.id, title=record.title, completed=record.completed)

    def save(self, task: Task) -> None:
        record = self._session.query(TaskRecord).filter_by(id=task.id).first()
        if not record:
            record = TaskRecord(id=task.id, title=task.title, completed=task.completed)
            self._session.add(record)
        else:
            record.title = task.title
            record.completed = task.completed
        self._session.commit()
```
- **What it demonstrates**: The SQLAlchemy driver lives strictly in the infrastructure layer; domain entities have zero awareness of SQLAlchemy tables or sessions.

## Reference Tables

| Layer Component | Technology Examples | Allowed Imports |
|---|---|---|
| **Web Driver** | FastAPI, Flask, Django Ninja | Interface Adapters, Application DTOs |
| **CLI Driver** | Click, Typer, Argparse | Interface Adapters, Application DTOs |
| **Database Driver**| SQLAlchemy, Tortoise, Motor, Psycopg | Domain Entities, Application Ports |
| **External Service**| Boto3, SendGrid, Stripe SDK | Application Ports, Adapters |

## Worked Example
Plugging multiple drivers into the same use case:

```python
# main_web.py (FastAPI Delivery Driver)
from fastapi import FastAPI, Depends
app = FastAPI()

@app.post("/tasks")
def create_task_endpoint(title: str, use_case: CreateTaskUseCase = Depends(get_use_case)):
    return use_case.execute(CreateTaskRequest(title))

# main_cli.py (Typer CLI Delivery Driver)
import typer
cli_app = typer.Typer()

@cli_app.command()
def create(title: str):
    use_case = get_use_case()
    result = use_case.execute(CreateTaskRequest(title))
    typer.echo(f"Created task {result.task_id}")
```
Both entry points share the identical application core, demonstrating absolute UI flexibility.

## Key Takeaways
1. Frameworks and drivers are at the outermost circle and depend on the inner layers.
2. Keep ORM model classes separate from pure domain entities.
3. Decouple delivery mechanisms (FastAPI, CLI, Lambdas) so multiple interfaces can drive the same use cases.
4. Assemble and configure drivers in a dedicated composition root at application startup.

## Connects To
- **Ch 14**: Inward Dependency Rule in practice.
- **Ch 19**: Interface Adapters act as the bridge between drivers and use cases.
- **Ch 22**: Adding web UI interfaces flexibly.
