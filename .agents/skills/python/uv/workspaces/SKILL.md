---
name: uv-workspaces
description: >
  uv workspaces for monorepo setups: shared lockfiles, workspace members,
  inter-package dependencies, workspace layout, and Docker with workspaces.
---

# uv Workspaces (Monorepo)

Workspaces allow multiple packages to share a single lockfile, inspired by Cargo workspaces.

---

## Key Concepts

- Workspace = collection of packages sharing a **single lockfile**
- Each member has its own `pyproject.toml`
- `uv lock` operates on entire workspace
- `uv run` / `uv sync` operate on workspace root by default
- `uv run --package <name>` targets a specific member

---

## Configuration

**Workspace root `pyproject.toml`:**
```toml
[project]
name = "albatross"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["bird-feeder", "tqdm>=4,<5"]

[tool.uv.sources]
bird-feeder = { workspace = true }

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/seeds"]

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"
```

**Member `pyproject.toml`:**
```toml
[project]
name = "bird-feeder"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["anyio>=4,<5"]

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"
```

---

## Workspace Layout

```
albatross/
├── packages/
│   ├── bird-feeder/
│   │   ├── pyproject.toml
│   │   └── src/bird_feeder/__init__.py
│   └── seeds/
│       ├── pyproject.toml
│       └── src/seeds/__init__.py
├── pyproject.toml           # Root workspace config
├── uv.lock                  # Single lockfile for all members
└── src/albatross/main.py
```

### Larger Monorepo Layout

```
my-monorepo/
├── pyproject.toml           # Root workspace config with [tool.uv.workspace]
├── uv.lock                  # Single lockfile for all members
├── packages/
│   ├── core/
│   │   └── pyproject.toml
│   ├── api/
│   │   └── pyproject.toml
│   └── cli/
│       └── pyproject.toml
├── services/
│   └── web-app/
│       └── pyproject.toml
└── shared/
    └── utils/
        └── pyproject.toml
```

---

## Workspace Commands

```bash
uv run --package my-core pytest     # Run in specific member
uv build --package my-core          # Build specific member
uv sync --no-install-workspace      # Install deps, skip workspace members
uv lock                             # Lock entire workspace
```

---

## Key Behaviors

- **Editable installs:** Workspace member dependencies are always editable
- **Shared sources:** `tool.uv.sources` in workspace root applies to all members, unless overridden by a member
- **`requires-python`:** Workspace uses the **intersection** of all members' `requires-python`
- **No isolation:** Python doesn't provide dependency isolation — members may import each other's dependencies

---

## When NOT to Use Workspaces

Use simple path dependencies instead when you need separate virtual environments per member:

```toml
[tool.uv.sources]
bird-feeder = { path = "packages/bird-feeder" }
```

---

## Docker with Workspaces

Use `--no-install-workspace` and `--frozen` in staged Docker builds:

```dockerfile
# Install dependencies first (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace

# Copy all workspace members
COPY . .

# Install workspace members
RUN uv sync --locked
```

---

## Documentation

- **Workspaces:** https://docs.astral.sh/uv/concepts/projects/workspaces/
