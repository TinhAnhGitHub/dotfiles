# Chapter 22: Adding Web UI: Clean Architecture’s Interface Flexibility

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 3: Advanced Practices and Real-World Application (Chapter 9)

## Core Idea
Clean Architecture allows you to swap or add entirely new user interfaces (HTML templates, single-page app APIs, or command lines) without modifying a single line of business logic in the application or domain layers.

## Frameworks Introduced
- **Multi-Delivery Interface Pattern**:
  - When to use: When a system needs to support multiple client formats simultaneously (e.g. server-side rendered HTML via Jinja2 and JSON API for mobile apps).
  - How:
    1. Keep Use Case Interactors strictly format-agnostic.
    2. Build distinct Presenters: `HtmlOrderPresenter` producing template context dicts, and `JsonOrderPresenter` producing REST response dicts.
    3. Expose distinct Controllers or routes for each delivery mechanism.
- **UI Independence Principle**:
  - When to use: Guiding architectural decisions when web design trends shift.
  - How: Treat web presentation as a peripheral detail; business workflows remain immutable regardless of whether the client is Jinja2, HTMX, React, or a terminal CLI.

## Key Concepts
- **Delivery Mechanism**: The transport and display medium (HTTP/HTML, REST, GraphQL, gRPC, CLI).
- **Presentation Model**: A data model specifically structured for the quirks of a particular UI template engine or client framework.
- **Server-Side Rendering (SSR)**: Rendering HTML pages on the server (e.g. Jinja2/HTMX).
- **Decoupled Controllers**: Controllers that handle request routing and dispatch without containing rendering logic.

## Mental Models
- **The Core Application Is a Headless Service**: The business core is naturally headless; any UI (web, mobile, CLI) is just an interchangeable head bolted onto the body.
- **Templates Are Outer Shells**: Jinja2 templates live in the Frameworks & Drivers layer. They receive View Models prepared by Presenters and never call domain objects directly.

## Anti-patterns
- **Calling Repositories Inside Jinja Templates**: Passing domain entities with lazy-loaded relationships into templates, triggering unexpected N+1 database queries during rendering.
- **Coupling Use Cases to HTML Forms**: Designing Use Case inputs to match the field names of a specific HTML form or file upload payload.
- **Rewriting Business Logic for Mobile APIs**: Reimplementing business rules in a new API controller when adding a mobile app alongside an existing web app.

## Code Examples

```python
# 1. Shared Use Case Output
@dataclass(frozen=True)
class AccountBalanceDTO:
    account_number: str
    balance: float
    currency: str

# 2. Presenter for Server-Side HTML Rendering (Jinja2)
class HtmlAccountPresenter:
    def present(self, dto: AccountBalanceDTO) -> dict:
        return {
            "account_title": f"Account {dto.account_number}",
            "display_balance": f"{dto.currency} {dto.balance:,.2f}",
            "balance_class": "text-success" if dto.balance >= 0 else "text-danger",
        }

# 3. Presenter for REST API (JSON)
class JsonAccountPresenter:
    def present(self, dto: AccountBalanceDTO) -> dict:
        return {
            "account_id": dto.account_number,
            "balance": dto.balance,
            "currency": dto.currency,
        }

# 4. Web Endpoints (Drivers) sharing the same use case!
@app.get("/web/accounts/{acc_id}", response_class=HTMLResponse)
def account_page(acc_id: str, request: Request, use_case=Depends(get_use_case)):
    dto = use_case.execute(acc_id)
    context = HtmlAccountPresenter().present(dto)
    return templates.TemplateResponse("account.html", {"request": request, **context})

@app.get("/api/v1/accounts/{acc_id}")
def account_api(acc_id: str, use_case=Depends(get_use_case)):
    dto = use_case.execute(acc_id)
    return JsonAccountPresenter().present(dto)
```
- **What it demonstrates**: Two completely different delivery mechanisms (HTML and REST API) cleanly sharing the exact same use case through specialized Presenters.

## Reference Tables

| Delivery Mode | Transport | Presenter Role | Primary Consumer |
|---|---|---|---|
| **SSR Web (Jinja/HTMX)** | HTTP GET/POST | Builds template context dicts | Browser DOM |
| **REST / JSON API** | HTTP POST/PUT/DELETE | Serializes to standard JSON DTO | Mobile App / SPA |
| **CLI (Typer/Click)** | Standard Streams | Formats terminal tables / colors | Developer / DevOps |
| **Background Worker** | Redis / Celery | Serializes log/event payload | Async Worker Queue |

## Worked Example
Adding an HTMX inline edit feature without altering the use case:
1. Existing Use Case: `UpdateTaskTitleUseCase(task_id, new_title)`
2. REST Endpoint: returns JSON `{id: "1", title: "New"}`
3. New HTMX Endpoint:
```python
@app.put("/htmx/tasks/{task_id}/title", response_class=HTMLResponse)
def htmx_update_title(task_id: str, title: str = Form(...), use_case=Depends(get_use_case)):
    dto = use_case.execute(UpdateTaskTitleRequest(task_id, title))
    # Return a partial HTML snippet for HTMX DOM replacement
    return f"<span id='task-{dto.id}' class='task-title'>{dto.title}</span>"
```
The core use case did not know or care that HTMX was introduced.

## Key Takeaways
1. Keep use case interactors completely delivery-agnostic.
2. Build dedicated Presenters for each client format (HTML, JSON, CLI).
3. Do not pass domain entities directly into UI templates; use View Models.
4. Multiple interfaces can drive the same application core simultaneously.

## Connects To
- **Ch 14**: Clean Architecture's independence of UI principle.
- **Ch 19**: Detailed breakdown of Presenters and View Models.
- **Ch 20**: Managing Web Frameworks as external details.
