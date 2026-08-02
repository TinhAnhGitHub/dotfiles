"""Inspect local MLflow MCP Registry capabilities without contacting any server."""

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

    functions = [
        "genai.register_mcp_server",
        "genai.register_mcp_server_from_url",
        "genai.search_mcp_servers",
        "genai.get_mcp_server_version",
        "genai.get_mcp_server_version_by_alias",
        "genai.get_latest_mcp_server_version",
        "genai.update_mcp_server_version",
        "genai.set_mcp_server_alias",
        "genai.create_mcp_access_endpoint",
        "genai.search_mcp_access_endpoints",
        "genai.refresh_mcp_server_version_tools",
    ]
    try:
        importlib.import_module("mcp")
        mcp_extra = True
    except ImportError:
        mcp_extra = False

    print(
        json.dumps(
            {
                "mlflow_version": getattr(mlflow, "__version__", "unknown"),
                "mcp_package_importable": mcp_extra,
                "capabilities": {name: has_attr(mlflow, name) for name in functions},
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
