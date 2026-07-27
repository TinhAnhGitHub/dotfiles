---
name: uv-templates
description: >
  Production-grade Python project templates using uv: curated list of battle-tested
  scaffolding tools, common tool stacks, project structures, and quick-start guides
  for bootstrapping new Python projects.
---

# Production-Grade Python Templates with uv

Curated templates and patterns for bootstrapping production Python projects.

---

## Recommended Templates

| Template | Stars | Type | Best For |
|----------|-------|------|----------|
| [cookiecutter-uv](https://github.com/osprey-oss/cookiecutter-uv) | ~1.3k | Cookiecutter | Most complete, battle-tested scaffold |
| [uv-docker-example](https://github.com/astral-sh/uv-docker-example) | ~800 | Reference | Official Docker best practices from Astral |
| [python-uv](https://github.com/a5chin/python-uv) | ~370 | Standalone | Full-featured with Nox, Pydantic config |
| [substrate](https://github.com/superlinear-ai/substrate) | ~370 | Copier | Copier updates + GitHub/GitLab dual CI |
| [simple-modern-uv](https://github.com/jlevy/simple-modern-uv) | ~280 | Copier | Minimal + AI agent skill + supply chain security |
| [cookiecutter-fastapi](https://github.com/arthurhenrique/cookiecutter-fastapi) | ~710 | Cookiecutter | FastAPI-specific scaffold with uv |
| [PyStrict](https://github.com/Ranteck/PyStrict-strict-python) | ~190 | Config | Strict type checking + anti-slop patterns |

---

## Quick Start Commands

### cookiecutter-uv (Most Complete)

```bash
uvx cookiecutter gh:osprey-oss/cookiecutter-uv
# Follow prompts for project name, layout, features
```

**Includes:** ruff, mypy/ty, deptry, pytest, codecov, MkDocs, tox-uv, Docker/Podman, devcontainers, GitHub Actions, PyPI publishing

### substrate (Copier-based)

```bash
uvx copier copy gh:superlinear-ai/substrate path/to/repo
# Supports template updates:
uvx copier update --exclude src/ --exclude tests/
```

**Includes:** Poe the Poet, ruff, pre-commit, ty, Conventional Commits, Commitizen, GPG commits, GitHub Actions OR GitLab CI/CD, MkDocs, Dev Containers

### simple-modern-uv (Minimal + Secure)

```bash
uvx copier copy gh:jlevy/simple-modern-uv path/to/repo
```

**Includes:** ruff, basedpyright (strict), dynamic versioning from git tags, AI agent skill, supply chain hardening (cooling-off period, SHA pinning)

---

## Common Tool Stack

| Purpose | Tool | Notes |
|---------|------|-------|
| Package Manager | **uv** | 10-100x faster than pip |
| Linting/Formatting | **ruff** | Replaces Black, isort, Flake8, autoflake, pyupgrade |
| Type Checking | **ty** or **basedpyright** or **mypy** | ty is fastest (Astral); basedpyright is strictest |
| Testing | **pytest** + **coverage** | 75-80% min coverage typical |
| Task Runner | **nox**, **poethepoet**, or **Makefile** | nox is most flexible; poe is simplest |
| Pre-commit | **pre-commit** | Ruff, trailing-whitespace, YAML/TOML validation |
| Docs | **MkDocs** + Material | Most popular for Python projects |
| CI/CD | **GitHub Actions** | `astral-sh/setup-uv` action |
| Docker | Multi-stage with uv | `--no-install-project` for layer caching |
| Versioning | **Dynamic from git tags** | `uv-dynamic-versioning` or `commitizen` |
| Dep Updates | **Renovate** or **Dependabot** | Renovate has better uv support |
| Unused Deps | **deptry** | Detects missing/obsolete dependencies |
| Code Quality | **radon** + **skylos** | Complexity metrics (optional) |

### Type Checker Comparison

| Checker | Speed | Strictness | Notes |
|---------|-------|------------|-------|
| **ty** (Astral) | Fastest | Good | Still in beta, same team as uv/ruff |
| **basedpyright** | Fast | Strictest | TypeScript-style strict mode |
| **pyright** | Fast | Strict | Microsoft, basis for Pylance |
| **mypy** | Slower | Good | Most mature, largest plugin ecosystem |

---

## Production Project Structure

```
my-project/
├── .devcontainer/              # VSCode Dev Container
│   └── devcontainer.json
├── .github/
│   └── workflows/
│       ├── ci.yml              # Lint + test on PR
│       └── publish.yml         # Publish on tag
├── docs/                       # MkDocs documentation
│   └── index.md
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── core.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_core.py
├── .dockerignore
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version             # Pinned Python version
├── Dockerfile
├── Makefile                    # or noxfile.py / poethepoet in pyproject.toml
├── pyproject.toml              # Single source of truth
├── README.md
└── uv.lock                     # Committed for reproducibility
```

---

## Production pyproject.toml Template

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
    "Typing :: Typed",
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

[dependency-groups]
dev = [
    { include-group = "lint" },
    { include-group = "test" },
    { include-group = "docs" },
]
lint = ["ruff>=0.8"]
test = ["pytest>=8", "pytest-cov>=5", "coverage>=7"]
docs = ["mkdocs>=1.6", "mkdocs-material>=9"]

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"

[tool.uv]
default-groups = ["dev"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "TCH", "RUF", "S", "FBT"]
ignore = ["S101"]

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

## Makefile Template

```makefile
.PHONY: help install lint format test coverage build clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --locked

lint:  ## Run linters
	uv run ruff check .
	uv run ty check

format:  ## Format code
	uv run ruff format .
	uv run ruff check --fix .

test:  ## Run tests
	uv run pytest

coverage:  ## Run tests with coverage
	uv run pytest --cov=src --cov-report=term-missing --cov-report=html

build:  ## Build distributions
	uv build

clean:  ## Clean build artifacts
	rm -rf dist/ .coverage htmlcov/ .pytest_cache/
```

---

## Supply Chain Hardening Checklist

- [ ] Set `exclude-newer` for cooling-off period (e.g., 14 days)
- [ ] Pin GitHub Actions to commit SHA (not just version tag)
- [ ] Commit `uv.lock` for reproducible installs
- [ ] Pin uv version in CI (`astral-sh/setup-uv` with `version:`)
- [ ] Use `uv sync --locked` in CI
- [ ] Enable malware checks: `UV_MALWARE_CHECK=1`
- [ ] Vet dependencies before adding
- [ ] Use `deptry` to detect unused/missing dependencies
- [ ] Use `first-index` strategy (default) to prevent dependency confusion

---

## Template Selection Guide

| If you need... | Use... |
|----------------|--------|
| Full-featured scaffold with all options | **cookiecutter-uv** |
| Docker-first project | **uv-docker-example** |
| Template that can be updated later | **substrate** (Copier) |
| Minimal + security-focused | **simple-modern-uv** |
| FastAPI project | **cookiecutter-fastapi** |
| Strict type checking + anti-slop | **PyStrict** |
| Just copy a good pyproject.toml | Production template above |
