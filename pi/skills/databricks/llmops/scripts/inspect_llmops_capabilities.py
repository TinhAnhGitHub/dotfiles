"""Inspect local LLMOps dependencies without making workspace mutations."""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import json
import shutil
from typing import Any


def package_state(distribution: str, import_name: str) -> dict[str, Any]:
    try:
        spec = importlib.util.find_spec(import_name)
    except (ImportError, ModuleNotFoundError, ValueError) as exc:
        spec = None
    result: dict[str, Any] = {"available": spec is not None}
    if spec is not None:
        result["origin"] = spec.origin
    result["import_name"] = import_name
    try:
        result["version"] = importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        result["version"] = None
    return result


def import_capabilities(module_name: str, attributes: list[str]) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # Import errors can come from optional dependencies.
        return {"imported": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "imported": True,
        "origin": getattr(module, "__file__", None),
        "attributes": {name: hasattr(module, name) for name in attributes},
    }


def main() -> None:
    payload = {
        "packages": {
            "mlflow": package_state("mlflow", "mlflow"),
            "databricks-sdk": package_state("databricks-sdk", "databricks.sdk"),
            "databricks-agents": package_state("databricks-agents", "databricks.agents"),
            "databricks-vector-search": package_state(
                "databricks-vector-search", "databricks.vector_search"
            ),
        },
        "commands": {
            "databricks": shutil.which("databricks"),
            "git": shutil.which("git"),
        },
        "imports": {
            "mlflow": import_capabilities(
                "mlflow",
                [
                    "genai",
                    "genai.evaluate",
                    "genai.optimize_prompts",
                    "search_traces",
                    "set_active_model",
                    "start_span",
                    "log_feedback",
                    "models.set_model",
                    "pyfunc.ResponsesAgent",
                ],
            ),
            "databricks.agents": import_capabilities(
                "databricks.agents", ["deploy"]
            ),
            "databricks.sdk": import_capabilities(
                "databricks.sdk", ["WorkspaceClient"]
            ),
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
