# Chapter 27: Iterate to Achieve Good Design

**Source**: *Software Design for Python Programmers* (Ronald Mak, Manning 2026) — Part 1: Introduction (Chapter 2)

## Core Idea
Good design is rarely achieved in a single pass; software architecture evolves through disciplined iterations of drafting a simple working solution, identifying design smells, and refactoring toward proven design patterns.

## Frameworks Introduced
- **The Three-Phase Design Iteration Cycle**:
  - When to use: Developing any non-trivial application or subsystem.
  - How:
    1. **Phase 1: Make It Work**: Build a simple, working solution that satisfies core functional requirements. Verify with automated tests.
    2. **Phase 2: Make It Right**: Inspect for code smells (coupling, duplication, SRP violations). Apply design patterns to separate concerns.
    3. **Phase 3: Make It Fast (Only if needed)**: Profile execution bottlenecks. Optimize algorithms without destroying architectural boundaries.
- **The Refactoring Spike Framework**:
  - When to use: When exploring alternative architectures under uncertainty.
  - How: Branch code, rapidly prototype the alternative pattern to test feasibility, evaluate trade-offs, and discard the prototype before deliberately implementing the clean version.

## Key Concepts
- **Iterative Design**: Refining architecture incrementally as understanding of domain requirements deepens.
- **Refactoring**: Changing the internal structure of software without altering its observable external behavior.
- **Code Smell**: A surface indication in source code that usually corresponds to a deeper design problem (e.g. Long Method, Feature Envy).
- **Premature Optimization**: Spending time and introducing complexity to speed up code before profiling proves it is a bottleneck.

## Mental Models
- **Design as Sculpting**: Start with a rough block of clay (Phase 1: Make it work). Carefully carve away excess bulk and define clean edges (Phase 2: Make it right). Finally, polish the surface (Phase 3: Optimize).
- **The Two Hats of Kent Beck**: Wear the "Feature Hat" to make tests pass; switch to the "Refactoring Hat" to clean the design. Never wear both hats at the same time.

## Anti-patterns
- **Big Design Up Front (BDUF)**: Spending weeks drawing static UML diagrams before writing any code; fails as soon as real requirements emerge.
- **Stopping at "Make It Work"**: Committing the initial crude prototype directly to production without refactoring into clean class structures.
- **Refactoring Without Tests**: Modifying class hierarchies and methods without automated tests, causing regressions and fear of future refactoring.

## Code Examples

```python
# Iteration 1: Make It Work (Monolithic script)
def generate_report(data: list[dict], report_type: str) -> str:
    if report_type == "text":
        out = "REPORT\n"
        for row in data:
            out += f"{row['name']}: {row['score']}\n"
        return out
    elif report_type == "html":
        out = "<table>\n"
        for row in data:
            out += f"<tr><td>{row['name']}</td><td>{row['score']}</td></tr>\n"
        out += "</table>"
        return out
    raise ValueError("Unknown format")

# Iteration 2: Make It Right (Refactored using Strategy Pattern)
from typing import Protocol

class ReportFormatter(Protocol):
    def format(self, data: list[dict]) -> str:
        ...

class TextFormatter:
    def format(self, data: list[dict]) -> str:
        lines = ["REPORT"] + [f"{r['name']}: {r['score']}" for r in data]
        return "\n".join(lines)

class HtmlFormatter:
    def format(self, data: list[dict]) -> str:
        rows = "".join(f"<tr><td>{r['name']}</td><td>{r['score']}</td></tr>" for r in data)
        return f"<table>{rows}</table>"

class ReportGenerator:
    def __init__(self, formatter: ReportFormatter):
        self._formatter = formatter

    def generate(self, data: list[dict]) -> str:
        return self._formatter.format(data)
```
- **What it demonstrates**: Evolving from a fragile conditional function (Iteration 1) to an extensible Strategy pattern (Iteration 2) that satisfies the Open/Closed Principle.

## Reference Tables

| Phase | Goal | Focus | Common Trap |
|---|---|---|---|
| **1. Make It Work** | Functional correctness | Passing tests quickly | Stopping here and shipping technical debt |
| **2. Make It Right** | Maintainability & Cleanliness | Patterns, SOLID, decoupling | Over-engineering abstractions |
| **3. Make It Fast** | Performance & Throughput | Profiling, caching, indexing | Premature optimization before profiling |

## Worked Example
Iterative design of an expression parser:
- *Iteration 1*: Evaluates single addition operations (`3 + 5`) in a 20-line function. Verified with tests.
- *Iteration 2*: Requirement adds multiplication and operator precedence (`3 + 5 * 2`). Code becomes an unmaintainable tangle of nested loops.
- *Iteration 3*: Refactored to an Abstract Syntax Tree (AST) with composite nodes (`NumberNode`, `AddNode`, `MultiplyNode`) and a recursive evaluator.
- *Iteration 4*: Added Visitor pattern to support printing, code generation, and evaluation without changing AST node classes.

## Key Takeaways
1. Great architectures are grown through deliberate iterations, not drafted in one perfect attempt.
2. Follow Kent Beck's dictum: "Make it work, make it right, make it fast."
3. Use automated unit tests as the safety harness that makes aggressive refactoring safe.
4. Refactor when you identify smells: replace sprawling conditionals with polymorphic strategies.

## Connects To
- **Ch 26**: Understanding software decay and maintainability goals.
- **Ch 33**: Strategy and Template Method patterns used to resolve conditional smells.
- **Ch 25**: Clean Architecture journey and evolutionary design.
