# Chapter 23: Implementing Observability: Monitoring and Verification

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 3: Advanced Practices and Real-World Application (Chapter 10)

## Core Idea
Observability (structured logging, tracing, and metrics) should be implemented at architectural boundaries using decorators, middleware, or interface adapters without tangling telemetry code into core business logic.

## Frameworks Introduced
- **The Boundary Telemetry Pattern**:
  - When to use: Instrumenting applications with distributed tracing, latency metrics, and audit logging.
  - How: Wrap Use Case Interactors using Python decorators or Interceptor patterns. Telemetry captures execution time, input parameters, and errors at the boundary, leaving core use cases pure.
- **Three Pillars of Observability at Boundaries**:
  - **Structured Logging**: Emit contextual JSON logs with correlation IDs (`trace_id`, `use_case`).
  - **Metrics**: Measure duration, throughput, and error rates at use case entry points.
  - **Distributed Tracing**: Propagate trace contexts across service and layer boundaries.

## Key Concepts
- **Boundary Instrumentation**: Placing monitoring hooks at the ports and adapters perimeter rather than inside domain entities.
- **Trace Context / Correlation ID**: A unique identifier passed through all layers and external calls to correlate a single transaction.
- **Decorator / Interceptor**: A Python wrapper modifying use case behavior (measuring execution time, catching errors) transparently.
- **Clean Logging**: Logging business facts at the application boundary rather than polluting domain classes with logger instances.

## Mental Models
- **Security Cameras at the Borders, Not in the Kitchen**: You don't put security cameras inside the soup bowl (domain entity); you put them at the entrance and exit doors (use case boundaries and HTTP adapters).
- **Separation of Concerns for Telemetry**: A business rule calculates taxes; it should not know about Prometheus histograms or OpenTelemetry spans.

## Anti-patterns
- **Logger Injection in Domain Entities**: Passing `logger` into entities and writing `logger.info()` inside business calculation loops.
- **Scattered `print()` or Raw Logging**: Unstructured, uncoordinated logging that lacks correlation IDs, making debugging in microservices impossible.
- **Swallowing Errors for Metrics**: Catching exceptions inside observability hooks and failing to re-raise them, hiding bugs from the caller.

## Code Examples

```python
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("use_case_monitor")

# Boundary Decorator: Adds telemetry without altering use case code
def observe_use_case(use_case_name: str):
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            logger.info("Starting use case", extra={"use_case": use_case_name})
            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start_time
                logger.info(
                    "Use case succeeded",
                    extra={"use_case": use_case_name, "duration_seconds": duration}
                )
                return result
            except Exception as e:
                duration = time.perf_counter() - start_time
                logger.error(
                    "Use case failed",
                    extra={
                        "use_case": use_case_name,
                        "duration_seconds": duration,
                        "error": str(e),
                    },
                    exc_info=True
                )
                raise
        return wrapper
    return decorator

# Use Case Interactor remains clean!
class RegisterUserUseCase:
    @observe_use_case("RegisterUser")
    def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        # Pure business orchestration; zero logging setup needed here
        return RegisterUserResponse(user_id="123", success=True)
```
- **What it demonstrates**: Comprehensive latency, status, and error telemetry wrapped cleanly around a use case execution without polluting the core logic.

## Reference Tables

| Telemetry Type | What to Measure | Best Architectural Location | Tooling |
|---|---|---|---|
| **Use Case Latency** | Execution time of interactor | Decorator around `execute()` | Prometheus, OpenTelemetry |
| **HTTP Request Metric** | Status codes, network latency | Web Framework Middleware | FastAPI Middleware |
| **Audit Log** | User action, altered records | Application Layer Output Port | Structured JSON / Elasticsearch |
| **Domain Events** | Business milestones reached | Message Bus dispatcher | Datadog, Kafka |

## Worked Example
Injecting OpenTelemetry spans transparently at the Use Case boundary:

```python
from opentelemetry import trace

tracer = trace.get_tracer("clean_app")

class TracedUseCaseWrapper:
    """Decorator or Proxy wrapping any use case in an OpenTelemetry span."""
    def __init__(self, use_case, name: str):
        self._use_case = use_case
        self._name = name

    def execute(self, request):
        with tracer.start_as_current_span(f"UseCase.{self._name}") as span:
            span.set_attribute("request.type", type(request).__name__)
            response = self._use_case.execute(request)
            span.set_attribute("response.success", getattr(response, "success", True))
            return response
```
The application code remains pristine while infrastructure gains full OpenTelemetry visibility.

## Key Takeaways
1. Keep domain entities and business rules completely free of logging and metrics code.
2. Instrument observability at the Use Case boundaries and delivery adapters.
3. Use decorators or proxy wrappers to attach metrics and spans transparently.
4. Always pass correlation IDs to maintain distributed tracing across layers.

## Connects To
- **Ch 18**: Wrapping Use Case Interactors with monitoring decorators.
- **Ch 20**: Middleware in the Frameworks & Drivers layer.
- **Ch 39**: Ronald Mak's Decorator pattern applied to system concerns.
