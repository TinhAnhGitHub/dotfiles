"""Print MLflow GenAI capability hints without mutating the environment."""

from __future__ import annotations

import importlib.util
import inspect
import os
from importlib.metadata import PackageNotFoundError, version


def package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def has_symbol(module_name: str, symbol: str) -> bool:
    if importlib.util.find_spec(module_name) is None:
        return False
    try:
        module = __import__(module_name, fromlist=[symbol])
    except Exception:
        return False
    return hasattr(module, symbol)


def signature(module_name: str, symbol: str) -> str | None:
    if not has_symbol(module_name, symbol):
        return None
    try:
        module = __import__(module_name, fromlist=[symbol])
        return str(inspect.signature(getattr(module, symbol)))
    except (ImportError, AttributeError, TypeError, ValueError):
        return "<signature unavailable>"


def main() -> None:
    mlflow_version = package_version("mlflow")
    print(f"mlflow={mlflow_version or 'not installed'}")
    print(f"mlflow-tracing={package_version('mlflow-tracing') or 'not installed'}")
    print(f"databricks-agents={package_version('databricks-agents') or 'not installed'}")
    print(f"tracking_uri_env={os.getenv('MLFLOW_TRACKING_URI', '<unset>')}")
    print(f"databricks_host_set={bool(os.getenv('DATABRICKS_HOST'))}")
    print(f"sql_warehouse_set={bool(os.getenv('MLFLOW_TRACING_SQL_WAREHOUSE_ID'))}")

    if mlflow_version is None:
        return

    checks = [
        ("mlflow.genai", "evaluate"),
        ("mlflow.genai", "optimize_prompts"),
        ("mlflow.genai.scorers", "scorer"),
        ("mlflow.genai.scorers", "ScorerSamplingConfig"),
        ("mlflow.genai.simulators", "ConversationSimulator"),
        ("mlflow.genai.datasets", "create_dataset"),
        ("mlflow", "test"),
        ("mlflow", "log_feedback"),
        ("mlflow", "log_expectation"),
    ]
    for module_name, symbol in checks:
        print(f"{module_name}.{symbol}: {signature(module_name, symbol) or 'unavailable'}")


if __name__ == "__main__":
    main()
