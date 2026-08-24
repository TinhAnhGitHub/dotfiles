#!/usr/bin/env python3
"""Static coverage checks for the git-usage-skill references.

This intentionally performs only local checks. Network availability and the exact
installed Git version are checked by the skill user with `git --version` and `git -h`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []

    skill = root / "SKILL.md"
    if not skill.exists():
        failures.append("SKILL.md is missing")
    else:
        lines = skill.read_text(encoding="utf-8").splitlines()
        if len(lines) > 500:
            failures.append(f"SKILL.md has {len(lines)} lines; keep it under 500")

    manifest_path = root / "references" / "command-manifest.json"
    catalog_path = root / "references" / "command-catalog.md"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        catalog = catalog_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"cannot read command coverage files: {exc}")
        manifest = {"categories": {}}
        catalog = ""

    commands: set[str] = set()
    for values in manifest.get("categories", {}).values():
        commands.update(values)

    # A catalog entry may be a grouped helper/legacy row, so accept either a literal
    # `git command` invocation or a backticked/bold command-name mention.
    missing: list[str] = []
    for command in sorted(commands):
        patterns = (
            rf"\bgit\s+{re.escape(command)}\b",
            rf"`{re.escape(command)}`",
            rf"\b{re.escape(command)}\b",
        )
        if not any(re.search(pattern, catalog) for pattern in patterns):
            missing.append(command)
    if missing:
        failures.append(
            "commands absent from command-catalog.md: " + ", ".join(missing)
        )

    required_files = [
        "references/README.md",
        "references/source-ledger.md",
        "references/decision-tree.md",
        "references/workflows.md",
        "references/safety-recovery.md",
        "references/command-catalog.md",
        "references/guides-and-book.md",
        "references/command-manifest.json",
    ]
    for relative in required_files:
        if not (root / relative).exists():
            failures.append(f"missing required reference: {relative}")

    if failures:
        print("Coverage check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"Coverage check passed: {len(commands)} manifest command entries are represented."
    )
    print(f"SKILL.md lines: {len(skill.read_text(encoding='utf-8').splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
