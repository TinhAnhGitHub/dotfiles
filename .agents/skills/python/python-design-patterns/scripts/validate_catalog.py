"""Validate the structure and evidence contract of the pattern skills."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT.parent / "python-clean-code"
REQUIRED_FRAMEWORKS = {
    "verl",
    "huggingface-hub",
    "transformers",
    "pydantic-ai",
    "langchain",
    "langgraph",
    "agno",
    "google-adk",
    "vllm",
    "openai-python",
    "mlflow",
    "qwen-agent",
    "openrlhf",
    "slime",
    "dspy",
    "trl",
    "litellm",
}
FRAMEWORK_MARKERS = {
    "verl": ("verl",),
    "huggingface-hub": ("hugging face hub", "huggingface_hub", "hfapi"),
    "transformers": ("transformers",),
    "pydantic-ai": ("pydantic ai", "pydantic_ai", "pydanticai"),
    "langchain": ("langchain",),
    "langgraph": ("langgraph",),
    "agno": ("agno",),
    "google-adk": ("google adk", "google.adk", "google-adk"),
    "vllm": ("vllm",),
    "openai-python": ("openai python", "openai sdk", "openai-python", "from openai"),
    "mlflow": ("mlflow",),
    "qwen-agent": ("qwen-agent", "qwen agent", "qwen_agent"),
    "openrlhf": ("openrlhf",),
    "slime": ("slime",),
    "dspy": ("dspy",),
    "trl": ("trl",),
    "litellm": ("litellm",),
}
ARJAN_2026_DIRS = {
    "apidata",
    "clean",
    "composite",
    "coupling",
    "cqrs",
    "dataclass",
    "dctricks",
    "descriptors",
    "dry",
    "facade",
    "features",
    "flexible",
    "fluent",
    "generators",
    "god",
    "libraries",
    "nested",
    "none",
    "oop",
    "param",
    "pattern",
    "policy",
    "ports",
    "props",
    "spec",
    "state",
    "type",
    "value",
    "webhook",
}
CLEAN_CODE_SOURCE_URLS = {
    "https://github.com/zedr/clean-code-python#table-of-contents",
}
ARJAN_SOURCE_URLS = {
    "https://github.com/ArjanCodes/examples/tree/main/2026",
    "https://www.youtube.com/watch?v=wYeDGkdMi3g",
    "https://github.com/ArjanCodes/examples/tree/main/2026/policy",
    "https://www.youtube.com/watch?v=OeirQdzYdnc",
    "https://github.com/ArjanCodes/examples/tree/main/2026/state",
    "https://www.youtube.com/watch?v=g7EGMWvJ1fI",
    "https://github.com/ArjanCodes/examples/tree/main/2025/registry",
    "https://www.youtube.com/watch?v=SNqwNILX1Gg",
    "https://github.com/ArjanCodes/examples/tree/main/2025/abstraction",
    "https://www.youtube.com/watch?v=YA0Wq1rcs6U",
    "https://github.com/ArjanCodes/examples/tree/main/2024/burn",
    "https://www.youtube.com/watch?v=fsB8_79zI_A",
    "https://github.com/ArjanCodes/2022-adapter",
    "https://www.youtube.com/watch?v=0mcP8ZpUR38",
    "https://github.com/ArjanCodes/2021-composition-vs-inheritance",
    "https://www.youtube.com/watch?v=2ejbLVkCndI",
    "https://github.com/ArjanCodes/2021-dependency-injection-inversion",
    "https://www.youtube.com/watch?v=uxwjXLjJOoM",
    "https://www.youtube.com/watch?v=ss6je4-nDx8",
    "https://www.youtube.com/watch?v=h8ZwhU3PpVw",
    "https://www.youtube.com/watch?v=xns3InDkAiA",
    "https://www.youtube.com/watch?v=RqcEK7sWesQ",
    "https://github.com/ArjanCodes/examples/tree/main/2026/oop",
    "https://www.youtube.com/watch?v=GMBiCMsEsq8",
    "https://github.com/ArjanCodes/examples/tree/main/2025/production",
    "https://www.youtube.com/watch?v=FXwBWS4qDAA",
    "https://github.com/ArjanCodes/examples/tree/main/2026/ports",
    "https://www.youtube.com/watch?v=ENnDxEOAKKc",
    "https://github.com/ArjanCodes/examples/tree/main/2025/lazy",
}
PATTERN_DIRS = (
    "principles",
    "composition",
    "construction",
    "behavior",
    "extensibility",
    "lifecycle",
    "architecture",
    "python-specific",
    "anti-patterns",
)
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)


def check_entrypoint(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\nname:" not in text or "\ndescription:" not in text:
        errors.append(f"{path}: missing required frontmatter")
    if len(text.splitlines()) > 500:
        errors.append(f"{path}: entrypoint exceeds 500 lines")
    if "references/chapters" in text:
        errors.append(f"{path}: chapter-first navigation remains in entrypoint")


def check_links(path: Path, errors: list[str]) -> None:
    text = FENCED_CODE_RE.sub("", path.read_text(encoding="utf-8"))
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (path.parent / target_path).resolve()
        if not resolved.exists():
            errors.append(f"{path}: broken link target {target}")


def check_pattern_pages(errors: list[str]) -> None:
    required_groups = (
        ("## Use when",),
        ("## Why",),
        ("## When not to use",),
        ("## Trade-offs", "## Trade-offs and tests"),
        ("## Tests", "## Trade-offs and tests"),
    )

    def check_tree(tree: Path) -> None:
        for path in sorted(tree.glob("*.md")):
            if path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8")
            for alternatives in required_groups:
                if not any(marker in text for marker in alternatives):
                    errors.append(f"{path}: missing one of {alternatives}")
            if "```python" not in text:
                errors.append(f"{path}: missing Python example")
            if "## Framework examples" not in text:
                errors.append(f"{path}: missing embedded framework examples")
            else:
                examples = text.split("## Framework examples", 1)[1]
                if "https://" not in examples or "```python" not in examples:
                    errors.append(f"{path}: framework examples need a source URL and Python snippet")

    for directory in PATTERN_DIRS:
        check_tree(ROOT / "references" / directory)
    check_tree(CLEAN / "references" / "patterns")


def check_embedded_framework_coverage(errors: list[str]) -> None:
    pages = [
        path
        for directory in PATTERN_DIRS
        for path in sorted((ROOT / "references" / directory).glob("*.md"))
        if path.name != "README.md"
    ]
    pages.extend(sorted((CLEAN / "references" / "patterns").glob("*.md")))
    examples = "\n".join(
        path.read_text(encoding="utf-8").split("## Framework examples", 1)[1].lower()
        for path in pages
        if "## Framework examples" in path.read_text(encoding="utf-8")
    )
    for framework, markers in FRAMEWORK_MARKERS.items():
        if not any(marker in examples for marker in markers):
            errors.append(f"embedded framework examples: missing {framework}")


def check_sources(errors: list[str]) -> None:
    source_path = ROOT / "references" / "sources.json"
    try:
        sources = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{source_path}: invalid JSON ({exc})")
        return
    frameworks = {entry.get("framework") for entry in sources if entry.get("framework")}
    missing = REQUIRED_FRAMEWORKS - frameworks
    if missing:
        errors.append(f"{source_path}: missing framework evidence for {sorted(missing)}")
    urls = {entry.get("url") for entry in sources}
    missing_urls = ARJAN_SOURCE_URLS - urls
    if missing_urls:
        errors.append(f"{source_path}: missing ArjanCodes source URLs {sorted(missing_urls)}")
    missing_clean_urls = CLEAN_CODE_SOURCE_URLS - urls
    if missing_clean_urls:
        errors.append(f"{source_path}: missing clean-code source URLs {sorted(missing_clean_urls)}")
    for index, entry in enumerate(sources):
        for field in ("url", "source_type", "revision_or_version", "fetched", "pattern_ids", "evidence_status"):
            if not entry.get(field):
                errors.append(f"{source_path}: entry {index} missing {field}")


def check_arjancodes_coverage(errors: list[str]) -> None:
    map_path = ROOT / "references" / "provenance" / "arjancodes-2026-map.md"
    try:
        text = map_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{map_path}: cannot read coverage map ({exc})")
        return
    for directory in sorted(ARJAN_2026_DIRS):
        marker = f"| `{directory}` |"
        if marker not in text:
            errors.append(f"{map_path}: missing 2026 directory {directory}")
    if "https://github.com/ArjanCodes/examples/tree/main/2026" not in text:
        errors.append(f"{map_path}: missing complete-tree source URL")


def check_clean_code_coverage(errors: list[str]) -> None:
    map_path = CLEAN / "references" / "provenance" / "zedr-clean-code-python-map.md"
    try:
        text = map_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{map_path}: cannot read clean-code coverage map ({exc})")
        return
    for url in CLEAN_CODE_SOURCE_URLS:
        if url not in text:
            errors.append(f"{map_path}: missing source URL {url}")


def main() -> int:
    errors: list[str] = []
    for path in (ROOT / "SKILL.md", CLEAN / "SKILL.md"):
        check_entrypoint(path, errors)
    for tree in (ROOT, CLEAN / "references" / "patterns"):
        for path in tree.rglob("*.md"):
            check_links(path, errors)
    check_pattern_pages(errors)
    check_embedded_framework_coverage(errors)
    check_sources(errors)
    check_arjancodes_coverage(errors)
    check_clean_code_coverage(errors)
    for cache in ROOT.rglob("__pycache__"):
        errors.append(f"generated cache remains: {cache}")
    if errors:
        print("pattern catalog validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("pattern catalog validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
