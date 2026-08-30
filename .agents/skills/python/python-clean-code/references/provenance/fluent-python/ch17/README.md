# Fluent Python 2e — Chapter 17 reference bundle

This bundle distills **Iterators, Generators, and Classic Coroutines** from the local
`example-code-2e/17-it-generator/` examples into reusable clean-code guidance.

## Files

| File | Purpose |
|---|---|
| [`iterators-generators-coroutines.md`](iterators-generators-coroutines.md) | Concepts, design rules, typing, pitfalls, and production analogues |
| [`examples/lazy_iterables.py`](examples/lazy_iterables.py) | Reusable iterables, generator functions, `iter(callable, sentinel)`, and bounded chunks |
| [`examples/delegation.py`](examples/delegation.py) | Recursive generators and `yield from` delegation/return values |
| [`examples/coroutines.py`](examples/coroutines.py) | Typed classic coroutines using `send`, `throw`, `close`, and `finally` |
| [`examples/test_ch17_examples.py`](examples/test_ch17_examples.py) | Focused behavior tests |

## Local source examples

The book examples are in:

```text
/home/tinhanhnguyen/Desktop/project/reference/python_learn/example-code-2e/17-it-generator/
```

The repository README is the authoritative chapter mapping. Its local directory README is
first-edition text and says “Chapter 14”; in Fluent Python 2e this material is Chapter 17.

## Recommended order

1. Read the iterable/iterator distinction.
2. Replace hand-written iterator classes with generator functions where the protocol is simple.
3. Use generator expressions for short, one-expression transformations.
4. Use `itertools` for standard lazy composition and reduction.
5. Use `yield from` for recursive traversal or generator delegation.
6. Reach for classic coroutines only when a deliberate bidirectional state-machine protocol is
   required; use native `async`/`await` for modern asynchronous I/O.
