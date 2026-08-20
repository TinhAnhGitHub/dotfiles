---
name: python-clean-code
description: >-
  Apply Python clean-code best practices distilled from Fluent Python (2nd ed.) and verified
  against real production code in CPython, Django, Flask, Starlette, FastAPI, NumPy, pandas,
  scikit-learn, SQLAlchemy, Celery, pip, pytest, requests, botocore and more. Covers the
  functional-programming patterns of Chapters 7–10: first-class functions, type-hint contracts,
  closures/decorators, registries, dispatch tables, hooks, and strategy-via-functions. Includes
  100+ verified examples across standard Python, agentic/LLM frameworks, Hugging Face, MLflow,
  vLLM, verl, ms-swift, and GUI-agent repositories.
  TRIGGER THIS SKILL whenever the user writes, reviews, refactors, or asks for advice on Python
  code involving lambdas, sorted/max/min keys, map/filter/reduce, operator functions, partial,
  __call__ classes, registries, dispatch tables, plugin/hook systems, Protocol, Annotated, Literal,
  ParamSpec, decorators, closures, or any "clean up this Python code" request — even if they don't
  mention the skill by name. Also triggers for style questions like "is a lambda better here", "how
  do pros sort this", "why would anyone use itemgetter", or "how should I structure my Python project".
---

# python-clean-code — Functional Patterns (Fluent Python Ch. 7–10)

A living skill that turns Fluent Python's Chapters 7–10 into concrete, verified, production-grade
coding rules. Every pattern below is backed by real code from famous open-source projects. Start
with the chapter module that matches the problem, then use the repository field guides for concrete
comparisons.

## The one idea

In Python, **a function is a value**: you can store it, pass it, return it, and build it at
runtime. Almost every "clean code" win in this chapter is one of these moves:

1. **Hand a function to a generic tool** — `sorted(..., key=...)`, `map`, `filter`, `reduce`,
   `max`/`min`/`nlargest`, `groupby`. The tool doesn't know your data; the function is the answer
   to "what should I compare/extract".
2. **Let the standard library build the function for you** — `itemgetter`, `attrgetter`,
   `methodcaller`, `functools.partial` are factories for accessor/frozen callables.
3. **Use the function version of an operator** — `operator.add` instead of `lambda a, b: a + b`,
   because operators themselves are syntax and cannot be passed around.
4. **Make your own callables** — `__call__` on a class for stateful function-like objects, and
   classes/descriptors that *return* functions.
5. **Treat functions as data** — dispatch tables, registries, hooks, strategies. Adding behavior
   becomes "add one dict entry" or "decorate one function", not editing an `if/elif` chain.

## When to apply (and how to decide)

| Situation in your code | Replace with | Why (verified win) |
|---|---|---|
| `key=lambda x: x[1]` / `x[i]` on sequences or dicts | `itemgetter(i)` | C-level fetch, up to 2x faster than lambda (CPython json bpo-23493); works on dicts |
| `key=lambda o: o.attr` or `getattr` loops | `attrgetter('attr')` | Dotted paths, multi-attr tuple fetch, runtime-built names (Django, Celery) |
| `lambda s: s.method(args)` in `map`/`sort`/`apply` | `methodcaller('method', args)` | No closure frame; named intent (NumPy npyio, sklearn six, Werkzeug) |
| `lambda a, b: a + b` / `a >= b` passed around | `operator.add` / `operator.ge` | Function versions of operators, passable as values (pandas/xarray dunder factories) |
| `int(x)` when you need a *true integer* index | `operator.index(x)` | Rejects floats; only `__index__` objects pass (NumPy, CPython random) |
| `lambda: fn(a, b)` / pre-binding arguments | `functools.partial(fn, a, b)` | Introspectable (`.func/.args/.keywords`), C-implemented, no closure (Starlette, pytest, Django) |
| Hand-written fetch loop in a hot row loop | Build `itemgetter(*cols)` **once**, reuse per row | One C callable per fetch instead of a Python loop per element (SQLAlchemy, NumPy) |
| An object that must act like a function *and* keep state | `__call__` on a class | State lives on the instance between calls (Celery Task, Werkzeug Response, Flask app) |
| Long `if/elif` chains dispatching by name/type | dict of callables (dispatch table) | Add behavior = add an entry; lazy import possible (pip commands_dict, FastAPI overrides) |
| Extension points for users/plugins | Registry decorators + lists/dicts of callables | Third parties extend without touching core code (Django template.Library, requests hooks, botocore) |

**When a lambda is still fine:** one-off keys that need logic a factory can't express
(e.g. `key=lambda p: (p.category, -p.rating)`), tiny throwaway scripts, or when the callable is
created and used exactly once with no hot-loop concerns. Reaching for `itemgetter` there is
over-engineering; the pros use lambdas there too.

## The distilled patterns — when to use each

The full cheat-sheet — patterns **P1–P8** (accessor factory, method caller, operator-as-value,
strict int coercion, freeze arguments, callable object, dispatch table, registry decorator) with
  their triggers, clean shapes, and anti-triggers — lives in
  **`references/chapters/ch07/patterns-cheatsheet.md`**.
Read it whenever you're deciding between a lambda, `itemgetter`, `partial`, `__call__`, a dict of
callables, or a registry. The decision table above covers the same ground at a glance.

## Workflow for reviewing/refactoring code

1. **Hunt the patterns** — grep for `lambda`, `key=`, `map(`, `filter(`, `reduce(`, `getattr`,
   `int(` on index-like values, hand-written `for` loops extracting fields, `if/elif` dispatch
   chains, and methods whose only job is to wrap another call.
2. **Classify each hit** with the decision table above. Ask: is the extraction/comparison name
   *known at write time* (→ lambda is fine) or *only at runtime* (→ `itemgetter`/`attrgetter` with
   a variable, or build the accessor once)?
3. **Check the hot path** — if the callable runs per row / per element (sort keys, row factories,
   `map` bodies, `apply`), prefer operator functions/`itemgetter` and *pre-build* them outside the
   loop.
4. **Prefer data over control flow** — if you see `if name == "x": ... elif name == "y": ...`,
   refactor to a dict of callables; if you see "users should extend this", use a registry.
5. **Verify the win** — state which category you're fixing: PERFORMANCE (C-level callable in hot
   loop), DYNAMIC RUNTIME CONSTRUCTION (name/index known only at runtime), READABILITY
   (intent-named factory vs lambda), CORRECTNESS (operator.index vs int, `__index__` protocol),
   EXTENSIBILITY (registry/hooks), MEMORY (no per-call wrapper objects), STATE (`__call__`).

## Pitfalls (things the pros avoid)

- **`functools.partial` has no `__name__`/`__module__`** — tools like `update_wrapper` and
  pickling break. SQLAlchemy's `wrap_callable` exists precisely for this; when you need metadata,
  wrap with `functools.update_wrapper` or fall back to a small `def`.
- **`operator.index` is not `int()`** — `int(3.7)` silently truncates; `operator.index(3.7)`
  raises `TypeError`. Use `index` for array indices, exponents, and any "must be a real integer"
  contract (NumPy, CPython random, and Fluent Python's `Vector.__getitem__`).
- **`itemgetter(a, b)` returns a tuple** — multi-arg forms are `(x[a], x[b])`; single-arg returns
  the bare value. Same for `attrgetter('a', 'b')`. Don't confuse the two when sorting by
  multiple keys (that tuple behavior is a feature: sort by grade then age).
- **Don't stack `attrgetter('a.b.c')` manually** — dotted paths are supported; writing nested
  `attrgetter` calls is noise.
- **Class-based decorators must preserve metadata** — if a class instance replaces a function,
  call `functools.update_wrapper(self, func)` in `__init__` (Fluent Python ch. 9 `clock` class).
- **A lambda that appears in many places should become one named callable** — pre-build it once;
  if it only needs to exist in one place and one use, keep it.

## Examples worth keeping in mind

**Runtime-built accessor (the #1 pro move):**
```python
# name comes from a DB cursor / config / user input — unknown at write time
get_key = itemgetter(field_index)          # build ONCE
result = {get_key(row): row for row in rows}   # C-speed per row
```

**Operator as value (pandas/xarray dunder factories):**
```python
class OpsMixin:
    __add__ = _create_method(operator.add, "add", True, False, False)
    __ge__  = _create_method(operator.ge, "ge", False, True, False)
```

**partial to defer a call (pytest finalizers):**
```python
self.addfinalizer(partial(_call_with_optional_argument, teardown_module, init_mod))
```

**Dispatch table instead of if/elif (pip):**
```python
commands_dict = {"install": CommandInfo("pip._internal.commands.install", "InstallCommand", "Install packages."), ...}
command = getattr(importlib.import_module(mod), cls)(name=name, summary=summary)
```

## The full catalog

Read **`references/chapters/ch07/functional-patterns.md`** for the complete, verified catalog of 60+
real-world cases (repo, file, context, naive version, real code, and what it solves) organized by
pattern family:

- **Family A — Accessor factories** (`itemgetter`/`attrgetter`/`methodcaller`): NumPy npyio,
  SQLAlchemy result, Django deletion/query, Celery, scikit-learn, more-itertools, Ansible,
  CPython statistics/email, Werkzeug, lxml, six
- **Family B — Operator-as-function**: CPython random/json/collections, NumPy einsum/matrix_power,
  pandas OpsMixin, xarray _typed_ops, Django `reduce(operator.or_)`
- **Family C — functools.partial**: Starlette, pytest, CPython inspect, Django query_utils/migrations,
  pydantic, SQLAlchemy wrap_callable, Werkzeug ClosingIterator
- **Family D — Callable objects (`__call__`)**: Celery Task, Werkzeug Response, Flask app, BingoCage
- **Family E — First-class function architectures**: pip dispatch table, Django template.Library,
  shutil.copy_function strategy, requests hooks, Starlette request_response, FastAPI
  dependency_overrides, unittest sortTestMethodsUsing, botocore HierarchicalEmitter
- **Family F — Agentic/LLM libraries**: LangChain (PII redaction `itemgetter`, `RunnableLambda`
  repr introspection, `RouterRunnable`, `@tool`), LlamaIndex (`@step`, `FunctionTool`,
  CallbackManager hooks), AutoGen/AG2 (`register_for_llm`/`register_for_execution`,
  `execute_function` dispatch, `register_reply` hooks, `partial` for threadpools), Agno
  (Toolkit sync/async registries, `@tool`, entrypoint dispatch, hook `reduce`, partial-aware
  docstrings) — the exact shapes your own LLM tool layer (`function/context.py`) should mirror

The distilled P1–P8 cheat-sheet lives in **`references/chapters/ch07/patterns-cheatsheet.md`**.

## Chapter 8 — type hints at functional boundaries

Read **`references/chapters/ch08/type-hints.md`** when a function is a tool, plugin, callback, decorator,
registry entry, or strategy. The key patterns are:

- `Literal` for closed protocol vocabularies;
- `Annotated` for runtime-consumed metadata;
- `Callable` aliases for one-operation strategies and hooks;
- `Protocol` for structural plugin contracts;
- bounded/covariant `TypeVar` and `Self` for subtype-preserving APIs;
- `ParamSpec` for transparent decorators;
- overloads for bare/configured decorator forms.

The user's `function/context.py` pattern—`inspect.signature`, `Annotated`, `get_type_hints`, and
decorator registration—is exactly this boundary: type the metadata contract, then make the runtime
schema extraction explicit and tested.

## Chapter 9 — closures and decorators

Read **`references/chapters/ch09/closures-decorators.md`** when behavior must be wrapped, configured, scoped,
cached, or adapted between sync/async execution. The key patterns are:

- configuration → decorator → wrapper factories;
- `@wraps` and deliberate signature repair;
- decorators that return a `Tool`, `Function`, or workflow step object;
- private closure state for retry counters, observers, and one-shot execution;
- `@contextmanager` for reliable acquire/restore behavior;
- `cache`/`lru_cache` for stable observations only.

## Chapter 10 — design patterns with first-class functions

Read **`references/chapters/ch10/design-patterns.md`** when a class hierarchy exists mainly to vary one
operation, or when a central function contains growing dispatch branches. The key patterns are:

- strategy as a plain function;
- command as a stored callable or `partial`;
- dispatch tables and lazy factories;
- registry decorators for additive extension;
- observer/hook collections;
- callable pipelines and setup-time strategy binding.

## Repository field guides

- **`references/case-studies/library-repos-analysis.md`** — verified patterns and conservative refactor targets
  in Hugging Face Transformers/Hub, MLflow, vLLM, verl, and ms-swift.
- **`references/case-studies/gui-repos-analysis.md`** — usage and “current problem → functional fix” findings
  across the GUI repositories under `~/Desktop/project/reference`, including agent-s, ClawGUI,
  CogAgent, dart-gui, deer-flow-agent, SCALE-CUA, ShowUI, TongUI-agent, and TuriX-CUA.

Use the field guides as review examples, not as automatic refactoring instructions. Check whether a
branch is in a hot path, whether registration order is semantic, and whether a class owns state or
invariants before replacing it with a function.

## Roadmap (future chapters)

Chapters 7–10 are now covered. Planned next modules:
- ch. 5/11/12+ — data classes, pythonic objects, sequence hacking
