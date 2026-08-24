"""Dependency-free Chapter 24 examples using the least-powerful hooks first."""

from __future__ import annotations

from typing import Any


class Plugin:
    registry: dict[str, type["Plugin"]] = {}

    def __init_subclass__(cls, *, key: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        name = key or cls.__name__.lower()
        if name in Plugin.registry:
            raise ValueError(f"duplicate plugin key: {name}")
        Plugin.registry[name] = cls
        cls.plugin_key = name

    @classmethod
    def __class_getitem__(cls, key: str) -> type["Plugin"]:
        try:
            return cls.registry[key]
        except KeyError as exc:
            raise KeyError(f"unknown plugin: {key}") from exc

    def run(self, value: str) -> str:
        raise NotImplementedError


class Upper(Plugin, key="upper"):
    def run(self, value: str) -> str:
        return value.upper()


class Lower(Plugin, key="lower"):
    def run(self, value: str) -> str:
        return value.lower()


def make_record(name: str, fields: tuple[str, ...]) -> type:
    """Create a small slotted record class with explicit arity checking."""
    if not fields or len(set(fields)) != len(fields):
        raise ValueError("fields must be non-empty and unique")

    def __init__(self, *values: Any) -> None:
        if len(values) != len(fields):
            raise TypeError(f"expected {len(fields)} values, got {len(values)}")
        for field, value in zip(fields, values):
            setattr(self, field, value)

    namespace = {"__slots__": fields, "__init__": __init__}
    return type(name, (), namespace)
