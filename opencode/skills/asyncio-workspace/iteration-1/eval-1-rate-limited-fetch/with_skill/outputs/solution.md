# Concurrent, failure-tolerant, rate-limited fetching

## Solution

```python
import asyncio


async def fetch_all(urls: list[str]) -> tuple[list[str], list[BaseException]]:
    """Fetch all URLs with at most 10 requests in flight.

    Returns (results, errors): results[i] corresponds to urls[i] for
    successful fetches; failures are collected instead of raised.
    """
    sem = asyncio.Semaphore(10)  # cap concurrent in-flight requests

    async def fetch_limited(url: str):
        async with sem:          # blocks (suspends) here if 10 already in flight
            return await fetch_url(url)

    # return_exceptions=True: one failed fetch does NOT cancel or kill the others
    outcomes = await asyncio.gather(*(fetch_limited(u) for u in urls),
                                    return_exceptions=True)

    results: list[str] = []
    errors: list[BaseException] = []
    for outcome in outcomes:
        if isinstance(outcome, BaseException):
            errors.append(outcome)
        else:
            results.append(outcome)
    return results, errors


async def main() -> None:
    results, errors = await fetch_all(urls)
    print(f"{len(results)} succeeded, {len(errors)} failed")


if __name__ == "__main__":
    asyncio.run(main())
```

## Design choices

### `Semaphore(10)` — the concurrency cap
The skill's sync-primitives guidance lists `Semaphore(n)` as exactly the tool for "limit concurrency to n (rate limiting, connection pools)". Wrapping each fetch in `async with sem:` means at most 10 coroutines are inside the critical section at once. The other 40 tasks exist but are *suspended* at the semaphore acquire point — they cost nothing until a slot frees up. This preserves result-to-URL positional mapping because every URL still gets its own coroutine/task.

Note this caps **concurrency**, not request *rate* per second. If the API limits requests/second rather than simultaneous connections, you'd add a small `await asyncio.sleep(...)` between acquisitions or use a token-bucket — but for a typical rate limiter that counts in-flight requests, the semaphore alone is correct.

### `gather(..., return_exceptions=True)` — collect successes, don't die on failure
The skill explicitly recommends: "`TaskGroup` over `gather` for fail-fast semantics; `gather(return_exceptions=True)` when partial results are acceptable." Here partial results are exactly what we want, so:

- `TaskGroup` is deliberately **not** used — its defining behavior is cancelling all sibling tasks when one raises, which would kill the remaining 49 fetches on the first failure.
- With `return_exceptions=True`, `gather` never propagates child exceptions; it returns exceptions as values in position order, so we can partition into successes and failures afterward.

One subtlety worth knowing (from the skill): even without `return_exceptions=True`, `gather` doesn't cancel siblings when one fails — but it would raise immediately and orphan the still-running results. `return_exceptions=True` makes the intent explicit and lets us wait for everything.

### Why keep per-URL tasks instead of a shared worker pool?
A queue + worker-pool pattern (also covered in the skill) works too, but it adds bookkeeping (`task_done()` pairing, worker cancellation/reaping) for no benefit here. Semaphore-wrapped `gather` is the minimal idiom when the workload fits in memory and you just need bounded fan-out.

### Things I did *not* do, on purpose
- **No bare exception swallowing of `CancelledError`:** if the whole operation is cancelled from outside, `CancelledError` (a `BaseException`) will surface correctly — filtering by `isinstance(BaseException)` collects real errors without interfering with cancellation propagation out of `gather`.
- **No fire-and-forget `create_task`:** all work is owned and awaited by `gather`, so no weak-reference GC risk and no unretrieved-exception warnings.
- **Sequential fallback preserved semantics:** output ordering matches input ordering (`results` are appended in gather's positional order), so callers can still map a result back to its URL via index if needed.

### Optional hardening (if `fetch_url` can hang)
Wrap each fetch in a timeout so one stuck request doesn't hold a semaphore slot forever:

```python
import asyncio

async def fetch_limited(url: str):
    async with sem:
        try:
            async with asyncio.timeout(30):  # Python >= 3.11
                return await fetch_url(url)
        except TimeoutError:
            return f"timeout: {url}"  # or raise a custom error to land in `errors`
```

Per the skill: catch `TimeoutError` *outside* the `asyncio.timeout()` block — the CM converts the internal `CancelledError` to `TimeoutError` at exit.
