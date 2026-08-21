---
name: uv-core
description: >
  Core uv project management: creating projects, managing dependencies, running commands,
  lockfile management, pyproject.toml configuration, dependency groups, entry points,
  build systems, and common patterns/anti-patterns.
---

# uv Core — Project Management

The foundational workflow for uv: creating projects, adding/removing dependencies,
running commands, and managing lockfiles.

---

## Creating Projects

```bash
uv init                        # Create new project (app by default)
uv init --lib my-lib           # Create a library (src layout, implies --package)
uv init --package my-app       # Create a packaged application
uv init --bare my-project      # Minimal pyproject.toml only
uv init --app my-app           # Explicit application creation
uv init --build-backend hatchling my-project  # Choose build backend
```

### Project Structures

**Application (default, no package):**
```
my-app/
├── .python-version
├── README.md
├── main.py
└── pyproject.toml
```

**Library / Packaged App (src layout):**
```
my-lib/
├── .python-version
├── README.md
├── pyproject.toml
├── uv.lock
└── src/
    └── my_lib/
        └── __init__.py
```

**Production-grade project:**
```
my-project/
├── .devcontainer/              # VSCode Dev Container
├── .github/workflows/          # CI/CD workflows
├── docs/                       # Documentation (MkDocs)
├── src/my_package/             # Source code (src layout)
│   └── __init__.py
├── tests/                      # Test suite
│   └── __init__.py
├── .dockerignore
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version             # Pinned Python version
├── Dockerfile
├── pyproject.toml              # Single source of truth
├── README.md
└── uv.lock                     # Committed for reproducibility
```

---

## Managing Dependencies

```bash
uv add requests                # Add dependency
uv add 'requests>=2.31'        # Add with version constraint
uv add --dev pytest            # Add to dev dependency group
uv add --group lint ruff       # Add to named group
uv remove requests             # Remove dependency
uv remove --dev pytest         # Remove from dev group
```

### Dependency Groups (PEP 735)

```toml
[dependency-groups]
dev = [
    { include-group = "lint" },
    { include-group = "test" },
    { include-group = "docs" },
]
lint = ["ruff>=0.8"]
test = ["pytest>=8", "pytest-cov>=5", "coverage>=7"]
docs = ["mkdocs>=1.6", "mkdocs-material>=9"]
```

**Group commands:**
```bash
uv sync --no-dev                 # Exclude dev group
uv sync --only-dev               # Install only dev (no project deps)
uv sync --group lint             # Include specific group
uv sync --only-group lint        # Install only that group
uv sync --no-group docs          # Exclude specific group
uv sync --all-groups             # Include all groups
uv sync --no-default-groups      # Disable all defaults
```

**Default groups setting:**
```toml
[tool.uv]
default-groups = ["dev", "docs"]    # default is ["dev"]
# Or enable all:
default-groups = "all"
```

**Group `requires-python` override:**
```toml
[tool.uv.dependency-groups]
dev = { requires-python = ">=3.12" }
```

---

## Running Commands

```bash
uv run <command>               # Run commands in environment
uv run python -c ""            # Run Python in project environment
uv run -p 3.12 <command>       # Run with specific Python version
uv run --locked <command>      # Run without auto-locking
uv run --frozen <command>      # Run with stale lockfile
uv run --no-sync <command>     # Run without syncing environment
uv run --no-project script.py  # Run without project context
```

---

## Syncing & Lockfiles

```bash
uv sync                        # Install from lockfile
uv sync --locked               # Error if lockfile is outdated (use in CI)
uv sync --frozen               # Skip lockfile check entirely
uv sync --no-dev               # Exclude dev group
uv sync --inexact              # Don't remove extraneous packages
uv lock                        # Create/update lockfile
uv lock --check                # Check if lockfile is up-to-date
uv lock --upgrade              # Upgrade all packages
uv lock --upgrade-package httpx  # Upgrade specific package
uv lock --upgrade-package "httpx==0.28.0"  # Pin to specific version
```

### Partial Installations (Docker-friendly)

```bash
uv sync --no-install-project         # Install deps, skip the project
uv sync --no-install-workspace       # Install deps, skip all workspace members
uv sync --no-install-package torch   # Install everything except torch
```

### Lockfile Export

```bash
uv export --format requirements.txt -o requirements.txt  # To pip-compatible format
uv export --format pylock.toml                           # To PEP 751 standard format
uv export --format cyclonedx1.5                          # To CycloneDX SBOM (in preview)
```

### When Lockfile is Considered Outdated

- Dependencies added/removed from `pyproject.toml`
- Version constraints changed such that locked version is **excluded**
- **NOT outdated** when new package versions are released — explicit upgrade needed

> **Important:** `uv.lock` is universal (all platforms). **Always commit it to version control.**

### Malware Checks (Preview)

```bash
UV_MALWARE_CHECK=1 uv sync    # Check against OSV malicious packages DB
```

---

## pyproject.toml — Full Reference

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "A production Python package"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
authors = [{ name = "Author", email = "author@example.com" }]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.optional-dependencies]
ml = ["torch>=2.0", "numpy>=1.26"]
api = ["fastapi>=0.115", "uvicorn>=0.30"]

[project.scripts]
my-cli = "my_package.cli:main"

[project.gui-scripts]
my-gui = "my_package.gui:main"

[project.entry-points.'my_package.plugins']
plugin-a = "my_package.plugins.a:PluginA"

# --- Dependency Groups (PEP 735) ---
[dependency-groups]
dev = [
    { include-group = "lint" },
    { include-group = "test" },
]
lint = ["ruff>=0.8"]
test = ["pytest>=8", "pytest-cov>=5", "coverage>=7"]
docs = ["mkdocs>=1.6", "mkdocs-material>=9"]

# --- Build System ---
[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"

# --- uv-specific settings ---
[tool.uv]
default-groups = ["dev"]

# --- Tool Configuration ---
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # ruff-specific rules
    "S",    # flake8-bandit (security)
    "FBT",  # flake8-boolean-trap
]
ignore = ["S101"]  # Allow assert in tests

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "FBT"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing -v"
minversion = "8.0"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
```

---

## Entry Points

**CLI scripts:**
```toml
[project.scripts]
hello = "example:hello"
```
Then run: `uv run hello`

**GUI scripts (Windows-specific wrapping):**
```toml
[project.gui-scripts]
hello = "example:app"
```

**Plugin entry points:**
```toml
[project.entry-points.'example.plugins']
a = "example_plugin_a"
```

> **Important:** Entry points require a `[build-system]` definition.

---

## Build Systems

| Backend | Use Case |
|---------|----------|
| `uv_build` | Default, built into uv. Fastest. |
| `hatchling` | Feature-rich, plugin system |
| `flit-core` | Minimal, PEP 621 native |
| `pdm-backend` | PDM ecosystem |
| `setuptools` | Legacy compatibility |
| `maturin` | Rust extensions |
| `scikit-build-core` | C/C++ extensions |

**Key behaviors:**
- uv uses presence of `[build-system]` to decide whether to build/install the project
- Without `[build-system]`, uv installs **only dependencies**, not the project itself
- To force package behavior: `[tool.uv] package = true`
- To disable packaging: `[tool.uv] package = false`

**Build isolation:**
- By default, uv builds all packages in **isolated virtual environments** (PEP 517)
- Disable per-package: `[tool.uv] no-build-isolation-package = ["cchardet"]`
- Augment build dependencies: `[tool.uv.extra-build-dependencies] cchardet = ["cython"]`

---

## Tools (uvx)

**Use when:** Running command-line tools without installation.

```bash
uvx ruff check .                    # Run ruff without installing
uvx ruff@0.8.0 check .             # Specific version
uvx --with pytest pytest tests      # Run with extra deps
uv tool install ruff                # Install globally
uv tool upgrade ruff                # Upgrade installed tool
uv tool list                        # List installed tools
```

> **Safety:** `uvx` runs tools from PyPI by package name. Only run well-known tools. Only use `uv tool install` when specifically requested by the user.

---

## Pip Interface (Legacy)

**Use when:** Legacy workflows with `requirements.txt`, no `uv.lock` present.

```bash
uv venv                                    # Create virtual environment
uv pip install -r requirements.txt         # Install from requirements
uv pip compile requirements.in -o requirements.txt  # Compile
uv pip sync requirements.txt               # Sync environment
uv pip compile --universal requirements.in -o requirements.txt  # Cross-platform
```

> **Don't** use the pip interface unless clearly needed. Don't introduce new `requirements.txt` files. Prefer `uv init` for new projects.

---

## Common Patterns & Anti-patterns

### Don't use pip in uv projects

```bash
# Bad
pip install requests

# Good
uv add requests
```

### Don't run python directly

```bash
# Bad
python script.py
python -c "..."
python3.12 -c "..."

# Good
uv run script.py
uv run python -c "..."
uvx python@3.12 -c "..."
```

### Don't manually manage environments

```bash
# Bad
python -m venv .venv
source .venv/bin/activate

# Good
uv run <command>
```

### Don't commit .venv

```gitignore
# .gitignore
.venv/
```

### Always commit uv.lock

```gitignore
# .gitignore — do NOT ignore uv.lock
# uv.lock should be committed for reproducibility
```

### Use --locked in CI

```bash
# Bad — auto-updates lockfile
uv sync

# Good — errors if lockfile is stale
uv sync --locked
```

---

## Documentation

- **Projects guide:** https://docs.astral.sh/uv/guides/projects/
- **Dependencies:** https://docs.astral.sh/uv/concepts/projects/dependencies/
- **Locking & syncing:** https://docs.astral.sh/uv/concepts/projects/sync/
- **Build backend:** https://docs.astral.sh/uv/concepts/build-backend/
- **CLI reference:** https://docs.astral.sh/uv/reference/cli/
