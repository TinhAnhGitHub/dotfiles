---
name: uv-migration
description: >
  Migrating to uv from other Python tools: pyenv, pipx, pip, pip-tools, poetry,
  virtualenv, and hatch. Command equivalents and pyproject.toml migration patterns.
---

# Migrating to uv from Other Tools

Command equivalents and migration patterns for switching to uv.

---

## pyenv -> uv python

```bash
pyenv install 3.12       ->  uv python install 3.12
pyenv versions           ->  uv python list --only-installed
pyenv local 3.12         ->  uv python pin 3.12
pyenv global 3.12        ->  uv python install 3.12 --default
pyenv shell 3.12         ->  uv run -p 3.12 <command>
```

---

## pipx -> uvx

```bash
pipx run ruff            ->  uvx ruff
pipx install ruff        ->  uv tool install ruff
pipx upgrade ruff        ->  uv tool upgrade ruff
pipx list                ->  uv tool list
pipx uninstall ruff      ->  uv tool uninstall ruff
pipx runpip ruff install ->  (not needed, use uvx)
```

---

## pip and pip-tools -> uv pip

```bash
pip install package      ->  uv pip install package
pip install -r req.txt   ->  uv pip install -r req.txt
pip freeze               ->  uv pip freeze
pip list                 ->  uv pip list
pip uninstall package    ->  uv pip uninstall package
pip-compile req.in       ->  uv pip compile req.in
pip-compile --universal  ->  uv pip compile --universal
pip-sync req.txt         ->  uv pip sync req.txt
virtualenv .venv         ->  uv venv
```

---

## virtualenv -> uv

```bash
python -m venv .venv     ->  uv venv
source .venv/bin/activate ->  uv run <command>
deactivate               ->  (not needed, uv run is scoped)
```

---

## Poetry -> uv

### Command Equivalents

```bash
poetry init              ->  uv init
poetry add requests      ->  uv add requests
poetry add -D pytest     ->  uv add --dev pytest
poetry add -G test pytest -> uv add --group test pytest
poetry remove requests   ->  uv remove requests
poetry install           ->  uv sync
poetry run <cmd>         ->  uv run <cmd>
poetry build             ->  uv build
poetry publish           ->  uv publish
poetry lock              ->  uv lock
poetry update            ->  uv lock --upgrade
poetry show              ->  uv pip list
poetry env info          ->  uv python find
poetry self update       ->  (update uv itself)
```

### pyproject.toml Migration

**Poetry format (old):**
```toml
[tool.poetry]
name = "my-package"
version = "0.1.0"
description = "My package"
authors = ["Author <author@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
requests = "^2.31"
pydantic = { version = "^2.0", optional = true }

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
ruff = "^0.8"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.6"

[tool.poetry.extras]
ml = ["pydantic"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

**uv format (new):**
```toml
[project]
name = "my-package"
version = "0.1.0"
description = "My package"
requires-python = ">=3.12"
authors = [{ name = "Author", email = "author@example.com" }]
dependencies = [
    "requests>=2.31",
]

[project.optional-dependencies]
ml = ["pydantic>=2.0"]

[dependency-groups]
dev = [
    { include-group = "lint" },
    { include-group = "test" },
]
lint = ["ruff>=0.8"]
test = ["pytest>=8"]
docs = ["mkdocs>=1.6"]

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"
```

### Key Differences

| Poetry | uv | Notes |
|--------|-----|-------|
| `^2.31` (caret) | `>=2.31` | uv uses standard PEP 440 |
| `[tool.poetry.dependencies]` | `[project] dependencies` | PEP 621 standard |
| `[tool.poetry.group.X.dependencies]` | `[dependency-groups]` | PEP 735 |
| `poetry.lock` | `uv.lock` | Different format |
| `poetry-core` build backend | `uv_build` | Or keep hatchling/flit |
| `~=` (tilde) | `>=X.Y,<X+1` | Use explicit ranges |

---

## Hatch -> uv

```bash
hatch env create         ->  uv sync
hatch run test:pytest    ->  uv run --group test pytest
hatch build              ->  uv build
hatch publish            ->  uv publish
hatch version            ->  uv version
hatch dep show           ->  uv pip list
```

---

## PDM -> uv

```bash
pdm init                 ->  uv init
pdm add requests         ->  uv add requests
pdm install              ->  uv sync
pdm run <cmd>            ->  uv run <cmd>
pdm build                ->  uv build
pdm publish              ->  uv publish
pdm lock                 ->  uv lock
pdm update               ->  uv lock --upgrade
pdm list                 ->  uv pip list
```

---

## Conda -> uv

```bash
conda create -n myenv    ->  uv init my-project
conda activate myenv     ->  uv run <command>
conda install numpy      ->  uv add numpy
conda list               ->  uv pip list
conda env export         ->  uv export --format requirements.txt
```

> **Note:** Conda manages non-Python dependencies (C libraries, etc.) that uv cannot handle. For projects needing conda-only packages (e.g., specific CUDA builds), consider keeping conda for those and using uv for pure-Python deps.

---

## Migration Checklist

1. **Remove old lock files:** `poetry.lock`, `pdm.lock`, `Pipfile.lock`
2. **Convert pyproject.toml:** Update to PEP 621 `[project]` format
3. **Initialize uv:** Run `uv lock` to generate `uv.lock`
4. **Update CI/CD:** Replace tool-specific actions with `astral-sh/setup-uv`
5. **Update Dockerfiles:** Use uv-based installation steps
6. **Update pre-commit:** Add `uv-pre-commit` hooks
7. **Remove old tool configs:** `[tool.poetry]`, `[tool.pdm]`, etc.
8. **Verify:** Run `uv sync --locked` and `uv run pytest`
9. **Commit:** Add `uv.lock` to version control

---

## Documentation

- **Getting started:** https://docs.astral.sh/uv/getting-started/features/
- **Pip compatibility:** https://docs.astral.sh/uv/pip/compatibility/
