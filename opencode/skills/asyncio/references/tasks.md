# asyncio Tasks — Deep Reference

Distilled from https://docs.python.org/3/library/asyncio-task.html (Python 3.14).

## Contents
1. [Task object API](#task-object-api)
2. [cancel() exact semantics](#cancel-exact-semantics)
3. [cancelling() / uncancel()](#cancelling--uncancel)
4. [TaskGroup failure & termination semantics](#taskgroup-failure--termination-semantics)
5. [Eager task factory](#eager-task-factory)
6. [gather / wait / as_completed subtleties](#gather--wait--as_completed-subtleties)
7. [Threads: to_thread and run_coroutine_threadsafe](#threads-to_thread-and-run_coroutine_threadsafe)
8. [Introspection](#introspection)

## Task object API

```python
class asyncio.Task(coro, *, loop=None, name=None, context=None, eager_start=False)
```

- A Future-like object running a coroutine. **Not thread-safe.**
- Inherits all Future APIs **except** `set_result()`/`set_exception()`.
- Manual instantiation is discouraged — use `asyncio.create_task()` or `TaskGroup.create_task()`.
- `context`: custom `contextvars.Context`; if omitted, the task copies the current context at creation.
- Generic over the wrapped coroutine's return type.

| Method | Since | Semantics |
|---|---|---|
| `done()` | | True when the coro returned, raised, or the task was cancelled |
| `result()` | | Returns the result; **re-raises** the coro's exception; raises `CancelledError` if cancelled; `InvalidStateError` if not done |
| `exception()` | | Raised exception, or `None` if returned normally; raises `CancelledError` if cancelled; `InvalidStateError` if not done |
| `add_done_callback(cb, *, context=None)` | | Low-level only; callback receives the task |
| `remove_done_callback(cb)` | | Low-level only |
| `get_name()` / `set_name(v)` | 3.8 | Task name, visible in repr |
| `get_coro()` | 3.8 | Wrapped coroutine; **may be None for eagerly-completed tasks (3.12+)** |
| `get_context()` | 3.12 | The task's contextvars Context |
| `get_stack(*, limit=None)` | | Frames of the suspended coro; empty list if completed/cancelled; traceback frames if terminated by exception |
| `print_stack(*, limit=None, file=None)` | | Prints stack/traceback |

## cancel() exact semantics

```python
cancel(msg=None) -> bool
```

- Returns `False` if the task is already done/cancelled, else `True`.
- Arranges for `CancelledError(msg)` to be thrown into the coroutine at its
  next await point on a later loop iteration — **not synchronously**.
- A not-yet-started task may be cancelled without any of its body executing.
- If the task awaits a Future, that Future is cancelled too, propagating down
  the whole chain of awaited objects.
- Unlike `Future.cancel`, cancellation is **not guaranteed**: the coroutine can
  catch and suppress `CancelledError` (discouraged; requires `uncancel()`).
- `cancelled()` returns True only when the thrown `CancelledError` propagated out.
- `msg` added in 3.9; since 3.11 the msg propagates from the cancelled task to its awaiter.

```python
task = asyncio.create_task(cancel_me())
await asyncio.sleep(1)
task.cancel()
try:
    await task
except asyncio.CancelledError:
    print("main(): cancel_me is cancelled now")
```

## cancelling() / uncancel()

Both added in **3.11**; intended for library internals, not ordinary user code.

```python
cancelling() -> int   # pending cancellation requests = cancel() calls − uncancel() calls
uncancel() -> int     # decrements the count; returns remaining count
```

Why they exist: structured-concurrency primitives (`asyncio.timeout()`,
TaskGroup) call `cancel()` on the *current* task internally to unwind their own
block, then call `uncancel()` so outer code keeps running:

```python
try:
    async with asyncio.timeout(1):
        await make_request()
        await make_another_request()
except TimeoutError:
    log("timeout")
await unrelated_code()   # NOT affected by the timeout above
```

Rules:
- If you deliberately suppress `CancelledError`, you must also call
  `uncancel()` to fully clear cancellation state.
- `cancelling() > 0` while still executing does **not** mean the task will be
  cancelled — subsequent `uncancel()` calls could bring it to zero.
- 3.13: when the count reaches zero, uncancel() rescinds a pending arranged throw.

## TaskGroup failure & termination semantics

```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(some_coro())
    t2 = tg.create_task(another_coro())
print(t1.result(), t2.result())
```

- All tasks awaited on exit; new tasks may be added even while waiting.
- First non-CancelledError failure → siblings cancelled and awaited; no new
  tasks accepted; the containing task's body is also cancelled (the
  CancelledError interrupts an await inside the body but doesn't escape the
  `async with`).
- After all finish, failures are combined into an `ExceptionGroup`
  (or `BaseExceptionGroup`) — handle with `except*`:

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(job(1))
        tg.create_task(job(2))
except* ValueError as eg:
    ...  # eg.exceptions holds the individual exceptions
```

- `KeyboardInterrupt`/`SystemExit` from a child: siblings still cancelled and
  awaited, but the original exception is re-raised bare, not grouped.
- If the `async with` body itself raises, that exception joins the group too.
- Nested groups don't mix internal/external cancellations; external
  cancellation + required ExceptionGroup re-cancels the parent so cancellation
  isn't lost (improved 3.13).
- 3.13: `create_task()` closes the given coroutine if the group is inactive.
- 3.14: tasks created but shut down before starting are cancelled without
  their coroutine running at all.

### Terminating a task group early (no native support)

Inject an exception-raising task and filter it with `except*`:

```python
class TerminateTaskGroup(Exception):
    """Exception raised to terminate a task group."""

async def force_terminate_task_group():
    raise TerminateTaskGroup()

async def main():
    try:
        async with TaskGroup() as group:
            group.create_task(job(1, 0.5))
            group.create_task(job(2, 1.5))
            await asyncio.sleep(1)
            group.create_task(force_terminate_task_group())
    except* TerminateTaskGroup:
        pass
```

## Eager task factory

Enable with `loop.set_task_factory(asyncio.eager_task_factory)` (3.12+).

- Coroutines begin executing **synchronously during Task construction**;
  scheduled onto the loop only if they block.
- Benefit: avoids scheduling overhead for coroutines that complete without
  blocking (e.g., cache/memoization hits).
- Caveats: semantic change — task execution order changes; eagerly-completed
  tasks never touch the loop; `get_coro()` returns None for them.
- `create_eager_task_factory(custom_task_constructor)` builds an equivalent
  factory with a custom Task subclass.
- 3.14: `create_task(..., eager_start=...)` overrides per-call; `None` defers
  to the loop's factory mode.

## gather / wait / as_completed subtleties

### gather(*aws, return_exceptions=False)
- Results ordered by input order, not completion order.
- `return_exceptions=False`: first exception propagates immediately; other
  children **keep running** (not cancelled).
- `return_exceptions=True`: exceptions appear in the result list.
- Cancelling the gather cancels all unfinished children; cancelling one child
  does NOT cancel the gather or siblings.
- Cancelling gather after it's marked done cancels nothing.

### wait(aws, *, timeout=None, return_when=ALL_COMPLETED)
- Takes Tasks/Futures only (bare coroutines forbidden since 3.11).
- Returns `(done, pending)` sets; never raises TimeoutError; never cancels on
  timeout; cancelling wait() leaves children running.
- `return_when`: FIRST_COMPLETED | FIRST_EXCEPTION | ALL_COMPLETED.

### as_completed(aws, *, timeout=None)
- Yields results as they finish. Since 3.13 usable both as async iterator
  (yields original tasks/futures) and plain iterator (yields coroutines to
  await). TimeoutError raised if deadline passes before all done; remaining
  tasks keep running.

## Threads: to_thread and run_coroutine_threadsafe

### asyncio.to_thread(func, /, *args, **kwargs)  (3.9+)
- Runs func in a separate thread; propagates current contextvars.Context.
- For I/O-bound work under the GIL; CPU-bound needs processes/GIL-releasing C extensions.

### asyncio.run_coroutine_threadsafe(coro, loop)  (3.5.1+)
- Submit a coroutine to a loop from another OS thread. Thread-safe.
- Returns a `concurrent.futures.Future`: `.result(timeout)`, `.cancel()`
  (cancels the task in the loop), exceptions surface through it.
- Requires explicit `loop` argument — unique among asyncio APIs.

```python
future = asyncio.run_coroutine_threadsafe(coro, loop)
try:
    result = future.result(timeout=10)
except TimeoutError:
    future.cancel()
```

Cross-thread rules (from asyncio-dev):
- Almost all asyncio objects are NOT thread-safe.
- Only `call_soon_threadsafe` / `run_coroutine_threadsafe` may be called from
  another thread; wrap everything else:
  `loop.call_soon_threadsafe(fut.cancel)`.
- Debug mode makes wrong-thread calls raise.

## Introspection

| Function | Since | Behavior |
|---|---|---|
| `asyncio.current_task(loop=None)` | 3.7 | Running Task or None |
| `asyncio.all_tasks(loop=None)` | 3.7 | Set of unfinished tasks on the loop |
| `asyncio.iscoroutine(obj)` | 3.4 | True if obj is a coroutine *object* |

## Misc version notes

- `sleep(delay, result=None)`: always suspends; `sleep(0)` yields; NaN delay
  raises ValueError (3.13).
- `wait_for(aw, timeout)`: waits for actual cancellation to finish (total time
  may exceed timeout); since 3.12 implemented via `asyncio.timeout()` and no
  longer wraps the coroutine in a Task for positive timeouts.
- Timeouts nest safely; `Timeout.when()/reschedule()/expired()` available.
