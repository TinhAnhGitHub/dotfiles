# Chapter 14 — Inheritance: For Better or For Worse

## Default: compose before inheriting

Use inheritance when the subtype relationship is stable, substitutability is real, and the
base class owns a useful contract. Otherwise prefer:

- composition of a collaborator,
- a function passed as a strategy,
- a small `Protocol` boundary,
- or a wrapper/decorator around an object.

Inheritance is a coupling mechanism. It exposes base-class implementation details, constrains
future changes, and makes initialization/MRO behavior harder to reason about.

## Cooperative multiple inheritance

If multiple inheritance is intentional:

1. Every participating method calls `super()` exactly once when it is part of the cooperative
   chain.
2. Constructors accept compatible keyword arguments and forward unused arguments.
3. Mixins are small and generally stateless; they add one coherent behavior.
4. Base classes document the methods/attributes a mixin expects from its neighbors.
5. Test the concrete class's `__mro__` and the full call order.

The local `diamond.py` demonstrates why `super()` follows the MRO rather than naming a
particular parent. `diamond2.py` shows that a “standalone” sibling only works when it is
designed as a cooperative participant; `super()` is not a magic call to a known superclass.

## Mixins

A good mixin:

- has one responsibility,
- does not represent a complete domain object by itself,
- calls `super()` rather than directly naming the next base,
- documents the methods it expects,
- and composes with more than one compatible host.

`UpperCaseMixin` is a good shape: it normalizes mapping operations and delegates storage to
`UserDict` or `Counter`. It is better than duplicating the normalization logic in both classes.

## Built-in subclassing

Built-in subclasses can have C-level methods that bypass Python overrides or take a different
construction path than expected. If invariants must hold on every operation, use
`collections.UserDict`, `UserList`, `UserString`, or composition. The local
`strkeydict_dictsub.py` is a useful warning: a `dict` subclass must carefully override several
methods to preserve key normalization.

## Template methods and framework bases

An ABC/base class can provide a stable algorithm and delegate narrow steps to subclasses. Keep
the template method's invariant in the base; keep customization points small. This is common
in LangChain's `Runnable`, LlamaIndex's prompt/instrumentation mixins, MLflow's `PythonModel`,
and vLLM's engine/quantization ABCs.

## `__init_subclass__` and metaprogramming

Use `__init_subclass__` when every subclass must be validated or registered at definition time.
Keep it predictable:

- validate explicit configuration early,
- call `super().__init_subclass__(**kwargs)`,
- avoid hidden global side effects,
- produce errors that name the subclass and violated rule,
- and test both valid and invalid subclasses.

LlamaIndex's instrumentation mixin and Hugging Face's model/Hub mixins are production examples.

## Anti-patterns

- Deep “is-a” hierarchies used only to reuse a few lines.
- A mixin that stores unrelated state or requires a specific sibling base silently.
- Direct parent calls (`Base.method(self)`) inside a cooperative hierarchy.
- Overriding `__init__` without forwarding required base initialization.
- Subclassing a framework class when a documented protocol or callback extension point exists.
