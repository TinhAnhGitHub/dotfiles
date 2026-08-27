"""Inspect installed MLflow GenAI flavor capabilities without loading user models."""

from __future__ import annotations

import importlib
import json


def has_attr(root: object, path: str) -> bool:
    current = root
    for part in path.split("."):
        if not hasattr(current, part):
            return False
        current = getattr(current, part)
    return True


def package_version(name: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(name)
    except Exception:
        return None


def main() -> None:
    try:
        mlflow = importlib.import_module("mlflow")
    except ImportError:
        print(json.dumps({"mlflow": "not installed"}, indent=2))
        return
    if getattr(mlflow, "__file__", None) is None or not hasattr(mlflow, "set_tracking_uri"):
        print(
            json.dumps(
                {
                    "mlflow": "not installed or shadowed by a local namespace package",
                    "module_origin": getattr(mlflow, "__file__", None),
                },
                indent=2,
            )
        )
        return

    checks = [
        "models.set_model",
        "models.predict",
        "pyfunc.PythonModel",
        "pyfunc.ResponsesAgent",
        "pyfunc.log_model",
        "pyfunc.load_model",
        "langchain.log_model",
        "langchain.autolog",
        "dspy.log_model",
        "dspy.autolog",
        "llama_index.log_model",
        "llama_index.autolog",
    ]
    print(
        json.dumps(
            {
                "versions": {
                    "mlflow": getattr(mlflow, "__version__", "unknown"),
                    "langchain": package_version("langchain"),
                    "langgraph": package_version("langgraph"),
                    "dspy": package_version("dspy"),
                    "llama-index": package_version("llama-index"),
                    "pydantic": package_version("pydantic"),
                },
                "capabilities": {name: has_attr(mlflow, name) for name in checks},
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
