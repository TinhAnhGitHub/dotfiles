# python-clean-code references

This directory is organized by **chapter** and **case-study source**. The installed entry point is
the parent `../SKILL.md`; these files are supporting material, not additional opencode skills.

## Start here

| Need | Read |
|---|---|
| Quick ch. 7 pattern decision | [`chapters/ch07/patterns-cheatsheet.md`](chapters/ch07/patterns-cheatsheet.md) |
| Full ch. 7 catalog | [`chapters/ch07/functional-patterns.md`](chapters/ch07/functional-patterns.md) |
| Type hints at callable boundaries | [`chapters/ch08/type-hints.md`](chapters/ch08/type-hints.md) |
| Closures and decorators | [`chapters/ch09/closures-decorators.md`](chapters/ch09/closures-decorators.md) |
| Strategy/registry/dispatch patterns | [`chapters/ch10/design-patterns.md`](chapters/ch10/design-patterns.md) |
| Chapters 11–15 | [`chapters/ch11-15/README.md`](chapters/ch11-15/README.md) |
| Framework/library evidence | [`case-studies/library-repos-analysis.md`](case-studies/library-repos-analysis.md) |
| GUI-repository review | [`case-studies/gui-repos-analysis.md`](case-studies/gui-repos-analysis.md) |

## Layout

```text
references/
├── README.md
├── chapters/
│   ├── ch07/
│   │   ├── functional-patterns.md
│   │   └── patterns-cheatsheet.md
│   ├── ch08/type-hints.md
│   ├── ch09/closures-decorators.md
│   ├── ch10/design-patterns.md
│   └── ch11-15/
│       ├── README.md
│       ├── pythonic-objects.md
│       ├── sequence-protocols.md
│       ├── protocols-abcs.md
│       ├── inheritance.md
│       ├── more-type-hints.md
│       ├── framework-patterns.md
│       └── review-checklist.md
└── case-studies/
    ├── library-repos-analysis.md
    └── gui-repos-analysis.md
```

## Naming convention

- `chapters/chNN/` contains material distilled from Fluent Python chapter `NN`.
- `case-studies/` contains evidence gathered from external repositories and concrete review targets.
- Keep one focused topic per file; add an index entry here when adding a new reference bundle.
