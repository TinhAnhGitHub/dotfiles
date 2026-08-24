# Chapter 17 — Iterators, Generators, and Classic Coroutines

Chapter 17 is about **lazy control flow**: produce or consume one value at a time, preserve
state between values, and make the direction of communication explicit.

The most important design question is not “can this be a generator?” It is:

> Should this boundary be a reusable iterable, a single-pass iterator, a lazy transformation,
> or a bidirectional state machine?

## The protocol ladder

| Concept | Contract | Typical use |
|---|---|---|
| Iterable | `iter(obj)` returns an iterator | A collection or source that can be traversed repeatedly |
| Iterator | `__iter__()` returns `self`; `__next__()` advances | A single traversal with internal position |
| Generator function | A function containing `yield` | A small stateful lazy producer |
| Generator expression | `(expression for item in source)` | A short lazy transformation |
| Classic coroutine | A generator driven with `send`, optionally `throw`/`close` | A deliberate bidirectional state machine |

For input boundaries, prefer the broadest useful type:

```python
from collections.abc import Iterable, Iterator

def normalize(names: Iterable[str]) -> Iterator[str]:
    for name in names:
        yield name.strip().casefold()
```

`Iterable[T]` says the caller does not need to provide a concrete list. `Iterator[T]` says the
result is lazy and single-pass. Use `Generator[YieldT, SendT, ReturnT]` when callers use the
generator-specific `send()` or return-value protocol.

## P17.1 — Keep reusable iterables separate from iterators

An iterable should usually return a **new iterator** each time:

```python
class Sentence:
    def __init__(self, text: str) -> None:
        self.text = text

    def __iter__(self):
        for word in self.text.split():
            yield word


sentence = Sentence("one two")
assert list(sentence) == ["one", "two"]
assert list(sentence) == ["one", "two"]  # independent traversal
```

Do not make a reusable collection return `self` unless the object is intentionally a
single-pass iterator. Returning `self` from `__iter__` means two consumers share the same cursor.

The hand-written `SentenceIterator` in the local `sentence_iter.py` is useful for learning the
protocol, but the generator version in `sentence_gen.py` is the idiomatic implementation.

## P17.2 — Use generator functions for lazy stateful production

Calling a generator function does not execute its body. It creates a generator object. Execution
starts at `next()` and resumes after each `yield`:

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

This gives constant working memory regardless of how many values are consumed. It also supports
infinite sequences, early termination, and backpressure from the consumer.

Use a generator when:

- the source may be large or infinite;
- the consumer may stop early;
- computation should happen only when requested;
- state naturally lives between successive values.

Do not use a generator merely to hide a small list that callers need to traverse repeatedly.

## P17.3 — Use generator expressions for short transformations

```python
words = (match.group() for match in RE_WORD.finditer(text))
```

The local `sentence_genexp.py` demonstrates the right boundary: the expression is short, linear,
and has no separate control-flow policy. Use a named generator function when the logic needs
branches, cleanup, documentation, or more than a small expression.

## P17.4 — Use `iter(callable, sentinel)` for pull-based sources

Python has a two-argument form of `iter`:

```python
for line in iter(file.readline, ""):
    process(line)
```

It repeatedly calls the zero-argument callable and stops when the result equals the sentinel.
This is clearer than writing a manual `while True`/`break` loop for file-like or chunked sources.

The callable must be safe to call repeatedly, and the sentinel comparison must be unambiguous.

## P17.5 — Prefer `itertools` for standard lazy composition

The local `aritprog_v3.py` evolves from a hand-written loop to:

```python
from itertools import count, takewhile

def arithmetic_progression(begin, step, end=None):
    first = type(begin + step)(begin)
    values = count(first, step)
    return values if end is None else takewhile(lambda value: value < end, values)
```

Use the standard-library iterator vocabulary before inventing another helper:

- `chain` / `chain.from_iterable` — flatten sequential sources;
- `islice` — bounded or stepped consumption without materializing;
- `takewhile` / `dropwhile` — prefix selection;
- `filterfalse`, `compress`, `starmap`, `accumulate`, `groupby` — named stream operations;
- `sum`, `any`, `all`, `min`, `max`, and `reduce` — reducing consumers.

For numeric progressions, compute `begin + step * index` when repeated floating-point addition
would accumulate drift. Use `Fraction` or `Decimal` when the domain requires exact arithmetic.

## P17.6 — Use `yield from` for delegation

`yield from` is more than a shorter `for` loop. It delegates iteration and, for generators,
creates a transparent channel for `send`, `throw`, and `close`. It also captures the subgenerator's
`return` value:

```python
def subgenerator(values):
    total = 0
    for value in values:
        total += value
        yield value
    return total


def report(values):
    total = yield from subgenerator(values)
    yield {"total": total}
```

Use it for recursive tree traversal, flattening nested streams, and splitting a large generator
into focused subgenerators. Avoid replacing a simple loop with `yield from` if it makes ownership
or exception handling less obvious.

The local `tree/step6/tree.py` is the model recursive example:

```python
def tree(cls, level=0):
    yield cls.__name__, level
    for sub_cls in cls.__subclasses__():
        yield from tree(sub_cls, level + 1)
```

## P17.7 — Understand generator control methods

For a generator `gen`:

- `next(gen)` is equivalent to `gen.send(None)`;
- `gen.send(value)` makes the suspended `yield` expression evaluate to `value`;
- a non-`None` value cannot be sent until the generator reaches its first `yield`;
- `gen.throw(exc)` raises an exception at the suspended `yield`;
- `gen.close()` injects `GeneratorExit` and asks the generator to terminate;
- a generator that yields after `GeneratorExit` causes `RuntimeError`;
- a generator's `return value` appears as `StopIteration.value`.

Prime a coroutine explicitly with `next(coro)` or `send(None)`, or provide a small, documented
priming helper. Do not silently make a complex protocol “magical” with a decorator unless every
caller benefits from the same lifecycle.

## P17.8 — Make cleanup reliable

Generators can own resources, but ownership must be visible:

```python
def read_lines(path):
    with open(path, encoding="utf-8") as file:
        yield from file
```

Prefer `with open(...)` when the file lifetime is naturally scoped to the generator's active
iteration. Use an explicit `try/finally` for resources whose cleanup is not expressed by an
existing context manager.

For async resources, use an async generator plus `async with`/`aclosing` and preserve cancellation.

## P17.9 — Classic coroutines are state machines, not modern async I/O

A classic coroutine usually contains an assignment from `yield`:

```python
def running_average():
    total = count = 0
    average = 0.0
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count
```

The caller pushes values with `send`. This is useful for a compact state machine, parser, event
consumer, or testable protocol. It is not the modern way to perform network or file I/O: use
`async def`/`await` and async iterators for that. Chapter 17 introduces the mechanism; later
chapters cover modern concurrency.

The local `coroaverager2.py` demonstrates a typed coroutine that returns a `NamedTuple` through
`StopIteration.value`. The `coroutines.py` example in this bundle additionally demonstrates
exception injection and cleanup.

## P17.10 — Avoid the `StopIteration` trap

Inside a generator, do not manually raise `StopIteration` to finish normal work. Use `return` or
fall off the end. Since PEP 479, an accidental `StopIteration` escaping a generator is converted
to `RuntimeError`, preventing a nested iterator bug from silently terminating the outer generator.

Use `next(iterator, default)` when exhaustion is expected at a single pull boundary. Use a
`for` loop or `yield from` when exhaustion is normal stream control flow.

## Review checklist

- Is the input typed as `Iterable[T]` rather than unnecessarily requiring `list[T]`?
- Is the output intentionally lazy and single-pass?
- Can the iterable be traversed twice, or is that limitation documented?
- Is a generator expression clearer than a named generator function here?
- Would an `itertools` primitive make the operation more recognizable?
- Does `yield from` preserve the intended values, exceptions, and return value?
- Is the coroutine primed before a non-`None` `send`?
- Are `throw`, `close`, `GeneratorExit`, and `finally` behavior tested if exposed?
- Is a classic coroutine being used for a state protocol rather than modern async I/O?
- Is materialization (`list(...)`, `tuple(...)`) deliberately placed at the boundary?

## Production analogues

These examples use the same boundary discipline:

- **Hugging Face Hub:** paginated listing APIs expose lazy generators instead of materializing
  remote results; document pagination and failure behavior.
- **vLLM:** `AsyncLLM.generate` exposes an async generator, keeping streaming separate from output
  value objects.
- **LangChain:** `RunnableGenerator` and `stream`/`astream` APIs keep pipeline output incremental;
  the runnable itself is not disguised as a sequence.
- **LlamaIndex:** `StreamingResponse` and agent response APIs expose generator/async-generator
  token flows.
- **LangGraph:** checkpoint saver interfaces expose sync and async iterator methods for listing or
  streaming state instead of forcing implementations into a materialized collection.
- **AG2:** turn-scoped async generator/context-manager code keeps task and subscription cleanup
  attached to the lifecycle boundary.

See [`../ch11-15/framework-patterns.md`](../ch11-15/framework-patterns.md) for the source links
and the cross-framework review rules.

## Source basis

- Local examples: `/home/tinhanhnguyen/Desktop/project/reference/python_learn/example-code-2e/17-it-generator/`
- Official chapter page: <https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/ch17.html>
- PEP 342 — enhanced generators: <https://peps.python.org/pep-0342/>
- PEP 380 — `yield from`: <https://peps.python.org/pep-0380/>
- PEP 479 — `StopIteration` handling: <https://peps.python.org/pep-0479/>
