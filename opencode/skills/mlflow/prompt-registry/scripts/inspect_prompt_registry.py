"""Inspect local Prompt Registry APIs without mutating a tracking backend."""

from __future__ import annotations

import importlib
import importlib.metadata
import json


def main() -> None:
    try:
        mlflow = importlib.import_module("mlflow")
    except ImportError:
        print(json.dumps({"mlflow": "not installed"}, indent=2))
        return

    origin = getattr(mlflow, "__file__", None)
    genai = getattr(mlflow, "genai", None)
    names = [
        "register_prompt",
        "load_prompt",
        "set_prompt_alias",
        "delete_prompt_alias",
        "search_prompts",
        "optimize_prompts",
    ]
    try:
        version = importlib.metadata.version("mlflow")
    except importlib.metadata.PackageNotFoundError:
        version = getattr(mlflow, "__version__", None)

    payload = {
        "mlflow_version": version,
        "module_origin": origin,
        "shadowed_or_incomplete": origin is None or genai is None,
        "genai_prompt_capabilities": {
            name: bool(genai and hasattr(genai, name)) for name in names
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
