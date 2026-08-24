"""Dependency-free Chapter 23 descriptor examples."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Validated(ABC):
    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{owner.__name__}__{name}"

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: Any, value: Any) -> None:
        setattr(instance, self.storage_name, self.validate(value))

    @abstractmethod
    def validate(self, value: Any) -> Any:
        raise NotImplementedError


class Positive(Validated):
    def validate(self, value: Any) -> float:
        value = float(value)
        if value <= 0:
            raise ValueError(f"{self.public_name} must be positive")
        return value


class NonBlank(Validated):
    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{self.public_name} must be text")
        value = value.strip()
        if not value:
            raise ValueError(f"{self.public_name} must not be blank")
        return value


class LineItem:
    description = NonBlank()
    weight = Positive()

    def __init__(self, description: str, weight: float) -> None:
        self.description = description
        self.weight = weight
