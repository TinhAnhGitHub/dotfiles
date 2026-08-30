---
name: python
description: Route Python development, maintenance, testing, packaging, dependency-management,
  architecture, design-pattern, and code-quality tasks to the most appropriate child skill. Use
  this skill whenever a request involves Python code or a Python project, including clean-code
  improvements, design patterns, Pydantic, pytest, PySpark/Databricks testing, or uv.
---

# Python skills

Choose the child skill that matches the primary concern. Read it before acting.

- [python-clean-code](python-clean-code/SKILL.md) — implementation idioms, refactoring, closures,
  decorators, typing, protocols, object-model behavior, iteration, resources, and concurrency.
- [python-design-patterns](python-design-patterns/SKILL.md) — problem-first design-pattern
  selection, composition, factories, strategies, registries, workflows, lifecycle, architecture,
  and framework-aware examples.
- [pydantic-skill](pydantic-skill/SKILL.md) — Pydantic models, validation, settings, and serialization.
- [pytest-skill](pytest-skill/SKILL.md) — production-grade pytest guidance.
- [pytest-databricks](pytest-databricks/SKILL.md) — pytest for Databricks, PySpark, and Databricks Connect.
- [uv](uv/SKILL.md) — Python project and dependency management with uv.

## Routing rules

- Use `python-clean-code` for “make this Pythonic”, local refactors, typing, decorator, generator,
  resource, or concurrency questions.
- Use `python-design-patterns` for architecture choices, multiple implementations, provider or
  plugin boundaries, workflow/state design, or “which pattern should I use?” questions.
- Use both when a design-pattern decision must be implemented as an idiomatic Python refactor.
- Prefer the most specific child skill when the task is primarily Pydantic, pytest, Databricks, or uv.
