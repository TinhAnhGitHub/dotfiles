# Ch. 7 Functional Patterns — Verified Real-World Catalog

40+ use cases from famous public repositories, organized by pattern family. Every case was
verified against live source (raw GitHub fetches / search snippets) in Aug 2026. Each entry:
**context → naive version (what a typical dev writes) → real code → what it solves**.

Win tags: `PERF` performance · `DYNAMIC` dynamic runtime construction · `READ` readability ·
`CORRECT` correctness · `EXT` extensibility · `MEM` memory · `STATE` state.

---

## Family A — Accessor factories: `itemgetter` / `attrgetter` / `methodcaller`

### A1. NumPy — `loadtxt`/`genfromtxt` column extraction
- **File:** `numpy/lib/npyio.py`
- **Context:** converts millions of text lines to dtypes, extracting only `usecols` columns per row.
- **Naive:** per-line Python loop with lambdas: `cols = tuple(row[i] for i in usecols)`.
- **Real:**
  ```python
  decoder = methodcaller("decode", encoding or "latin1")   # built once
  line_iter = map(decoder, line_iter)                       # C-level per line
  usecols_getter = itemgetter(*usecols)                     # built once for N columns
  ```
- **Solves:** `PERF` (decode runs in C via map, no per-line Python call) + `DYNAMIC` (getter built
  at runtime for an arbitrary column list).

### A2. Werkzeug — `_make_encode_wrapper`
- **File:** `src/werkzeug/_internal.py`
- **Context:** returns the encoder for every string in a response — identity for `str`, latin-1 for `bytes`.
- **Naive:** `return lambda x: x.encode("latin1")`.
- **Real:** `return operator.methodcaller("encode", "latin1")`.
- **Solves:** `READ` (states intent without a closure) + `PERF` (no per-call Python frame on a hot path).

### A3. SQLAlchemy — per-row column getters
- **File:** `lib/sqlalchemy/engine/result.py`
- **Context:** every fetched DB row maps result keys to column indexes; getter computed once per key at setup, applied to every row.
- **Naive:** `lambda row: row[index]` per row processed.
- **Real:**
  ```python
  def _getter(self, key, map_=False):
      index = self._key_to_index.get(key)
      if index is not None:
          return operator.itemgetter(index)
  # mapping-style results:
  _post_creational_filter = operator.attrgetter("_mapping")
  ```
- **Solves:** `PERF` (C-level getter reused per row) + `DYNAMIC` (index from DB cursor metadata).

### A4. Django — deleting rows in PK order
- **File:** `django/db/models/deletion.py`
- **Context:** `Collector.delete()` sorts each batch by primary key so deletes happen in stable order (matters for cascades).
- **Naive:** `sorted(instances, key=lambda obj: obj.pk)`.
- **Real:** `self.data[model] = sorted(instances, key=attrgetter("pk"))`.
- **Solves:** `READ` + `PERF` (zero Python-level per-comparison calls).

### A5. Celery — dotted-path attribute resolution
- **File:** `celery/app/base.py`
- **Context:** unpickling receives an app path string like `"myapp.celery:app"` and must resolve the live object at runtime.
- **Naive:** manual `for part in path.split("."): obj = getattr(obj, part)`.
- **Real:** `return attrgetter(path)(self)`.
- **Solves:** `DYNAMIC` (dotted path accepted at call time; one C call replaces a split+getattr loop).

### A6. scikit-learn — vocabulary sorts
- **Files:** `sklearn/feature_extraction/text.py`, `sklearn/feature_extraction/_dict_vectorizer.py`, `sklearn/utils/__init__.py`
- **Context:** `CountVectorizer` emits feature names in vocabulary order; `all_estimators()` sorts estimators by name.
- **Naive:** `[t for t, i in sorted(self.vocabulary_.items(), key=lambda item: item[1])]`.
- **Real:**
  ```python
  [t for t, i in sorted(self.vocabulary_.items(), key=itemgetter(1))]
  return sorted(set(estimators), key=itemgetter(0))
  ```
- **Solves:** `CORRECT` (single-item fetch makes the "compare only the name" contract explicit — no tuple tie-breaks) + `PERF` (hot in text pipelines).

### A7. more-itertools — `unique_justseen`
- **File:** `more_itertools/recipes.py`
- **Context:** collapses consecutive equal elements from `groupby` output `(key, group)` pairs.
- **Naive:** `map(lambda pair: pair[0], groupby(iterable))`.
- **Real:**
  ```python
  if key is None:
      return map(itemgetter(0), groupby(iterable))
  return map(next, map(itemgetter(1), groupby(iterable, key)))
  ```
- **Solves:** `READ` (names exactly which tuple element) + `PERF` (C-level inside map).

### A8. Ansible — inventory host sort
- **File:** `lib/ansible/inventory/manager.py`
- **Context:** sorts cached pattern results by host name (or reverse).
- **Naive:** `sorted(hosts, key=lambda h: h.name, reverse=...)`.
- **Real:** `sorted(hosts, key=attrgetter('name'), reverse=(order == 'reverse_sorted'))`.
- **Solves:** `READ` (cleaner than a lambda on a property; identical semantics).

### A9. CPython — `statistics.rank()` / `multimode()`
- **File:** `Lib/statistics.py`
- **Context:** groups `(value, position)` pairs after sorting; groups `(value, count)` pairs from `Counter.most_common()`.
- **Naive:** `groupby(val_pos, key=lambda p: p[0])` and list comprehensions.
- **Real:**
  ```python
  for _, g in groupby(val_pos, key=itemgetter(0)):
      ...
  maxcount, mode_items = next(groupby(counts, key=itemgetter(1)), (0, []))
  return list(map(itemgetter(0), mode_items))
  ```
- **Solves:** `READ` + `PERF` (map(itemgetter(0)) replaces a comprehension on a hot path).

### A10. Django — `QuerySet.in_bulk()` row factories
- **File:** `django/db/models/query.py`
- **Context:** builds plain dicts/tuples from dynamically computed columns; the key function depends on the iterable flavor (model, values, flat).
- **Naive:** `get_key = lambda obj: getattr(obj, field_name)` per row.
- **Real:**
  ```python
  get_key = operator.attrgetter(field_name)      # ModelIterable branch
  get_key = operator.itemgetter(field_name)      # ValuesIterable branch
  get_key = operator.itemgetter(field_index)     # ValuesListIterable branch
  get_key = operator.itemgetter(0); get_obj = operator.itemgetter(1)
  return {get_key(obj): get_obj(obj) for obj in qs}
  ```
- **Solves:** `DYNAMIC` (index/name computed at query time) + `PERF` (C-speed getters in the row loop).

### A11. lxml — HTML diff grouping
- **File:** `src/lxml/html/diff.py`
- **Context:** post-processes `SequenceMatcher` opcodes into consecutive-change groups by insertion index.
- **Naive:** `itertools.groupby(rows, key=lambda row: row[0])`.
- **Real:**
  ```python
  group_by_first_item = functools.partial(itertools.groupby, key=operator.itemgetter(0))
  groups = group_by_first_item(rows)
  ```
- **Solves:** `READ` + `PERF` (itemgetter runs once per row in C; partial reuses it without a lambda).

### A12. scikit-learn (vendored six) — byte helpers
- **File:** `sklearn/externals/six.py`
- **Context:** Py2/3 compat layer; replaced hand-written byte functions on Py3.
- **Naive:** `def byte2int(bs): return ord(bs[0])`.
- **Real:**
  ```python
  # This is about 2x faster than the implementation above on 3.2+
  int2byte = operator.methodcaller("to_bytes", 1, "big")
  byte2int = operator.itemgetter(0)
  indexbytes = operator.getitem
  ```
- **Solves:** `PERF` (documented 2x; C-level callables) + `READ`.

### A13. CPython — email RFC 2231 continuation sort
- **File:** `Lib/email/_header_value_parser.py`
- **Context:** re-assembles MIME header parameters split across continuations; sorts segments by sequence number.
- **Naive:** `parts = sorted(parts, key=lambda x: x[0])`.
- **Real:** `parts = sorted(parts, key=itemgetter(0))`.
- **Solves:** `READ` + `PERF` (single C callable instead of per-item lambda; runs on most email traffic).

### A14. CPython — `json.dumps(sort_keys=True)`
- **File:** `Lib/json/encoder.py` (bpo-23493)
- **Context:** sorts `(key, value)` pairs by key.
- **Naive:** `sorted(dct.items(), key=lambda kv: kv[0])`.
- **Real:** `sorted(dct.items(), key=itemgetter(0))`.
- **Solves:** `PERF` — maintainers' benchmark: 904µs → 462µs (~2x), merged for it.

---

## Family B — Operator-as-function

### B1. CPython — `random.randrange` strict integer coercion
- **File:** `Lib/random.py`
- **Context:** `randrange`/`randint`/`binomialvariate` must accept integer-likes (`int`, `numpy.int64`) and reject floats — called in tight loops.
- **Naive:** `istart = int(start)` — silently truncates `randrange(1.5)`.
- **Real:**
  ```python
  from operator import index as _index
  istart = _index(start)
  istop = _index(stop)
  istep = _index(step)
  ```
- **Solves:** `CORRECT` (floats raise TypeError; only `__index__` objects pass) + `PERF` (~7% faster per CPython PR #23064).

### B2. NumPy — `einsum` subscript validation
- **File:** `numpy/_core/einsumfunc.py`
- **Context:** list-of-integers subscripts must be coerced to ints; anything else gets a clear error.
- **Naive:** `s = int(s)` — silently accepts floats, cryptic errors.
- **Real:**
  ```python
  try:
      s = operator.index(s)
  except TypeError as e:
      raise TypeError("For this input type lists must contain either int or Ellipsis") from e
  ```
- **Solves:** `CORRECT` (only `__index__` objects accepted; `from e` preserves traceback).

### B3. NumPy — `matrix_power` exponent validation
- **File:** `numpy/linalg/_linalg.py`
- **Context:** `np.linalg.matrix_power(a, n)` needs a true integer exponent — `2.0` rejected, `np.int64(3)` accepted.
- **Naive:** `n = int(n)`.
- **Real:**
  ```python
  try:
      n = operator.index(n)
  except TypeError as e:
      raise TypeError("exponent must be an integer") from e
  ```
- **Solves:** `CORRECT` (exact documented error, chained).

### B4. pandas — `OpsMixin` dunder factory
- **File:** `pandas/core/arraylike.py`
- **Context:** every array class (`NumpyExtensionArray`, `Categorical`, `IntervalArray`, ...) needs ~40 dunders; one factory generates them all.
- **Naive:** per-dunder, per-class one-liners: `def __add__(self, other): return self._arith_method(other, lambda a, b: a + b)`.
- **Real:**
  ```python
  class OpsMixin:
      __add__ = _create_method(operator.add, "add", True, False, False)
      __radd__ = _create_method(operator.add, "radd", True, False, False)
      __sub__ = _create_method(operator.sub, "sub", True, False, False)
      __mul__ = _create_method(operator.mul, "mul", True, False, False)
      __and__ = _create_method(operator.and_, "and", False, False, True)
      __lt__ = _create_method(operator.lt, "lt", False, True, False)
      ...
  ```
- **Solves:** `DYNAMIC`/DRY (one factory + operator callables generate the whole operator surface; `operator.and_` exists because `and` is a keyword).

### B5. xarray — generated operator mixins
- **File:** `xarray/core/_typed_ops.py` + `xarray/computation/ops.py`
- **Context:** `DataArray`/`Dataset`/`Variable` implement ~40 dunders each; a generated file declares them as one-liners.
- **Naive:** ~120 hand-written near-identical methods.
- **Real:**
  ```python
  __add__ = _binary_op(operator.add)
  __sub__ = _binary_op(operator.sub)
  ...
  __add__.__doc__ = operator.add.__doc__   # reuse official CPython docs as docstrings

  # ops.py — derive inplace->non-inplace pairs mechanically:
  NON_INPLACE_OP = {get_op("i" + name): get_op(name) for name in NUM_BINARY_OPS}
  ```
- **Solves:** `DYNAMIC` (getattr(operator, f"__{name}__") maps names to functions at runtime; zero duplication).

### B6. Django — `reduce(operator.or_)` to OR-join N Q objects
- **File:** `django/db/models/query.py`
- **Context:** folds N filter conditions into one OR expression.
- **Naive:** a loop building `q = q1 | q2 | q3 ...` by hand.
- **Real:** `.filter(reduce(operator.or_, filters))`.
- **Solves:** `READ` (canonical fold idiom; operator as value).

### B7. CPython — `Counter.most_common()` / `namedtuple`
- **File:** `Lib/collections/__init__.py`
- **Context:** top-N by count; namedtuple field access.
- **Naive:** `sorted(self.items(), key=lambda kv: kv[1], reverse=True)`.
- **Real:**
  ```python
  return _heapq.nlargest(n, self.items(), key=_itemgetter(1))
  _tuplegetter = lambda index, doc: property(_itemgetter(index), doc=doc)
  ```
- **Solves:** `PERF` (nlargest avoids full sort; itemgetter C-level) — and every `point.x` on a namedtuple *is* an itemgetter property.

### B8. CPython — `itemgetter` C implementation itself
- **File:** `Modules/_operator.c`
- **Context:** the reason all of Family A is fast: `itemgetter` is a C type with vectorcall and a specialized fast path.
- **Real (fast path):**
  ```c
  if (nitems == 1 && ig->index >= 0 && PyTuple_CheckExact(obj)
      && ig->index < PyTuple_GET_SIZE(obj)) {
      result = PyTuple_GET_ITEM(obj, ig->index);   /* direct C array read */
  }
  ```
- **Solves:** `PERF` — key extraction with zero Python frames; the mechanism behind every 2x benchmark.

### B9. CPython — `operator.index` in `Lib/random.py` (see B1) and NumPy `_check_nonneg_int`
- **File:** `numpy/lib/_npyio_impl.py`
- **Context:** validates non-negative integer arguments (e.g. `np.save` counts).
- **Naive:** `int(value)` + manual checks.
- **Real:**
  ```python
  try:
      operator.index(value)
  except TypeError:
      raise TypeError(f"{name} must be an integer") from None
  if value < 0:
      raise ValueError(f"{name} must be nonnegative")
  ```
- **Solves:** `CORRECT` (strict `__index__` protocol; clear errors).

---

## Family C — `functools.partial` / `partialmethod`

### C1. Starlette — sync endpoints in a threadpool
- **File:** `starlette/routing.py` (`request_response`)
- **Context:** ASGI is async; plain `def endpoint(request)` must run in a threadpool without blocking the loop.
- **Naive:** `lambda request: run_in_threadpool(func, request)`.
- **Real:**
  ```python
  f = func if is_async_callable(func) else functools.partial(run_in_threadpool, func)
  ...
  response = await f(request)
  ```
- **Solves:** `PERF` (C-level vectorcall partial, no closure frame per request) + `READ` (introspectable via `.func`).

### C2. Starlette — unwrapping partial to detect async
- **File:** `starlette/_utils.py` (`is_async_callable`)
- **Context:** `inspect.iscoroutinefunction(partial(async_fn))` returns False — must walk `.func`.
- **Naive:** `return iscoroutinefunction(obj)` — misclassifies partial-wrapped async as sync.
- **Real:**
  ```python
  while isinstance(obj, functools.partial):
      obj = obj.func
  return iscoroutinefunction(obj) or (callable(obj) and iscoroutinefunction(obj.__call__))
  ```
- **Solves:** `CORRECT` (async endpoints wrapped in partial would otherwise block the loop).

### C3. pytest — CLI argument type with context
- **File:** `src/_pytest/main.py`
- **Context:** `directory_arg` validator reused by several options; each needs its own name in error messages, but argparse calls `type(value)` with no context.
- **Naive:** `type=lambda value: directory_arg(value, optname="--confcutdir")` per option.
- **Real:** `type=functools.partial(directory_arg, optname="--confcutdir")`.
- **Solves:** `DYNAMIC` (callable constructed at registration time) + `READ`.

### C4. pytest — deferred teardown
- **File:** `src/_pytest/python.py` (`Module.setup`)
- **Context:** `addfinalizer` takes a zero-arg callable; teardown must run at end of module run.
- **Naive:** `self.addfinalizer(lambda: _call_with_optional_argument(teardown_module, init_mod))`.
- **Real:**
  ```python
  func = partial(_call_with_optional_argument, teardown_module, init_mod)
  self.addfinalizer(func)
  ```
- **Solves:** `STATE`/`DYNAMIC` (explicit, introspectable binding instead of a closure).

### C5. CPython — `inspect.signature` understands partial
- **File:** `Lib/inspect.py` (`_signature_get_partial`)
- **Context:** `inspect.signature(partial(f, 1))` must show the *remaining* parameters.
- **Naive:** `_get_signature_of(obj.func)` — shows parameters already bound away.
- **Real:** binds `partial.args`/`partial.keywords` against the wrapped signature and rebuilds the parameter list.
- **Solves:** `CORRECT` — the foundation FastAPI/pydantic/IDE tooling rely on.

### C6. Django — class-or-instance method descriptor
- **File:** `django/db/models/query_utils.py` (`class_or_instance_method`)
- **Context:** `RegisterLookupMixin` methods must behave differently on class vs instance.
- **Naive:** two hand-written classmethod/instance-method pairs, or lambdas in `__get__`.
- **Real:**
  ```python
  def __get__(self, instance, owner):
      if instance is None:
          return functools.partial(self.class_method, owner)
      return functools.partial(self.instance_method, instance)
  ```
- **Solves:** `DYNAMIC` + `READ` (one descriptor replaces two method pairs).

### C7. Django — serializing partial into migrations
- **File:** `django/db/migrations/serializer.py` (`FunctoolsPartialSerializer`)
- **Context:** migrations are stored as Python source; `default=partial(datetime.now, tz)` must round-trip.
- **Naive:** pickle/`__name__`-based serialization — fails (partial has no module path).
- **Real:**
  ```python
  return DeconstructibleSerializer.serialize_deconstructed(
      f"functools.{partial_name}",
      (self.value.func, *self.value.args),
      self.value.keywords,
  )
  ```
- **Solves:** `CORRECT` (partial's public `.func/.args/.keywords` make it a first-class deconstructible type).

### C8. pydantic — synthesized property setter/deleter
- **File:** `pydantic/_internal/_decorators.py` (`PydanticDescriptorProxy.__post_init__`)
- **Context:** must mirror the wrapped item's `.setter`/`.deleter` APIs, each remembering which attribute it is.
- **Naive:** `self.setter = lambda func: self._call_wrapped_attr(func, name='setter')`.
- **Real:**
  ```python
  for attr in 'setter', 'deleter':
      if hasattr(self.wrapped, attr):
          f = partial(self._call_wrapped_attr, name=attr)
          setattr(self, attr, f)
  ```
- **Solves:** `DYNAMIC` + `READ` (two API surfaces from one method in two lines).

### C9. SQLAlchemy — `wrap_callable` tolerates partial
- **File:** `lib/sqlalchemy/util/langhelpers.py`
- **Context:** `Column(default=partial(datetime.now, timezone.utc))` is documented; `update_wrapper` crashes on partial (no `__name__`/`__module__` — issue #3823).
- **Naive:** `update_wrapper(wrapper, fn)` → AttributeError.
- **Real:** checks `hasattr(fn, "__name__")`; falls back to copying `__class__.__name__`, `__module__`, and `__call__.__doc__`.
- **Solves:** `CORRECT` (graceful handling of callable objects without function attributes).

### C10. Werkzeug — `ClosingIterator` freezes `next`
- **File:** `werkzeug/wsgi.py`
- **Context:** WSGI iterator must answer `__next__()` with no args; `next(iterator)` needs the iterator passed.
- **Naive:** `self._next = lambda: next(iterator)`.
- **Real:** `self._next = partial(next, iterator)`.
- **Solves:** `READ` + `PERF` (C-level partial, introspectable `.args`; Flask's cleanup pipeline rides on it).

---

## Family D — Callable objects (`__call__`)

### D1. Celery — `Task.__call__` wraps state around `run()`
- **File:** `celery/app/task.py`
- **Context:** calling `task(args)` must execute `run()` *and* maintain request context (stack push/pop).
- **Naive:** callers would call `task.run(*args)` directly, losing bookkeeping, or wrap every call in a context manager.
- **Real:**
  ```python
  def __call__(self, *args, **kwargs):
      _task_stack.push(self)
      self.push_request(args=args, kwargs=kwargs)
      try:
          return self.run(*args, **kwargs)
      finally:
          self.pop_request()
          _task_stack.pop()
  ```
- **Solves:** `STATE` (the object carries its own state; `task(...)` is both public API and correct execution path).

### D2. Werkzeug — `Response.__call__` is a WSGI app
- **File:** `src/werkzeug/wrappers/response.py`
- **Context:** WSGI servers call `app(environ, start_response)`; a Response object should be usable directly as the app.
- **Naive:** every caller writes an adapter: `def as_wsgi(response, environ, start_response): ...`.
- **Real:**
  ```python
  def __call__(self, environ, start_response):
      app_iter, status, headers = self.get_wsgi_response(environ)
      start_response(status, headers)
      return app_iter
  ```
- **Solves:** `READ` + `STATE` (one object serves two protocols, carrying its own headers/status).

### D3. Flask — `Flask.__call__` as middleware seam
- **File:** `src/flask/app.py`
- **Context:** WSGI servers need a callable app; Flask keeps logic in `wsgi_app` so middleware can wrap `app.wsgi_app`.
- **Naive:** expose `wsgi_app` only — every server/compat shim needs an adapter.
- **Real:**
  ```python
  def __call__(self, environ, start_response):
      """The WSGI server calls the Flask application object as the WSGI application."""
      return self.wsgi_app(environ, start_response)
  ```
- **Solves:** `STATE` + `READ` (app object is the callable; `wsgi_app` stays a plain method — the documented middleware seam).

### D4. Fluent Python — `BingoCage` (the book's canonical example)
- **File:** `example-code-2e/07-1class-func/bingocall.py`
- **Context:** a callable that pops a random item each call, remembering remaining items between calls.
- **Naive:** a class with only `pick()` — callers must remember the method.
- **Real:**
  ```python
  class BingoCage:
      def __init__(self, items):
          self._items = list(items)
          random.shuffle(self._items)
      def pick(self): ...
      def __call__(self):
          return self.pick()
  ```
- **Solves:** `STATE` (state on the instance; `bingo()` reads like a function).

---

## Family E — First-class function architectures

### E1. pip — command dispatch table with lazy import
- **File:** `src/pip/_internal/commands/__init__.py`
- **Context:** maps CLI subcommand names to Command classes; importing all ~20 modules at startup is expensive.
- **Naive:** `if/elif` chain per name, or eager imports of every command module.
- **Real:**
  ```python
  commands_dict: dict[str, CommandInfo] = {
      "install": CommandInfo("pip._internal.commands.install", "InstallCommand", "Install packages."),
      "lock": CommandInfo("pip._internal.commands.lock", "LockCommand", "Generate a lock file."),
      ...
  }
  def create_command(name, **kwargs):
      module_path, class_name, summary = commands_dict[name]
      module = importlib.import_module(module_path)
      return getattr(module, class_name)(name=name, summary=summary, **kwargs)
  ```
- **Solves:** `PERF` (lazy import — `--help` never imports every command) + `EXT` (new subcommand = one dict entry).

### E2. Django — `template.Library` import-time registration
- **File:** `django/template/library.py`
- **Context:** `@register.filter` / `@register.simple_tag` stash plain functions into `self.filters`/`self.tags` at import time; rendering looks them up by name.
- **Naive:** one central hardcoded registry dict maintained by hand; third-party apps would edit core code.
- **Real:**
  ```python
  def tag_function(self, func):
      self.tags[func.__name__] = func
      return func
  def filter(self, name=None, filter_func=None, **flags):
      ...
      self.filters[name] = filter_func
      return filter_func
  ```
- **Solves:** `EXT` (any app contributes filters by importing a module) + `READ` (`@register.filter` next to the definition) + `DYNAMIC` (name→callable dict queryable at runtime).

### E3. CPython — `shutil.copytree` strategy via plain function
- **File:** `Lib/shutil.py`
- **Context:** "how to copy a single file" is a parameter — `copy_function=copy2`; callers pass `copyfile` or custom compressors.
- **Naive:** a `CopyStrategy` ABC with subclasses, or a boolean `copy_metadata=True` + if/else call sites.
- **Real:**
  ```python
  def copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2, ...):
      ...
      use_srcentry = copy_function is copy2 or copy_function is copy   # identity fast path
      ...
      copy_function(srcobj, dstname)
  ```
  (Same file: `ignore_patterns(*patterns)` is a function factory; `_ARCHIVE_FORMATS` is a dispatch table with `register_archive_format`.)
- **Solves:** `EXT` (inject behavior without subclassing) + `PERF` (identity check keeps fast path) + `MEM` (plain functions, zero wrapper objects).

### E4. requests — hooks as dicts of callables
- **Files:** `src/requests/hooks.py`, `src/requests/sessions.py`, `src/requests/models.py`
- **Context:** event system: `default_hooks()` returns `{"response": []}`; users register callables; `Session.send()` dispatches them, chaining return values.
- **Naive:** subclass `Session` per extension point, or a fixed `EventBus` only the library can extend.
- **Real:**
  ```python
  def dispatch_hook(key, hooks, hook_data, **kwargs):
      hooks_dict = hooks or {}
      hook_list = hooks_dict.get(key)
      if hook_list:
          if isinstance(hook_list, Callable):
              hook_list = [hook_list]
          for hook in hook_list:
              _hook_data = hook(hook_data, **kwargs)
              if _hook_data is not None:
                  hook_data = _hook_data
      return hook_data
  ```
- **Solves:** `EXT` (auth/retry/logging plugins without subclassing) + `DYNAMIC` (hook lists merged per session/request at call time).

### E5. Starlette — `request_response` function factory
- **File:** `starlette/routing.py`
- **Context:** users write `def endpoint(request) -> response`; the factory returns an ASGI app closure, built once per endpoint.
- **Naive:** every endpoint author writes ASGI boilerplate, or a per-endpoint adapter class.
- **Real:**
  ```python
  def request_response(func):
      f = func if is_async_callable(func) else functools.partial(run_in_threadpool, func)
      async def app(scope, receive, send):
          request = Request(scope, receive, send)
          response = await f(request)
          await response(scope, receive, send)
      return app
  ```
- **Solves:** `READ` (handlers stay plain functions) + `DYNAMIC` (wrapper built once at setup, not per request) + `PERF` (async handlers take the identity branch).

### E6. FastAPI — `dependency_overrides` keyed by callables
- **Files:** `fastapi/applications.py`, `fastapi/dependencies/utils.py`
- **Context:** dependencies are callables; tests swap them via a dict where the *original function object is the key*.
- **Naive:** string-keyed registry (`app.dependency_overrides["get_db"]`) — fragile under refactors; or global test flags.
- **Real:**
  ```python
  self.dependency_overrides: dict[Callable, Callable] = {}
  ...
  call = dependency_overrides_provider.dependency_overrides.get(original_call, original_call)
  ```
- **Solves:** `DYNAMIC` (test-time substitution, zero app changes) + `STATE` (override table on the app, keyed by callable identity — refactor-proof, typo-proof).

### E7. CPython — `unittest.TestLoader.sortTestMethodsUsing`
- **File:** `Lib/unittest/loader.py`
- **Context:** test ordering policy is a plain function stored as a class attribute; `getTestCaseNames` sorts with it.
- **Naive:** hardcode `sorted(testFnNames)`; custom order requires copying the loader.
- **Real:**
  ```python
  sortTestMethodsUsing = staticmethod(util.three_way_cmp)
  ...
  testFnNames.sort(key=functools.cmp_to_key(self.sortTestMethodsUsing))
  ```
- **Solves:** `EXT` (one swappable attribute — `defaultTestLoader.sortTestMethodsUsing = None` is a documented idiom) + `STATE` (callable lives as data on the object).

### E8. botocore — `HierarchicalEmitter` event dispatch
- **File:** `botocore/hooks.py`
- **Context:** plugin system: dotted event names (`before-call.ec2.DescribeInstances`); handlers registered via `register()`/`register_first()`/`register_last()`, stored in a prefix trie.
- **Naive:** fixed call sites invoking named methods — every plugin needs core SDK changes.
- **Real:**
  ```python
  def _emit(self, event_name, kwargs, stop_on_response=False):
      handlers_to_call = self._lookup_cache.get(event_name)
      if handlers_to_call is None:
          handlers_to_call = self._handlers.prefix_search(event_name)
          self._lookup_cache[event_name] = handlers_to_call
      ...
      for handler in handlers_to_call:
          response = handler(**kwargs)
          responses.append((handler, response))
          if stop_on_response and response is not None:
              return responses
      return responses
  ```
- **Solves:** `EXT` (external plugins register without touching SDK code) + `PERF` (lookup cache short-circuits the common "nobody listening" case).

---

## Family F — Agentic / LLM libraries (LangChain, LlamaIndex, AutoGen/AG2, Agno)

Verified against the agentic frameworks themselves (LangChain `master`, LlamaIndex `main` +
`run-llama/llama-agents` `main`, AG2 `v0.8.7`, Agno `main`). **Orientation:** these are the
patterns your own LLM tool-calling code (`function/context.py`: `inspect.signature` +
`Annotated` + `get_type_hints` + a decorator registry) is already touching — tool registration,
signature introspection, and dispatch are exactly where the pros use ch. 7 moves. When you build
an agent tool layer, mirror these shapes.

### F1. LangChain — PII redaction sorts matches with `itemgetter` (PERF / CORRECT)
- **File:** `libs/langchain_v1/langchain/agents/middleware/_redaction.py`
- **Context:** regex finds PII spans (start/end offsets) in an LLM input; replacements must run
  from the *end backwards* so earlier offsets stay valid.
- **Naive:** `matches.sort(key=lambda m: m["start"], reverse=True)` — or replacing forward and
  tracking offset drift.
- **Real:**
  ```python
  for match in sorted(matches, key=operator.itemgetter("start"), reverse=True):
      replacement = f"[REDACTED_{match['type'].upper()}]"
      result = result[: match["start"]] + replacement + result[match["end"] :]
  ```
- **Solves:** `READ` (intent-named key) + `CORRECT` (reverse order keeps offsets valid) + `PERF`
  (C-level key on a hot path).

**How it works (deep dive):** the whole module is a ch. 7 showcase. Detectors are plain
functions — `Detector = Callable[[str], list[PIIMatch]]` — collected in a **dispatch table**:
```python
BUILTIN_DETECTORS: dict[str, Detector] = {
    "email": detect_email, "credit_card": detect_credit_card,
    "ip": detect_ip, "mac_address": detect_mac_address, "url": detect_url,
}
```
`apply_strategy()` dispatches on the strategy string to `_apply_redact_strategy` /
`_apply_mask_strategy` / `_apply_hash_strategy` (or raises `PIIDetectionError` for `"block"`).
All three apply functions use the same `itemgetter("start")` reverse sort. Why reverse? A match
is a `TypedDict` with `start`/`end` offsets into the *original* string. Slicing
`result[:start] + replacement + result[end:]` changes the length of everything after `end`, so
any later match's offsets would be wrong. Processing highest-`start` first means you only ever
edit text *after* the next match you'll touch. `itemgetter("start")` works because `PIIMatch` is
dict-like — exactly the "accessor factory on dicts" case from Family A. Note also
`resolve_detector()`: custom detectors are normalized by wrapping them in a `_normalizing_detector`
closure (a function factory), and string detectors become `regex_detector` closures — "build the
callable at runtime" everywhere.

### F2. LangChain — `RunnableLambda` introspects `itemgetter` via `repr` (CORRECT / DYNAMIC)
- **File:** `libs/core/langchain_core/runnables/base.py` (~lines 4901–4921)
- **Context:** `RunnableLambda` wraps arbitrary functions; to build a Pydantic input schema it
  must understand what the function consumes — including `operator.itemgetter` objects.
- **Naive:** `isinstance` special-casing for every callable type, or giving up on schema for
  accessor-style lambdas.
- **Real:** parse the `repr` of an `itemgetter` (e.g. `operator.itemgetter(0)`) to recover the
  indices and synthesize matching schema fields.
- **Solves:** `CORRECT` (schema matches the real input contract) + `DYNAMIC` (runtime
  introspection instead of hand-written schema).

**How it works (deep dive):** `RunnableLambda` accepts *any* callable — `def`, `lambda`,
`functools.partial`, `operator.itemgetter`, a callable object. When LangChain needs the input
schema (to validate, to document, to feed a model), it introspects the wrapped callable. For
`itemgetter` there is no signature to read — `inspect.signature` fails — so LangChain falls back
to parsing `repr(func)`: `operator.itemgetter(0)` → index `0` → a schema with one positional
field. This is the "function as data" idea taken to its extreme: the *string representation* of
the callable is treated as data and parsed. The lesson for your own tool layer: when you accept
arbitrary callables, decide *at runtime* how to derive their contract instead of assuming every
callable has a signature.

### F3. LangChain — `RouterRunnable` dispatch table (EXT / READ)
- **File:** `libs/core/langchain_core/runnables/router.py`
- **Context:** route to one of several runnables by a runtime key.
- **Naive:** `if key == "a": ... elif key == "b": ...` chain.
- **Real:**
  ```python
  class RouterRunnable(RunnableSerializable[RouterInput, Output]):
      def __init__(self, runnables: Mapping[str, Runnable]):
          self.runnables = runnables

      def invoke(self, input, config=None, **kwargs):
          key = input["key"]
          actual_input = input["input"]
          if key not in self.runnables:
              msg = f"No runnable associated with key '{key}'"
              raise ValueError(msg)
          runnable = self.runnables[key]
          return runnable.invoke(actual_input, config)
  ```
- **Solves:** `EXT` (add a route = add a dict entry) + `READ` (no branching noise).

**How it works (deep dive):** the dict *is* the dispatch — there is no `if/elif` anywhere.
`invoke`/`ainvoke`/`batch`/`abatch` all do the same two steps: look up `self.runnables[key]`,
delegate. Unknown keys raise a clean `ValueError` naming the key (no silent fall-through, no
`KeyError` leaking). `batch` even pre-checks all keys up front (`if any(key not in
self.runnables for key in keys)`) so a batch fails before doing partial work. Note the input
shape: `{"key": ..., "input": ...}` — the key travels *with* the payload, so the router is
itself a runnable that can be composed in chains. This is P7 (dispatch table) as a reusable
component: LangChain didn't write one router for agents, one for tools, one for models — it
wrote one `Mapping[str, Runnable]` and reused it everywhere.

### F4. LangChain — `@tool` decorator factory (EXT / READ)
- **File:** `libs/core/langchain_core/tools/convert.py` + `tools/base.py` (schema) + `tools/structured.py` (StructuredTool)
- **Context:** expose a plain function as an LLM-callable tool; the schema is derived from the
  signature + docstring, not maintained by hand.
- **Naive:** hand-written `Tool` objects with duplicated schema definitions that drift from the
  function.
- **Real:** `@tool` (optionally `@tool(name=..., return_direct=True)`) wraps the function into a
  `StructuredTool`; `create_schema_from_function` builds the Pydantic model from the signature.
- **Solves:** `EXT` (add a tool = write one function) + `READ` (single source of truth).

**How it works (deep dive):** `tool()` is a decorator factory with overloads for every usage —
bare `@tool`, `@tool("search")`, `@tool(return_direct=True)`, and even runnable conversion. The
core is `_create_tool_factory(tool_name)` returning `_tool_factory(dec_func)`:
```python
if isinstance(dec_func, Runnable):
    # wrap the runnable in invoke/ainvoke closures
    def invoke_wrapper(callbacks=None, **kwargs):
        return runnable.invoke(kwargs, {"callbacks": callbacks})
    func, coroutine, schema = invoke_wrapper, ainvoke_wrapper, runnable.input_schema
elif inspect.iscoroutinefunction(dec_func):
    coroutine, func, schema = dec_func, None, args_schema
else:
    coroutine, func, schema = None, dec_func, args_schema

if infer_schema or args_schema is not None:
    return StructuredTool.from_function(func, coroutine, name=tool_name, ...)
```
Three branches, decided by `isinstance`/`inspect.iscoroutinefunction` — then one constructor.
The schema comes from `create_schema_from_function`: `inspect.signature(func)` → pydantic
`validate_arguments` → a model; `self`/`cls` are filtered out for methods; reserved
injection names (`config`, `run_manager`, `callbacks`) are excluded from the schema; with
`parse_docstring=True` the Google-style docstring supplies per-argument descriptions. The
decorator *returns a `StructuredTool` object, not the function* — so `@tool`-decorated functions
are no longer callable as plain functions; they became data (schema + description + callable)
that the agent loop consumes. That's the full P8 registry-decorator lifecycle: write one
function → decorate → framework derives everything else.

### F5. LlamaIndex — `@step` decorator registers workflow steps (EXT / CORRECT)
- **File:** `packages/llama-index-workflows/src/workflows/decorators.py` (run-llama/llama-agents; re-exported by `llama-index-core/llama_index/core/workflow/decorators.py`)
- **Context:** workflow steps are methods decorated with `@step`; the decorator validates the
  signature (must accept a `Context`) and registers the step.
- **Naive:** manual step registry dict + runtime validation scattered in the runner.
- **Real:** `@step(num_workers=...)` wraps the method, validates the signature, and registers it
  into the workflow's step configs.
- **Solves:** `EXT` (add a step = decorate a method) + `CORRECT` (fail-fast signature validation
  at definition time).

**How it works (deep dive):** the `step()` decorator supports both bare `@step` and factory
`@step(num_workers=4, retry_policy=...)` forms with one trick:
```python
def step(func=None, *, workflow=None, num_workers=4, retry_policy=None, ...):
    def decorator(func):
        localns = _capture_decorator_localns()
        return _apply_step_decorator(func, num_workers=num_workers, ..., localns=localns)
    if func is not None:
        # used WITHOUT parentheses: @step
        return _apply_step_decorator(func, num_workers=num_workers, ..., localns=_capture_callsite_localns())
    return decorator
```
`_apply_step_decorator` then: (1) validates `num_workers` is a positive int; (2) calls
`make_step_function`, which runs `inspect_signature(func, localns=localns)` and
`validate_step_signature(spec)` — raising `WorkflowValidationError` with a specific message if
the step doesn't accept a `Context` or its event types are wrong; (3) builds a `StepConfig`
dataclass (accepted events, return types, context parameter, num_workers, retry policy,
resources, fan-out/collect metadata); (4) **attaches it as an attribute on the function itself**:
```python
casted = cast(StepFunction, func)
casted._step_config = StepConfig(accepted_events=..., event_name=..., ...)
```
The function *carries its own metadata* — the workflow runner later reads `step._step_config`
to build the graph. Registration: for free functions the decorator calls
`workflow.add_step(func)` explicitly (and raises if you forgot `workflow=MyWorkflow`); for
methods, association is automatic via `__qualname__`. The `_capture_*_localns()` helpers walk
the caller's stack frames to grab local namespaces so `Annotated` types and event classes
defined at the call site resolve during signature evaluation — the same "signature is data"
idea as your `context.py`. `@catch_error` reuses the whole machinery: it validates the handler
accepts `StepFailedEvent` and stamps `role="catch_error"` onto the same `_step_config`.

### F6. LlamaIndex — `FunctionTool` callable object (STATE / READ)
- **File:** `llama-index-core/llama_index/core/tools/function_tool.py`
- **Context:** a tool must be callable *and* carry schema + metadata; the same object is passed
  to the LLM layer and the executor.
- **Naive:** closure + a parallel metadata dict that can drift.
- **Real:** `FunctionTool.__call__` invokes the wrapped function with validated args; schema and
  metadata live on the instance.
- **Solves:** `STATE` (schema/metadata travel with the callable) + `READ`.

**How it works (deep dive):** `FunctionTool(AsyncBaseTool)` is P6 (`__call__` class) in its
purest form:
```python
def __call__(self, *args, **kwargs) -> ToolOutput:
    all_kwargs = {**self.partial_params, **kwargs}
    return self.call(*args, **all_kwargs)

def call(self, *args, **kwargs) -> ToolOutput:
    all_kwargs = {**self._field_defaults, **self.partial_params, **kwargs}
    if self.requires_context and self.ctx_param_name is not None:
        if self.ctx_param_name not in all_kwargs:
            raise ValueError("Context is required for this tool")
    raw_output = self._fn(*args, **all_kwargs)
    ...
    return ToolOutput(blocks=output_blocks, tool_name=self.metadata.get_name(),
                      raw_input={"args": args, "kwargs": tool_output_kwargs},
                      raw_output=raw_output)
```
State lives on the instance: `_fn` (the wrapped callable), `_field_defaults` (defaults captured
from the signature), `partial_params` (pre-bound args — note the name!), `metadata` (name +
description + schema), `requires_context`/`ctx_param_name` (injected `Context` params). Calling
the tool merges defaults → partials → call kwargs, validates context requirements, invokes
`self._fn`, and wraps the raw output into a `ToolOutput` with full provenance. `from_defaults`
is the factory classmethod that builds all this from a function + metadata. The same object is
handed to the LLM (for its schema) and to the executor (for the call) — one object, two roles,
no drift.

### F7. LlamaIndex — `CallbackManager` hooks (EXT / STATE)
- **File:** `llama-index-core/llama_index/core/callbacks/base.py`
- **Context:** event handlers are registered callables; the manager dispatches events to all of
  them.
- **Naive:** hardcoded logging/telemetry calls at every event site.
- **Real:** `CallbackManager` holds a list of handler callables; `event()` fans out to each.
- **Solves:** `EXT` (add a handler = register a callable) + `STATE` (handlers live as data).

**How it works (deep dive):** the manager is a list of handlers plus a context-manager event
API:
```python
class CallbackManager(BaseCallbackHandler, ABC):
    def __init__(self, handlers=None):
        self.handlers: List[BaseCallbackHandler] = handlers or []

    def add_handler(self, handler): self.handlers.append(handler)
    def remove_handler(self, handler): self.handlers.remove(handler)

    def event(self, event_type, payload=None, event_id=None):
        event = EventContext(self, event_type, event_id=event_id)
        event.on_start(payload=payload)          # fans out to every handler
        try:
            yield event
        except Exception as e:
            ... event.on_end(payload={EventPayload.EXCEPTION: e}) ...
        finally:
            if not event.finished:
                event.on_end(payload=payload)
```
`on_event_start`/`on_event_end` are plain `for handler in self.handlers: handler.on_event_start(...)`
loops. Instrumentation sites just write `with callback_manager.event(CBEventType.QUERY, payload=...) as event:`.
Adding a tracer, a logger, or a metrics exporter = `add_handler(callable)` — zero changes to the
instrumented code. This is the requests-hooks pattern (Family E) scaled to a framework: hooks as
data, lifecycle managed by a context manager so `on_end` always fires, even on exceptions.

### F8. AG2 — `register_for_llm` / `register_for_execution` decorator factories (EXT / CORRECT / READ)
- **File:** `autogen/agentchat/conversable_agent.py` (AG2 v0.8.7, lines 3547–3620 and 3648–3706)
- **Context:** one function is exposed to the LLM (schema) and to the executor (real call) with
  two decorators; the decorator registers into the agent's function map and builds the schema
  from the signature.
- **Naive:** hand-maintained dict of name → (schema, callable) that drifts from the code.
- **Real:**
  ```python
  @agent.register_for_llm(description="...")   # builds schema from signature
  def get_weather(city: str) -> str: ...

  @agent.register_for_execution()              # registers the real callable
  def get_weather(city: str) -> str: ...
  ```
- **Solves:** `EXT` (add a tool = decorate two functions) + `CORRECT` (schema auto-built from
  signature) + `READ` (no duplication).

**How it works (deep dive):** both are decorator *factories* — `register_for_llm(*, name=None,
description=None, api_style="tool", silent_override=False)` returns `_decorator`, and
`_decorator` does three things:
```python
def _decorator(func_or_tool, name=name, description=description) -> Tool:
    tool = self._create_tool_if_needed(func_or_tool, name, description)
    self._register_for_llm(tool, api_style, silent_override=silent_override)
    self._tools.append(tool)
    return tool
```
`_create_tool_if_needed` is the polymorphic entry: if you pass a `Tool` it reuses it (re-wrapping
only if name/description changed); if you pass a function it builds
`Tool(func_or_tool=function, name=name, description=description)` — the `Tool` constructor reads
the signature (including `Annotated[str, "description of a parameter"]`!) to build the JSON
schema; anything else raises `TypeError`. `_register_for_llm` pushes that schema into the LLM
config (`update_tool_signature`/`update_function_signature`) so the model sees the tool. The
decorator **returns the `Tool`, not the function** — which is what makes the stacked form work:
```python
@user_proxy.register_for_execution()
@agent2.register_for_llm()
@agent1.register_for_llm(description="This is a very useful function")
def my_function(a: Annotated[str, "description of a parameter"] = "a", b: int, c=3.14) -> str:
    return a + str(b * c)
```
Inner decorator returns a `Tool`; the next decorator accepts `Union[F, Tool]` and reuses it;
each agent gets the schema, the executor gets the callable. `register_for_execution`'s
`_decorator` does the other half:
```python
tool = self._create_tool_if_needed(func_or_tool, name, description)
chat_context = ChatContext(self)
chat_context_params = {param: chat_context for param in tool._chat_context_param_names}
self.register_function(
    {tool.name: self._wrap_function(tool.func, chat_context_params, serialize=serialize)},
    silent_override=silent_override,
)
return tool
```
It binds a `ChatContext` into any parameter the tool declared for it, then registers
`name → wrapped callable` into `_function_map`. `_wrap_function` is itself a ch. 7 gem:
```python
@functools.wraps(func)
async def _a_wrapped_func(*args, **kwargs):
    retval = await func(*args, **kwargs, **inject_params)
    if logging_enabled():
        log_function_use(self, func, kwargs, retval)
    return serialize_to_str(retval) if serialize else retval

wrapped_func = _a_wrapped_func if inspect.iscoroutinefunction(func) else _wrapped_func
wrapped_func._origin = func   # keep a back-reference for tests
```
`@functools.wraps` preserves metadata, `inspect.iscoroutinefunction` picks the sync/async
wrapper, and `_origin` keeps the original callable reachable — the "partial has no `__name__`"
pitfall solved by wrapping properly.

### F9. AG2 — `execute_function` dispatch table (CORRECT / EXT)
- **File:** `autogen/agentchat/conversable_agent.py` (v0.8.7, line 3117)
- **Context:** when the LLM requests a tool call, the agent looks the function up by name and
  calls it.
- **Naive:** `if name == "get_weather": ... elif ...` chain.
- **Real:** `self._function_map[name](arguments)` — dict lookup + call; unknown names fail cleanly.
- **Solves:** `CORRECT` (unknown name → clean error, no fall-through) + `EXT`.

**How it works (deep dive):** the LLM emits a tool call as `{"name": ..., "arguments": "{json}"}`.
`execute_function` is the dispatch point:
```python
func_name = func_call.get("name", "")
func = self._function_map.get(func_name, None)
is_exec_success = False
if func is not None:
    input_string = self._format_json_str(func_call.get("arguments", "{}"))
    try:
        arguments = json.loads(input_string)
    except json.JSONDecodeError as e:
        arguments = None
        content = f"Error: {e}\n The argument must be in JSON format."
    if arguments is not None:
        ...
        try:
            content = func(**arguments)          # the actual call
            is_exec_success = True
        except Exception as e:
            content = f"Error: {e}"
```
Three failure modes handled without any branching on *which* tool: unknown name (`.get` →
None → error message), malformed JSON (caught → error message), runtime exception (caught →
error message). The dict lookup *is* the dispatch; the error handling is uniform because every
tool has the same shape `func(**arguments)`. `register_function` merges new entries into
`_function_map` — so adding a tool is purely additive.

### F10. AG2 — `register_reply` hooks with triggers (EXT / STATE)
- **File:** `autogen/agentchat/conversable_agent.py` (v0.8.7, line 538)
- **Context:** reply strategies (function calling, user input, code execution) are registered
  hooks; each declares a trigger predicate.
- **Naive:** one monolithic `generate_reply` with nested conditionals.
- **Real:** `register_reply(trigger, reply_func)` appends to `_reply_func_list`;
  `generate_reply` iterates hooks and calls those whose trigger matches.
- **Solves:** `EXT` (new reply strategy = register a hook) + `STATE` (ordered hook list on the
  agent).

**How it works (deep dive):** `register_reply` accepts a trigger that can be a class, a string,
an agent instance, a callable predicate, a list of any of those, or `None` — and validates it
up front (`raise ValueError("trigger must be a class, a string, an agent, a callable or a list.")`).
It inserts `{"trigger": trigger, "reply_func": reply_func, "config": config, ...}` at a
`position` in `_reply_func_list` (later registrations checked earlier by default; `position`
overrides). Each reply function has the uniform signature
`(recipient, messages, sender, config) -> (bool, reply)`. `generate_reply` walks the list,
evaluates each trigger against the sender, and calls the first matching reply function — which
may itself return `(False, None)` to say "not me, keep walking". The agent's whole behavior
(function calling, code execution, human input, custom strategies) is a *list of hooks*, not a
method with conditionals. Third parties extend the agent by appending to the list — the
botocore `HierarchicalEmitter` idea (E8) with trigger predicates instead of dotted names.

### F11. AutoGen — `FunctionTool.run` uses `partial` for the threadpool (PERF / CORRECT)
- **File:** `autogen/function_utils.py`
- **Context:** sync tool functions must run in a threadpool so the event loop never blocks.
- **Naive:** `run_in_executor(None, lambda: fn(*args, **kwargs))` — lambda hides the callable.
- **Real:** `functools.partial(fn, *args, **kwargs)` handed to `run_in_executor`.
- **Solves:** `PERF` (no blocking) + `CORRECT` (kwargs preserved, callable introspectable).

**How it works (deep dive):** when an async agent calls a sync tool, blocking the event loop
would freeze every other task. The fix is P5 (freeze arguments): build the call *now* with
`functools.partial(fn, *args, **kwargs)` and hand the frozen callable to
`asyncio.get_event_loop().run_in_executor(None, partial)`. Why `partial` and not a lambda?
`partial` preserves the call as data — `.func`, `.args`, `.keywords` are inspectable, and the
callable's identity is stable for caching/dedup; a lambda creates a fresh closure object each
time with no introspection. Same shape as Starlette's `run_in_threadpool` (Family C): the
framework can't pass context later, so you freeze it now.

### F12. AG2 — `AllOf.arm` uses `partial` to avoid the late-binding bug (CORRECT / STATE)
- **File:** `autogen/agentchat/contrib/` (AllOf aggregation)
- **Context:** AllOf aggregates replies from multiple agents; each arm must capture *its own*
  agent at creation time.
- **Naive:** closure over a loop variable → late binding: every arm calls the last agent.
- **Real:** `functools.partial(agent.generate_reply, ...)` per arm — the agent is bound eagerly.
- **Solves:** `CORRECT` (no late-binding) + `STATE` (each arm carries its own callable).

**How it works (deep dive):** the classic Python trap: build N closures in a loop, each
referencing the loop variable, and all N closures see the *final* value (late binding). AllOf
builds one "arm" per child agent; if an arm were `lambda: agent.generate_reply(...)` the lambda
would resolve `agent` from the enclosing scope at call time — by then the loop has finished and
every arm points at the last agent. `functools.partial(agent.generate_reply, ...)` evaluates
`agent` *at partial-construction time* and stores it in `.args` — eager binding, no closure
scope involved. This is the single most common real-world `partial` bug fix; if you ever write
`[lambda: f(x) for x in xs]`, this is why you shouldn't.

### F13. Agno — `Toolkit.register` keeps sync/async registries (EXT / CORRECT)
- **File:** `libs/agno/agno/tools/toolkit.py`
- **Context:** a toolkit collects functions; sync and async functions are registered separately
  so the runner can call each correctly.
- **Naive:** one list + runtime `isinstance`/`inspect.iscoroutinefunction` dispatch.
- **Real:** `self.functions` and `self.async_functions` lists; `register()` appends to the right
  one.
- **Solves:** `EXT` + `CORRECT` (no isinstance dispatch at call time).

**How it works (deep dive):** the toolkit keeps two `OrderedDict[str, Function]` registries —
`self.functions` and `self.async_functions` — and `register()` decides *at registration time*
which one gets the entry:
```python
def register(self, function, name=None):
    if isinstance(function, Function):
        is_async = function.entrypoint is not None and iscoroutinefunction(function.entrypoint)
        return self._register_decorated_tool(function, name, is_async=is_async)
    is_async = iscoroutinefunction(function)
    tool_name = name or function.__name__
    if self.include_tools is not None and tool_name not in self.include_tools:
        return
    if self.exclude_tools is not None and tool_name in self.exclude_tools:
        return
    f = Function(name=tool_name, entrypoint=function, cache_results=..., ...)
    if is_async:
        self.async_functions[f.name] = f
    else:
        self.functions[f.name] = f
```
The `iscoroutinefunction` check happens once, at registration; the runner later just iterates
`self.functions` (sync) or `self.async_functions` (async) with no per-call type checks.
`_register_decorated_tool` handles `@tool`-decorated methods: the decorator produced a
`Function` whose entrypoint is an *unbound* method, so registration rebinds it to `self`
(preserving all decorator settings). Include/exclude filters are applied at registration too —
"data over control flow" for tool selection.

### F14. Agno — `@tool` decorator factory (EXT / READ)
- **File:** `libs/agno/agno/tools/decorator.py`
- **Context:** turn a plain function into a `Tool` with schema derived from signature/docstring.
- **Naive:** hand-written `Tool` + duplicated schema.
- **Real:** `@tool` builds the `Function`/`Tool` from the decorated function.
- **Solves:** `EXT` + `READ` (single source of truth).

**How it works (deep dive):** `tool(*args, **kwargs)` handles both `@tool` and `@tool(...)`:
```python
if len(args) == 1 and callable(args[0]) and not kwargs:
    return decorator(args[0])   # bare @tool
return decorator                # @tool(name=..., ...)
```
The `decorator(func)` body is a masterclass in decorator hygiene:
1. **Fail fast on config:** unknown kwargs raise `ValueError` listing the valid ones
   (`VALID_KWARGS` frozenset); mutually exclusive flags (`requires_user_input` /
   `requires_confirmation` / `external_execution`) are checked — at most one may be true.
2. **Wrap with metadata preserved:** three `@wraps(func)` wrappers (sync / async / async-gen)
   chosen by `isasyncgenfunction` / `_is_async_function`, plus `update_wrapper(wrapper, func)`.
3. **Read sentinels from stacked decorators:** `getattr(func, "_agno_approval_type", None)` —
   an `@approval` decorator applied *below* `@tool` stamps an attribute the tool decorator
   reads to set HITL flags. Decorators communicating through function attributes!
4. **Build the Function:** `description` falls back to `get_entrypoint_docstring(wrapper)`
   (see F17), `name` falls back to `func.__name__`, then
   `function = Function(**tool_config)` and `function.process_entrypoint()` derives the schema
   from the signature.
The decorated name is now a `Function` object — data (schema, description, hooks, cache config)
plus the wrapped callable as `entrypoint`.

### F15. Agno — `FunctionCall.execute` dispatches via stored entrypoint (PERF / EXT)
- **File:** `libs/agno/agno/tools/function.py`
- **Context:** a `FunctionCall` knows its entrypoint (the wrapped callable); `execute()` calls it
  with parsed arguments.
- **Naive:** re-dispatch by name at call time.
- **Real:** `self.function.entrypoint(**arguments)` — the callable is stored as data.
- **Solves:** `PERF` (direct call, no lookup) + `EXT`.

**How it works (deep dive):** `Function` stores `entrypoint: Optional[Callable]` as a field
(line 808) — the callable is data on the model. `FunctionCall.execute()` builds a closure that
calls it directly:
```python
def execute_entrypoint(name, func, args):
    if cached_result is not None and not self._moved_its_key(cache_key, entrypoint_args):
        return _detached(cached_result)
    arguments = entrypoint_args.copy()
    if self.arguments is not None:
        arguments.update(self.arguments)
    slot = _start_entrypoint_call(raw_results) if raw_results is not None else -1
    result = self.function.entrypoint(**arguments)
    if raw_results is not None:
        _record_entrypoint_result(raw_results, slot, result)
    return result
```
No name lookup, no registry walk — the callable was bound when the `FunctionCall` was built.
Caching, result recording, and argument merging all happen around the direct call. This is the
"function as data" payoff: because the callable travels with its metadata, execution is a
one-liner.

### F16. Agno — `reduce` composes tool hooks (EXT / READ)
- **File:** `libs/agno/agno/tools/function.py`
- **Context:** tools support pre/post-processing hooks; hooks are chained so each output feeds
  the next.
- **Naive:** nested hand-written wrappers.
- **Real:** hooks composed with `functools.reduce` into one pipeline callable.
- **Solves:** `EXT` (add a hook = append a callable) + `READ`.

**How it works (deep dive):** `FunctionCall.execute()` composes the hook chain with
`functools.reduce`:
```python
if not self.function.tool_hooks:
    return execute_entrypoint          # fast path: no hooks, no composition

def create_hook_wrapper(inner_func, hook):
    """Create a nested wrapper for the hook."""
    def wrapper(name, func, args):
        # Pass the inner function as next_func to the hook
        # The hook will call next_func to continue the chain
        def next_func(**kwargs):
            return inner_func(name, func, kwargs)
        hook_args = self._build_hook_args(hook, name, next_func, args)
        return self._safe_hook_call(hook, hook_args)
    return wrapper

chain = reduce(create_hook_wrapper, hooks, execute_entrypoint)
```
`reduce` folds the list of hooks into a single callable: each hook becomes a wrapper around the
next, and the innermost element is `execute_entrypoint` itself. A hook receives `next_func` and
decides whether to call it (before/after/around semantics). Adding a hook = appending to
`tool_hooks` — no wrapper surgery. Note the async twin at line 2398 (`reduce(create_hook_wrapper,
hooks, execute_entrypoint_async)`) and the guard that filters coroutine hooks out of the sync
path with a warning. This is P3 (operator-as-value) applied to composition: `reduce` with a
wrapper factory instead of a hand-rolled loop.

### F17. Agno — partial-aware docstring/signature extraction (CORRECT)
- **File:** `libs/agno/agno/tools/function.py` (`get_entrypoint_docstring`, line 607)
- **Context:** when a tool function is built via `functools.partial`, the docstring/signature
  must come from the *underlying* function.
- **Naive:** `inspect.getdoc(func)` on the partial → empty docstring, broken schema.
- **Real:** unwrap partials (`func.func` when `isinstance(func, functools.partial)`) before
  extracting docstring/signature.
- **Solves:** `CORRECT` (schema/docstring survive `partial` wrapping — the flip side of P5's
  "partial has no `__name__`" pitfall).

**How it works (deep dive):** `functools.partial` objects have no `__doc__`, no `__name__`, and
`inspect.signature` on them is unreliable — the exact pitfall from the SKILL.md pitfalls
section. Agno's tool layer must handle tools built from partials (e.g. a toolkit method
pre-bound with config), so `get_entrypoint_docstring` special-cases them:
```python
def get_entrypoint_docstring(entrypoint: Callable) -> str:
    if isinstance(entrypoint, partial):
        return str(entrypoint)
    docstring = getdoc(entrypoint)
    ...
```
For a partial it returns the repr (`functools.partial(<function foo at 0x...>, ...)`) rather
than an empty string — the tool still gets *some* description, and the schema derivation
(`process_entrypoint`) unwraps the partial to reach the real signature. Lesson: if your tool
layer accepts callables, decide explicitly what a `partial` means — unwrap it
(`entrypoint.func`), or document the fallback. The pros don't let `partial` silently break
metadata.

---

## Quick reference: which family for which symptom

| Symptom in your code | Family | Canonical fix |
|---|---|---|
| `key=lambda x: x[i]` / `x.attr` | A | `itemgetter(i)` / `attrgetter('attr')` |
| `map(lambda s: s.method(...), xs)` | A | `map(methodcaller('method', ...), xs)` |
| `int(x)` for indices/exponents | B | `operator.index(x)` |
| `lambda a, b: a + b` passed around | B | `operator.add` |
| framework calls my callable with no context | C | `functools.partial(fn, **ctx)` |
| callable must remember state | D | `__call__` class |
| `if name == ... elif ...` chain | E | dict of callables |
| "users should extend this" | E | registry decorator / hooks list |
| LLM tool registration (`@tool`, `register_for_llm`) | F | decorator factory + signature-derived schema |
| LLM tool dispatch (LLM asks for `name(args)`) | F | dict of callables keyed by tool name |
| agent reply strategies / event handlers | F | hook lists with trigger predicates |
| sync tool in an async agent loop | F | `functools.partial` + `run_in_executor` |
