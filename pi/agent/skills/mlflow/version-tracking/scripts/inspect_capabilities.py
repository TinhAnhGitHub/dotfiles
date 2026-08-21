"""Inspect local MLflow version-tracking APIs without changing tracking state."""

from __future__ import annotations

import importlib
import json


def dotted_attr(root: object, path: str) -> bool:
    current = root
    for part in path.split("."):
        if not hasattr(current, part):
            return False
        current = getattr(current, part)
    return True


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
        "set_active_model",
        "get_active_model_id",
        "initialize_logged_model",
        "finalize_logged_model",
        "create_external_model",
        "get_logged_model",
        "search_logged_models",
        "last_logged_model",
        "log_model_params",
        "set_logged_model_tags",
        "genai.enable_git_model_versioning",
        "genai.evaluate",
    ]
    print(
        json.dumps(
            {
                "mlflow_version": getattr(mlflow, "__version__", "unknown"),
                "capabilities": {name: dotted_attr(mlflow, name) for name in checks},
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
