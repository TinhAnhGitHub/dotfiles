---
name: uv-config
description: >
  uv configuration reference: uv.toml vs pyproject.toml, configuration file priority,
  index configuration (private registries), resolution settings, environment variables,
  caching, and supply chain security.
---

# uv Configuration Reference

Comprehensive reference for configuring uv behavior.

---

## Configuration File Priority

1. Environment variables (highest)
2. Command-line flags
3. `uv.toml` (project-level)
4. `pyproject.toml [tool.uv]` (project-level)
5. User-level `~/.config/uv/uv.toml` (Linux/macOS) or `%APPDATA%\uv\uv.toml` (Windows)
6. System-level `/etc/uv/uv.toml` or `%PROGRAMDATA%\uv\uv.toml`

Settings are merged; project-level takes precedence. Arrays are **concatenated** (project-level first).

---

## `uv.toml` vs `pyproject.toml [tool.uv]`

**`uv.toml`** — No `[tool.uv]` prefix needed:
```toml
cache-dir = "./.uv_cache"
[[index]]
url = "https://test.pypi.org/simple"
default = true
```

**`pyproject.toml [tool.uv]`** — With prefix:
```toml
[tool.uv]
cache-dir = "./.uv_cache"
[[tool.uv.index]]
url = "https://test.pypi.org/simple"
default = true
```

> **Note:** `uv.toml` takes precedence over `pyproject.toml [tool.uv]` if both exist in the same directory.

---

## Index Configuration (Private Registries)

### Basic Additional Index

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
```

### Make an Index the Default (Disables PyPI)

```toml
[[tool.uv.index]]
name = "internal"
url = "https://internal.example.com/simple"
default = true
```

### Explicit Index (Only for Pinned Packages)

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
```

### Publishing to Custom Registries

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

### Authentication via Environment Variables

```bash
UV_INDEX_INTERNAL_PROXY_USERNAME=public
UV_INDEX_INTERNAL_PROXY_PASSWORD=koala
```

(Index name uppercased, non-alphanumeric characters replaced with underscores)

### Flat Indexes (like pip `--find-links`)

```toml
[[tool.uv.index]]
name = "example"
url = "/path/to/directory"
format = "flat"
```

### Index Strategy

| Strategy | Description |
|----------|-------------|
| `first-index` (default) | Stop at first index that has the package. Prevents dependency confusion. |
| `unsafe-first-match` | Search all, prefer first index |
| `unsafe-best-match` | Search all, best from combined set (closest to pip behavior) |

---

## Resolution Settings

| Setting | Values | Description |
|---------|--------|-------------|
| `resolution` | `highest`, `lowest`, `lowest-direct` | Version selection strategy |
| `fork-strategy` | `requires-python`, `fewest` | Multi-platform version handling |
| `prerelease` | `disallow`, `allow`, `if-necessary`, `explicit`, `if-necessary-or-explicit` | Pre-release policy |
| `environments` | List of PEP 508 markers | Limit resolution to specific platforms |
| `required-environments` | List of PEP 508 markers | Require wheels for specific platforms |
| `exclude-newer` | RFC 3339 timestamp | Limit to packages before a date |

### Limiting Resolution to Platforms

```toml
[tool.uv]
environments = [
    "sys_platform == 'darwin'",
    "sys_platform == 'linux'",
]
```

### Requiring Wheels for Specific Platforms

```toml
[tool.uv]
required-environments = [
    "sys_platform == 'linux' and platform_machine == 'x86_64'",
]
```

---

## Constraint & Override Dependencies

**Constraint dependencies (additive restrictions):**
```toml
[tool.uv]
constraint-dependencies = ["grpcio<1.65"]
```

**Override dependencies (absolute, replaces all other constraints):**
```toml
[tool.uv]
override-dependencies = ["werkzeug==2.3.0"]
```

---

## Conflicting Extras/Groups

```toml
[tool.uv]
conflicts = [
    [{ extra = "ml-cpu" }, { extra = "ml-gpu" }],
    [{ group = "dev" }, { group = "prod-only" }],
]
```

---

## Source Overrides

```toml
[tool.uv.sources]
# Local path dependency
my-local-lib = { path = "../my-local-lib", editable = true }

# Git dependency
my-git-lib = { git = "https://github.com/org/repo", rev = "main" }

# Git with tag
my-tagged-lib = { git = "https://github.com/org/repo", tag = "v1.0.0" }

# URL dependency
my-url-lib = { url = "https://example.com/package.tar.gz" }

# Workspace member
my-workspace-lib = { workspace = true }

# Pin to specific index
torch = { index = "pytorch" }
```

---

## Supply Chain Security

### Cooling-off Period

```toml
[tool.uv]
exclude-newer = "2025-06-01T00:00:00Z"  # Only packages published before this date
```

### Malware Detection (Preview)

```bash
UV_MALWARE_CHECK=1 uv sync    # Check against OSV malicious packages DB
```

### Lockfile Integrity

```bash
uv sync --locked              # Error if lockfile is stale
uv lock --check               # Verify lockfile matches pyproject.toml
```

---

## Caching

```bash
uv cache clean                 # Clear entire cache
uv cache clean <package>       # Clear specific package
uv cache prune                 # Remove unused entries
uv cache prune --ci            # Optimize for CI (aggressive pruning)
uv cache dir                   # Show cache directory
```

### Cache Environment Variables

| Variable | Description |
|----------|-------------|
| `UV_CACHE_DIR` | Custom cache directory |
| `UV_NO_CACHE` | Disable caching |

---

## Key Environment Variables

| Variable | Description |
|----------|-------------|
| `UV_PYTHON_INSTALL_DIR` | Where to install Python versions |
| `UV_SYSTEM_PYTHON` | Install to system Python (no venv) |
| `UV_NO_SYNC` | Disable automatic syncing |
| `UV_LOCKED` | Error if lockfile is stale |
| `UV_FROZEN` | Skip lockfile check |
| `UV_COMPILE_BYTECODE` | Compile `.pyc` files |
| `UV_LINK_MODE` | `copy`, `hardlink`, `symlink` |
| `UV_EXCLUDE_NEWER` | Cooling-off period |
| `UV_INDEX_<NAME>_USERNAME` | Index authentication |
| `UV_INDEX_<NAME>_PASSWORD` | Index authentication |
| `UV_PUBLISH_TOKEN` | PyPI publish token |
| `UV_MALWARE_CHECK` | Enable malware detection |

---

## Documentation

- **Settings reference:** https://docs.astral.sh/uv/reference/settings/
- **Configuration files:** https://docs.astral.sh/uv/concepts/configuration-files/
- **Package indexes:** https://docs.astral.sh/uv/concepts/indexes/
- **Environment variables:** https://docs.astral.sh/uv/reference/environment/
- **Caching:** https://docs.astral.sh/uv/concepts/cache/
- **Authentication:** https://docs.astral.sh/uv/concepts/authentication/
