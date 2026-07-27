---
name: uv-python
description: >
  Python version management with uv: installing Python versions, pinning versions,
  .python-version file, managed vs system Python, request formats, and discovery order.
---

# uv Python Version Management

uv can install, manage, and discover Python versions — replacing pyenv.

---

## Key Commands

| Command | Description |
|---------|-------------|
| `uv python install 3.12` | Install Python 3.12 (latest patch) |
| `uv python install 3.12.3` | Install exact version |
| `uv python install 3.9 3.10 3.11` | Install multiple versions |
| `uv python install pypy` | Install PyPy |
| `uv python list` | List installed and available |
| `uv python list --all-versions` | All available versions |
| `uv python list --only-installed` | Only installed versions |
| `uv python find` | Find Python executable |
| `uv python find '>=3.11'` | Find matching version |
| `uv python pin 3.12` | Create `.python-version` file |
| `uv python pin --global 3.12` | Create global `.python-version` |
| `uv python upgrade 3.12` | Upgrade to latest patch |
| `uv python upgrade` | Upgrade all managed versions |
| `uv python update-shell` | Add `~/.local/bin` to PATH |

---

## Request Formats

| Format | Example | Description |
|--------|---------|-------------|
| Version | `3`, `3.12`, `3.12.3` | Specific version |
| Specifier | `>=3.12,<3.13` | Version range |
| Free-threaded | `3.13t`, `3.13+freethreaded` | No GIL variant |
| Debug | `3.12.0d`, `3.12+debug` | Debug build |
| Implementation | `cpython`, `cp`, `pypy`, `pp`, `graalpy`, `gp`, `pyodide` | Python impl |
| Combined | `cpython@3.12`, `cp312` | Impl + version |
| Path | `/opt/homebrew/bin/python3` | System interpreter path |

---

## `.python-version` File

- Created by `uv python pin`
- Searched upward from working directory
- Any request format is valid
- Project-bound (won't search beyond project boundary)
- Global file at user config directory

```bash
uv python pin 3.12          # Creates .python-version with "3.12"
uv python pin --global 3.12 # Creates global .python-version
```

---

## Managed vs System Python

| Setting | Values | Description |
|---------|--------|-------------|
| `python-preference` | `managed`, `system`, `only-managed`, `only-system` | Which Python to prefer |
| `python-downloads` | `automatic`, `manual`, `never` | When to download Python |

**Default:** `python-preference = managed` — prefer uv-managed Python over system.

**Free-threaded Python (3.13+):** Not selected by default on 3.13, allowed for 3.14+.

---

## Discovery Order

1. Managed Python installations (`UV_PYTHON_INSTALL_DIR`)
2. `PATH` interpreters (`python`, `python3`, `python3.x`)
3. Windows registry / Microsoft Store interpreters

---

## Important Notes

- CPython distributions come from Astral's `python-build-standalone` (not official Python.org builds)
- Available Python versions are **frozen per uv release** — upgrade uv for newer versions
- Python is installed to `~/.local/bin` as `python3.12` etc.
- Edit `.python-version` to pin project Python version

---

## Documentation

- **Python versions:** https://docs.astral.sh/uv/concepts/python-versions/
- **Installing Python:** https://docs.astral.sh/uv/guides/install-python/
