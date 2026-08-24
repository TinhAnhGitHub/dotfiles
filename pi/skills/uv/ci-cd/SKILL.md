---
name: uv-ci-cd
description: >
  CI/CD integration with uv: GitHub Actions setup, caching strategies, matrix testing,
  PyPI publishing via Trusted Publishing, GitLab CI/CD, private git dependencies,
  and pre-commit integration.
---

# uv CI/CD Integration

Continuous integration and deployment workflows for uv-managed projects.

---

## GitHub Actions — Setup

### Recommended: `astral-sh/setup-uv`

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v6
  with:
    version: "0.11.21"       # Pin specific version
    enable-cache: true       # Built-in caching support
    python-version: "3.12"   # Set Python version (optional)
```

### Using `actions/setup-python` for Python

```yaml
- name: Setup Python
  uses: actions/setup-python@v6
  with:
    python-version-file: ".python-version"
```

Or using `pyproject.toml`:
```yaml
  with:
    python-version-file: "pyproject.toml"
```

---

## Full CI Workflow

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          version: "0.11.21"
          enable-cache: true

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --locked --all-extras --dev

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run ty check

      - name: Test
        run: uv run pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```

---

## Matrix Testing

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12", "3.13"]
steps:
  - uses: astral-sh/setup-uv@v6
    with:
      python-version: ${{ matrix.python-version }}
```

---

## Manual Caching with `actions/cache`

```yaml
env:
  UV_CACHE_DIR: /tmp/.uv-cache
steps:
  - name: Restore uv cache
    uses: actions/cache@v4
    with:
      path: /tmp/.uv-cache
      key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
      restore-keys: |
        uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
        uv-${{ runner.os }}
  - name: Minimize cache
    run: uv cache prune --ci
```

---

## Using `uv pip` in CI

```yaml
env:
  UV_SYSTEM_PYTHON: 1    # Install to system Python (no virtual env needed)
```

Or per-step:
```yaml
- name: Install requirements
  run: uv pip install -r requirements.txt
  env:
    UV_SYSTEM_PYTHON: 1
```

---

## Private Git Dependencies in CI

```yaml
steps:
  - name: Register PAT
    run: echo "${{ secrets.MY_PAT }}" | gh auth login --with-token
  - name: Configure Git credential helper
    run: gh auth setup-git
```

---

## Pre-commit Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.11.21
    hooks:
      - id: uv-sync
      - id: uv-lock
        args: ["--check"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

---

## Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Renovate Configuration

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "matchManagers": ["pep621"],
      "groupName": "all dependencies"
    }
  ]
}
```

---

## Documentation

- **GitHub Actions:** https://docs.astral.sh/uv/guides/integration/github/
- **GitLab CI/CD:** https://docs.astral.sh/uv/guides/integration/gitlab/
- **Pre-commit:** https://docs.astral.sh/uv/guides/integration/pre-commit/
- **Dependabot:** https://docs.astral.sh/uv/guides/integration/dependabot/
- **Renovate:** https://docs.astral.sh/uv/guides/integration/renovate/
