# The distilled patterns — when to use each (P1–P8)

A cheat-sheet of the 8 core patterns from Fluent Python ch. 7. Each says: **use when** (the
trigger), **clean shape** (the code), **skip when** (the anti-trigger). Every pattern is backed
by verified real-world cases in `functional-patterns.md` (families A–F).

---

### P1. Accessor factory — `itemgetter(i)` / `attrgetter('name')`
- **Use when:** you need a `key=`/`map`/`groupby` callable that fetches by position, dict key,
  or attribute; the index/name is a *variable* (runtime-known); or the fetch runs in a hot loop.
- **Clean shape:**
  ```python
  sorted(rows, key=itemgetter('price'))          # dicts
  sorted(people, key=attrgetter('last'))         # objects
  get_key = itemgetter(*cols)                    # build once, reuse per row
  ```
- **Skip when:** the key needs computation (e.g. `key=lambda p: -p.rating`), or it's a single
  throwaway use on cold code — a lambda is fine.

### P2. Method caller — `methodcaller('name', *args)`
- **Use when:** you map/sort/apply over objects calling the *same method with the same args*
  (`s.strip()`, `b.decode('latin1')`, `x.to_bytes(1, 'big')`).
- **Clean shape:**
  ```python
  list(map(methodcaller('strip'), lines))
  decoder = methodcaller('decode', 'latin1')     # build once, reuse
  ```
- **Skip when:** args differ per element — then a lambda or a real function is required.

### P3. Operator as value — `operator.add`, `operator.eq`, `operator.or_`, ...
- **Use when:** you must *pass* an operation (`reduce`, `sorted` with `functools.cmp_to_key`,
  dunder factories, proxy forwarding) or generate dunders from names.
- **Clean shape:**
  ```python
  reduce(operator.or_, filters)                  # fold N conditions
  __eq__ = _create_method(operator.eq, ...)      # dunder factories
  get_op = lambda name: getattr(operator, f'__{name}__')
  ```
- **Skip when:** the operator is used inline in normal expressions — `a + b` stays `a + b`.

### P4. Strict integer coercion — `operator.index(x)`
- **Use when:** the value must be a *true integer* (array index, exponent, randrange bound) and
  floats/strings must be rejected, not silently truncated.
- **Clean shape:**
  ```python
  try:
      n = operator.index(n)
  except TypeError as e:
      raise TypeError('exponent must be an integer') from e
  ```
- **Skip when:** you genuinely accept anything `int()` accepts (user input parsing).

### P5. Freeze arguments — `functools.partial(fn, *args, **kw)`
- **Use when:** a framework will call your callable later with *no* way to pass context
  (argparse `type=`, finalizers, threadpool runners, descriptors); or you pre-bind config.
- **Clean shape:**
  ```python
  type=functools.partial(directory_arg, optname='--confcutdir')
  self.addfinalizer(partial(_call_with_optional_argument, teardown_module, init_mod))
  ```
- **Skip when:** you need `__name__`/`__doc__` preserved (use `update_wrapper` or a `def`), or
  the bound call is a one-liner in the same scope — a lambda is fine.

### P6. Callable object — `__call__` on a class
- **Use when:** the callable must *remember state between calls* (remaining items, request
  context, response headers) or expose extra methods/attributes alongside being callable.
- **Clean shape:**
  ```python
  class Task:
      def __call__(self, *args, **kwargs):
          self.push_request(args=args, kwargs=kwargs)
          try:
              return self.run(*args, **kwargs)
          finally:
              self.pop_request()
  ```
- **Skip when:** there's no state — a plain function is simpler and faster.

### P7. Dispatch table — dict of callables
- **Use when:** you dispatch on a name/type/key with 3+ branches, or users must extend behavior
  without editing your code.
- **Clean shape:**
  ```python
  commands_dict = {'install': CommandInfo('pip._internal.commands.install', 'InstallCommand', ...), ...}
  command = getattr(importlib.import_module(mod), cls)(name=name, summary=summary)
  ```
- **Skip when:** 1–2 branches, or the branches share so much logic that a table obscures it.

### P8. Registry decorator — decorate-and-register at import time
- **Use when:** you want "add a new X = write one function, decorate it" (plugins, strategies,
  template filters, promotions).
- **Clean shape:**
  ```python
  registry = {}
  def register(name=None):
      def deco(func):
          registry[name or func.__name__] = func
          return func
      return deco
  ```
- **Skip when:** registration order/duplicates matter and need explicit control — prefer an
  explicit list or a config file.

---

## Quick lookup

| Symptom | Pattern |
|---|---|
| "sort/map by a field, index known at runtime" | P1 accessor factory |
| "call the same method with same args on many objects" | P2 methodcaller |
| "I need to pass `+`/`==`/`or` as a value" | P3 operator-as-value |
| "must be a real int, floats must fail" | P4 operator.index |
| "framework calls me later without context" | P5 partial |
| "callable that remembers state between calls" | P6 `__call__` |
| "if/elif chain dispatching by name" | P7 dispatch table |
| "users add new X by writing one function" | P8 registry decorator |
