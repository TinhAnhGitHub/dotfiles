# Chapter 18 — `with`, `match`, and `else` blocks

## P18.1 — Make resource ownership lexical

Use a context manager when setup and cleanup must be paired even if the body raises:

```python
from contextlib import contextmanager

@contextmanager
def transaction(store):
    store.begin()
    try:
        yield store
    except Exception:
        store.rollback()
        raise
    else:
        store.commit()
```

For a class manager, `__enter__` returns the value bound by `as`; `__exit__` receives
`exc_type`, `exc_value`, and `traceback`. Returning a truthy value suppresses the exception, so
do that only for a deliberately narrow, documented exception.

`contextlib.contextmanager` turns the code before `yield` into setup and the code after it into
cleanup. Exceptions from the `with` body are raised at the `yield` point, which is why `try`/
`except`/`finally` must surround the yield when restoration is required.

## P18.2 — Prefer standard managers over global monkey-patching

The local `mirror.py` teaching example temporarily replaces `sys.stdout.write`. It illustrates
the protocol but changes process-global state and is unsafe under concurrency. Prefer
`contextlib.redirect_stdout`, an explicit stream object, or a narrow dependency-injected writer.

Always restore global state in `finally`. Test both normal exit and exceptional exit.

## P18.3 — Use structural pattern matching for closed shape dispatch

`match` is useful when the cases are a finite vocabulary of data shapes:

```python
match action:
    case Click(x=x, y=y):
        return click(x, y)
    case TypeText(text=text) if text:
        return type_text(text)
    case KeyPress(key=key):
        return press(key)
    case _:
        raise ValueError("unsupported action")
```

Keep cases specific-to-general. Use guards for semantic validation, and keep the wildcard case
explicit. Do not replace open-ended polymorphism or ordinary boolean checks with a giant pattern
matching statement.

The local `lispy/py3.10/lis.py` is the strongest example: it dispatches literals, symbols,
special forms, lambdas, definitions, mutation, and calls by shape. The `py3.9` version provides
the useful `if`/`elif` comparison.

## P18.4 — Understand `for`/`else` and `try`/`else`

- `for`/`else` runs the `else` block only when the loop was not exited by `break`.
- `while`/`else` has the same rule.
- `try`/`else` runs only when the `try` body completed without an exception.

Use these clauses to make “not found” and “success after risky operation” explicit. Avoid them when
the control flow becomes harder to scan than a named helper.

## Agentic repository evidence

- **LangGraph:** `SyncLangGraphClient.__enter__`/`__exit__` close the HTTP client; async stream
  objects cancel and gather watcher tasks during close. Local source:
  `reference/langgraph/libs/sdk-py/langgraph_sdk/_sync/client.py` and `_async/stream.py`.
- **LlamaIndex Workflows:** `_DurableWorkflowRuntime` owns async lifecycle; control-plane API
  code uses structural `match access` dispatch. Local source:
  `reference/llama-agents/packages/llama-agents-server/.../runtime.py` and
  `.../control_plane/build_api/build_app.py`.
- **AG2/AutoGen:** `LLMConfig` and cache contexts restore `ContextVar` state in `__exit__`; the
  Docker code executor stops its container on exit. Local source is vendored under
  `reference/SCALE-CUA/osworld_eval/mm_agents/coact/autogen/`.
- **ClawGUI Nanobot:** `AsyncExitStack` owns MCP connections and drains them during shutdown.
- **CogAgent:** FastAPI lifespan cleanup releases GPU resources after server shutdown.
- **browser-use:** GUI action handling uses structural action dispatch and browser cleanup in
  `finally`.

## Review checklist

- Does every acquired resource have one obvious owner and cleanup path?
- Is cleanup guaranteed on exceptions, cancellation, and early return?
- Is exception suppression narrow and tested?
- Is `match` dispatching a closed data vocabulary rather than hiding polymorphism?
- Are `for`/`else` and `try`/`else` expressing the intended success condition?
