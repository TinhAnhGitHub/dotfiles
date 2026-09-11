# Chapter 19: The Interface Adapters Layer: Controllers and Presenters

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 2: Implementing Clean Architecture Layers (Chapter 6)

## Core Idea
Interface Adapters translate data between the format most convenient for use cases and entities and the format most convenient for external agencies like web frameworks, databases, and user interfaces.

## Frameworks Introduced
- **The Controller-Presenter-ViewModel Triad**:
  - When to use: When rendering responses for diverse clients (REST APIs, HTML pages, mobile apps) without polluting use cases with formatting rules.
  - How:
    - **Controller**: Parses incoming request, maps it to a `RequestDTO`, calls the Use Case.
    - **Presenter**: Implements the Output Port callback; formats the `ResponseDTO` into a presentation-friendly `ViewModel` (formatting currencies, localized dates, masks).
    - **ViewModel**: A pure data structure containing display strings ready for immediate template rendering or JSON serialization.
- **Gateway Pattern**:
  - When to use: Wrapping third-party APIs or database connections to satisfy an Output Port.
  - How: Implement the domain's abstract repository or service interface, translating between domain entities and external SDK data models.

## Key Concepts
- **Interface Adapter**: A component converting data from the external format to the internal use case format, and vice-versa.
- **Controller**: Accepts external input and translates it into use case invocations.
- **Presenter**: Formats use case output data for presentation.
- **ViewModel**: Display-ready data structure containing string representations of dates, currencies, and UI flags.
- **Boundary Crossing**: The mechanism of passing data across architectural layers while respecting the Dependency Rule.

## Mental Models
- **Interface Adapters as Language Translators**: The use case speaks "Business English". The database speaks "SQL". The client speaks "HTTP JSON". Adapters translate between them at the border.
- **Presenters Keep Controllers Dumb**: Controllers shouldn't decide if an error is displayed as a toast or a red label, or format `$1,200.50`; presenters prepare the exact strings.

## Anti-patterns
- **Formatting Logic in Use Cases**: Writing `f"${amount:,.2f}"` or formatting dates inside use case interactors.
- **Direct ORM Exposure**: Returning SQLAlchemy model instances directly through API controllers.
- **Bypassing the Presenter in Complex UIs**: Stuffing complex UI conditional logic into Jinja2 templates or React components instead of computing it in a Presenter.

## Code Examples

```python
from dataclasses import dataclass
from typing import Protocol
from datetime import datetime

# 1. Output DTO from Use Case
@dataclass(frozen=True)
class OrderResponseDTO:
    order_id: str
    total_amount: float
    created_at: datetime
    is_delivered: bool

# 2. ViewModel: Tailored strictly for the UI
@dataclass(frozen=True)
class OrderViewModel:
    order_number: str
    formatted_total: str
    formatted_date: str
    status_color: str
    status_label: str

# 3. Presenter: Translates DTO into ViewModel
class OrderPresenter:
    def present(self, response: OrderResponseDTO) -> OrderViewModel:
        return OrderViewModel(
            order_number=f"#{response.order_id.upper()}",
            formatted_total=f"${response.total_amount:,.2f}",
            formatted_date=response.created_at.strftime("%b %d, %Y"),
            status_color="green" if response.is_delivered else "orange",
            status_label="Delivered" if response.is_delivered else "In Progress",
        )

# 4. Controller: Thin orchestrator
class OrderWebController:
    def __init__(self, use_case, presenter: OrderPresenter):
        self._use_case = use_case
        self._presenter = presenter

    def get_order_details(self, order_id: str) -> dict:
        dto = self._use_case.execute(order_id)
        view_model = self._presenter.present(dto)
        return view_model.__dict__
```
- **What it demonstrates**: Complete separation between Use Case output (`OrderResponseDTO`), Presenter formatting logic, and the resulting UI-ready `OrderViewModel`.

## Reference Tables

| Component | Input | Output | Primary Role |
|---|---|---|---|
| **Controller** | HTTP / CLI / Event | Request DTO | Ingests input, calls use case |
| **Gateway** | Entity / Domain call | SQL / HTTP API | Implements output port for external systems |
| **Presenter** | Response DTO | View Model | Formats data for display/serialization |
| **View Model** | Formatted data | Template / JSON | Render-ready data bundle |

## Worked Example
Decoupling an API response from web framework conventions:

```python
# FastAPI Route delegating to Controller and Presenter
@router.get("/orders/{order_id}", response_model=OrderViewModel)
def get_order_endpoint(
    order_id: str,
    controller: OrderWebController = Depends(get_order_controller)
):
    try:
        return controller.get_order_details(order_id)
    except OrderNotFoundException:
        raise HTTPException(status_code=404, detail="Order not found")
```
If you switch from FastAPI to a command-line terminal client, you can reuse `OrderPresenter` or introduce a `CliOrderPresenter` while the use case remains 100% untouched.

## Key Takeaways
1. Interface Adapters isolate the application core from the specifics of frameworks, databases, and UI tools.
2. Use Controllers to translate incoming requests into use case DTOs.
3. Use Presenters to convert use case responses into display-ready View Models.
4. Keep controllers and web endpoints completely free of business logic and data formatting.

## Connects To
- **Ch 18**: How Use Cases hand off data to Presenters.
- **Ch 20**: Integrating interface adapters with frameworks and drivers.
- **Ch 35**: Ronald Mak's Adapter pattern applied at the system architecture level.
