---
name: uv-scripts
description: >
  Running Python scripts with uv: single-file scripts, inline script metadata (PEP 723),
  executable shebang scripts, script dependencies, script locking, and reproducibility.
---

# uv Scripts

Running single Python files and standalone scripts with uv.

---

## Running Simple Scripts

```bash
uv run script.py                        # Run a script
uv run --no-project script.py           # Run without project context
uv run -                                # Run from stdin
echo 'print("hello")' | uv run -
uv run - << 'EOF' ... EOF               # Here-document
uv run script.py arg1 arg2             # With arguments
uv run --python 3.10 script.py         # Run with specific Python
```

---

## Scripts with Dependencies

**Per-invocation dependencies:**
```bash
uv run --with rich script.py                   # Install rich before running
uv run --with 'rich>12,<13' script.py          # With version constraints
uv run --with pkg1 --with pkg2 script.py       # Multiple packages
```

---

## Inline Script Metadata (PEP 723)

Embed dependencies directly in a script — no `pyproject.toml` needed:

```python
# /// script
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# requires-python = ">=3.12"
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
pprint(list(resp.json().items())[:10])
```

**Creating scripts with inline metadata:**
```bash
uv init --script example.py --python 3.12      # Initialize with metadata
uv add --script example.py 'requests<3' rich   # Add dependencies
```

> **Important:** When inline metadata is present, project dependencies are **ignored** — `--no-project` is not needed.

---

## Executable Shebang Scripts

```python
#!/usr/bin/env -S uv run --script

print("Hello, world!")
```

With dependencies:
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx
print(httpx.get("https://example.com"))
```

Then: `chmod +x greet && ./greet`

---

## Alternative Package Indexes in Scripts

```bash
uv add --index "https://example.com/simple" --script example.py requests rich
```

Results in inline metadata:
```python
# [[tool.uv.index]]
# url = "https://example.com/simple"
```

---

## Script Locking

```bash
uv lock --script example.py
```

Creates `example.py.lock` adjacent to the script for reproducible script execution.

---

## Script Reproducibility

```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2023-10-16T00:00:00Z"
# ///
```

This ensures the script always uses packages published before the specified date.

---

## GUI Scripts (`.pyw`)

On Windows, `uv run example.pyw` uses `pythonw` (no console window).

---

## Documentation

- **Scripts guide:** https://docs.astral.sh/uv/guides/scripts/
