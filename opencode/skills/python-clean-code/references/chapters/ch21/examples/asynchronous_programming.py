"""Dependency-free Chapter 21 examples."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager


async def bounded_map(values: Iterable[int], limit: int = 2) -> list[int]:
    """Run cooperative work with an explicit in-flight limit."""
    if limit < 1:
        raise ValueError("limit must be positive")
    semaphore = asyncio.Semaphore(limit)

    async def one(value: int) -> int:
        async with semaphore:
            await asyncio.sleep(0)
            return value * 2

    return await asyncio.gather(*(one(value) for value in values))


async def stream_values(values: Iterable[int]) -> AsyncIterator[int]:
    for value in values:
        await asyncio.sleep(0)
        yield value


@asynccontextmanager
async def managed_state() -> AsyncIterator[dict[str, bool]]:
    state = {"open": True}
    try:
        yield state
    finally:
        state["open"] = False


async def consume(values: Iterable[int]) -> tuple[list[int], bool]:
    async with managed_state() as state:
        result = [value async for value in stream_values(values)]
    return result, state["open"]
