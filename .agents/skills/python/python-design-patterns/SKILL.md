---
name: python-design-patterns
description: >-
  Select and apply Python design patterns by problem, constraints, and trade-offs. Use whenever
  Python code needs composition over inheritance, adapters, facades, factories, strategies,
  policy pipelines, composite trees, commands, registries, dependency injection, hooks, state
  machines, workflows, value objects, CQRS, SOLID boundaries, provider abstraction, plugin
  boundaries, or architecture guidance. Includes verified examples from modern AI/ML frameworks
  and adapted lessons from the ArjanCodes 2026 pattern examples; use it for framework-aware
  pattern selection and for deciding when no named pattern is needed.
---

# Python design patterns

Use this skill as a decision guide, not as a catalog of classes to copy. Start from the problem
pressure, choose the least powerful design that solves it, and explain why the pattern is worth its
complexity.

## Workflow

1. Describe the current problem, independent variation axes, ownership, lifecycle, and constraints.
2. Search [`references/index.md`](references/index.md) by symptom, family, or framework.
3. Read the selected pattern page and its related alternatives.
4. Compare a simple function/module design with composition and class-based alternatives.
5. Use the selected page's embedded framework example when one is relevant; do not substitute a
   separate framework reference for the example attached to the pattern.
6. Implement the smallest stable interface, then test behavior, lifecycle, failure, and
   observability.
7. State the rejected alternatives and the conditions that would make the recommendation change.

## Pattern families

| Family | Typical question | Index |
|---|---|---|
| Principles | Should this be composition, inheritance, a function, or a module? | [`principles/`](references/principles/) |
| Composition | How do I vary providers, behavior, or capabilities without subclass explosion? | [`composition/`](references/composition/) |
| Construction | How do I select or build implementations safely? | [`construction/`](references/construction/) |
| Behavior | How do I vary algorithms, commands, events, and rules? | [`behavior/`](references/behavior/) |
| Extensibility | How can plugins, tools, callbacks, protocols, or dependencies be added safely? | [`extensibility/`](references/extensibility/) |
| Lifecycle | How do I model state, retry, pause/resume, and recovery? | [`lifecycle/`](references/lifecycle/) |
| Architecture | How should agents, model providers, workers, and workflows compose? | [`architecture/`](references/architecture/) |
| Python-specific | What Python idiom replaces a traditional pattern? | [`python-specific/`](references/python-specific/) |
| Anti-patterns | When is a familiar pattern harmful or unnecessary? | [`anti-patterns/`](references/anti-patterns/) |

## Required reasoning

For every recommendation, include the condition that triggered it, the problem it solves, why it
fits Python, the main trade-off, and at least one simpler alternative. Do not introduce a named
pattern when a small function, module, dataclass, or dependency parameter is sufficient.

## Embedded framework examples

Every pattern page persists its own concise, adapted framework examples under `## Framework
examples`. Each example includes the framework/API, the problem solved, why the pattern fits, and
an official source link. The [framework matrix](references/frameworks/index.md) is a crosswalk for
finding pages and source evidence, not a replacement for the examples stored in those pages.
Treat rolling `main`, `latest`, and `stable` documentation as version-sensitive. Record the exact
source URL, revision or package version, fetch date, and whether an example is verified or adapted.
The core examples in this skill remain standard-library-only; framework imports belong in optional
examples or documentation snippets.

## Source basis

The catalog distills the inventory and trade-off emphasis of [`faif/python-patterns`](https://github.com/faif/python-patterns#readme)
and the Python-specific reasoning in [`python-patterns.guide`](https://python-patterns.guide/).
It also incorporates the supplied [ArjanCodes OOP video](https://www.youtube.com/watch?v=RqcEK7sWesQ)
and its [2026 OOP examples](https://github.com/ArjanCodes/examples/tree/main/2026/oop), the
[Parameter Object video](https://www.youtube.com/watch?v=43sDzyanzR0) and
[examples](https://github.com/ArjanCodes/examples/tree/main/2026/param), the
[Policy video](https://www.youtube.com/watch?v=wYeDGkdMi3g) and
[policy examples](https://github.com/ArjanCodes/examples/tree/main/2026/policy), and the
[State Machine video](https://www.youtube.com/watch?v=OeirQdzYdnc) and
[state examples](https://github.com/ArjanCodes/examples/tree/main/2026/state).
The catalog also records the supplied [Registry video](https://www.youtube.com/watch?v=g7EGMWvJ1fI),
[SOLID video](https://www.youtube.com/watch?v=uxwjXLjJOoM),
[Composite video](https://www.youtube.com/watch?v=ss6je4-nDx8),
[sentinel video](https://www.youtube.com/watch?v=h8ZwhU3PpVw), and
[simplest-design video](https://www.youtube.com/watch?v=xns3InDkAiA), together with the
[complete 2026 source tree](https://github.com/ArjanCodes/examples/tree/main/2026). Keep GoF
labels as aliases, but organize navigation around the problem being solved.
