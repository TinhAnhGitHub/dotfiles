"""Dependency-free Chapter 22 examples."""

from __future__ import annotations

from collections.abc import Mapping
from functools import cached_property
from keyword import iskeyword
from typing import Any


class Product:
    def __init__(self, name: str, weight: float) -> None:
        self.name = name
        self.weight = weight

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        if value <= 0:
            raise ValueError("weight must be positive")
        self._weight = value

    @cached_property
    def shipping_label(self) -> str:
        return f"{self.name}:{self.weight:g}kg"


class FrozenJSON:
    """A narrow, read-only attribute façade over JSON-like mappings."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self._data = dict(data)

    def __getattr__(self, name: str) -> Any:
        key = name[:-1] if name.endswith("_") else name
        try:
            value = self._data[key]
        except KeyError as exc:
            raise AttributeError(name) from exc
        if isinstance(value, Mapping):
            return type(self)(value)
        if isinstance(value, list):
            return [
                type(self)(item) if isinstance(item, Mapping) else item
                for item in value
            ]
        return value

    def __dir__(self) -> list[str]:
        names = set(super().__dir__())
        names.update(
            key if key.isidentifier() and not iskeyword(key) else f"{key}_"
            for key in self._data
        )
        return sorted(names)
