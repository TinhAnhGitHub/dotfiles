"""Inspect MLflow registry capabilities and configuration without mutating it."""

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

    client_type = getattr(mlflow, "MlflowClient", None)
    methods = [
        "create_registered_model",
        "create_model_version",
        "copy_model_version",
        "search_registered_models",
        "search_model_versions",
        "set_registered_model_alias",
        "get_model_version_by_alias",
        "set_model_version_tag",
        "create_webhook",
    ]
    client_capabilities = {
        method: bool(client_type and hasattr(client_type, method)) for method in methods
    }
    registry_uri = None
    try:
        registry_uri = mlflow.get_registry_uri()
    except Exception as exc:
        registry_uri = f"unavailable: {type(exc).__name__}: {exc}"

    print(
        json.dumps(
            {
                "mlflow_version": getattr(mlflow, "__version__", "unknown"),
                "registry_uri": registry_uri,
                "fluent_capabilities": {
                    name: has_attr(mlflow, name)
                    for name in [
                        "register_model",
                        "set_registry_uri",
                        "models.infer_signature",
                        "models.set_signature",
                    ]
                },
                "client_capabilities": client_capabilities,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
