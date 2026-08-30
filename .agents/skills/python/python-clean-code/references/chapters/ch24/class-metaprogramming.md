# Chapter 24 — Class Metaprogramming

## P24.1 — Understand the class-creation pipeline

The useful order is:

1. `__prepare__` creates the class namespace.
2. The class body executes in that namespace.
3. The metaclass creates the class with `__new__`.
4. Descriptors receive `__set_name__`.
5. Base classes receive `__init_subclass__`.
6. The metaclass initializes the class.
7. A class decorator receives the finished class.

The local `evaltime` examples print this order. Use them to debug class transformations rather
than guessing which hook runs first.

## P24.2 — Prefer the least powerful hook

Choose in this order unless the requirement proves otherwise:

1. A normal class or factory.
2. A descriptor with `__set_name__`.
3. A class decorator.
4. `__init_subclass__` for a base-class convention or registration.
5. A metaclass only when class construction/namespace creation itself must be controlled.

Many “metaclass” examples in the local `bulkfood` progression become simpler with descriptors and
`__init_subclass__`. Metaclasses create hidden inheritance and import-time coupling; use them for
framework-wide invariants, not convenience.

## P24.3 — Use class subscription only for a real class-level DSL

`__class_getitem__` supports class-level subscription such as `Model[42]` or a strongly documented
time/query DSL. It should return a predictable value and reject incompatible keys clearly. A named
constructor is often more readable than clever subscription syntax.

## P24.4 — Annotation-driven transformation is not full validation

Calling an annotation as a constructor performs coercion (`float("1.2")`), not complete runtime
type checking. `Optional`, `Union`, protocols, and arbitrary typing constructs are not generally
callable. Keep runtime validation explicit at untrusted boundaries.

## Agentic repository evidence

- **LlamaIndex Workflows:** `WorkflowMeta` creates a per-subclass `_step_functions` registry.
- **AG2/AutoGen:** `MetaLLMConfig` exposes class-level configuration properties.
- **TuriX-CUA:** action registration dynamically creates Pydantic parameter classes with
  `create_model`.
- **InfiGUI-G1 / Dart-GUI:** `DataProtoConfigMeta` and `DynamicEnumMeta` provide class-level
  configuration, iteration, containment, indexing, and dynamic registration.
- **LangGraph, Agent-S, ClawGUI, CogAgent, DeerFlow, ShowUI, TongUI-agent:** no meaningful
  repository-owned metaclass/class-creation hook was verified in the inspected code. Do not add
  metaclasses merely because a framework has registries.

These are local repository paths under `/home/tinhanhnguyen/Desktop/project/reference/` and are
the source evidence for the agentic examples in this bundle.

## Local examples worth comparing

`checked/` implements annotation-driven behavior three ways: decorator, metaclass, and
`__init_subclass__`. `persistent/` uses annotations, descriptors, `__init_subclass__`, and
`__class_getitem__` for a miniature ORM. `hours/`, `timeslice.py`, `autoconst/`, and `tinyenums/`
demonstrate class-level DSLs, namespaces, and generated constants.

## Review checklist

- Can a normal class, factory, descriptor, decorator, or `__init_subclass__` solve it?
- Does the transformation preserve inheritance and static-analysis expectations?
- Are class-body side effects documented and deterministic?
- Are generated fields, methods, and constructor errors predictable?
- Is class subscription clearer than a named constructor?
- Is annotation coercion being mistaken for validation?
- Are metaclass conflicts and import-time work tested?
