# Concurrent Rate-Limited URL Fetching with asyncio

## Solution

```python
import asyncio
from typing import Iterable


async def fetch_url(url: str) -> str:
    """Your existing fetch function (network I/O goes here)."""
    ...


async def fetch_with_error(url: str) -> tuple[str, str | None]:
    """
    Wraps fetch_url so a failure never propagates and kills the batch.
    Returns (url, result) on success, or (url, None) on failure.
    """
    try:
        return url, await fetch_url(url)
    except Exception as e:  # noqa: BLE001 - deliberately broad: we collect failures, not raise them
        print(f"fetch failed for {url}: {e!r}")
        return url, None


async def fetch_all_concurrently(
    urls: Iterable[str],
    concurrency: int = 10,
) -> list[tuple[str, str]]:
    """
    Fetch all URLs concurrently with at most `concurrency` in-flight requests.
    Returns only successful results as (url, body) pairs; failures are logged
    and skipped.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_fetch(url: str) -> tuple[str, str | None]:
        async with semaphore:
            return await fetch_with_error(url)

    # gather(return_exceptions=True) is a second safety net: even if something
    # escapes fetch_with_error (e.g. CancelledError handling quirks or a bug),
    # it won't abort the whole gather — we just filter it out below.
    outcomes = await asyncio.gather(
        *(bounded_fetch(u) for u in urls),
        return_exceptions=True,
    )

    return [
        (url, body)
        for outcome in outcomes
        if isinstance(outcome, tuple)  # skip exception objects
        for url, body in [outcome]
        if body is not None
    ]


# Usage:
#
# results = await fetch_all_concurrently(urls)
#   or from sync code:
# results = asyncio.run(fetch_all_concurrently(urls))
```

## Design choices explained

### 1. Why `asyncio.gather` (not `TaskGroup` or manual tasks)

- `gather` fires all 50 coroutines at once and returns their results **in input order** — so `results[i]` corresponds to `urls[i]`, which keeps the output predictable and testable.
- With `return_exceptions=True`, a failed task becomes an exception *value* in the results list instead of raising. Combined with the per-task `try/except` wrapper, one failure can't take down the rest.

(Python 3.11's `asyncio.TaskGroup` is a good alternative, but it re-raises the first unhandled exception by default and cancels siblings — the opposite of "collect whatever succeeded". You'd need to catch exceptions inside every task anyway, so `gather` is simpler here.)

### 2. Concurrency cap via `asyncio.Semaphore(10)`

- All 50 tasks are created immediately, but each must acquire the semaphore before doing network I/O. Only 10 hold it at any time → **never more than 10 requests in flight**, which respects the API rate limit.
- The semaphore is acquired *around* the actual fetch, not around task creation, so queuing is free and slots are released as soon as each response arrives.

Why not other approaches:

| Alternative | Why not |
|---|---|
| `asyncio.BoundedSemaphore` | Unnecessary — nothing here releases more than once. |
| Chunking into batches of 10 (`for chunk ...: await gather(...)`) | A slow request stalls its whole batch ("head-of-line blocking"). The semaphore keeps exactly 10 in flight continuously — better throughput. |
| Third-party libs (`aiolimiter`, `anyio.CapacityLimiter`) | Overkill for a fixed in-flight cap; stdlib suffices. (If you later need a *requests-per-second* rate limit rather than a concurrency cap, `aiolimiter.AsyncLimiter` is the right tool.) |

### 3. Error handling strategy

- **Inner `try/except`** (`fetch_with_error`): catches failures per-request so the failure is associated with its URL and can be logged meaningfully. Catching broad `Exception` is intentional — the requirement is resilience of the batch, not crash-fast semantics. Note this does *not* catch `asyncio.CancelledError` (it's a `BaseException`), so cancellation/shutdown still works correctly.
- **`return_exceptions=True`** on gather: belt-and-suspenders. Even if an unexpected error type escapes the wrapper, the whole `gather` won't blow up.
- Failed URLs yield `(url, None)` / are filtered out, so you end up with only successes — but you still know which URLs they were if you want retries later.

### 4. Things worth knowing

- **Ordering:** `gather` preserves input order regardless of completion order, so no need to sort afterwards.
- **No timeout shown:** consider wrapping each fetch (`await asyncio.wait_for(fetch_url(url), timeout=30)`) inside `fetch_with_error`; otherwise one hung connection permanently occupies a semaphore slot and effectively reduces your concurrency.
- **Session reuse:** if you're using aiohttp/httpx, create one `ClientSession`/client outside the loop and pass it in — creating a client per request wastes connections and TLS handshakes.
